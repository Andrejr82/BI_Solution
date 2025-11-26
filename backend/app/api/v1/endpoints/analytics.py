"""
Analytics Endpoints
Data analysis, metrics, export and custom queries
"""

import csv
import io
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, require_permission
from app.infrastructure.database.models import User
from app.schemas.analytics import (
    AnalyticsData,
    AnalyticsFilter,
    AnalyticsMetric,
    CustomQueryRequest,
    ExportRequest,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/data", response_model=list[AnalyticsData])
async def get_analytics_data(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("VIEW_ANALYTICS"))],
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    min_value: float | None = Query(None),
    max_value: float | None = Query(None),
) -> list[dict]:
    """
    Get analytics data with filters
    
    TODO: Integrate with real data source (SQL Server/Parquet)
    For now, returns mock data
    """
    
    # Real implementation using Parquet
    import polars as pl
    from pathlib import Path
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Caminho híbrido Docker/Dev
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"

        parquet_path = docker_path if docker_path.exists() else dev_path

        if not parquet_path.exists():
            logger.warning(f"Parquet file not found at: {parquet_path}")
            return []
            
        df = pl.read_parquet(parquet_path)
        
        # TODO: Implementar filtros reais com Polars
        # Por enquanto retorna lista vazia para não mostrar dados falsos
        # A implementação completa dos filtros será feita na próxima etapa
        
        return []
        
    except Exception as e:
        logger.error(f"Error reading analytics data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics data")


@router.get("/metrics", response_model=list[AnalyticsMetric])
async def get_analytics_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("VIEW_ANALYTICS"))],
) -> list[dict]:
    """
    Get aggregated analytics metrics
    
    TODO: Calculate from real data
    """
    
    # Real implementation
    # Retorna lista vazia se não implementado, para evitar dados falsos
    return []


@router.post("/export")
async def export_analytics(
    export_request: ExportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("VIEW_ANALYTICS"))],
) -> StreamingResponse:
    """
    Export analytics data to CSV or Excel

    Uses real Parquet data for export.
    """
    import polars as pl
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Read data from Parquet
        project_root = Path(__file__).parent.parent.parent.parent.parent
        parquet_path = project_root / "data" / "parquet" / "admmat.parquet"

        if not parquet_path.exists():
            logger.warning(f"Parquet file not found at: {parquet_path}")
            raise HTTPException(status_code=404, detail="Data source not found")

        df = pl.read_parquet(parquet_path)

        # Apply filters if provided
        if export_request.filters:
            filters = export_request.filters
            if filters.date_start and "DATA" in df.columns:
                df = df.filter(pl.col("DATA") >= filters.date_start)
            if filters.date_end and "DATA" in df.columns:
                df = df.filter(pl.col("DATA") <= filters.date_end)
            if filters.category and "CATEGORIA" in df.columns:
                df = df.filter(pl.col("CATEGORIA") == filters.category)

        # Convert to list of dicts for export
        data = df.to_dicts()

        if not data:
            raise HTTPException(status_code=404, detail="No data to export")

        fieldnames = list(data[0].keys()) if data else []

        if export_request.format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

            # Return as streaming response
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )

        elif export_request.format == "excel":
            # Export to Excel using Polars
            output = io.BytesIO()
            df.write_excel(output)
            output.seek(0)

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d')}.xlsx"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@router.post("/query")
async def custom_query(
    query_request: CustomQueryRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("VIEW_ANALYTICS"))],
) -> dict:
    """
    Execute custom analytics query using natural language

    This endpoint will integrate with LangChain/LLM for natural language queries.
    Currently not implemented to avoid returning mock data.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Custom query execution not yet implemented. This feature will integrate with LangChain for natural language queries."
    )
