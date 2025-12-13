from typing import Annotated, List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_active_user
from app.infrastructure.database.models import User
from app.core.tools.une_tools import (
    validar_transferencia_produto,
    sugerir_transferencias_automaticas,
)
from app.core.utils.error_handler import APIError

router = APIRouter(prefix="/transfers", tags=["Transfers"])

# Path to store transfer requests
TRANSFER_REQUESTS_DIR = Path("data/transferencias")
os.makedirs(TRANSFER_REQUESTS_DIR, exist_ok=True)


class TransferRequestPayload(BaseModel):
    produto_id: int
    une_origem: int
    une_destino: int
    quantidade: int
    solicitante_id: str # Will be populated by current_user


class TransferReportQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProductSearchRequest(BaseModel):
    segmento: Optional[str] = None
    fabricante: Optional[str] = None
    estoque_min: Optional[int] = None
    limit: int = Field(default=50, le=500)


class BulkTransferRequestPayload(BaseModel):
    """Payload para transferências múltiplas (1→N ou N→N)"""
    items: List[TransferRequestPayload]
    modo: str = Field(description="Modo: '1→1', '1→N', ou 'N→N'")


@router.post("/validate")
async def validate_transfer(
    payload: TransferRequestPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """
    Endpoint to validate a product transfer between UNEs.
    Integrates with `validar_transferencia_produto` tool.
    Includes priority score (0-100) and urgency level.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        # Validação básica usando a tool existente
        result = validar_transferencia_produto.invoke({
            "produto_id": payload.produto_id,
            "une_origem": payload.une_origem,
            "une_destino": payload.une_destino,
            "quantidade": payload.quantidade,
        })

        # Calcular score de prioridade baseado em criticidade
        score_prioridade = 50  # Default
        nivel_urgencia = "NORMAL"

        try:
            df = data_scope_service.get_filtered_dataframe(current_user)

            # Buscar dados do produto na UNE destino
            df_produto = df.filter(
                (pl.col("PRODUTO") == payload.produto_id) &
                (pl.col("UNE") == payload.une_destino)
            )

            if len(df_produto) > 0:
                row = df_produto.row(0, named=True)

                estoque_loja = float(row.get("ESTOQUE_UNE", 0) or 0)
                estoque_cd = float(row.get("ESTOQUE_CD", 0) or 0)
                linha_verde = float(row.get("ESTOQUE_LV", 0) or 0)
                venda_30dd = float(row.get("VENDA_30DD", 0) or 0)

                # Calcular score (0-100)
                # Fatores: ruptura, vendas, relação estoque/linha verde
                score = 0

                # +40 pontos se CD zerado
                if estoque_cd == 0:
                    score += 40

                # +30 pontos se estoque loja < linha verde
                if estoque_loja < linha_verde:
                    score += 30

                # +20 pontos baseado em vendas (normalizado)
                if venda_30dd > 0:
                    score += min(20, int(venda_30dd / 10))

                # +10 pontos se estoque crítico (< 50% da LV)
                if linha_verde > 0 and estoque_loja < (linha_verde * 0.5):
                    score += 10

                score_prioridade = min(100, score)

                # Determinar nível de urgência
                if score_prioridade >= 80:
                    nivel_urgencia = "URGENTE"
                elif score_prioridade >= 60:
                    nivel_urgencia = "ALTA"
                elif score_prioridade >= 40:
                    nivel_urgencia = "MÉDIA"
                else:
                    nivel_urgencia = "BAIXA"

        except Exception as e:
            print(f"Erro ao calcular score: {e}")

        # Adicionar score ao resultado
        result["score_prioridade"] = score_prioridade
        result["nivel_urgencia"] = nivel_urgencia

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating transfer: {str(e)}",
        )


@router.get("/suggestions")
async def get_transfer_suggestions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    segmento: Optional[str] = Query(None),
    une_origem_excluir: Optional[int] = Query(None),
    limit: int = Query(5),
) -> List[Dict[str, Any]]:
    """
    Endpoint to get automatic transfer suggestions.
    Integrates with `sugerir_transferencias_automaticas` tool.
    """
    try:
        suggestions = sugerir_transferencias_automaticas(
            segmento=segmento, une_origem_excluir=une_origem_excluir, limite=limit
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting transfer suggestions: {str(e)}",
        )


@router.post("")
async def create_transfer_request(
    payload: TransferRequestPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """
    Endpoint to create and save a transfer request.
    """
    try:
        transfer_data = payload.model_dump()
        transfer_data["solicitante_id"] = current_user.username
        transfer_data["timestamp"] = datetime.now().isoformat()
        transfer_id = f"transfer_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        file_path = TRANSFER_REQUESTS_DIR / f"{transfer_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(transfer_data, f, ensure_ascii=False, indent=4)

        return {"message": "Transfer request created successfully", "transfer_id": transfer_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transfer request: {str(e)}",
        )


@router.get("/report")
async def get_transfers_report(
    current_user: Annotated[User, Depends(get_current_active_user)],
    query: TransferReportQuery = Depends(),
) -> List[Dict[str, Any]]:
    """
    Endpoint to generate a report of transfer requests.
    Reads JSON files from the `data/transferencias/` directory.
    """
    all_transfers = []
    start_date = datetime.fromisoformat(query.start_date) if query.start_date else datetime.min
    end_date = datetime.fromisoformat(query.end_date) if query.end_date else datetime.max

    for filename in os.listdir(TRANSFER_REQUESTS_DIR):
        if filename.endswith(".json"):
            file_path = TRANSFER_REQUESTS_DIR / filename
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    transfer_data = json.load(f)
                    transfer_timestamp = datetime.fromisoformat(transfer_data.get("timestamp"))
                    if start_date <= transfer_timestamp <= end_date:
                        all_transfers.append(transfer_data)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading or decoding transfer file {file_path}: {e}")
                # Optionally, raise HTTPException if corrupt file is critical

    # Basic aggregation or sorting could be done here if needed
    all_transfers.sort(key=lambda x: x.get("timestamp"), reverse=True)

    return all_transfers


@router.get("/filters")
async def get_transfer_filters(
    current_user: Annotated[User, Depends(get_current_active_user)],
    segmento: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """
    Endpoint to get available filter options for transfers.
    Returns unique values for segmento and fabricante.
    If 'segmento' is provided, filters 'fabricantes' accordingly.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Determinar nomes corretos das colunas
        segmento_col = "NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else None
        fabricante_col = "NOMEFABRICANTE" if "NOMEFABRICANTE" in df.columns else None

        # Obter valores únicos de segmentos (independentemente do filtro)
        segmentos = []
        if segmento_col:
            segmentos = df.select(pl.col(segmento_col)).unique().drop_nulls().sort(segmento_col).to_series().to_list()
            segmentos = [str(s) for s in segmentos if s and str(s).strip()]

        # Filtrar DF se segmento for fornecido
        if segmento and segmento_col:
            # Usar contains para flexibilidade ou == para exato. Backend original usava contains.
            # Vamos usar exato se possível para filtros de combo, ou contains se o frontend mandar parcial.
            # O frontend manda o valor do option, então deve ser exato.
            # Mas como o searchProducts usa contains, vou usar == para ser preciso na lista dependente.
            df = df.filter(pl.col(segmento_col) == segmento)

        # Obter fabricantes (filtrados ou não)
        fabricantes = []
        if fabricante_col:
            fabricantes = df.select(pl.col(fabricante_col)).unique().drop_nulls().sort(fabricante_col).to_series().to_list()
            fabricantes = [str(f) for f in fabricantes if f and str(f).strip()]

        return {
            "segmentos": segmentos[:100],  # Limitar a 100 para performance
            "fabricantes": fabricantes[:100]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting filters: {str(e)}",
        )


@router.post("/products/search")
async def search_products(
    request: ProductSearchRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Dict[str, Any]]:
    """
    Endpoint to search products with filters for transfer management.
    Returns products matching criteria with stock information.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Determinar nomes corretos das colunas
        segmento_col = "NOMESEGMENTO" if "NOMESEGMENTO" in df.columns else None
        fabricante_col = "NOMEFABRICANTE" if "NOMEFABRICANTE" in df.columns else None

        # Aplicar filtros
        if request.segmento and segmento_col:
            df = df.filter(pl.col(segmento_col).str.contains(request.segmento, literal=False))

        if request.fabricante and fabricante_col:
            df = df.filter(pl.col(fabricante_col).str.contains(request.fabricante, literal=False))

        if request.estoque_min is not None:
            df = df.filter(pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0) >= request.estoque_min)

        # Preparar colunas para agrupamento
        group_cols = ["PRODUTO", "NOME"]
        if segmento_col:
            group_cols.append(segmento_col)
        if fabricante_col:
            group_cols.append(fabricante_col)

        # Agrupar por produto e agregar informações
        df_grouped = df.group_by(group_cols).agg([
            pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0).sum().alias("estoque_total_loja"),
            pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0).sum().alias("estoque_total_cd"),
            pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0).sum().alias("vendas_30dd"),
            pl.col("UNE").n_unique().alias("unes_com_estoque")
        ])

        df_result = df_grouped.head(request.limit)

        products = []
        for row in df_result.iter_rows(named=True):
            products.append({
                "produto_id": int(row["PRODUTO"]),
                "nome": str(row["NOME"])[:60],
                "segmento": str(row.get(segmento_col, "N/A")) if segmento_col else "N/A",
                "fabricante": str(row.get(fabricante_col, "N/A"))[:30] if fabricante_col else "N/A",
                "estoque_loja": int(row["estoque_total_loja"]),
                "estoque_cd": int(row["estoque_total_cd"]),
                "vendas_30dd": int(row["vendas_30dd"]),
                "unes": int(row["unes_com_estoque"])
            })

        return products

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching products: {str(e)}",
        )


@router.post("/bulk")
async def create_bulk_transfer_request(
    payload: BulkTransferRequestPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """
    Endpoint to create multiple transfer requests at once (1→N or N→N modes).
    Saves all transfers in a single batch file.
    """
    try:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        batch_data = {
            "batch_id": batch_id,
            "modo": payload.modo,
            "solicitante_id": current_user.username,
            "timestamp": datetime.now().isoformat(),
            "total_transferencias": len(payload.items),
            "transferencias": []
        }

        for item in payload.items:
            transfer = item.model_dump()
            transfer["solicitante_id"] = current_user.username
            batch_data["transferencias"].append(transfer)

        file_path = TRANSFER_REQUESTS_DIR / f"{batch_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=4)

        return {
            "message": f"Batch transfer request created successfully ({len(payload.items)} items)",
            "batch_id": batch_id,
            "modo": payload.modo
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bulk transfer request: {str(e)}",
        )


@router.get("/unes")
async def get_available_unes(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Dict[str, Any]]:
    """
    Endpoint to get list of available UNEs for transfer selection.
    """
    import polars as pl
    from app.core.data_scope_service import data_scope_service

    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Obter UNEs únicas com contagem de produtos
        unes_data = df.group_by("UNE").agg([
            pl.col("PRODUTO").n_unique().alias("total_produtos"),
            pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0).sum().alias("estoque_total")
        ]).sort("UNE")

        unes = []
        for row in unes_data.iter_rows(named=True):
            unes.append({
                "une": int(row["UNE"]),
                "total_produtos": int(row["total_produtos"]),
                "estoque_total": int(row["estoque_total"])
            })

        return unes

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching UNEs: {str(e)}",
        )
