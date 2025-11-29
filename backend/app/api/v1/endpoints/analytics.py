"""
Analytics Endpoints
Data analysis, metrics, export and custom queries
"""

import csv
import io
from datetime import datetime, timedelta, date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_active_user
from app.infrastructure.database.models import User
from app.core.parquet_cache import cache
from app.core.data_scope_service import data_scope_service # Adicionado

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Modelos Pydantic para resposta
class AnalyticsDataPoint(BaseModel):
    date: str
    product: str
    sales: int
    revenue: float
    une: str


class AnalyticsResponse(BaseModel):
    data: list[AnalyticsDataPoint]
    totalRecords: int
    summary: dict


@router.get("/data", response_model=AnalyticsResponse)
async def get_analytics_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    startDate: str = Query(None, description="Data início (YYYY-MM-DD)"),
    endDate: str = Query(None, description="Data fim (YYYY-MM-DD)"),
    groupBy: str = Query("day", description="Agrupamento: day/week/month"),
    limit: int = Query(100, description="Limite de resultados")
) -> AnalyticsResponse:
    """
    Retorna dados analíticos filtrados

    Fornece análises customizadas com dados reais do Parquet.
    Suporta filtros de data e agrupamento flexível.
    """
    import polars as pl
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Usar o DataScopeService para obter o DataFrame já filtrado
        # Limitar a 5000 linhas para analytics (performance)
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=5000)

        # Filtrar por vendas > 0 (produtos ativos)
        df_filtered = df.filter(pl.col("VENDA_30DD") > 0)

        logger.info(f"Analytics query: {len(df_filtered)} records with sales")

        # Agrupar por produto e UNE
        df_agg = df_filtered.group_by(["PRODUTO", "NOME", "UNE"]).agg([
            pl.col("VENDA_30DD").sum().alias("sales"),
            pl.col("MES_01").sum().alias("revenue")
        ]).sort("sales", descending=True).head(limit)

        # Converter para lista de AnalyticsDataPoint
        data = []
        for row in df_agg.iter_rows(named=True):
            data.append(AnalyticsDataPoint(
                date=str(date.today()),  # Placeholder
                product=str(row["NOME"])[:50],
                sales=int(row["sales"]),
                revenue=float(row["revenue"]),
                une=str(row["UNE"])
            ))

        # Calcular summary
        summary = {
            "totalSales": int(df_filtered.select(pl.col("VENDA_30DD").sum()).item()),
            "totalRevenue": float(df_filtered.select(pl.col("MES_01").sum()).item()),
            "uniqueProducts": df_filtered.select(pl.col("PRODUTO")).n_unique(),
            "uniqueUnes": df_filtered.select(pl.col("UNE")).n_unique(),
            "avgSalesPerProduct": float(df_filtered.select(pl.col("VENDA_30DD").mean()).item())
        }

        logger.info(f"Analytics response: {len(data)} records")

        return AnalyticsResponse(
            data=data,
            totalRecords=len(data),
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error fetching analytics data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")
