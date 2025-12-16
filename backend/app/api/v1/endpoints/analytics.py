"""
Analytics Endpoints
Data analysis, metrics, export and custom queries
"""

from typing import Annotated, List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.api.dependencies import get_current_active_user
from app.infrastructure.database.models import User
from app.core.monitoring.metrics_dashboard import MetricsDashboard
from app.config.settings import settings # For initializing MetricsDashboard

logger = logging.getLogger(__name__)

# Initialize MetricsDashboard globally
# In a larger application, consider dependency injection or FastAPI lifespan events.
metrics_dashboard: Optional[MetricsDashboard] = None

# @Deprecate this global initialization in favor of FastAPI's lifespan events. This is for quick setup.
def _initialize_metrics_dashboard():
    global metrics_dashboard
    if metrics_dashboard is None:
        metrics_dashboard = MetricsDashboard(
            query_history=None, # Will use default from settings in MetricsDashboard
            response_cache=None # Will use default from settings in MetricsDashboard
        )
        logger.info("MetricsDashboard initialized.")

_initialize_metrics_dashboard()

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class MetricsSummary(BaseModel):
    total_queries: int
    total_errors: int
    success_rate_feedback: float
    cache_hit_rate: float
    average_response_time_ms: str


class ErrorTrendItem(BaseModel):
    date: str
    error_count: int


class TopQueryItem(BaseModel):
    query: str
    count: int


@router.get("/kpis", response_model=MetricsSummary)
async def get_kpis(
    current_user: Annotated[User, Depends(get_current_active_user)],
    days: int = Query(7, description="Number of days to look back for metrics"),
) -> MetricsSummary:
    """
    Retrieves key performance indicators (KPIs) for the agent system.
    (T4.4.1: GET /analytics/kpis)
    """
    if metrics_dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MetricsDashboard not initialized."
        )
    try:
        kpis = metrics_dashboard.get_metrics(days=days)
        return MetricsSummary(**kpis)
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching KPIs: {str(e)}"
        )


@router.get("/error-trend", response_model=List[ErrorTrendItem])
async def get_error_trend(
    current_user: Annotated[User, Depends(get_current_active_user)],
    days: int = Query(30, description="Number of days to look back for error trend"),
) -> List[ErrorTrendItem]:
    """
    Provides a daily trend of errors for the agent system.
    (T4.4.1: GET /analytics/error-trend)
    """
    if metrics_dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MetricsDashboard not initialized."
        )
    try:
        trend = metrics_dashboard.get_error_trend(days=days)
        return [ErrorTrendItem(**item) for item in trend]
    except Exception as e:
        logger.error(f"Error fetching error trend: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching error trend: {str(e)}"
        )


@router.get("/top-queries", response_model=List[TopQueryItem])
async def get_top_queries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    days: int = Query(7, description="Number of days to look back for top queries"),
    limit: int = Query(10, description="Maximum number of top queries to return"),
) -> List[TopQueryItem]:
    """
    Identifies the most frequent queries made to the agent system.
    (T4.4.1: GET /analytics/top-queries)
    """
    if metrics_dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MetricsDashboard not initialized."
        )
    try:
        top_queries = metrics_dashboard.get_top_queries(days=days, limit=limit)
        return [TopQueryItem(**item) for item in top_queries]
    except Exception as e:
        logger.error(f"Error fetching top queries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching top queries: {str(e)}"
        )


@router.get("/filter-options")
async def get_filter_options(
    current_user: Annotated[User, Depends(get_current_active_user)],
    segmento: Optional[str] = Query(None, description="Segmento para filtrar as categorias retornadas")
) -> Dict[str, List[str]]:
    """
    Retorna valores únicos de categoria e segmento para os filtros.
    Pode filtrar categorias por um segmento específico.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=50000)

        categorias = []
        segmentos = []
        
        # Filtrar o DataFrame pelo segmento se fornecido
        if segmento and "NOMESEGMENTO" in df.columns:
            df = df.filter(pl.col("NOMESEGMENTO").str.to_lowercase() == segmento.lower())

        # Categorias únicas
        if "NOMECATEGORIA" in df.columns:
            cat_unique = df.select("NOMECATEGORIA").unique().sort("NOMECATEGORIA")
            for row in cat_unique.iter_rows(named=True):
                cat = str(row["NOMECATEGORIA"]).strip()
                if cat and cat != "null" and cat != "None":
                    categorias.append(cat)

        # Segmentos únicos (sempre da base original, não filtrada por categoria)
        df_all_segments = data_scope_service.get_filtered_dataframe(current_user, max_rows=50000)
        if "NOMESEGMENTO" in df_all_segments.columns:
            seg_unique = df_all_segments.select("NOMESEGMENTO").unique().sort("NOMESEGMENTO")
            for row in seg_unique.iter_rows(named=True):
                seg = str(row["NOMESEGMENTO"]).strip()
                if seg and seg != "null" and seg != "None":
                    segmentos.append(seg)

        return {
            "categorias": categorias,
            "segmentos": segmentos
        }

    except Exception as e:
        logger.error(f"Error getting filter options: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting filter options: {str(e)}"
        )


@router.get("/sales-analysis")
async def get_sales_analysis(
    current_user: Annotated[User, Depends(get_current_active_user)],
    categoria: Optional[str] = Query(None),
    segmento: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """
    Análise de vendas e estoque com gráficos.
    Retorna dados para gráficos de vendas por categoria, giro de estoque e distribuição ABC.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=50000)

        # Determinar nomes corretos das colunas
        categoria_col = "NOMECATEGORIA" if "NOMECATEGORIA" in df.columns else ("CATEGORIA" if "CATEGORIA" in df.columns else None)
        segmento_col = "NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else ("SEGMENTO" if "SEGMENTO" in df.columns else None)

        # Aplicar filtros se fornecidos (exato, case-insensitive)
        if categoria and categoria_col:
            df = df.filter(pl.col(categoria_col).str.to_lowercase() == categoria.lower())
        if segmento and segmento_col:
            df = df.filter(pl.col(segmento_col).str.to_lowercase() == segmento.lower())

        # 1. Vendas por Categoria
        vendas_categoria = []
        if categoria_col:
            df_cat = df.group_by(categoria_col).agg([
                pl.col("VENDA_30DD").sum().alias("vendas")
            ]).sort("vendas", descending=True).head(10)

            for row in df_cat.iter_rows(named=True):
                cat = str(row[categoria_col]).strip()
                if cat and cat != "null" and cat != "None":
                    vendas_categoria.append({
                        "categoria": cat[:30],
                        "vendas": int(row["vendas"])
                    })

        # 2. Giro de Estoque (vendas / estoque médio)
        giro_estoque = []
        if "VENDA_30DD" in df.columns and "ESTOQUE_UNE" in df.columns:
            # Clean and cast ESTOQUE_UNE, handling empty strings
            estoque_cleaned = pl.col("ESTOQUE_UNE").replace("", None).cast(pl.Float64)

            df_giro = df.filter(
                (pl.col("VENDA_30DD") > 0) &
                (estoque_cleaned > 0)
            ).group_by("PRODUTO", "NOME").agg([
                pl.col("VENDA_30DD").sum().alias("vendas"),
                estoque_cleaned.mean().alias("estoque_medio")
            ])

            df_giro = df_giro.with_columns([
                (pl.col("vendas") / pl.col("estoque_medio")).alias("giro")
            ]).sort("giro", descending=True).head(15)

            for row in df_giro.iter_rows(named=True):
                giro_estoque.append({
                    "produto": str(row["PRODUTO"]),
                    "nome": str(row["NOME"])[:40],
                    "giro": round(float(row["giro"]), 2)
                })

        # 3. Distribuição ABC (baseado em vendas)
        distribuicao_abc = {"A": 0, "B": 0, "C": 0}
        if "VENDA_30DD" in df.columns:
            df_abc = df.filter(pl.col("VENDA_30DD") > 0).sort("VENDA_30DD", descending=True)

            total_produtos = len(df_abc)
            if total_produtos > 0:
                # Curva ABC: A=20%, B=30%, C=50%
                limite_a = int(total_produtos * 0.2)
                limite_b = int(total_produtos * 0.5)

                distribuicao_abc["A"] = limite_a
                distribuicao_abc["B"] = limite_b - limite_a
                distribuicao_abc["C"] = total_produtos - limite_b

        return {
            "vendas_por_categoria": vendas_categoria,
            "giro_estoque": giro_estoque,
            "distribuicao_abc": distribuicao_abc
        }

    except Exception as e:
        logger.error(f"Error in sales analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing sales: {str(e)}"
        )

