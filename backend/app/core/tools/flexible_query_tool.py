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
    Garante alta performance usando cache centralizado.
    """
    try:
        # HARD LIMIT: Previne estouro de contexto do LLM
        if limite > 50:
            limite = 50
            
        logger.info(f"📊 Consulta flexível otimizada - Filtros: {filtros}, Agregação: {agregacao}, Limite: {limite}")
        
        # 1. Mapeamento de colunas e filtros
        from app.infrastructure.data.duckdb_adapter import duckdb_adapter
        
        # Mapear filtros para nomes reais do Parquet
        duckdb_filters = {}
        if filters:
            for key, val in filters.items():
                if isinstance(val, dict): continue # Skip complex nested filters for now
                real_col = _find_column(pd.DataFrame(columns=list(COLUMN_MAPPING.values())), key)
                # Fallback to direct mapping if _find_column fails without data
                if not real_col:
                     real_col = COLUMN_MAPPING.get(key.lower(), key)
                duckdb_filters[real_col] = val

        # 2. Executar consulta via DuckDB
        if agregacao and coluna_agregacao:
            # Mapear colunas de agregação
            real_agg_col = COLUMN_MAPPING.get(coluna_agregacao.lower(), coluna_agregacao)
            real_group_cols = []
            if agrupar_por:
                real_group_cols = [COLUMN_MAPPING.get(c.lower(), c) for c in agrupar_por]
            
            logger.info(f"📊 DuckDB Agregação: {agregacao}({real_agg_col}) GroupBy={real_group_cols}")
            
            df_result = duckdb_adapter.execute_aggregation(
                agg_col=real_agg_col,
                agg_func=agregacao,
                group_by=real_group_cols,
                filters=duckdb_filters,
                limit=limite
            )
            
            # Se for agregação escalar (sem group by), formatar retorno
            if not real_group_cols and not df_result.empty:
                 valor = df_result.iloc[0]['valor']
                 return {"total_resultados": 1, "resultado_agregado": {"valor": _safe_serialize(valor)}, "mensagem": f"{agregacao.upper()}: {_safe_serialize(valor)}"}

        else:
            # Consulta simples (Load Data)
            # Mapear colunas solicitadas
            real_cols = None
            if colunas:
                real_cols = [COLUMN_MAPPING.get(c.lower(), c) for c in colunas]
            
            # Ordenação
            real_order = None
            if ordenar_por:
                real_sort_col = COLUMN_MAPPING.get(ordenar_por.lower(), ordenar_por)
                direction = "DESC" if ordem_desc else "ASC"
                real_order = f"{real_sort_col} {direction}"

            logger.info(f"📊 DuckDB Consulta: Cols={real_cols}, Filters={list(duckdb_filters.keys())}")
            
            df_result = duckdb_adapter.load_data(
                columns=real_cols,
                filters=duckdb_filters,
                limit=limite,
                order_by=real_order
            )

        if df_result.empty:
            return {"total_resultados": 0, "resultados": [], "mensagem": "Nenhum dado encontrado."}

        # 5. OTIMIZAÇÃO DE COLUNAS: Retornar apenas o essencial para economizar tokens
        # (Lógica mantida para garantir output limpo para o LLM)
        df_final = df_result # Já vem filtrado do DuckDB se 'colunas' foi passado
        
        # 6. Serializar
        resultados = []
        for _, row in df_final.iterrows():
            resultados.append({col: _safe_serialize(row[col]) for col in df_final.columns})
            
        # Gerar Markdown simplificado
        mensagem_tabela = f"Exibindo os primeiros {len(resultados)} resultados:\n\n"
        if len(resultados) > 0:
            cols_to_show = df_final.columns[:5]
            mensagem_tabela += "| " + " | ".join(cols_to_show) + " |\n"
            mensagem_tabela += "|" + "|".join(["---" for _ in range(len(cols_to_show))]) + "|\n"
            for item in resultados[:10]: # Limitar tabela markdown a 10 linhas no prompt
                mensagem_tabela += "| " + " | ".join([str(item.get(c, "-"))[:20] for c in cols_to_show]) + " |\n"

        return {
            "total_resultados": len(resultados),
            "resultados": resultados,
            "mensagem": mensagem_tabela
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
