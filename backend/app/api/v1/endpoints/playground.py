from typing import Annotated, Dict, Any, List

import polars as pl
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import require_role
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User

router = APIRouter(prefix="/playground", tags=["Playground"])

class QueryRequest(BaseModel):
    query: str # Não usada diretamente como SQL, mas sim como intent
    columns: List[str] = []
    limit: int = 100

@router.post("/query")
async def execute_query(
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: QueryRequest
):
    """
    Endpoint para exploração de dados (Admin Only).
    Permite selecionar colunas e visualizar dados brutos.
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)
        
        # Selecionar colunas se especificadas
        if request.columns:
            valid_cols = [c for c in request.columns if c in df.columns]
            if valid_cols:
                df = df.select(valid_cols)
        
        # Limitar resultados
        result = df.head(request.limit)
        
        return {
            "rows": result.to_dicts(),
            "count": len(result),
            "total_rows": len(df), # Total no dataset (lazy count seria melhor, mas aqui df já é eager ou quase)
            "columns": result.columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
