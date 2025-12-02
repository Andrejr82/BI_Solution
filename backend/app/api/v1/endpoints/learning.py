from typing import Annotated, Dict, Any, List

import polars as pl
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User

router = APIRouter(prefix="/learning", tags=["Learning"])

@router.get("/insights", response_model=Dict[str, List[Dict[str, Any]]])
async def get_insights(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Gera insights simples baseados em regras sobre os dados.
    (Placeholder para futura integração com LLM)
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user, max_rows=10000)
        
        insights = []
        
        # 1. Top Performer
        if "VENDA_30DD" in df.columns and "NOME" in df.columns:
            top = df.sort("VENDA_30DD", descending=True).head(1)
            if len(top) > 0:
                nome = top["NOME"][0]
                vendas = top["VENDA_30DD"][0]
                insights.append({
                    "type": "top_performer",
                    "title": "Produto Campeão de Vendas",
                    "description": f"O produto '{nome}' teve {vendas} vendas nos últimos 30 dias."
                })

        # 2. Stock Alert
        if "ESTOQUE_UNE" in df.columns and "VENDA_30DD" in df.columns:
            low_stock = df.filter(
                (pl.col("VENDA_30DD") > 10) & (pl.col("ESTOQUE_UNE") < 5)
            )
            if len(low_stock) > 0:
                insights.append({
                    "type": "stock_alert",
                    "title": "Risco de Ruptura",
                    "description": f"{len(low_stock)} produtos com alta venda e estoque baixo."
                })

        return {"insights": insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
