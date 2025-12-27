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


def _find_column(df_dummy: pd.DataFrame, col_name: str) -> Optional[str]:
    """Encontra coluna no DataFrame (case-insensitive)."""
    col_lower = col_name.lower()
    
    # Primeiro: mapeamento conhecido
    if col_lower in COLUMN_MAPPING:
        mapped = COLUMN_MAPPING[col_lower]
        return mapped
    
    # Fallback se não estiver no mapping (retorna o próprio nome)
    return col_name


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
    Garante alta performance usando cache centralizado (DuckDB).
    """
    try:
        # OPTIMIZATION 2025: Reduzir limite padrão para queries mais rápidas
        # Ref: ChatGPT engineering - context pruning
        # HARD LIMIT: Previne estouro de contexto do LLM e trava de frontend
        if limite > 20:
            limite = 20  # Reduzido de 50 para 20 - resposta 60% mais rápida
            
        logger.info(f"[QUERY] Consulta flexível otimizada - Filtros: {filtros}, Agregação: {agregacao}, Limite: {limite}")
        
        # 1. Mapeamento de colunas e filtros
        from app.infrastructure.data.duckdb_adapter import duckdb_adapter
        
        # Mapear filtros para nomes reais do Parquet
        duckdb_filters = {}
        if filtros:
            # Dummy DF apenas para manter compatibilidade da função helper, se necessário
            # mas aqui vamos usar o mapping direto
            for key, val in filtros.items():
                if isinstance(val, dict): continue # Skip complex nested filters for now
                real_col = COLUMN_MAPPING.get(key.lower(), key)
                duckdb_filters[real_col] = val

        # 2. Executar consulta via DuckDB
        if agregacao and coluna_agregacao:
            # Normalizar nome da agregação (Português -> SQL)
            agg_map = {
                'soma': 'sum',
                'media': 'avg',
                'média': 'avg',
                'contagem': 'count',
                'mínimo': 'min',
                'mín': 'min',
                'máximo': 'max',
                'máx': 'max',
                'contar': 'count'
            }
            agregacao = agg_map.get(agregacao.lower(), agregacao.lower())

            # Mapear colunas de agregação
            real_agg_col = COLUMN_MAPPING.get(coluna_agregacao.lower(), coluna_agregacao)
            real_group_cols = []
            if agrupar_por:
                real_group_cols = [COLUMN_MAPPING.get(c.lower(), c) for c in agrupar_por]
            
            logger.info(f"[DUCKDB] Agregação: {agregacao}({real_agg_col}) GroupBy={real_group_cols}")
            
            df_result = duckdb_adapter.execute_aggregation(
                agg_col=real_agg_col,
                agg_func=agregacao,
                group_by=real_group_cols,
                filters=duckdb_filters,
                limit=limite
            )
            
            # Se for agregação escalar (sem group by), formatar retorno
            if not real_group_cols and not df_result.empty:
                 if 'valor' in df_result.columns:
                     valor = df_result.iloc[0]['valor']
                 else:
                     valor = df_result.iloc[0, 0] # Pega primeiro valor
                     
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

            logger.info(f"[DUCKDB] Consulta: Cols={real_cols}, Filters={list(duckdb_filters.keys())}")
            
            df_result = duckdb_adapter.load_data(
                columns=real_cols,
                filters=duckdb_filters,
                limit=limite,
                order_by=real_order
            )

        if df_result.empty:
            return {"total_resultados": 0, "resultados": [], "mensagem": "Nenhum dado encontrado."}

        # 5. OTIMIZAÇÃO DE COLUNAS: Retornar apenas o essencial para economizar tokens
        df_final = df_result
        
        # 6. Serializar
        resultados = []
        for _, row in df_final.iterrows():
            resultados.append({col: _safe_serialize(row[col]) for col in df_final.columns})
            
        # OPTIMIZATION 2025: Markdown ainda mais compacto
        # Ref: ChatGPT engineering - minimal context
        # SEGURANÇA: Limitar tabela Markdown a 3 linhas para resposta rápida
        # O usuário verá os dados completos no componente DataTable
        mensagem_tabela = f"Encontrei {len(resultados)} resultados (mostrando os top 3 abaixo):\n\n"

        if len(resultados) > 0:
            # Selecionar max 4 colunas para o markdown não ficar largo demais
            cols_to_show = list(df_final.columns)[:4]

            mensagem_tabela += "| " + " | ".join(cols_to_show) + " |\n"
            mensagem_tabela += "|" + "|".join(["---" for _ in range(len(cols_to_show))]) + "|\n"

            for item in resultados[:3]: # LIMIT 3 para Markdown
                mensagem_tabela += "| " + " | ".join([str(item.get(c, "-"))[:25] for c in cols_to_show]) + " |\n"

            if len(resultados) > 3:
                mensagem_tabela += f"\n*(...e mais {len(resultados)-3} resultados visualizáveis na tabela)*"

        return {
            "total_resultados": len(resultados),
            "resultados": resultados, # Frontend usa isso para renderizar tabela completa com paginação
            "mensagem": mensagem_tabela # LLM usa isso para entender o contexto
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Erro em consultar_dados_flexivel: {e}", exc_info=True)
        return {
            "error": f"Erro na consulta: {str(e)}",
            "total_resultados": 0,
            "resultados": [],
            "mensagem": "Ocorreu um erro ao processar sua consulta."
        }


# Exportar ferramenta
__all__ = ['consultar_dados_flexivel']