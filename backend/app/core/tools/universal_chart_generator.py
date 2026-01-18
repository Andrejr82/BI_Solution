"""
Ferramenta Universal de Geração de Gráficos - Context7 2025
Solução definitiva para gráficos com filtros dinâmicos e performance otimizada.
"""

import logging
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import plotly.graph_objects as go
from langchain_core.tools import tool
from app.core.data_source_manager import get_data_manager

logger = logging.getLogger(__name__)


def _export_chart_to_json(fig: go.Figure) -> str:
    """Exporta figura como JSON para frontend."""
    return fig.to_json()


@tool
def gerar_grafico_universal_v2(
    descricao: str,
    filtro_une: Optional[Union[str, int]] = None,
    filtro_segmento: Optional[str] = None,
    filtro_categoria: Optional[str] = None,
    filtro_produto: Optional[Union[str, int]] = None,
    tipo_grafico: str = "auto",
    limite: Optional[Union[str, int]] = None
) -> Dict[str, Any]:
    """
    Gera qualquer tipo de gráfico com filtros dinâmicos.

    Esta é a ferramenta UNIVERSAL para geração de gráficos.
    Substitui todas as ferramentas específicas anteriores.

    Args:
        descricao: Descrição do que deve ser visualizado (ex: "vendas por segmento")
        filtro_une: Código da loja/UNE (ex: "1685" ou "1685, 2365" para comparação).
        filtro_segmento: Nome do segmento para filtrar (ex: "ARMARINHO")
        filtro_categoria: Nome da categoria para filtrar
        filtro_produto: Código do produto (SKU) (ex: "369946").
        tipo_grafico: Tipo de gráfico ("bar", "pie", "line", "auto")
        limite: Número máximo de itens no gráfico (ex: "10").

    Returns:
        Gráfico Plotly JSON com dados filtrados
    """
    # 1. Parse de Filtros Numéricos (Lista ou Único)
    lista_unes = []
    if filtro_une is not None:
        try:
            if isinstance(filtro_une, str) and "," in filtro_une:
                lista_unes = [int(u.strip()) for u in filtro_une.split(",") if u.strip().isdigit()]
            elif isinstance(filtro_une, list):
                lista_unes = [int(u) for u in filtro_une]
            else:
                lista_unes = [int(filtro_une)]
        except (ValueError, TypeError):
            logger.warning(f"Erro ao parsear filtro_une: {filtro_une}")

    lista_produtos = []
    if filtro_produto is not None:
        try:
            if isinstance(filtro_produto, str) and "," in filtro_produto:
                lista_produtos = [int(p.strip()) for p in filtro_produto.split(",") if p.strip().isdigit()]
            elif isinstance(filtro_produto, list):
                lista_produtos = [int(p) for p in filtro_produto]
            else:
                lista_produtos = [int(filtro_produto)]
        except (ValueError, TypeError):
            logger.warning(f"Erro ao parsear filtro_produto: {filtro_produto}")

    try:
        if limite is not None:
            limite = int(limite)
        else:
            limite = 10
    except:
        limite = 10
        
    logger.info(f"[UNIVERSAL CHART] Gerando: {descricao} | UNEs={lista_unes} | Segmento={filtro_segmento}")

    df = None
    
    # -------------------------------------------------------------------------
    # OTIMIZAÇÃO DUCKDB (Push-down Predicates)
    # Tenta filtrar via SQL antes de carregar para Pandas
    # -------------------------------------------------------------------------
    try:
        from app.core.parquet_cache import cache
        from app.core.context import get_current_user_segments # RLS
        
        # 1. Garantir que a tabela está carregada em memória (Zero-Copy)
        # Usar get_memory_table carrega o arquivo no DuckDB mas NÃO materializa o DataFrame
        table_name = cache._adapter.get_memory_table("admmat.parquet")
        
        # 2. Construir Query SQL
        sql_query = f"SELECT * FROM {table_name} WHERE 1=1"
        
        # --- RLS INJECTION (SEGURANÇA) ---
        allowed_segments = get_current_user_segments()
        if allowed_segments and "*" not in allowed_segments:
            safe_segments = [s.replace("'", "''") for s in allowed_segments]
            segments_sql = ",".join([f"'{s}'" for s in safe_segments])
            sql_query += f" AND NOMESEGMENTO IN ({segments_sql})"
            logger.info(f"[RLS] Aplicando filtro SQL: NOMESEGMENTO IN ({segments_sql})")
        # ---------------------------------
        
        if lista_unes:
            unes_str = ",".join(map(str, lista_unes))
            sql_query += f" AND UNE IN ({unes_str})"
            
        if filtro_segmento:
            # Escape simples para evitar injeção básica
            seg_clean = filtro_segmento.replace("'", "''")
            sql_query += f" AND NOMESEGMENTO ILIKE '%{seg_clean}%'"
            
        if filtro_categoria:
            cat_clean = filtro_categoria.replace("'", "''")
            sql_query += f" AND NOMECATEGORIA ILIKE '%{cat_clean}%'"
            
        if lista_produtos:
            prods_str = ",".join(map(str, lista_produtos))
            # Cast para garantir comparação correta com ints
            sql_query += f" AND CAST(PRODUTO AS BIGINT) IN ({prods_str})"
            
        logger.info(f"[DUCKDB OPTIMIZATION] Executando SQL: {sql_query}")
        
        # 3. Executar via Adapter
        result = cache._adapter.query(sql_query)
        
        if hasattr(result, 'df'):
            df = result.df()
        elif hasattr(result, 'to_pandas'):
            df = result.to_pandas()
        else:
            df = pd.DataFrame(result)
            
        logger.info(f"[DUCKDB OPTIMIZATION] Sucesso! {len(df)} registros recuperados via SQL.")
        
    except Exception as sql_err:
        logger.warning(f"[DUCKDB OPTIMIZATION] Falhou, usando fallback Pandas lento: {sql_err}")
        df = None

    # -------------------------------------------------------------------------
    # FALLBACK PANDAS (Lógica Original)
    # -------------------------------------------------------------------------
    if df is None:
        # 1. Obter dados (Full Scan lento)
        manager = get_data_manager()
        df = manager.get_data()
        
        # Conversão robusta para Pandas
        if hasattr(df, 'to_pandas'):
            df = df.to_pandas()
        elif hasattr(df, 'df'):
            df = df.df()
        elif not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception:
                pass 

        if df is None or df.empty:
            return {"status": "error", "message": "Dados não disponíveis"}

        # 2. Aplicar filtros (Lento em Pandas)
        df_filtered = df

        if lista_unes:
            if 'UNE' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['UNE'].isin(lista_unes)]
                logger.info(f"Filtrado UNEs {lista_unes}: {len(df_filtered)} registros")

        if filtro_segmento:
            if 'NOMESEGMENTO' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMESEGMENTO'].str.contains(filtro_segmento, case=False, na=False)]

        if filtro_categoria:
            if 'NOMECATEGORIA' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMECATEGORIA'].str.contains(filtro_categoria, case=False, na=False)]

        if lista_produtos:
            if 'PRODUTO' in df_filtered.columns:
                df_filtered['PRODUTO'] = pd.to_numeric(df_filtered['PRODUTO'], errors='coerce')
                df_filtered = df_filtered[df_filtered['PRODUTO'].isin(lista_produtos)]
    else:
        # Se veio do SQL, já está filtrado
        df_filtered = df

    if df_filtered.empty:
        return {
            "status": "error",
            "message": f"Nenhum dado encontrado para os filtros aplicados."
        }

    # 3. Detectar o que visualizar (ANTES DA QUERY para otimização SQL)
    descricao_lower = descricao.lower()
    
    # Lógica de Comparação: Se tem múltiplas UNEs e pede comparação
    is_comparison = len(lista_unes) > 1 and ("compar" in descricao_lower or "entre" in descricao_lower or "vs" in descricao_lower)
    # Detectar "por loja" / "todas as lojas"
    is_by_store = any(kw in descricao_lower for kw in ["por loja", "por une", "todas as lojas", "cada loja", "em todas", "todas lojas"])

    # Definição de Colunas de Agrupamento (Dimensão)
    if is_comparison or is_by_store:
        group_col = "UNE"
        titulo_dimensao = "Loja (UNE)"
    elif "segmento" in descricao_lower:
        group_col = "NOMESEGMENTO"
        titulo_dimensao = "Segmento"
    elif "categoria" in descricao_lower:
        group_col = "NOMECATEGORIA"
        titulo_dimensao = "Categoria"
    elif "grupo" in descricao_lower:
        group_col = "NOMEGRUPO"
        titulo_dimensao = "Grupo"
    elif "fabricante" in descricao_lower:
        group_col = "NOMEFABRICANTE"
        titulo_dimensao = "Fabricante"
    elif "produto" in descricao_lower and not lista_produtos:
        group_col = "NOME" # Nome do produto
        titulo_dimensao = "Produto"
    elif lista_produtos:
        # Se tem produtos específicos e não pediu outro agrupamento, agrupa por loja ou mostra detalhe
        # Default para por loja se não especificado
        group_col = "UNE"
        titulo_dimensao = "Loja (UNE)"
    else:
        # Default fallback
        group_col = "NOMESEGMENTO"
        titulo_dimensao = "Segmento"

    # Definição de Métricas
    if "estoque" in descricao_lower:
        metric_col = "ESTOQUE_UNE"
        titulo_metrica = "Estoque"
        agg_func = "SUM"
    elif "preco" in descricao_lower:
        metric_col = "PRECO_VENDA"
        titulo_metrica = "Preço Médio"
        agg_func = "AVG"
    elif "custo" in descricao_lower:
        metric_col = "PRECO_CUSTO" # Ajuste conforme nome real da coluna se necessário
        titulo_metrica = "Custo Médio"
        agg_func = "AVG"
    else:
        # Default vendas
        metric_col = "VENDA_30DD"
        titulo_metrica = "Vendas"
        agg_func = "SUM"

    df_agg = None

    # -------------------------------------------------------------------------
    # OTIMIZAÇÃO DUCKDB (Aggregation Push-down)
    # Executa o GROUP BY direto no motor SQL
    # -------------------------------------------------------------------------
    try:
        from app.core.parquet_cache import cache
        from app.core.context import get_current_user_segments # RLS
        
        table_name = cache._adapter.get_memory_table("admmat.parquet")
        
        # Monta a query de agregação
        # Ex: SELECT NOMESEGMENTO as dimensao, SUM(VENDA_30DD) as valor FROM ...
        
        select_clause = f"SELECT {group_col} as dimensao, {agg_func}(CAST({metric_col} AS DOUBLE)) as valor"
        where_clause = " FROM " + table_name + " WHERE 1=1"
        
        # --- RLS INJECTION (SEGURANÇA) ---
        allowed_segments = get_current_user_segments()
        if allowed_segments and "*" not in allowed_segments:
            safe_segments = [s.replace("'", "''") for s in allowed_segments]
            segments_sql = ",".join([f"'{s}'" for s in safe_segments])
            where_clause += f" AND NOMESEGMENTO IN ({segments_sql})"
        # ---------------------------------
        
        if lista_unes:
            unes_str = ",".join(map(str, lista_unes))
            where_clause += f" AND UNE IN ({unes_str})"
            
        if filtro_segmento:
            seg_clean = filtro_segmento.replace("'", "''")
            where_clause += f" AND NOMESEGMENTO ILIKE '%{seg_clean}%'"
            
        if filtro_categoria:
            cat_clean = filtro_categoria.replace("'", "''")
            where_clause += f" AND NOMECATEGORIA ILIKE '%{cat_clean}%'"
            
        if lista_produtos:
            prods_str = ",".join(map(str, lista_produtos))
            where_clause += f" AND CAST(PRODUTO AS BIGINT) IN ({prods_str})"
            
        # Group By e Order By
        group_by_clause = f" GROUP BY {group_col}"
        
        if group_col == "UNE":
             # Ordenar por número da loja se for comparação
             order_by_clause = " ORDER BY 1 ASC" 
        else:
             # Ordenar por valor descrescente (Ranking)
             order_by_clause = " ORDER BY 2 DESC"
             
        full_sql = select_clause + where_clause + group_by_clause + order_by_clause + f" LIMIT {limite}"
            
        logger.info(f"[DUCKDB AGGREGATION] Executando SQL: {full_sql}")
        
        # Executar
        result = cache._adapter.query(full_sql)
        
        if hasattr(result, 'df'):
            df_agg = result.df()
        elif hasattr(result, 'to_pandas'):
            df_agg = result.to_pandas()
        else:
            df_agg = pd.DataFrame(result, columns=["dimensao", "valor"])
            
        logger.info(f"[DUCKDB AGGREGATION] Sucesso! {len(df_agg)} linhas agregadas.")
        
    except Exception as sql_err:
        logger.warning(f"[DUCKDB AGGREGATION] Falhou: {sql_err}. Tentando fallback Pandas...")
        df_agg = None

    # -------------------------------------------------------------------------
    # FALLBACK PANDAS (Código legado para segurança)
    # -------------------------------------------------------------------------
    if df_agg is None:
        # 1. Obter dados (Full Scan lento)
        manager = get_data_manager()
        df = manager.get_data()
        
        # Conversão robusta para Pandas
        if hasattr(df, 'to_pandas'):
            df = df.to_pandas()
        elif hasattr(df, 'df'):
            df = df.df()
        elif not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception:
                pass 

        if df is None or df.empty:
            return {"status": "error", "message": "Dados não disponíveis"}

        # 2. Aplicar filtros
        df_filtered = df

        if lista_unes:
            if 'UNE' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['UNE'].isin(lista_unes)]

        if filtro_segmento:
            if 'NOMESEGMENTO' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMESEGMENTO'].str.contains(filtro_segmento, case=False, na=False)]

        if filtro_categoria:
            if 'NOMECATEGORIA' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMECATEGORIA'].str.contains(filtro_categoria, case=False, na=False)]

        if lista_produtos:
            if 'PRODUTO' in df_filtered.columns:
                df_filtered['PRODUTO'] = pd.to_numeric(df_filtered['PRODUTO'], errors='coerce')
                df_filtered = df_filtered[df_filtered['PRODUTO'].isin(lista_produtos)]

        # 3. Agregar em Pandas
        if group_col not in df_filtered.columns:
            return {"status": "error", "message": f"Coluna {group_col} não encontrada"}

        if metric_col:
            df_filtered = df_filtered.copy()
            df_filtered.loc[:, metric_col] = pd.to_numeric(df_filtered[metric_col], errors='coerce').fillna(0)
            
            if agg_func == "SUM":
                df_agg = df_filtered.groupby(group_col)[metric_col].sum().reset_index()
            elif agg_func == "AVG":
                df_agg = df_filtered.groupby(group_col)[metric_col].mean().reset_index()
            else:
                df_agg = df_filtered.groupby(group_col)[metric_col].count().reset_index()
        else:
            df_agg = df_filtered[group_col].value_counts().reset_index()
        
        df_agg.columns = ["dimensao", "valor"]
        
        if group_col == "UNE":
                df_agg["dimensao"] = pd.to_numeric(df_agg["dimensao"], errors='coerce')
                df_agg = df_agg.sort_values("dimensao")
        else:
                df_agg = df_agg.sort_values("valor", ascending=False).head(limite)

    # -------------------------------------------------------------------------
    # GERAÇÃO DO GRÁFICO (Comum para ambos os caminhos)
    # -------------------------------------------------------------------------
    
    if df_agg is None or df_agg.empty:
        return {"status": "error", "message": "Sem dados agregados"}

    # Garantir tipos
    df_agg["dimensao"] = df_agg["dimensao"].astype(str)
    
    # 5. Gerar gráfico
    if tipo_grafico == "auto":
        tipo_grafico = "bar" 

    fig = go.Figure()
    
    if tipo_grafico == "pie":
        fig.add_trace(go.Pie(labels=df_agg["dimensao"], values=df_agg["valor"], hole=0.3))
    else:
        fig.add_trace(go.Bar(
            x=df_agg["dimensao"], 
            y=df_agg["valor"],
            marker_color='#1f77b4',
            text=df_agg["valor"].apply(lambda x: f"{x:,.0f}"),
            textposition='auto'
        ))

    titulo = f"{titulo_metrica} por {titulo_dimensao}"
    if filtro_segmento: titulo += f" ({filtro_segmento})"

    fig.update_layout(
        title=titulo,
        template="plotly_white",
        height=600,  # Aumentado de 500 para 600
        margin=dict(l=60, r=40, t=80, b=120),  # Margens maiores para labels
        xaxis_title=titulo_dimensao,
        yaxis_title=titulo_metrica,
        xaxis_tickangle=-45  # Rotacionar labels do eixo X para melhor leitura
    )

    return {
        "status": "success",
        "chart_type": tipo_grafico,
        "chart_data": _export_chart_to_json(fig),
        "summary": {
            "dimensao": titulo_dimensao,
            "metrica": titulo_metrica,
            "total_itens": len(df_agg),
            "mensagem": f"Gráfico gerado via DuckDB Aggregation."
        }
    }
