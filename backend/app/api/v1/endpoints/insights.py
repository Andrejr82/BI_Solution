"""
AI Insights Endpoints
Proactive AI-powered business insights
"""

from typing import Any, List
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.infrastructure.database.models import User
from app.core.llm_gemini_adapter import GeminiLLMAdapter
from app.infrastructure.data.hybrid_adapter import HybridDataAdapter
from app.core.data_scope_service import DataScopeService
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
    try:
        # Initialize adapters
        data_adapter = HybridDataAdapter()
        llm_adapter = GeminiLLMAdapter()
        data_scope = DataScopeService()

        # Get user segments
        segments = data_scope.get_user_segments(current_user)

        # Collect business metrics
        insights_data = []

        # 1. Sales Trends Analysis
        sales_query = """
        SELECT TOP 10
            SEGMENTO,
            SUM(QtdVenda) as total_vendas,
            SUM(VrVenda) as receita_total,
            COUNT(DISTINCT CODPRODUTO) as produtos_vendidos
        FROM AdmMatao
        WHERE SEGMENTO IN ({})
        GROUP BY SEGMENTO
        ORDER BY receita_total DESC
        """.format(','.join(f"'{s}'" for s in segments))

        try:
            sales_df = await data_adapter.execute_query(sales_query)
            if not sales_df.empty:
                insights_data.append({
                    "type": "sales",
                    "data": sales_df.to_dict('records')
                })
        except Exception as e:
            logger.warning(f"Sales query failed: {e}")

        # 2. Stock Rupture Analysis
        rupture_query = """
        SELECT TOP 10
            NOMPRODUTO,
            CODPRODUTO,
            QtdEstoque,
            QtdVenda,
            SEGMENTO,
            CASE WHEN QtdEstoque = 0 THEN 1 ELSE 0 END as is_rupture
        FROM AdmMatao
        WHERE SEGMENTO IN ({})
            AND QtdEstoque < QtdVenda * 0.5
        ORDER BY QtdVenda DESC
        """.format(','.join(f"'{s}'" for s in segments))

        try:
            rupture_df = await data_adapter.execute_query(rupture_query)
            if not rupture_df.empty:
                insights_data.append({
                    "type": "rupture",
                    "data": rupture_df.to_dict('records')
                })
        except Exception as e:
            logger.warning(f"Rupture query failed: {e}")

        # 3. High Value Products
        high_value_query = """
        SELECT TOP 10
            NOMPRODUTO,
            CODPRODUTO,
            VrVenda,
            QtdVenda,
            (VrVenda / NULLIF(QtdVenda, 0)) as preco_medio,
            SEGMENTO
        FROM AdmMatao
        WHERE SEGMENTO IN ({})
            AND QtdVenda > 0
        ORDER BY VrVenda DESC
        """.format(','.join(f"'{s}'" for s in segments))

        try:
            high_value_df = await data_adapter.execute_query(high_value_query)
            if not high_value_df.empty:
                insights_data.append({
                    "type": "high_value",
                    "data": high_value_df.to_dict('records')
                })
        except Exception as e:
            logger.warning(f"High value query failed: {e}")

        # Generate insights using Gemini
        prompt = f"""
Você é um analista de BI expert. Analise os dados abaixo e gere 3-5 insights acionáveis.

**Dados Disponíveis:**
{insights_data}

**Suas tarefas:**
1. Identifique padrões, tendências e anomalias
2. Destaque oportunidades de negócio
3. Sinalize riscos potenciais
4. Forneça recomendações práticas

**Formato da resposta (JSON):**
```json
{{
  "insights": [
    {{
      "id": "unique-id-1",
      "title": "Título curto do insight",
      "description": "Descrição detalhada do que foi identificado",
      "category": "trend|anomaly|opportunity|risk",
      "severity": "low|medium|high",
      "recommendation": "Ação recomendada específica",
      "data_points": [{{ "key": "value" }}]
    }}
  ]
}}
```

Seja conciso, objetivo e focado em ações práticas. Use dados quantitativos sempre que possível.
"""

        # Call Gemini
        response = await llm_adapter.generate_response(prompt)

        # Parse JSON response
        import json
        import re

        # Extract JSON from response (handles markdown code blocks)
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        insights_response = json.loads(json_str)

        # Format insights with timestamps
        formatted_insights = []
        for idx, insight in enumerate(insights_response.get('insights', [])):
            formatted_insights.append(InsightResponse(
                id=insight.get('id', f"insight-{idx}"),
                title=insight['title'],
                description=insight['description'],
                category=insight['category'],
                severity=insight['severity'],
                recommendation=insight.get('recommendation'),
                data_points=insight.get('data_points'),
                created_at=datetime.utcnow().isoformat()
            ))

        return InsightsListResponse(
            insights=formatted_insights,
            total=len(formatted_insights),
            generated_at=datetime.utcnow().isoformat()
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights. Please try again."
        )
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
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
    data_scope = DataScopeService()
    segments = data_scope.get_user_segments(current_user)

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
