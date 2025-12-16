"""
Metrics Endpoints
Dashboard metrics and summary data
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.infrastructure.database.models import User
from app.core.data_scope_service import data_scope_service # Importar o serviço

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class MetricsSummary(BaseModel):
    totalSales: int
    totalUsers: int
    revenue: float
    productsCount: int
    salesGrowth: float
    usersGrowth: float


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    # db: Annotated[AsyncSession, Depends(get_db)] # Não mais usada diretamente aqui
) -> MetricsSummary:
    """
    Get dashboard metrics summary

    Returns aggregated metrics for dashboard display using real Parquet data.
    Requires authentication and active user status.
    """

    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Limitar a 10000 linhas para cálculo de métricas (performance)
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=10000)

        # Calcular métricas reais baseado no schema do admmat.parquet
        # Produtos únicos
        products_count = df.select(pl.col("PRODUTO")).n_unique()

        # Total de vendas últimos 30 dias (soma de VENDA_30DD)
        total_sales = int(df.select(pl.col("VENDA_30DD").sum()).item()) if "VENDA_30DD" in df.columns else 0

        # Receita estimada (considerando média de volume de vendas)
        # Usando MES_01 (mês mais recente) como proxy de movimentação
        revenue = float(df.select(pl.col("MES_01").sum()).item()) if "MES_01" in df.columns else 0.0

        # UNEs ativas (lojas/unidades)
        total_users = df.select(pl.col("UNE")).n_unique() if "UNE" in df.columns else 0

        # Calcular crescimento comparando MES_01 vs MES_02
        sales_growth = 0.0
        users_growth = 0.0

        if "MES_01" in df.columns and "MES_02" in df.columns:
            mes_01 = float(df.select(pl.col("MES_01").sum()).item())
            mes_02 = float(df.select(pl.col("MES_02").sum()).item())
            if mes_02 > 0:
                sales_growth = ((mes_01 - mes_02) / mes_02) * 100

        # Crescimento de UNEs ativas (comparando MES_01 vs MES_02 agregado por UNE)
        if "UNE" in df.columns and "MES_01" in df.columns and "MES_02" in df.columns:
            unes_atual = df.filter(pl.col("MES_01") > 0).select("UNE").n_unique()
            unes_anterior = df.filter(pl.col("MES_02") > 0).select("UNE").n_unique()
            if unes_anterior > 0:
                users_growth = ((unes_atual - unes_anterior) / unes_anterior) * 100
            else:
                users_growth = 0.0
        
        return MetricsSummary(
            totalSales=total_sales,
            totalUsers=total_users if total_users > 0 else 0,
            revenue=revenue,
            productsCount=products_count,
            salesGrowth=sales_growth,
            usersGrowth=users_growth
        )
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")


class SaleItem(BaseModel):
    date: str
    product: str
    value: float
    quantity: int


class TopProduct(BaseModel):
    product: str
    productName: str
    totalSales: int
    revenue: float


@router.get("/recent-sales", response_model=list[SaleItem])
async def get_recent_sales(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 10
) -> list[SaleItem]:
    """
    Get recent sales from Parquet data

    Returns the most recent sales transactions.
    """
    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Usar colunas reais do admmat.parquet
        # Filtrar produtos com vendas na semana atual (converter para numérico primeiro)
        df_recent = df.filter(
            pl.col("QTDE_SEMANA_ATUAL").cast(pl.Float64).fill_null(0) > 0
        ).head(limit)

        sales = []
        for row in df_recent.iter_rows(named=True):
            sales.append(SaleItem(
                date=str(row.get("updated_at", "N/A")),
                product=str(row.get("NOME", row.get("PRODUTO", "N/A"))),
                value=float(row.get("MES_01", 0.0)),
                quantity=int(row.get("QTDE_SEMANA_ATUAL", 1))
            ))

        return sales

    except Exception as e:
        logger.error(f"Error fetching recent sales: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching recent sales: {str(e)}")


@router.get("/top-products", response_model=list[TopProduct])
async def get_top_products(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 5
) -> list[TopProduct]:
    """
    Get top selling products from Parquet data

    Returns products ranked by total sales count and revenue.
    """
    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Usar VENDA_30DD para ranking de top produtos
        df_with_sales = df.filter(pl.col("VENDA_30DD") > 0)

        # Agrupar por produto
        df_grouped = df_with_sales.group_by(["PRODUTO", "NOME"]).agg([
            pl.col("VENDA_30DD").sum().alias("total_sales"),
            pl.col("MES_01").sum().alias("revenue")
        ])

        df_sorted = df_grouped.sort("total_sales", descending=True).head(limit)

        # Criar resultado
        top_products = []
        for row in df_sorted.iter_rows(named=True):
            top_products.append(TopProduct(
                product=str(row["PRODUTO"]),
                productName=str(row["NOME"])[:50],  # Limitar tamanho
                totalSales=int(row["total_sales"]),
                revenue=float(row["revenue"])
            ))

        return top_products

    except Exception as e:
        logger.error(f"Error fetching top products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching top products: {str(e)}")


class BusinessKPIs(BaseModel):
    total_produtos: int
    total_unes: int
    produtos_ruptura: int
    valor_estoque: float
    top_produtos: list[dict]
    vendas_por_categoria: list[dict]


@router.get("/business-kpis", response_model=BusinessKPIs)
async def get_business_kpis(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> BusinessKPIs:
    """
    Get business KPIs for Dashboard

    Returns key business metrics including products, UNEs, stock ruptures, and top sellers.
    Optimized to use Polars LazyFrame for memory efficiency.
    """
    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Usar LazyFrame para evitar carregar tudo na memória
        lf = data_scope_service.get_filtered_lazyframe(current_user)
        
        # Verificar se temos dados antes de tentar processar
        # collect_schema é rápido
        schema = lf.collect_schema()
        if not schema.names():
             return BusinessKPIs(total_produtos=0, total_unes=0, produtos_ruptura=0, valor_estoque=0.0, top_produtos=[], vendas_por_categoria=[])

        logger.info(f"📊 KPIs: Iniciando processamento LAZY")

        # Preparar expressões de agregação para rodar em UMA ÚNICA PASSADA se possível
        # Nota: Polars otimiza scans, então múltiplas coletas são eficientes se o grafo for simples,
        # mas agregar tudo de uma vez é melhor.
        
        # Casting seguro para colunas numéricas
        def safe_col(name):
            if name in schema.names():
                return pl.col(name)
            return pl.lit(0)

        # Definições de colunas
        c_produto = safe_col("PRODUTO")
        c_une = safe_col("UNE")
        c_venda30 = safe_col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0)
        c_est_une = safe_col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0)
        c_est_cd = safe_col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0)
        c_est_lv = safe_col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0)
        c_nome = safe_col("NOME")
        c_segmento = safe_col("NOMESEGMENTO") if "NOMESEGMENTO" in schema.names() else safe_col("SEGMENTO")

        # 1. Métricas Escalares (Count, Sum)
        # Podemos coletar isso em uma query rápida
        metrics_lf = lf.select([
            pl.col("PRODUTO").n_unique().alias("total_produtos"),
            pl.col("UNE").n_unique().alias("total_unes") if "UNE" in schema.names() else pl.lit(0).alias("total_unes"),
            c_est_une.sum().alias("sum_estoque_une"),
            c_est_cd.sum().alias("sum_estoque_cd"),
            # Ruptura: CD=0 & Loja < LV & Venda > 0
            ((c_est_cd == 0) & (c_est_une < c_est_lv) & (c_venda30 > 0)).sum().alias("produtos_ruptura")
        ])
        
        metrics_df = metrics_lf.collect() # Executa
        metrics = metrics_df.row(0, named=True)
        
        valor_estoque = metrics["sum_estoque_une"] + metrics["sum_estoque_cd"]
        
        # 2. Top Produtos (precisa de group_by)
        top_produtos_lf = lf.filter(c_venda30 > 0)\
            .group_by(["PRODUTO", "NOME"])\
            .agg([c_venda30.sum().alias("vendas")])\
            .sort("vendas", descending=True)\
            .head(10)
            
        top_produtos_df = top_produtos_lf.collect()
        
        top_produtos = []
        for row in top_produtos_df.iter_rows(named=True):
            top_produtos.append({
                "produto": str(row["PRODUTO"]),
                "nome": str(row["NOME"])[:40],
                "vendas": int(row["vendas"])
            })

        # 3. Vendas por Categoria (NOMEGRUPO de produto, NÃO segmento)
        # O segmento já está filtrado pelo allowed_segments do usuário
        # Agora queremos ver a distribuição por NOMEGRUPO (categoria) dentro do(s) segmento(s)
        grupo_col_name = "NOMEGRUPO" if "NOMEGRUPO" in schema.names() else "NOMECATEGORIA" if "NOMECATEGORIA" in schema.names() else "NOMESEGMENTO"
        c_grupo = safe_col(grupo_col_name)
        
        vendas_cat_lf = lf.filter(c_grupo.is_not_null())\
            .group_by(grupo_col_name)\
            .agg([
                c_venda30.sum().alias("vendas"),
                pl.col("PRODUTO").n_unique().alias("produtos")
            ])\
            .sort("vendas", descending=True)\
            .head(10)  # Top 10 categorias
            
        vendas_cat_df = vendas_cat_lf.collect()
        
        vendas_por_categoria = []
        
        for row in vendas_cat_df.iter_rows(named=True):
            categoria = str(row.get(grupo_col_name, "N/A")).strip()
            
            if categoria and categoria != "null":
                vendas_por_categoria.append({
                    "categoria": categoria[:30],
                    "vendas": int(row["vendas"]),
                    "produtos": int(row["produtos"])
                })

        logger.info(f"📊 KPIs calculados (Lazy) - Produtos: {metrics['total_produtos']}")

        return BusinessKPIs(
            total_produtos=metrics["total_produtos"],
            total_unes=metrics["total_unes"],
            produtos_ruptura=metrics["produtos_ruptura"],
            valor_estoque=valor_estoque,
            top_produtos=top_produtos,
            vendas_por_categoria=vendas_por_categoria
        )

    except Exception as e:
        logger.error(f"Error fetching business KPIs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching business KPIs: {str(e)}")

