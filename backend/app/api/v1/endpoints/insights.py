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
from app.core.llm_gemini_adapter_v2 import GeminiLLMAdapterV2 as GeminiLLMAdapter
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
    data_points: List[Any] | None
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
    Gera insights de varejo modernos e proativos usando IA.
    Analisa tendências, riscos de ruptura e oportunidades de mix.
    """
    logger.info(f"🧠 Gerando insights modernos para: {current_user.username} (Role: {current_user.role})")
    try:
        llm_adapter = GeminiLLMAdapter()
        
        # Obtém o dataframe já filtrado por escopo (Segmentos do Usuário ou Global para Admin)
        df_raw = data_scope_service.get_filtered_dataframe(current_user)
        
        if df_raw.is_empty():
            return InsightsListResponse(insights=[], total=0, generated_at=datetime.utcnow().isoformat())

        # Coleta de métricas avançadas usando Polars para alta performance
        # Garantir tipos numéricos para cálculos, tratando strings vazias
        def safe_cast_col(col_name):
            return pl.col(col_name).cast(pl.Utf8).str.strip_chars().replace("", None).cast(pl.Float64).fill_null(0)

        df_numeric = df_raw.with_columns([
            safe_cast_col("VENDA_30DD"),
            safe_cast_col("MES_01"),
            safe_cast_col("MES_02"),
            safe_cast_col("ESTOQUE_UNE"),
            safe_cast_col("ESTOQUE_CD")
        ])

        insights_context = []

        # 1. Resumo Executivo (Macro)
        exec_summary = df_numeric.select([
            pl.col("VENDA_30DD").sum().alias("vendas_totais"),
            pl.col("MES_01").sum().alias("receita_atual"),
            pl.col("MES_02").sum().alias("receita_anterior"),
            pl.col("ESTOQUE_UNE").sum().alias("estoque_lojas"),
            pl.col("ESTOQUE_CD").sum().alias("estoque_cd"),
            pl.col("PRODUTO").n_unique().alias("skus_ativos")
        ]).to_dicts()[0]
        
        # Calcular crescimento MoM
        if exec_summary["receita_anterior"] > 0:
            growth = ((exec_summary["receita_atual"] - exec_summary["receita_anterior"]) / exec_summary["receita_anterior"]) * 100
            exec_summary["crescimento_mom"] = round(growth, 2)
        else:
            exec_summary["crescimento_mom"] = 0
        
        insights_context.append({"type": "executive_summary", "data": exec_summary})

        # 2. Top Categorias/Segmentos por Performance
        group_col = "NOMESEGMENTO" if current_user.role == "admin" else "NOMECATEGORIA"
        if group_col in df_numeric.columns:
            top_performers = df_numeric.group_by(group_col).agg([
                pl.col("MES_01").sum().alias("receita"),
                pl.col("VENDA_30DD").sum().alias("unidades"),
                (pl.col("ESTOQUE_UNE").sum() / (pl.col("VENDA_30DD").sum().clip(0.01) / 30)).alias("cobertura_dias")
            ]).sort("receita", descending=True).head(5).to_dicts()
            
            insights_context.append({"type": "top_categories", "data": top_performers})

        # 3. Alertas de Ruptura e Estoque Crítico
        venda_media = df_numeric.select(pl.col("VENDA_30DD").mean()).item() or 0
        df_critical = df_numeric.filter(
            (pl.col("VENDA_30DD") > venda_media) & 
            (pl.col("ESTOQUE_UNE") < (pl.col("VENDA_30DD") / 30 * 5))
        ).sort("VENDA_30DD", descending=True).head(5).select([
            "NOME", "VENDA_30DD", "ESTOQUE_UNE", "ESTOQUE_CD", "NOMESEGMENTO"
        ]).to_dicts()
        
        if df_critical:
            insights_context.append({"type": "critical_stock_alerts", "data": df_critical})

        # Preparar o Prompt para o Especialista em Varejo
        context_description = "todos os segmentos da rede" if current_user.role == "admin" else f"seu segmento específico ({', '.join(current_user.segments_list)})";
        
        prompt = f"""
        Você é um Diretor de BI da Caculinha (Varejo de Armarinhos/Tecidos).
        Analise os dados abaixo para o usuário {current_user.username}, que tem visão sobre {context_description}.
        
        DADOS ESTRUTURADOS:
        {json.dumps(insights_context, indent=2, ensure_ascii=False)}
        
        SUA TAREFA:
        Gere 4 insights estratégicos e modernos seguindo estas diretrizes:
        1. TENDÊNCIA: Analise o crescimento MoM e o que ele indica.
        2. EFICIÊNCIA: Comente sobre a 'cobertura_dias'. Ideal é entre 15-30 dias. Menos é risco, mais é capital parado.
        3. PARETO: Identifique se há concentração excessiva em poucos SKUs ou categorias.
        4. AÇÃO: Cada insight DEVE ter uma recomendação prática (Ex: 'Transferir X do CD', 'Realizar queima de estoque', 'Aumentar pedido de compra').

        REGRAS DE FORMATO:
        - Retorne APENAS um objeto JSON.
        - Linguagem: Português PT-BR profissional mas direta.
        - Categorias: 'trend', 'anomaly', 'opportunity', 'risk'.
        - Severidade: 'low', 'medium', 'high'.

        ESTRUTURA DO JSON:
        {{
            "insights": [
                {{
                    "id": "unique-id",
                    "title": "Título Impactante",
                    "description": "Explicação baseada em números reais",
                    "category": "risk",
                    "severity": "high",
                    "recommendation": "Ação sugerida",
                    "data_points": [] 
                }}
            ]
        }}
        """

        # Chamada ao Gemini
        response = await llm_adapter.generate_response(prompt)
        
        # Limpeza e parse do JSON
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            try:
                insights_response = json.loads(json_match.group(1))
            except:
                logger.error("Erro ao parsear JSON do Gemini")
                raise Exception("AI Response parsing failed")
        else:
            raise Exception("No JSON found in AI response")

        # Formatação final
        formatted_insights = [
            InsightResponse(
                id=i.get('id', f"ins-{idx}"),
                title=i.get('title', 'Insight Estratégico'),
                description=i.get('description', ''),
                category=i.get('category', 'opportunity'),
                severity=i.get('severity', 'medium'),
                recommendation=i.get('recommendation'),
                data_points=i.get('data_points', []),
                created_at=datetime.utcnow().isoformat()
            )
            for idx, i in enumerate(insights_response.get('insights', []))
        ]

        return InsightsListResponse(
            insights=formatted_insights,
            total=len(formatted_insights),
            generated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"❌ Erro em Proactive Insights: {str(e)}", exc_info=True)
        return InsightsListResponse(
            insights=[
                InsightResponse(
                    id="err-1",
                    title="Análise em processamento",
                    description="Estamos consolidando os dados do seu segmento para gerar novos insights.",
                    category="trend",
                    severity="low",
                    recommendation="Tente atualizar em alguns instantes.",
                    data_points=[],
                    created_at=datetime.utcnow().isoformat()
                )
            ],
            total=1,
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
