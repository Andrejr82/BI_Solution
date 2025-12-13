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
    Uses FULL dataset without limits for accurate counts.
    """
    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Usar TODOS os dados sem limite para contagens precisas
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=None)
        
        logger.info(f"📊 KPIs: Processando {df.height} linhas do DataFrame completo")

        # 1. Total de Produtos (únicos)
        total_produtos = df.select(pl.col("PRODUTO")).n_unique()
        logger.info(f"📊 Total produtos únicos: {total_produtos}")

        # 2. Total de UNEs (unidades/lojas únicas)
        total_unes = df.select(pl.col("UNE")).n_unique() if "UNE" in df.columns else 0
        logger.info(f"📊 Total UNEs: {total_unes}")

        # 3. Produtos em Ruptura (CD=0 E Loja < Linha Verde/MC)
        # Ruptura crítica: estoque CD zerado E estoque loja abaixo da Linha Verde (MC)
        df_ruptura = df.filter(
            (pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0) == 0) &
            (pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0) < pl.col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0)) &
            (pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0) > 0)  # Apenas produtos com vendas
        )
        produtos_ruptura = len(df_ruptura)
        logger.info(f"📊 Produtos em ruptura: {produtos_ruptura}")

        # 4. Valor do Estoque Total (usando estoque loja + CD)
        estoque_loja = float(df.select(pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0).sum()).item())
        estoque_cd = float(df.select(pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0).sum()).item())
        valor_estoque = estoque_loja + estoque_cd
        logger.info(f"📊 Valor estoque total: {valor_estoque}")

        # 5. Top 10 Produtos Mais Vendidos (baseado em VENDA_30DD)
        df_top = df.filter(pl.col("VENDA_30DD") > 0).group_by(["PRODUTO", "NOME"]).agg([
            pl.col("VENDA_30DD").sum().alias("vendas")
        ]).sort("vendas", descending=True).head(10)

        top_produtos = []
        for row in df_top.iter_rows(named=True):
            top_produtos.append({
                "produto": str(row["PRODUTO"]),
                "nome": str(row["NOME"])[:40],
                "vendas": int(row["vendas"])
            })

        # 6. Vendas por Categoria (usando NOMESEGMENTO que é mais descritivo)
        vendas_por_categoria = []
        segmento_col = "NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else "SEGMENTO"
        if segmento_col in df.columns:
            df_categoria = df.group_by(segmento_col).agg([
                pl.col("VENDA_30DD").sum().alias("vendas"),
                pl.col("PRODUTO").n_unique().alias("produtos")
            ]).sort("vendas", descending=True).head(8)

            for row in df_categoria.iter_rows(named=True):
                segmento = str(row[segmento_col]).strip()
                if segmento and segmento != "null" and segmento != "None" and segmento != "":
                    vendas_por_categoria.append({
                        "categoria": segmento[:30],
                        "vendas": int(row["vendas"]),
                        "produtos": int(row["produtos"])
                    })

        logger.info(f"📊 KPIs calculados com sucesso - Produtos: {total_produtos}, UNEs: {total_unes}, Rupturas: {produtos_ruptura}")

        return BusinessKPIs(
            total_produtos=total_produtos,
            total_unes=total_unes,
            produtos_ruptura=produtos_ruptura,
            valor_estoque=valor_estoque,
            top_produtos=top_produtos,
            vendas_por_categoria=vendas_por_categoria
        )

    except Exception as e:
        logger.error(f"Error fetching business KPIs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching business KPIs: {str(e)}")

