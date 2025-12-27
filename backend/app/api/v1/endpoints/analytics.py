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
    segmento: Optional[str] = Query(None, description="Segmento para filtrar as categorias retornadas"),
    categoria: Optional[str] = Query(None, description="Categoria para filtrar os grupos retornados")
) -> Dict[str, List[str]]:
    """
    Retorna valores únicos de segmento, categoria e grupo para os filtros.
    Pode filtrar categorias por segmento e grupos por categoria.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=50000)

        categorias = []
        segmentos = []
        grupos = []

        # Filtrar o DataFrame pelo segmento se fornecido
        df_filtered = df
        if segmento and "NOMESEGMENTO" in df.columns:
            df_filtered = df_filtered.filter(pl.col("NOMESEGMENTO").str.to_lowercase() == segmento.lower())

        # Filtrar pelo categoria se fornecido (para grupos)
        if categoria and "NOMECATEGORIA" in df.columns:
            df_filtered = df_filtered.filter(pl.col("NOMECATEGORIA").str.to_lowercase() == categoria.lower())

        # Categorias únicas (filtradas por segmento se fornecido)
        if "NOMECATEGORIA" in df_filtered.columns:
            cat_unique = df_filtered.select("NOMECATEGORIA").unique().sort("NOMECATEGORIA")
            for row in cat_unique.iter_rows(named=True):
                cat = str(row["NOMECATEGORIA"]).strip()
                if cat and cat != "null" and cat != "None":
                    categorias.append(cat)

        # Grupos únicos (filtrados por segmento e categoria se fornecidos)
        if "NOMEGRUPO" in df_filtered.columns:
            grp_unique = df_filtered.select("NOMEGRUPO").unique().sort("NOMEGRUPO")
            for row in grp_unique.iter_rows(named=True):
                grp = str(row["NOMEGRUPO"]).strip()
                if grp and grp != "null" and grp != "None":
                    grupos.append(grp)

        # Segmentos únicos (sempre da base original)
        df_all_segments = data_scope_service.get_filtered_dataframe(current_user, max_rows=50000)
        if "NOMESEGMENTO" in df_all_segments.columns:
            seg_unique = df_all_segments.select("NOMESEGMENTO").unique().sort("NOMESEGMENTO")
            for row in seg_unique.iter_rows(named=True):
                seg = str(row["NOMESEGMENTO"]).strip()
                if seg and seg != "null" and seg != "None":
                    segmentos.append(seg)

        return {
            "categorias": categorias,
            "segmentos": segmentos,
            "grupos": grupos
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
    segmento: Optional[str] = Query(None),
    grupo: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """
    Análise de vendas e estoque com gráficos.
    Retorna dados para gráficos de vendas por categoria, giro de estoque e distribuição ABC.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        # Obter o DataFrame completo (Lazy) para máxima performance sem limites arbitrários no início
        df = data_scope_service.get_filtered_dataframe(current_user)

        if df.is_empty():
            return {
                "vendas_por_categoria": [],
                "giro_estoque": [],
                "distribuicao_abc": {"A": 0, "B": 0, "C": 0, "detalhes": []}
            }

        # Determinar nomes corretos das colunas (suporta tanto maiúsculas quanto minúsculas)
        categoria_col = "nomecategoria" if "nomecategoria" in df.columns else ("NOMECATEGORIA" if "NOMECATEGORIA" in df.columns else ("CATEGORIA" if "CATEGORIA" in df.columns else None))
        segmento_col = "nomesegmento" if "nomesegmento" in df.columns else ("NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else ("SEGMENTO" if "SEGMENTO" in df.columns else None))
        grupo_col = "nomegrupo" if "nomegrupo" in df.columns else ("NOMEGRUPO" if "NOMEGRUPO" in df.columns else None)
        produto_col = "codigo" if "codigo" in df.columns else "PRODUTO"
        nome_col = "nome_produto" if "nome_produto" in df.columns else "NOME"
        venda_col = "venda_30_d" if "venda_30_d" in df.columns else "VENDA_30DD"
        estoque_col = "estoque_atual" if "estoque_atual" in df.columns else "ESTOQUE_UNE"

        # Aplicar filtros se fornecidos
        if categoria and categoria_col:
            df = df.filter(pl.col(categoria_col).str.to_lowercase() == categoria.lower())
        if segmento and segmento_col:
            df = df.filter(pl.col(segmento_col).str.to_lowercase() == segmento.lower())
        if grupo and grupo_col:
            df = df.filter(pl.col(grupo_col).str.to_lowercase() == grupo.lower())

        # Função auxiliar para casting seguro
        def safe_cast_col(col_name):
            if col_name not in df.columns: return pl.lit(0).cast(pl.Float64)
            # Se já for numérico, não precisa converter de string
            col_type = df.schema[col_name]
            if col_type in [pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8]:
                return pl.col(col_name).fill_null(0).cast(pl.Float64)
            return pl.col(col_name).cast(pl.Utf8).str.strip_chars().replace("", None).cast(pl.Float64).fill_null(0)

        # 1. Vendas por Categoria (Top 10)
        vendas_categoria = []
        if categoria_col and venda_col in df.columns:
            df_cat = df.group_by(categoria_col).agg([
                safe_cast_col(venda_col).sum().alias("vendas")
            ]).sort("vendas", descending=True).head(10)

            for row in df_cat.iter_rows(named=True):
                vendas_categoria.append({
                    "categoria": str(row[categoria_col])[:30],
                    "vendas": int(row["vendas"])
                })

        # 2. Giro de Estoque (Top 15)
        giro_estoque = []
        if venda_col in df.columns and estoque_col in df.columns and produto_col in df.columns and nome_col in df.columns:
            df_giro = df.with_columns([
                safe_cast_col(venda_col).alias("v_clean"),
                safe_cast_col(estoque_col).alias("e_clean")
            ]).filter(
                (pl.col("v_clean") > 0) & (pl.col("e_clean") > 0)
            ).group_by(produto_col, nome_col).agg([
                pl.col("v_clean").sum().alias("vendas"),
                pl.col("e_clean").mean().alias("estoque_medio")
            ]).with_columns([
                (pl.col("vendas") / pl.col("estoque_medio")).alias("giro")
            ]).sort("giro", descending=True).head(15)

            for row in df_giro.iter_rows(named=True):
                giro_estoque.append({
                    "produto": str(row[produto_col]),
                    "nome": str(row[nome_col])[:40],
                    "giro": round(float(row["giro"]), 2)
                })

        # 3. Distribuição ABC (Princípio de Pareto - Dataset Completo)
        distribuicao_abc = {"A": 0, "B": 0, "C": 0, "detalhes": [], "receita_por_classe": {}}

        # Usamos MES_01 para faturamento ou venda_col se MES_01 estiver zerado
        # No varejo, Pareto pode ser por Valor ou Volume
        val_col = "MES_01" if "MES_01" in df.columns else venda_col

        if val_col in df.columns and produto_col in df.columns and nome_col in df.columns:
            df_abc_raw = df.with_columns([
                safe_cast_col(val_col).alias("valor_clean")
            ]).filter(pl.col("valor_clean") > 0)

            if not df_abc_raw.is_empty():
                # Ordenar por valor decrescente
                df_abc = df_abc_raw.select([
                    pl.col(produto_col).alias("PRODUTO"),
                    pl.col(nome_col).alias("NOME"),
                    pl.col("valor_clean").alias("receita")
                ]).sort("receita", descending=True)

                total_receita = df_abc.select(pl.col("receita").sum()).item()

                if total_receita > 0:
                    # Calcular Acumulado
                    df_abc = df_abc.with_columns([
                        (pl.col("receita").cum_sum() / total_receita * 100).alias("perc_acumulada")
                    ])

                    # Classificação ABC (80/15/5)
                    df_abc = df_abc.with_columns([
                        pl.when(pl.col("perc_acumulada") <= 80).then(pl.lit("A"))
                        .when(pl.col("perc_acumulada") <= 95).then(pl.lit("B"))
                        .otherwise(pl.lit("C")).alias("classe")
                    ])

                    # Resultados
                    resumo = df_abc.group_by("classe").agg([
                        pl.count().alias("qtd"),
                        pl.col("receita").sum().alias("soma")
                    ])

                    for row in resumo.iter_rows(named=True):
                        distribuicao_abc[row["classe"]] = row["qtd"]
                        distribuicao_abc["receita_por_classe"][row["classe"]] = row["soma"]

                    distribuicao_abc["detalhes"] = df_abc.head(20).to_dicts()

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


class ABCDetailItem(BaseModel):
    PRODUTO: str
    NOME: str
    UNE: str
    UNE_NOME: Optional[str]
    receita: float
    perc_acumulada: float
    classe: str


@router.get("/abc-details", response_model=List[ABCDetailItem])
async def get_abc_details(
    current_user: Annotated[User, Depends(get_current_active_user)],
    classe: str = Query(..., description="Classe ABC (A, B ou C)"),
    categoria: Optional[str] = Query(None),
    segmento: Optional[str] = Query(None),
    grupo: Optional[str] = Query(None)
) -> List[ABCDetailItem]:
    """
    Retorna detalhes dos SKUs de uma classe ABC específica com informações de UNE.
    Usado para visualizar/baixar os produtos de cada classe.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        # Validar classe
        if classe not in ['A', 'B', 'C']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Classe deve ser A, B ou C"
            )

        # Obter DataFrame
        df = data_scope_service.get_filtered_dataframe(current_user)

        if df.is_empty():
            return []

        # Determinar colunas
        categoria_col = "nomecategoria" if "nomecategoria" in df.columns else ("NOMECATEGORIA" if "NOMECATEGORIA" in df.columns else None)
        segmento_col = "nomesegmento" if "nomesegmento" in df.columns else ("NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else None)
        grupo_col = "nomegrupo" if "nomegrupo" in df.columns else ("NOMEGRUPO" if "NOMEGRUPO" in df.columns else None)
        produto_col = "codigo" if "codigo" in df.columns else "PRODUTO"
        nome_col = "nome_produto" if "nome_produto" in df.columns else "NOME"
        une_col = "une" if "une" in df.columns else "UNE"
        une_nome_col = "une_nome" if "une_nome" in df.columns else ("UNE_NOME" if "UNE_NOME" in df.columns else None)

        # Aplicar filtros
        if categoria and categoria_col:
            df = df.filter(pl.col(categoria_col).str.to_lowercase() == categoria.lower())
        if segmento and segmento_col:
            df = df.filter(pl.col(segmento_col).str.to_lowercase() == segmento.lower())
        if grupo and grupo_col:
            df = df.filter(pl.col(grupo_col).str.to_lowercase() == grupo.lower())

        # Função auxiliar para casting seguro
        def safe_cast_col(col_name):
            if col_name not in df.columns:
                return pl.lit(0).cast(pl.Float64)
            col_type = df.schema[col_name]
            if col_type in [pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8]:
                return pl.col(col_name).fill_null(0).cast(pl.Float64)
            return pl.col(col_name).cast(pl.Utf8).str.strip_chars().replace("", None).cast(pl.Float64).fill_null(0)

        # Calcular ABC usando MES_01 ou VENDA_30DD
        val_col = "MES_01" if "MES_01" in df.columns else ("venda_30_d" if "venda_30_d" in df.columns else "VENDA_30DD")

        if val_col not in df.columns:
            return []

        # Preparar dados ABC
        df_abc_raw = df.with_columns([
            safe_cast_col(val_col).alias("valor_clean")
        ]).filter(pl.col("valor_clean") > 0)

        if df_abc_raw.is_empty():
            return []

        # Selecionar colunas necessárias
        select_cols = [
            pl.col(produto_col).alias("PRODUTO"),
            pl.col(nome_col).alias("NOME"),
            pl.col(une_col).cast(pl.Utf8).alias("UNE"),
            pl.col("valor_clean").alias("receita")
        ]

        if une_nome_col:
            select_cols.append(pl.col(une_nome_col).alias("UNE_NOME"))

        df_abc = df_abc_raw.select(select_cols).sort("receita", descending=True)

        total_receita = df_abc.select(pl.col("receita").sum()).item()

        if total_receita <= 0:
            return []

        # Calcular percentual acumulado
        df_abc = df_abc.with_columns([
            (pl.col("receita").cum_sum() / total_receita * 100).alias("perc_acumulada")
        ])

        # Classificar ABC
        df_abc = df_abc.with_columns([
            pl.when(pl.col("perc_acumulada") <= 80).then(pl.lit("A"))
            .when(pl.col("perc_acumulada") <= 95).then(pl.lit("B"))
            .otherwise(pl.lit("C")).alias("classe")
        ])

        # Filtrar pela classe solicitada
        df_result = df_abc.filter(pl.col("classe") == classe)

        # Converter para lista de dicts
        results = []
        for row in df_result.iter_rows(named=True):
            results.append(ABCDetailItem(
                PRODUTO=str(row["PRODUTO"]),
                NOME=str(row["NOME"]),
                UNE=str(row["UNE"]),
                UNE_NOME=str(row.get("UNE_NOME", "")),
                receita=float(row["receita"]),
                perc_acumulada=float(row["perc_acumulada"]),
                classe=str(row["classe"])
            ))

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ABC details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting ABC details: {str(e)}"
        )

