from typing import Annotated, List, Dict, Any

import polars as pl
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User

router = APIRouter(prefix="/transfers", tags=["Transfers"])

@router.get("/list", response_model=List[Dict[str, Any]])
async def get_transfers(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 100
):
    """
    Lista de transferências (sugestões de transferência entre lojas/UNEs).
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)
        
        # Simulação de lógica de transferência baseada em excesso em uma UNE e falta em outra
        # Como não temos múltiplas UNEs separadas claramente no dataset único (admmat é consolidado por produto/UNE?)
        # O dataset parece ter "UNE" como coluna.
        
        cols = ["PRODUTO", "NOME", "UNE", "ESTOQUE_UNE", "VENDA_30DD"]
        existing_cols = [c for c in cols if c in df.columns]
        
        if not existing_cols:
            return []

        transfers = df.select(existing_cols).filter(
            pl.col("VENDA_30DD") > 0
        ).sort("VENDA_30DD", descending=True).head(limit)
        
        return transfers.to_dicts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
