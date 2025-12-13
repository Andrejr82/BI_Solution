from typing import Annotated, Dict, Any, List
from pathlib import Path
import json
import os

import polars as pl
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User
from app.config.settings import settings

router = APIRouter(prefix="/learning", tags=["Learning"])

# Paths para dados de aprendizado
FEEDBACK_PATH = Path(settings.LEARNING_FEEDBACK_PATH) if hasattr(settings, 'LEARNING_FEEDBACK_PATH') else Path("data/feedback")
PATTERNS_PATH = Path(settings.LEARNING_EXAMPLES_PATH) if hasattr(settings, 'LEARNING_EXAMPLES_PATH') else Path("data/learning")

os.makedirs(FEEDBACK_PATH, exist_ok=True)
os.makedirs(PATTERNS_PATH, exist_ok=True)

@router.get("/insights", response_model=Dict[str, List[Dict[str, Any]]])
async def get_insights(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Gera insights simples baseados em regras sobre os dados.
    (Placeholder para futura integração com LLM)
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=10000)

        insights = []

        # 1. Top Performer
        if "VENDA_30DD" in df.columns and "NOME" in df.columns:
            try:
                # Converter VENDA_30DD para numérico, tratando strings vazias e erros
                df_clean = df.with_columns([
                    pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0).alias("VENDA_30DD")
                ])

                top = df_clean.sort("VENDA_30DD", descending=True).head(1)
                if len(top) > 0:
                    nome = top["NOME"][0]
                    vendas = top["VENDA_30DD"][0]
                    if vendas and vendas > 0:
                        insights.append({
                            "type": "top_performer",
                            "title": "Produto Campeão de Vendas",
                            "description": f"O produto '{nome}' teve {int(vendas)} vendas nos últimos 30 dias."
                        })
            except Exception as e:
                # Silenciosamente ignorar se não conseguir processar top performer
                pass

        # 2. Stock Alert
        if "ESTOQUE_UNE" in df.columns and "VENDA_30DD" in df.columns:
            try:
                # Converter colunas para numérico, tratando strings vazias
                df_clean = df.with_columns([
                    pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0).alias("VENDA_30DD"),
                    pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0).alias("ESTOQUE_UNE")
                ])

                low_stock = df_clean.filter(
                    (pl.col("VENDA_30DD") > 10) & (pl.col("ESTOQUE_UNE") < 5)
                )
                if len(low_stock) > 0:
                    insights.append({
                        "type": "stock_alert",
                        "title": "Risco de Ruptura",
                        "description": f"{len(low_stock)} produtos com alta venda e estoque baixo."
                    })
            except Exception as e:
                # Silenciosamente ignorar se não conseguir processar stock alert
                pass

        return {"insights": insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback-stats")
async def get_feedback_stats(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """
    Retorna estatísticas de feedback dos usuários.
    """
    try:
        feedback_file = FEEDBACK_PATH / "feedback.jsonl"

        if not feedback_file.exists():
            return {
                "total_feedback": 0,
                "positive": 0,
                "negative": 0,
                "partial": 0,
                "success_rate": 0.0,
                "problematic_queries": []
            }

        # Ler feedback
        feedbacks = []
        with open(feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    feedbacks.append(json.loads(line))
                except:
                    continue

        total = len(feedbacks)
        positive = sum(1 for f in feedbacks if f.get('feedback_type') == 'positive')
        negative = sum(1 for f in feedbacks if f.get('feedback_type') == 'negative')
        partial = sum(1 for f in feedbacks if f.get('feedback_type') == 'partial')

        success_rate = (positive / total * 100) if total > 0 else 0.0

        # Queries problemáticas (com feedback negativo)
        problematic = [
            {
                "query": f.get('comment', 'N/A'),
                "feedback_type": f.get('feedback_type'),
                "timestamp": f.get('timestamp')
            }
            for f in feedbacks if f.get('feedback_type') == 'negative'
        ][:10]

        return {
            "total_feedback": total,
            "positive": positive,
            "negative": negative,
            "partial": partial,
            "success_rate": round(success_rate, 1),
            "problematic_queries": problematic
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feedback stats: {str(e)}")


@router.get("/error-analysis")
async def get_error_analysis(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """
    Analisa erros do sistema de aprendizado.
    """
    try:
        # Simular dados de erro (em produção, ler de logs)
        error_types = {
            "query_timeout": 12,
            "data_not_found": 8,
            "invalid_filter": 5,
            "llm_error": 3,
            "permission_denied": 2
        }

        total_errors = sum(error_types.values())

        error_details = [
            {
                "error_type": "query_timeout",
                "count": 12,
                "suggestion": "Otimize queries complexas ou aumente o timeout"
            },
            {
                "error_type": "data_not_found",
                "count": 8,
                "suggestion": "Verifique se os filtros estão corretos"
            },
            {
                "error_type": "invalid_filter",
                "count": 5,
                "suggestion": "Valide os filtros antes de executar a query"
            }
        ]

        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "error_details": error_details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing errors: {str(e)}")


@router.get("/patterns")
async def get_patterns(
    current_user: Annotated[User, Depends(get_current_active_user)],
    search: str = None
) -> Dict[str, Any]:
    """
    Retorna padrões de queries bem-sucedidas.
    """
    try:
        # Padrões de exemplo (em produção, ler de arquivos de aprendizado)
        patterns = [
            {
                "id": 1,
                "keywords": ["vendas", "top", "produtos"],
                "pattern": "Listar top N produtos por vendas",
                "examples": [
                    "Quais os 10 produtos mais vendidos?",
                    "Top 5 produtos em vendas"
                ],
                "success_count": 45
            },
            {
                "id": 2,
                "keywords": ["ruptura", "estoque", "crítico"],
                "pattern": "Identificar produtos em ruptura",
                "examples": [
                    "Produtos com estoque zerado",
                    "Rupturas críticas"
                ],
                "success_count": 38
            },
            {
                "id": 3,
                "keywords": ["transferência", "UNE", "sugestão"],
                "pattern": "Sugerir transferências entre UNEs",
                "examples": [
                    "Sugerir transferências para UNE 101",
                    "Produtos para transferir"
                ],
                "success_count": 27
            },
            {
                "id": 4,
                "keywords": ["categoria", "segmento", "vendas"],
                "pattern": "Vendas por categoria/segmento",
                "examples": [
                    "Vendas por categoria",
                    "Qual segmento vende mais?"
                ],
                "success_count": 22
            },
            {
                "id": 5,
                "keywords": ["giro", "estoque", "rotatividade"],
                "pattern": "Análise de giro de estoque",
                "examples": [
                    "Produtos com maior giro",
                    "Giro de estoque por UNE"
                ],
                "success_count": 18
            }
        ]

        # Filtrar por busca se fornecido
        if search:
            search_lower = search.lower()
            patterns = [
                p for p in patterns
                if search_lower in p['pattern'].lower() or
                any(search_lower in kw for kw in p['keywords'])
            ]

        return {
            "total_patterns": len(patterns),
            "patterns": patterns
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patterns: {str(e)}")
