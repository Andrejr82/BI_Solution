"""
Ferramenta Universal de Geração de Gráficos - Context7 2025
Solução definitiva para gráficos com filtros dinâmicos e performance otimizada.
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import polars as pl
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
    filtro_une: Optional[int] = None,
    filtro_segmento: Optional[str] = None,
    filtro_categoria: Optional[str] = None,
    filtro_produto: Optional[int] = None,
    tipo_grafico: str = "auto",
    limite: int = 10
) -> Dict[str, Any]:
    """
    Gera qualquer tipo de gráfico com filtros dinâmicos.

    Esta é a ferramenta UNIVERSAL para geração de gráficos.
    Substitui todas as ferramentas específicas anteriores.

    Args:
        descricao: Descrição do que deve ser visualizado (ex: "vendas por segmento")
        filtro_une: Código da loja/UNE para filtrar (ex: 1685)
        filtro_segmento: Nome do segmento para filtrar (ex: "ARMARINHO")
        filtro_categoria: Nome da categoria para filtrar
        filtro_produto: Código do produto (SKU) para análise individual (ex: 369946)
        tipo_grafico: Tipo de gráfico ("bar", "pie", "line", "auto")
        limite: Número máximo de itens no gráfico

    Returns:
        Gráfico Plotly JSON com dados filtrados

    Exemplos:
        - gerar_grafico_universal_v2(descricao="vendas por segmento", filtro_une=1685)
        - gerar_grafico_universal_v2(descricao="top produtos", filtro_segmento="ARMARINHO", limite=20)
        - gerar_grafico_universal_v2(descricao="estoque por categoria", tipo_grafico="bar")
        - gerar_grafico_universal_v2(descricao="vendas mensais", filtro_produto=369946)
    """
    logger.info(f"[UNIVERSAL CHART] Gerando: {descricao} | UNE={filtro_une} | Segmento={filtro_segmento} | Produto={filtro_produto}")

    try:
        # 1. Obter dados
        manager = get_data_manager()
        df = manager.get_data()

        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Dados não disponíveis"
            }

        # 2. Aplicar filtros (sem cópia completa para economizar memória)
        df_filtered = df

        if filtro_une is not None:
            if 'UNE' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['UNE'] == filtro_une]
                logger.info(f"Filtrado UNE {filtro_une}: {len(df_filtered)} registros")

        if filtro_segmento:
            if 'NOMESEGMENTO' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMESEGMENTO'].str.contains(filtro_segmento, case=False, na=False)]
                logger.info(f"Filtrado Segmento {filtro_segmento}: {len(df_filtered)} registros")

        if filtro_categoria:
            if 'NOMECATEGORIA' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['NOMECATEGORIA'].str.contains(filtro_categoria, case=False, na=False)]
                logger.info(f"Filtrado Categoria {filtro_categoria}: {len(df_filtered)} registros")

        if filtro_produto is not None:
            if 'PRODUTO' in df_filtered.columns:
                # Converter para numérico e filtrar
                df_filtered['PRODUTO'] = pd.to_numeric(df_filtered['PRODUTO'], errors='coerce')
                df_filtered = df_filtered[df_filtered['PRODUTO'] == filtro_produto]
                logger.info(f"Filtrado Produto {filtro_produto}: {len(df_filtered)} registros")

        if df_filtered.empty:
            return {
                "status": "error",
                "message": f"Nenhum dado encontrado com os filtros aplicados (UNE={filtro_une}, Segmento={filtro_segmento})"
            }

        # 3. Detectar o que visualizar baseado na descrição
        descricao_lower = descricao.lower()

        # Detectar dimensão (por que agrupar)
        if "segmento" in descricao_lower:
            group_col = "NOMESEGMENTO"
            titulo_dimensao = "Segmento"
        elif "categoria" in descricao_lower:
            group_col = "NOMECATEGORIA"
            titulo_dimensao = "Categoria"
        elif "fabricante" in descricao_lower or "marca" in descricao_lower:
            group_col = "NOMEFABRICANTE"
            titulo_dimensao = "Fabricante"
        elif "produto" in descricao_lower:
            group_col = "NOME"
            titulo_dimensao = "Produto"
        else:
            # Padrão: segmento
            group_col = "NOMESEGMENTO"
            titulo_dimensao = "Segmento"

        # Detectar métrica (o que medir)
        if "venda" in descricao_lower or "vendido" in descricao_lower:
            metric_col = "VENDA_30DD"
            titulo_metrica = "Vendas (30 dias)"
            agg_func = "sum"
        elif "estoque" in descricao_lower:
            metric_col = "ESTOQUE_UNE"
            titulo_metrica = "Estoque Atual"
            agg_func = "sum"
        elif "preco" in descricao_lower or "preço" in descricao_lower:
            metric_col = "PRECO_VENDA"
            titulo_metrica = "Preço Médio"
            agg_func = "mean"
        else:
            # Padrão: contar produtos
            metric_col = None
            titulo_metrica = "Quantidade de Produtos"
            agg_func = "count"

        # 4. Agregar dados
        if group_col not in df_filtered.columns:
            return {
                "status": "error",
                "message": f"Coluna {group_col} não encontrada nos dados"
            }

        if metric_col and metric_col not in df_filtered.columns:
            return {
                "status": "error",
                "message": f"Coluna {metric_col} não encontrada nos dados"
            }

        if metric_col:
            # Converter para numérico - FIX: Usar .loc para evitar SettingWithCopyWarning
            df_filtered = df_filtered.copy()  # Criar cópia explícita para evitar warnings
            df_filtered.loc[:, metric_col] = pd.to_numeric(df_filtered[metric_col], errors='coerce').fillna(0)

            if agg_func == "sum":
                df_agg = df_filtered.groupby(group_col)[metric_col].sum().reset_index()
            elif agg_func == "mean":
                df_agg = df_filtered.groupby(group_col)[metric_col].mean().reset_index()
            else:
                df_agg = df_filtered.groupby(group_col)[metric_col].count().reset_index()

            df_agg.columns = ["dimensao", "valor"]
        else:
            # Apenas contar
            df_agg = df_filtered[group_col].value_counts().reset_index()
            df_agg.columns = ["dimensao", "valor"]

        # Ordenar e limitar
        df_agg = df_agg.sort_values("valor", ascending=False).head(limite)

        if df_agg.empty:
            return {
                "status": "error",
                "message": "Nenhum dado agregado após processamento"
            }

        # 5. Gerar gráfico
        if tipo_grafico == "auto":
            # Se poucas categorias, usar pizza; senão barras
            tipo_grafico = "pie" if len(df_agg) <= 5 else "bar"

        if tipo_grafico == "pie":
            fig = go.Figure(data=[
                go.Pie(
                    labels=df_agg["dimensao"],
                    values=df_agg["valor"],
                    hole=0.3,
                    hovertemplate="<b>%{label}</b><br>%{value:.0f}<br>%{percent}<extra></extra>"
                )
            ])
            titulo = f"{titulo_metrica} por {titulo_dimensao}"
        else:
            # Bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=df_agg["dimensao"],
                    y=df_agg["valor"],
                    marker=dict(color='#1f77b4'),
                    hovertemplate="<b>%{x}</b><br>%{y:.0f}<extra></extra>"
                )
            ])
            titulo = f"Top {len(df_agg)} - {titulo_metrica} por {titulo_dimensao}"

        # Adicionar título e customizações
        filtros_aplicados = []
        if filtro_une:
            filtros_aplicados.append(f"UNE {filtro_une}")
        if filtro_segmento:
            filtros_aplicados.append(f"Segmento: {filtro_segmento}")
        if filtro_categoria:
            filtros_aplicados.append(f"Categoria: {filtro_categoria}")

        if filtros_aplicados:
            titulo += f" ({', '.join(filtros_aplicados)})"

        fig.update_layout(
            title={
                "text": titulo,
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16}
            },
            template="plotly_white",
            hovermode="closest",
            height=500,
            margin=dict(l=50, r=50, t=80, b=100)
        )

        if tipo_grafico == "bar":
            fig.update_xaxes(title_text=titulo_dimensao, tickangle=-45)
            fig.update_yaxes(title_text=titulo_metrica)

        # 6. Retornar resultado
        return {
            "status": "success",
            "chart_type": tipo_grafico,
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "dimensao": titulo_dimensao,
                "metrica": titulo_metrica,
                "total_itens": len(df_agg),
                "filtros": {
                    "une": filtro_une,
                    "segmento": filtro_segmento,
                    "categoria": filtro_categoria
                },
                "total_registros_analisados": len(df_filtered),
                "mensagem": f"Gráfico gerado com {len(df_agg)} itens de {len(df_filtered)} registros filtrados"
            }
        }

    except Exception as e:
        logger.error(f"Erro ao gerar gráfico universal: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


# REMOVED 2025-12-27: Removido alias para evitar confusão
# Use gerar_grafico_universal_v2 diretamente
# OLD CODE: gerar_grafico_universal = gerar_grafico_universal_v2
