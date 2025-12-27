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

        # Mapeamento de colunas (usar schema atual do admmat.parquet)
        cols = df.columns
        c_produto = "PRODUTO" if "PRODUTO" in cols else "codigo"
        c_venda = "VENDA_30DD" if "VENDA_30DD" in cols else "venda_30_d"
        c_une = "UNE" if "UNE" in cols else "une"
        
        # Calcular métricas reais baseado no schema do admmat.parquet
        # Produtos únicos
        products_count = df.select(pl.col(c_produto)).n_unique() if c_produto in cols else 0

        # Total de vendas últimos 30 dias (soma de venda_30_d)
        total_sales = int(df.select(pl.col(c_venda).fill_null(0).sum()).item()) if c_venda in cols else 0

        # Receita estimada (considerando média de volume de vendas)
        # Se não tiver coluna de receita explícita (MES_01), usamos venda_30_d como proxy de volume/receita
        c_receita = "MES_01" if "MES_01" in cols else c_venda
        revenue = float(df.select(pl.col(c_receita).fill_null(0).sum()).item()) if c_receita in cols else 0.0

        # UNEs ativas (lojas/unidades)
        total_users = df.select(pl.col(c_une)).n_unique() if c_une in cols else 0

        # Calcular crescimento comparando MES_01 vs MES_02
        sales_growth = 0.0
        users_growth = 0.0

        # Tentar usar colunas de meses se existirem, ou ignorar crescimento
        if "MES_01" in cols and "MES_02" in cols:
            mes_01 = float(df.select(pl.col("MES_01").sum()).item())
            mes_02 = float(df.select(pl.col("MES_02").sum()).item())
            if mes_02 > 0:
                sales_growth = ((mes_01 - mes_02) / mes_02) * 100
        
        # Crescimento de UNEs ativas
        # Se não tiver histórico, assumimos 0
        
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
        cols = df.columns
        c_venda = "VENDA_30DD" if "VENDA_30DD" in cols else "venda_30_d"
        c_nome = "NOME" if "NOME" in cols else "nome_produto"
        c_produto = "PRODUTO" if "PRODUTO" in cols else "codigo"
        c_updated = "updated_at" if "updated_at" in cols else "created_at"

        # Filtrar produtos com vendas
        if c_venda in cols:
            df_recent = df.filter(
                pl.col(c_venda).cast(pl.Float64).fill_null(0) > 0
            ).head(limit)
        else:
            df_recent = df.head(limit)

        sales = []
        for row in df_recent.iter_rows(named=True):
            sales.append(SaleItem(
                date=str(row.get(c_updated, "N/A")),
                product=str(row.get(c_nome, row.get(c_produto, "N/A"))),
                value=float(row.get(c_venda, 0.0)),
                quantity=1 # Não temos quantidade explícita na semana
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

        # Mapeamento
        cols = df.columns
        c_venda = "VENDA_30DD" if "VENDA_30DD" in cols else "venda_30_d"
        c_produto = "PRODUTO" if "PRODUTO" in cols else "codigo"
        c_nome = "NOME" if "NOME" in cols else "nome_produto"
        
        # Usar VENDA_30DD para ranking de top produtos
        if c_venda in cols:
            df_with_sales = df.filter(pl.col(c_venda) > 0)
        else:
            return []

        # Agrupar por produto
        # Se não tiver NOME, usa PRODUTO
        grp_cols = [c_produto]
        if c_nome in cols:
            grp_cols.append(c_nome)
            
        df_grouped = df_with_sales.group_by(grp_cols).agg([
            pl.col(c_venda).sum().alias("total_sales"),
            pl.col(c_venda).sum().alias("revenue") # Fallback revenue = sales
        ])

        df_sorted = df_grouped.sort("total_sales", descending=True).head(limit)

        # Criar resultado
        top_products = []
        for row in df_sorted.iter_rows(named=True):
            p_name = str(row[c_nome]) if c_nome in row else str(row[c_produto])
            top_products.append(TopProduct(
                product=str(row[c_produto]),
                productName=p_name[:50],  # Limitar tamanho
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
             logger.warning(f"⚠️ KPIs: Schema vazio para usuário {current_user.username}")
             return BusinessKPIs(total_produtos=0, total_unes=0, produtos_ruptura=0, valor_estoque=0.0, top_produtos=[], vendas_por_categoria=[])

        logger.info(f"📊 KPIs: Iniciando processamento LAZY para user={current_user.username}, role={current_user.role}")
        logger.info(f"   Segments: {current_user.segments_list}")
        
        # Debug count (caro, mas necessário agora)
        # count_check = lf.select(pl.len()).collect().item()
        # logger.info(f"   Rows available to user: {count_check}")

        # Preparar expressões de agregação para rodar em UMA ÚNICA PASSADA se possível
        # Casting seguro para colunas numéricas
        def safe_col(name, alt_names=None):
            if name in schema.names():
                return pl.col(name)
            if alt_names:
                for alt in alt_names:
                    if alt in schema.names():
                        return pl.col(alt)
            return pl.lit(0)

        # Definições de colunas com fallback (priorizar MAIÚSCULAS do SQL Server)
        c_produto = safe_col("PRODUTO")
        c_une = safe_col("UNE")
        c_venda30 = safe_col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0)
        c_est_une = safe_col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0)
        c_est_cd = safe_col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0)
        c_est_lv = safe_col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0)
        c_nome = safe_col("NOME")
        c_segmento = safe_col("NOMESEGMENTO")

        # Identificar nome real das colunas para group_by (usar MAIÚSCULAS do schema atual)
        col_produto_name = "PRODUTO" if "PRODUTO" in schema.names() else None
        col_nome_name = "NOME" if "NOME" in schema.names() else None
        
        # 1. Métricas Escalares (Count, Sum)
        metrics_exprs = [
            c_produto.n_unique().alias("total_produtos"),
            c_est_une.sum().alias("sum_estoque_une"),
            c_est_cd.sum().alias("sum_estoque_cd"),
            # Ruptura: CD=0 & Loja < LV (se existir) & Venda > 0
            ((c_est_cd == 0) & (c_venda30 > 0)).sum().alias("produtos_ruptura") # Simplificado sem LV
        ]
        
        if "UNE" in schema.names():
             metrics_exprs.append(c_une.n_unique().alias("total_unes"))
        else:
             metrics_exprs.append(pl.lit(0).alias("total_unes"))

        metrics_lf = lf.select(metrics_exprs)
        
        metrics_df = metrics_lf.collect() # Executa
        metrics = metrics_df.row(0, named=True)
        
        valor_estoque = metrics["sum_estoque_une"] + metrics["sum_estoque_cd"]
        
        # 2. Top Produtos (precisa de group_by)
        top_produtos = []
        if col_produto_name:
            grp_cols = [col_produto_name]
            if col_nome_name:
                grp_cols.append(col_nome_name)
                
            top_produtos_lf = lf.filter(c_venda30 > 0)\
                .group_by(grp_cols)\
                .agg([c_venda30.sum().alias("vendas")])\
                .sort("vendas", descending=True)\
                .head(10)
                
            top_produtos_df = top_produtos_lf.collect()
            
            for row in top_produtos_df.iter_rows(named=True):
                p_nome = str(row[col_nome_name]) if col_nome_name else str(row[col_produto_name])
                top_produtos.append({
                    "produto": str(row[col_produto_name]),
                    "nome": p_nome[:40],
                    "vendas": int(row["vendas"])
                })

        # 3. Vendas por Categoria (usar MAIÚSCULAS do schema atual)
        grupo_candidates = ["NOMEGRUPO", "NOMECATEGORIA", "NOMESEGMENTO"]
        grupo_col_name = next((c for c in grupo_candidates if c in schema.names()), None)
        
        vendas_por_categoria = []
        if grupo_col_name:
            c_grupo = pl.col(grupo_col_name)
            vendas_cat_lf = lf.filter(c_grupo.is_not_null())\
                .group_by(grupo_col_name)\
                .agg([
                    c_venda30.sum().alias("vendas"),
                    c_produto.n_unique().alias("produtos")
                ])\
                .sort("vendas", descending=True)\
                .head(10)  # Top 10 categorias
                
            vendas_cat_df = vendas_cat_lf.collect()
            
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

