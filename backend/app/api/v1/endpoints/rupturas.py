from typing import Annotated, List, Dict, Any

import polars as pl
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User

router = APIRouter(prefix="/rupturas", tags=["Rupturas"])

@router.get("/critical", response_model=List[Dict[str, Any]])
async def get_critical_rupturas(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 50
):
    """
    Produtos com ruptura crítica (estoque zero + vendas altas nos últimos 30 dias).
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)
        
        # Filtrar: VENDA_30DD > 0 AND ESTOQUE (ESTOQUE_UNE) == 0
        # Assumindo colunas do parquet (checar admmat.parquet schema se necessário)
        # Colunas comuns: ESTOQUE_UNE, VENDA_30DD
        
        if "ESTOQUE_UNE" not in df.columns or "VENDA_30DD" not in df.columns:
             # Fallback se colunas não existirem exatamente com esses nomes
             return []

        # Casting para garantir tipos numéricos
        df = df.with_columns([
            pl.col("VENDA_30DD").cast(pl.Float64).fill_null(0),
            pl.col("ESTOQUE_UNE").cast(pl.Float64).fill_null(0)
        ])

        rupturas = df.filter(
            (pl.col("VENDA_30DD") > 0) & (pl.col("ESTOQUE_UNE") <= 0)
        ).sort("VENDA_30DD", descending=True).head(limit)
        
        return rupturas.to_dicts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
