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
from typing import Dict, Any, List, Optional, Union
from app.core.utils.error_handler import error_handler_decorator

logger = logging.getLogger(__name__)

# Mapeamento de colunas (lowercase → original)
# UPDATED 2026-01-06: Refactored to use Centralized Semantic Layer (FieldMapper)
# This removes hardcoded dictionary and ensures Single Source of Truth
from app.core.utils.field_mapper import FieldMapper
field_mapper = FieldMapper()

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
    """Encontra coluna no DataFrame (case-insensitive) usando Semantic Layer."""
    # Tenta usar o mapeador semântico
    mapped = field_mapper.map_term(col_name)
    if mapped:
        return mapped
    
    # Fallback: tenta encontrar correspondência exata no dataframe
    # (Embora não tenhamos o DF real aqui, mantém lógica original de fallback)
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
    ordem_desc: Optional[Union[bool, str]] = True,
    limite: Optional[Union[int, str]] = 20
) -> Dict[str, Any]:
    """
    Ferramenta GENÉRICA e FLEXÍVEL para consultar dados do Parquet.
    Garante alta performance usando cache centralizado (DuckDB SQL Push-down).
    """
    try:
        # FIX 2026-01-09: Converter parâmetros que podem vir como string do Groq
        if isinstance(limite, str):
            limite = int(limite) if limite.isdigit() else 20
        if limite is None:
            limite = 20
        if isinstance(ordem_desc, str):
            ordem_desc = ordem_desc.lower() in ['true', '1', 'yes', 'sim']
        if ordem_desc is None:
            ordem_desc = True
            
        # OPTIMIZATION 2025: Reduzir limite padrão para queries mais rápidas
        if limite > 50:
            limite = 50 
            
        logger.info(f"[QUERY] Consulta flexível otimizada (SQL) - Filtros: {filtros}, Agregação: {agregacao}, Limite: {limite}")
        
        from app.core.parquet_cache import cache
        from app.core.context import get_current_user_segments # RLS
        
        # 1. Garantir tabela em memória (Zero-Copy)
        table_name = cache._adapter.get_memory_table("admmat.parquet")
        
        # 2. Construir SQL Dinâmico
        select_clause = "*"
        where_clause = "1=1"
        
        # --- RLS INJECTION (SEGURANÇA) ---
        allowed_segments = get_current_user_segments()
        if allowed_segments and "*" not in allowed_segments:
            # Filtrar por segmentos permitidos
            # Escape strings to prevent injection
            safe_segments = [s.replace("'", "''") for s in allowed_segments]
            segments_sql = ",".join([f"'{s}'" for s in safe_segments])
            where_clause += f" AND NOMESEGMENTO IN ({segments_sql})"
            logger.info(f"[RLS] Aplicando filtro SQL: NOMESEGMENTO IN ({segments_sql})")
        # ---------------------------------
        
        group_by_clause = ""
        order_by_clause = ""
        
        # 2.1 Mapeamento de Colunas e Filtros
        mapped_filters = {}
        if filtros:
            for key, val in filtros.items():
                if isinstance(val, dict): continue
                real_col = field_mapper.map_term(key) or key
                mapped_filters[real_col] = val
                
                # Construir WHERE clause
                if isinstance(val, str):
                    clean_val = val.replace("'", "''")
                    where_clause += f" AND {real_col} ILIKE '%{clean_val}%'"
                elif isinstance(val, list):
                    vals_str = ",".join([f"'{str(v)}'" if isinstance(v, str) else str(v) for v in val])
                    where_clause += f" AND {real_col} IN ({vals_str})"
                else:
                    where_clause += f" AND {real_col} = {val}"

        # 2.2 Agregação (se houver)
        if agregacao and coluna_agregacao:
            agg_map = {
                'soma': 'SUM', 'media': 'AVG', 'média': 'AVG', 'contagem': 'COUNT',
                'mínimo': 'MIN', 'mín': 'MIN', 'máximo': 'MAX', 'máx': 'MAX', 'contar': 'COUNT'
            }
            sql_agg = agg_map.get(agregacao.lower(), agregacao.upper())
            real_agg_col = field_mapper.map_term(coluna_agregacao) or coluna_agregacao
            
            # Tratamento especial para VENDA R$
            if "venda" in real_agg_col.lower() and ("r$" in real_agg_col.lower() or "valor" in real_agg_col.lower()):
                 real_agg_col = "VENDA_30DD"
            
            select_clause = f"{sql_agg}({real_agg_col}) as valor"
            
            if agrupar_por:
                real_group_cols = [field_mapper.map_term(c) or c for c in agrupar_por]
                group_cols_str = ", ".join(real_group_cols)
                select_clause = f"{group_cols_str}, {select_clause}"
                group_by_clause = f"GROUP BY {group_cols_str}"
                order_by_clause = "ORDER BY valor DESC" # Default sort by agg value
        
        # 2.3 Seleção de Colunas (sem agregação)
        elif colunas:
            real_cols = []
            for c in colunas:
                mapped = field_mapper.map_term(c) or c
                real_cols.append(mapped)
            select_clause = ", ".join(list(set(real_cols)))
            
        # 2.4 Ordenação
        if ordenar_por and not order_by_clause:
            real_sort_col = field_mapper.map_term(ordenar_por) or ordenar_por
            direction = "DESC" if ordem_desc else "ASC"
            order_by_clause = f"ORDER BY {real_sort_col} {direction}"
            
        # Montar Query Final
        sql_query = f"""
            SELECT {select_clause}
            FROM {table_name}
            WHERE {where_clause}
            {group_by_clause}
            {order_by_clause}
            LIMIT {limite}
        """
        
        logger.info(f"[DUCKDB SQL] Executando: {sql_query}")
        
        # 3. Executar
        result = cache._adapter.query(sql_query)
        
        # Converter para DataFrame Pandas para manter compatibilidade com serialização existente
        if hasattr(result, 'to_pandas'):
            df_final = result.to_pandas()
        elif hasattr(result, 'df'):
            df_final = result.df()
        else:
            df_final = pd.DataFrame(result)
            
        # 4. Cálculo de Campos Virtuais (Pós-processamento Pandas para cálculos complexos)
        # Se Margem foi solicitada mas não calculada no SQL (simplificação)
        if colunas and any("margem" in c.lower() for c in colunas):
             if "LIQUIDO_38" in df_final.columns and "ULTIMA_ENTRADA_CUSTO_CD" in df_final.columns:
                try:
                    df_final['MARGEM'] = ((df_final['LIQUIDO_38'] - df_final['ULTIMA_ENTRADA_CUSTO_CD']) / df_final['LIQUIDO_38'] * 100).fillna(0).round(2)
                except:
                    pass

        # 5. Serializar
        if df_final.empty:
            return {"total_resultados": 0, "resultados": [], "mensagem": "Nenhum dado encontrado."}

        resultados = []
        for _, row in df_final.iterrows():
            resultados.append({col: _safe_serialize(row[col]) for col in df_final.columns})
            
        # Se for escalar (agregacao sem grupo)
        if agregacao and not agrupar_por and len(resultados) == 1:
             valor = resultados[0].get('valor')
             return {"total_resultados": 1, "resultado_agregado": {"valor": valor}, "mensagem": f"{agregacao.upper()}: {valor}"}

        # Formatar Markdown
        mensagem_tabela = f"Encontrei {len(resultados)} resultados:\n\n"
        if len(resultados) > 0:
            cols_to_show = list(df_final.columns)[:4]
            mensagem_tabela += "| " + " | ".join(cols_to_show) + " |\n"
            mensagem_tabela += "|" + "|".join(["---" for _ in range(len(cols_to_show))]) + "|\n"
            for item in resultados[:3]:
                mensagem_tabela += "| " + " | ".join([str(item.get(c, "-"))[:25] for c in cols_to_show]) + " |\n"
            if len(resultados) > 3:
                mensagem_tabela += f"\n*(...e mais {len(resultados)-3} resultados)*"

        return {
            "total_resultados": len(resultados),
            "resultados": resultados, 
            "mensagem": mensagem_tabela 
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Erro em consultar_dados_flexivel (SQL): {e}", exc_info=True)
        # Fallback silencioso não implementado para manter simplicidade e erro claro se SQL falhar
        return {
            "error": f"Erro na consulta: {str(e)}",
            "total_resultados": 0,
            "resultados": [],
            "mensagem": "Ocorreu um erro ao processar sua consulta."
        }


# Exportar ferramenta
__all__ = ['consultar_dados_flexivel']
