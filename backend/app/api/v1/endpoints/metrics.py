"""
Metrics Endpoints
Dashboard metrics and summary data
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.config.database import get_db
from app.infrastructure.database.models import User

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
    db: Annotated[AsyncSession, Depends(get_db)]
) -> MetricsSummary:
    """
    Get dashboard metrics summary

    Returns aggregated metrics for dashboard display using real Parquet data.
    Requires authentication and active user status.
    """

    import polars as pl
    from pathlib import Path

    import polars as pl
    from pathlib import Path
    import logging
    
    logger = logging.getLogger(__name__)

    try:
        # Caminho para o arquivo Parquet (híbrido Docker/Dev)
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"

        parquet_path = docker_path if docker_path.exists() else dev_path

        if not parquet_path.exists():
            logger.error(f"Parquet file not found at: {parquet_path}")
            raise HTTPException(status_code=500, detail=f"Data source not found: {parquet_path}")
        
        # Ler dados do Parquet (dados de estoque/movimentação)
        df = pl.read_parquet(parquet_path)

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

        # Crescimento de UNEs ativas (comparando frequência de vendas)
        if "FREQ_SEMANA_ATUAL" in df.columns and "FREQ_SEMANA_ANTERIOR_2" in df.columns:
            freq_atual = df.filter(pl.col("FREQ_SEMANA_ATUAL") > 0).height
            freq_anterior = df.filter(pl.col("FREQ_SEMANA_ANTERIOR_2") > 0).height
            if freq_anterior > 0:
                users_growth = ((freq_atual - freq_anterior) / freq_anterior) * 100
        
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
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    try:
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"
        parquet_path = docker_path if docker_path.exists() else dev_path

        if not parquet_path.exists():
            logger.error(f"Parquet file not found at: {parquet_path}")
            raise HTTPException(status_code=500, detail=f"Data source not found: {parquet_path}")

        df = pl.read_parquet(parquet_path)

        # Usar colunas reais do admmat.parquet
        # Filtrar produtos com vendas na semana atual
        df_recent = df.filter(pl.col("QTDE_SEMANA_ATUAL") > 0).head(limit)

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
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    try:
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"
        parquet_path = docker_path if docker_path.exists() else dev_path

        if not parquet_path.exists():
            logger.error(f"Parquet file not found at: {parquet_path}")
            raise HTTPException(status_code=500, detail=f"Data source not found: {parquet_path}")

        df = pl.read_parquet(parquet_path)

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

