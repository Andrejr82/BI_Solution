from typing import Annotated, List, Dict, Any, Optional

import polars as pl
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User

router = APIRouter(prefix="/rupturas", tags=["Rupturas"])

@router.get("/critical", response_model=List[Dict[str, Any]])
async def get_critical_rupturas(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = Query(50, description="Número máximo de resultados"),
    segmento: Optional[str] = Query(None, description="Filtro por segmento (NOMESEGMENTO)"),
    une: Optional[str] = Query(None, description="Filtro por UNE")
):
    """
    Produtos com ruptura crítica (ESTOQUE_CD=0 + Estoque Loja < Linha Verde).

    Definição de Ruptura Crítica (conforme regras de negócio):
    - ESTOQUE_CD = 0 (sem estoque no centro de distribuição)
    - ESTOQUE_UNE < ESTOQUE_LV (estoque da loja menor que linha verde)
    - VENDA_30DD > 0 (produtos com vendas nos últimos 30 dias)

    Retorna:
    - CRITICIDADE_PCT: percentual de criticidade (0-100%) baseado na razão venda/linha verde
    - NECESSIDADE: quantidade faltando para atingir a linha verde
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Verificar colunas necessárias
        required_cols = ["ESTOQUE_CD", "ESTOQUE_UNE", "ESTOQUE_LV", "VENDA_30DD"]
        if not all(col in df.columns for col in required_cols):
            return []

        # Casting para garantir tipos numéricos
        df = df.with_columns([
            pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0),
        ])

        # Aplicar filtros opcionais
        if segmento and "NOMESEGMENTO" in df.columns:
            df = df.filter(pl.col("NOMESEGMENTO") == segmento)

        if une:
            # UNE pode ser string ou int - tentar conversão
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[FILTER] Filtro UNE recebido: '{une}'")
            
            try:
                une_val = int(une)
                df = df.filter(pl.col("UNE") == une_val)
                logger.info(f"[OK] Filtro UNE aplicado como INT: {df.height} registros")
            except (ValueError, Exception) as e:
                # Se falhar, tentar como string
                logger.warning(f"[WARN] Conversão para int falhou, tentando como string: {e}")
                df = df.filter(pl.col("UNE").cast(pl.Utf8) == str(une))
                logger.info(f"[OK] Filtro UNE aplicado como STRING: {df.height} registros")

        # Definição de ruptura crítica:
        # CD=0 + Loja < Linha Verde + Vendas > 0
        rupturas = df.filter(
            (pl.col("ESTOQUE_CD") <= 0) &
            (pl.col("ESTOQUE_UNE") < pl.col("ESTOQUE_LV")) &
            (pl.col("VENDA_30DD") > 0)
        )

        # Calcular criticidade % e necessidade
        rupturas = rupturas.with_columns([
            # Criticidade = (Venda / Linha Verde) * 100, limitado a 100%
            pl.when(pl.col("ESTOQUE_LV") > 0)
              .then((pl.col("VENDA_30DD") / pl.col("ESTOQUE_LV") * 100).clip(0, 100))
              .otherwise(0)
              .alias("CRITICIDADE_PCT"),

            # Necessidade = Linha Verde - Estoque Atual
            (pl.col("ESTOQUE_LV") - pl.col("ESTOQUE_UNE"))
              .clip(0, None)
              .alias("NECESSIDADE")
        ])

        # Ordenar por criticidade e venda
        rupturas = rupturas.sort(["CRITICIDADE_PCT", "VENDA_30DD"], descending=[True, True]).head(limit)

        return rupturas.to_dicts()
    except Exception as e:
        logger.error(f"Error in critical rupturas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/segmentos", response_model=List[str])
async def get_segmentos(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Lista todos os segmentos disponíveis para filtro.
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        if "NOMESEGMENTO" not in df.columns:
            return []

        segmentos = df.select("NOMESEGMENTO").unique().sort("NOMESEGMENTO").to_series().to_list()
        return [s for s in segmentos if s is not None and str(s).strip()]
    except Exception as e:
        logger.error(f"Error in critical rupturas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/unes", response_model=List[str])
async def get_unes(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Lista todas as UNEs disponíveis para filtro.
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        if "UNE" not in df.columns:
            return []

        unes = df.select("UNE").unique().sort("UNE").to_series().to_list()
        return [str(u) for u in unes if u is not None]
    except Exception as e:
        logger.error(f"Error in critical rupturas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=Dict[str, Any])
async def get_rupturas_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    segmento: Optional[str] = Query(None, description="Filtro por segmento"),
    une: Optional[str] = Query(None, description="Filtro por UNE")
):
    """
    Retorna resumo de métricas de rupturas críticas.
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        required_cols = ["ESTOQUE_CD", "ESTOQUE_UNE", "ESTOQUE_LV", "VENDA_30DD"]
        if not all(col in df.columns for col in required_cols):
            return {"total": 0, "criticos": 0, "valor_estimado": 0}

        # Casting
        df = df.with_columns([
            pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0),
            pl.col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0),
        ])

        # Aplicar filtros
        if segmento and "NOMESEGMENTO" in df.columns:
            df = df.filter(pl.col("NOMESEGMENTO") == segmento)
        if une:
            try:
                une_val = int(une)
                df = df.filter(pl.col("UNE") == une_val)
            except (ValueError, Exception):
                df = df.filter(pl.col("UNE").cast(pl.Utf8) == str(une))

        # Filtrar rupturas
        rupturas = df.filter(
            (pl.col("ESTOQUE_CD") <= 0) &
            (pl.col("ESTOQUE_UNE") < pl.col("ESTOQUE_LV")) &
            (pl.col("VENDA_30DD") > 0)
        )

        # Calcular criticidade
        rupturas = rupturas.with_columns([
            pl.when(pl.col("ESTOQUE_LV") > 0)
              .then((pl.col("VENDA_30DD") / pl.col("ESTOQUE_LV") * 100).clip(0, 100))
              .otherwise(0)
              .alias("CRITICIDADE_PCT")
        ])

        total = rupturas.height
        criticos = rupturas.filter(pl.col("CRITICIDADE_PCT") >= 75).height

        return {
            "total": total,
            "criticos": criticos,
            "valor_estimado": 0  # Pode ser calculado se houver coluna de custo
        }
    except Exception as e:
        logger.error(f"Error in critical rupturas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
