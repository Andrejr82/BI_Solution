"""
AI Insights Endpoints
Proactive AI-powered business insights
"""

from typing import Any, List
from datetime import datetime, timedelta
import logging
import json
import re
import polars as pl

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.infrastructure.database.models import User
from app.core.llm_gemini_adapter import GeminiLLMAdapter
from app.infrastructure.data.hybrid_adapter import HybridDataAdapter
from app.core.data_scope_service import data_scope_service
from app.config.settings import settings

router = APIRouter(prefix="/insights", tags=["AI Insights"])
logger = logging.getLogger(__name__)


# Pydantic Models
class InsightResponse(BaseModel):
    """AI-generated insight"""
    id: str
    title: str
    description: str
    category: str  # trend, anomaly, opportunity, risk
    severity: str  # low, medium, high
    recommendation: str | None
    data_points: List[dict] | None
    created_at: str


class InsightsListResponse(BaseModel):
    """List of insights"""
    insights: List[InsightResponse]
    total: int
    generated_at: str


@router.get("/proactive", response_model=InsightsListResponse)
async def get_proactive_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get AI-powered proactive insights based on current business data.

    Analyzes recent data and generates intelligent insights about:
    - Sales trends
    - Inventory anomalies
    - Revenue opportunities
    - Stock risks
    """
    logger.info(f"🧠 Proactive Insights solicitado por: {current_user.username}")
    try:
        # Initialize adapters
        llm_adapter = GeminiLLMAdapter()
        
        # Get filtered dataframe using singleton service (Fast & Secure)
        df = data_scope_service.get_filtered_dataframe(current_user)
        
        # Collect business metrics using Polars
        insights_data = []

        # Helper to safely get column
        def get_col(candidates, default=None):
            for c in candidates:
                if c in df.columns: return c
            return default

        # Map columns based on ADMMAT schema
        col_segment = get_col(["NOMESEGMENTO", "SEGMENTO", "CATEGORIA"], "SEGMENTO")
        col_sales = get_col(["VENDA_30DD", "QtdVenda", "VENDA"], "VENDA_30DD")
        col_revenue = get_col(["MES_01", "VrVenda", "RECEITA"], "MES_01")
        col_stock = get_col(["ESTOQUE_UNE", "QtdEstoque"], "ESTOQUE_UNE")
        col_product = get_col(["PRODUTO", "CODPRODUTO"], "PRODUTO")
        col_name = get_col(["NOME", "NOMPRODUTO"], "NOME")

        # 1. Sales Trends Analysis (Aggregated by Segment)
        if col_segment and col_sales and col_revenue:
            try:
                # Group by Segment
                df_sales = df.group_by(col_segment).agg([
                    pl.col(col_sales).sum().alias("total_vendas"),
                    pl.col(col_revenue).sum().alias("receita_total"),
                    pl.col(col_product).n_unique().alias("produtos_vendidos")
                ]).sort("receita_total", descending=True).head(10)
                
                sales_data = df_sales.to_dicts()
                if sales_data:
                    insights_data.append({
                        "type": "sales_by_segment",
                        "data": sales_data
                    })
            except Exception as e:
                logger.warning(f"Sales analysis failed: {e}")

        # 2. Stock Rupture Analysis (Low Stock items)
        if col_name and col_stock and col_sales:
            try:
                # Filter potential ruptures: Stock < 10% of monthly sales
                df_rupture = df.filter(
                    (pl.col(col_stock).cast(pl.Float64).fill_null(0) < (pl.col(col_sales).cast(pl.Float64).fill_null(0) * 0.1)) &
                    (pl.col(col_sales).cast(pl.Float64).fill_null(0) > 0)
                ).sort(col_sales, descending=True).head(10).select([
                    col_name, col_stock, col_sales, col_segment
                ])

                rupture_data = df_rupture.to_dicts()
                if rupture_data:
                    insights_data.append({
                        "type": "critical_ruptures",
                        "data": rupture_data
                    })
            except Exception as e:
                logger.warning(f"Rupture analysis failed: {e}")

        # 3. High Value Products (Pareto/ABC)
        if col_name and col_revenue:
            try:
                df_high_value = df.sort(col_revenue, descending=True).head(10).select([
                    col_name, col_revenue, col_sales, col_segment
                ])
                
                high_value_data = df_high_value.to_dicts()
                if high_value_data:
                    insights_data.append({
                        "type": "top_revenue_products",
                        "data": high_value_data
                    })
            except Exception as e:
                logger.warning(f"High value analysis failed: {e}")

        # Generate insights using Gemini
        try:
            # Call Gemini
            response = await llm_adapter.generate_response(prompt)
            
            # Log raw response for debugging (truncated)
            logger.info(f"🤖 Gemini Raw Response: {response[:200]}...")

            # Extract JSON from response (handles markdown code blocks)
            # Regex robusto para capturar JSON dentro ou fora de blocos de código
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Tenta encontrar o primeiro { e o último }
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                else:
                    json_str = response

            insights_response = json.loads(json_str)

        except Exception as llm_error:
            logger.error(f"❌ Falha no LLM ou Parse: {llm_error}. Usando fallback.")
            # Fallback seguro para não quebrar o frontend
            insights_response = {
                "insights": [
                    {
                        "id": "fallback-1",
                        "title": "Análise de Dados Disponível",
                        "description": "Os dados foram processados com sucesso, mas a análise detalhada da IA está temporariamente indisponível.",
                        "category": "opportunity",
                        "severity": "low",
                        "recommendation": "Verifique os gráficos de KPI para análise manual.",
                        "data_points": []
                    }
                ]
            }

        # Format insights with timestamps
        formatted_insights = []
        for idx, insight in enumerate(insights_response.get('insights', [])):
            formatted_insights.append(InsightResponse(
                id=insight.get('id', f"insight-{idx}"),
                title=insight.get('title', 'Insight Gerado'),
                description=insight.get('description', 'Sem descrição disponível.'),
                category=insight.get('category', 'opportunity'),
                severity=insight.get('severity', 'low'),
                recommendation=insight.get('recommendation'),
                data_points=insight.get('data_points'),
                created_at=datetime.utcnow().isoformat()
            ))

        return InsightsListResponse(
            insights=formatted_insights,
            total=len(formatted_insights),
            generated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"🔥 Erro Crítico em Proactive Insights: {e}", exc_info=True)
        # Última linha de defesa: retornar lista vazia em vez de 500
        return InsightsListResponse(
            insights=[],
            total=0,
            generated_at=datetime.utcnow().isoformat()
        )


@router.get("/anomalies")
async def detect_anomalies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Detect anomalies in sales and stock data using AI.

    Returns unusual patterns that require attention.
    """
    data_adapter = HybridDataAdapter()
    segments = data_scope_service.get_user_segments(current_user)

    # Detect sudden drops in sales
    anomaly_query = """
    SELECT
        NOMPRODUTO,
        CODPRODUTO,
        QtdVenda,
        VrVenda,
        QtdEstoque,
        SEGMENTO
    FROM AdmMatao
    WHERE SEGMENTO IN ({})
        AND (
            QtdEstoque = 0 AND QtdVenda > 100
            OR QtdVenda = 0 AND QtdEstoque > 1000
        )
    ORDER BY QtdVenda DESC
    """.format(','.join(f"'{s}'" for s in segments))

    try:
        anomalies_df = await data_adapter.execute_query(anomaly_query)

        return {
            "anomalies": anomalies_df.to_dict('records') if not anomalies_df.empty else [],
            "count": len(anomalies_df),
            "detected_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting anomalies: {str(e)}"
        )


@router.post("/ask")
async def ask_insight_question(
    question: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ask a specific question about business insights.

    Example: "What products should I restock urgently?"
    """
    llm_adapter = GeminiLLMAdapter()

    prompt = f"""
Você é um assistente de BI. Responda a seguinte pergunta de negócio:

**Pergunta:** {question}

Forneça uma resposta clara, objetiva e com recomendações acionáveis.
Se precisar de dados específicos, mencione quais consultas seriam úteis.
"""

    try:
        response = await llm_adapter.generate_response(prompt)

        return {
            "question": question,
            "answer": response,
            "answered_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )
