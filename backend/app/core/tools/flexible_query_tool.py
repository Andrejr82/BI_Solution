"""
Ferramenta genérica e flexível para consultas ao Parquet
Permite ao agente consultar qualquer dado de forma inteligente

CORREÇÃO 2024-12-13: Resolvido erro "DataFrame constructor not properly called"
- Carrega Parquet diretamente (evita HybridAdapter problemático)
- Serialização JSON correta com .to_dict(orient='records')
- Mapeamento case-insensitive de colunas
"""

from langchain_core.tools import tool
import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Any, List, Optional
from app.core.utils.error_handler import error_handler_decorator

logger = logging.getLogger(__name__)

# Mapeamento de colunas (lowercase → original)
COLUMN_MAPPING = {
    'nomesegmento': 'NOMESEGMENTO',
    'nomefabricante': 'NOMEFABRICANTE',
    'nomecategoria': 'NOMECATEGORIA',
    'une': 'UNE',
    'produto': 'PRODUTO',
    'codigo': 'PRODUTO',
    'nome': 'NOME',
    'estoque_une': 'ESTOQUE_UNE',
    'estoque_atual': 'ESTOQUE_UNE',  # Alias para estoque_atual
    'estoque_lv': 'ESTOQUE_LV',
    'estoque_cd': 'ESTOQUE_CD',
    'venda_30dd': 'VENDA_30DD',
    'venda_30_d': 'VENDA_30DD',  # Alias para venda_30_d (compatibilidade com une_tools)
    'preco_venda': 'PRECO_VENDA',
    'preco_custo': 'PRECO_CUSTO',
}


def _safe_serialize(value):
    """Converte valor para JSON-safe."""
    if pd.isna(value) or value is None:
        return None
    elif isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value) if not np.isnan(value) else None
    elif isinstance(value, (pd.Timestamp, np.datetime64)):
        return str(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return value


def _get_parquet_path():
    """Retorna caminho do arquivo Parquet."""
    try:
        from app.config.settings import settings
        return getattr(settings, 'PARQUET_FILE_PATH', None)
    except:
        pass
    
    # Fallback
    default_path = os.path.join(os.getcwd(), 'data', 'parquet', 'admmat.parquet')
    if os.path.exists(default_path):
        return default_path
    return None


def _find_column(df: pd.DataFrame, col_name: str) -> Optional[str]:
    """Encontra coluna no DataFrame (case-insensitive)."""
    col_lower = col_name.lower()
    
    # Primeiro: mapeamento conhecido
    if col_lower in COLUMN_MAPPING:
        mapped = COLUMN_MAPPING[col_lower]
        if mapped in df.columns:
            return mapped
    
    # Segundo: busca exata
    if col_name in df.columns:
        return col_name
    
    # Terceiro: busca case-insensitive
    for df_col in df.columns:
        if df_col.lower() == col_lower:
            return df_col
    
    return None


@tool
@error_handler_decorator(
    context_func=lambda **kwargs: {"funcao": "consultar_dados_flexivel", "params": kwargs},
    return_on_error={"error": "Erro ao consultar dados", "total_resultados": 0, "resultados": []}
)
def consultar_dados_flexivel(
    filtros: Optional[Dict[str, Any]] = None,
    colunas: Optional[List[str]] = None,
    agregacao: Optional[str] = None,
    coluna_agregacao: Optional[str] = None,
    agrupar_por: Optional[List[str]] = None,
    ordenar_por: Optional[str] = None,
    ordem_desc: bool = True,
    limite: int = 20
) -> Dict[str, Any]:
    """
    Ferramenta GENÉRICA e FLEXÍVEL para consultar dados do Parquet.
    
    Use esta ferramenta quando:
    - Precisar buscar produtos por fabricante, nome, código
    - Quiser filtrar por UNE, segmento, ou qualquer campo
    - Precisar calcular totais, médias, contagens
    - Quiser agrupar dados por categoria
    
    Args:
        filtros: Dicionário de filtros (ex: {"nomesegmento": "TECIDOS", "une": 261})
        colunas: Lista de colunas a retornar (None = todas)
        agregacao: Tipo de agregação: "sum", "avg", "count", "min", "max"
        coluna_agregacao: Coluna para agregar (ex: "VENDA_30DD", "ESTOQUE_UNE")
        agrupar_por: Lista de colunas para agrupar (ex: ["NOMEFABRICANTE", "UNE"])
        ordenar_por: Coluna para ordenar resultados
        ordem_desc: Se True, ordem decrescente
        limite: Número máximo de resultados
    
    Returns:
        Dict com resultados da consulta (JSON-safe)
    
    Exemplos:
        # Buscar produtos do segmento TECIDOS
        >>> consultar_dados_flexivel(filtros={"nomesegmento": "TECIDOS"}, limite=10)
        
        # Total de vendas por UNE
        >>> consultar_dados_flexivel(
        ...     agregacao="sum",
        ...     coluna_agregacao="VENDA_30DD",
        ...     agrupar_por=["UNE"]
        ... )
    """
    try:
        logger.info(f"📊 Consulta flexível - Filtros: {filtros}, Agregação: {agregacao}")
        
        # 1. Carregar Parquet diretamente
        parquet_path = _get_parquet_path()
        if not parquet_path or not os.path.exists(parquet_path):
            return {
                "error": "Arquivo Parquet não encontrado",
                "total_resultados": 0,
                "resultados": []
            }
        
        try:
            df = pd.read_parquet(parquet_path)
            logger.info(f"✅ Parquet carregado: {len(df)} registros, {len(df.columns)} colunas")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar Parquet: {e}")
            return {
                "error": f"Erro ao carregar dados: {str(e)}",
                "total_resultados": 0,
                "resultados": []
            }
        
        # 2. Aplicar filtros
        if filtros:
            for col_key, val in filtros.items():
                # Ignorar valores complexos
                if isinstance(val, dict):
                    continue
                
                # Encontrar coluna real
                actual_col = _find_column(df, col_key)
                if actual_col is None:
                    logger.warning(f"⚠️ Coluna '{col_key}' não encontrada")
                    continue
                
                # Aplicar filtro
                if isinstance(val, str):
                    # Filtro texto: case-insensitive contains
                    mask = df[actual_col].astype(str).str.upper().str.contains(val.upper(), na=False)
                    df = df[mask]
                    logger.info(f"Filtro texto: {actual_col} contém '{val}' → {len(df)} registros")
                else:
                    # Filtro exato
                    df = df[df[actual_col] == val]
                    logger.info(f"Filtro exato: {actual_col} == {val} → {len(df)} registros")
        
        if df.empty:
            return {
                "total_resultados": 0,
                "resultados": [],
                "mensagem": "Nenhum dado encontrado com os filtros aplicados."
            }
        
        # 3. Aplicar agregação
        if agregacao and coluna_agregacao:
            # Encontrar coluna de agregação
            agg_col = _find_column(df, coluna_agregacao)
            if agg_col is None:
                return {
                    "error": f"Coluna '{coluna_agregacao}' não encontrada",
                    "colunas_disponiveis": list(df.columns)[:15],
                    "total_resultados": 0,
                    "resultados": []
                }
            
            if agrupar_por:
                # Encontrar colunas de agrupamento
                group_cols = []
                for g in agrupar_por:
                    gc = _find_column(df, g)
                    if gc:
                        group_cols.append(gc)
                
                if not group_cols:
                    return {
                        "error": f"Colunas de agrupamento não encontradas: {agrupar_por}",
                        "total_resultados": 0,
                        "resultados": []
                    }
                
                # Agregar
                agg_funcs = {"sum": "sum", "avg": "mean", "count": "count", "min": "min", "max": "max"}
                agg_func = agg_funcs.get(agregacao, "sum")
                
                df_result = df.groupby(group_cols)[agg_col].agg(agg_func).reset_index()
                df_result = df_result.rename(columns={agg_col: f"{agregacao}_{coluna_agregacao}"})
            else:
                # Agregação simples (sem agrupamento)
                agg_funcs = {"sum": df[agg_col].sum, "avg": df[agg_col].mean, 
                             "count": df[agg_col].count, "min": df[agg_col].min, "max": df[agg_col].max}
                valor = agg_funcs.get(agregacao, df[agg_col].sum)()
                
                return {
                    "total_resultados": 1,
                    "resultado_agregado": {
                        "agregacao": agregacao,
                        "coluna": coluna_agregacao,
                        "valor": _safe_serialize(valor)
                    },
                    "mensagem": f"{agregacao.upper()} de {coluna_agregacao}: {_safe_serialize(valor)}"
                }
        else:
            df_result = df
        
        # 4. Ordenar
        if ordenar_por:
            sort_col = _find_column(df_result, ordenar_por)
            if sort_col:
                df_result = df_result.sort_values(sort_col, ascending=not ordem_desc)
        
        # 5. Limitar resultados
        df_result = df_result.head(limite)
        
        # 6. ⭐ CRÍTICO: Converter para formato JSON-safe
        # Usar to_dict + serialização segura para evitar erros
        resultados = []
        for _, row in df_result.iterrows():
            item = {}
            for col in df_result.columns:
                item[col] = _safe_serialize(row[col])
            resultados.append(item)
        
        total = len(resultados)
        logger.info(f"✅ Consulta retornou {total} resultados")
        
        return {
            "total_resultados": total,
            "resultados": resultados,
            "limite_aplicado": limite,
            "mensagem": f"{total} resultado(s) encontrado(s)"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro em consultar_dados_flexivel: {e}", exc_info=True)
        return {
            "error": f"Erro na consulta: {str(e)}",
            "total_resultados": 0,
            "resultados": [],
            "mensagem": "Ocorreu um erro ao processar sua consulta."
        }


# Exportar ferramenta
__all__ = ['consultar_dados_flexivel']
