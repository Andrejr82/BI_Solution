"""
Generic Query Executor - Executa queries estruturadas sem usar LLM.
Recebe JSON estruturado do IntentClassifier e executa operações pandas.

ZERO RISCO: Este arquivo é NOVO e não afeta o sistema atual.
Usa ZERO tokens LLM - apenas operações pandas.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.utils.logger_config import get_logger
from core.visualization.advanced_charts import AdvancedChartGenerator

logger = get_logger('agent_bi.generic_executor')


class GenericQueryExecutor:
    """
    Executor genérico de queries estruturadas.

    Recebe JSON do IntentClassifier e executa operações pandas correspondentes.
    NÃO usa LLM - apenas manipulação de dados com pandas.
    """

    def __init__(self):
        """Inicializa o executor."""
        self.chart_generator = AdvancedChartGenerator()
        self.operations_executed = 0
        self.total_records_processed = 0

        logger.info("[OK] GenericQueryExecutor inicializado")

    def execute(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma query estruturada.

        Args:
            df: DataFrame com os dados
            intent: Dicionário com intenção classificada pelo IntentClassifier

        Returns:
            Dict com resultado da query:
            {
                "type": "chart" | "table" | "text",
                "title": str,
                "result": dict,
                "summary": str,
                "tokens_used": 0
            }
        """
        try:
            operation = intent.get('operation', 'unknown')
            logger.info(f"[INFO] Executando operação: {operation}")

            # Incrementar contador
            self.operations_executed += 1

            # Aplicar filtros primeiro
            df_filtered = self._apply_filters(df, intent.get('filters', {}))

            if df_filtered.empty:
                return {
                    "type": "text",
                    "title": "Nenhum Resultado Encontrado",
                    "result": {"message": "Nenhum dado corresponde aos filtros aplicados"},
                    "summary": "Nenhum resultado encontrado com os filtros especificados",
                    "tokens_used": 0
                }

            # Rotear para método específico
            if operation == 'ranking_produtos':
                return self._execute_ranking_produtos(df_filtered, intent)

            elif operation == 'ranking_unes':
                return self._execute_ranking_unes(df_filtered, intent)

            elif operation == 'ranking_segmentos':
                return self._execute_ranking_segmentos(df_filtered, intent)

            elif operation == 'ranking_categorias':
                return self._execute_ranking_categorias(df_filtered, intent)

            elif operation == 'distribuicao_categoria':
                return self._execute_distribuicao_categoria(df_filtered, intent)

            elif operation == 'consulta_une':
                return self._execute_consulta_une(df_filtered, intent)

            elif operation == 'analise_estoque':
                return self._execute_analise_estoque(df_filtered, intent)

            elif operation == 'evolucao_temporal':
                return self._execute_evolucao_temporal(df_filtered, intent)

            elif operation == 'comparacao':
                return self._execute_comparacao(df_filtered, intent)

            elif operation == 'agregacao':
                return self._execute_agregacao(df_filtered, intent)

            elif operation == 'filtro_complexo':
                return self._execute_filtro_complexo(df_filtered, intent)

            else:
                logger.warning(f"[AVISO] Operação desconhecida: {operation}")
                return {
                    "type": "error",
                    "title": "Operação Não Suportada",
                    "error": f"Operação '{operation}' não implementada",
                    "suggestion": "Use o sistema de fallback",
                    "tokens_used": 0
                }

        except Exception as e:
            logger.error(f"[ERRO] Erro ao executar query: {e}")
            import traceback
            traceback.print_exc()
            return {
                "type": "error",
                "error": str(e),
                "suggestion": "Use o sistema de fallback",
                "tokens_used": 0
            }

    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Aplica filtros ao DataFrame.

        Args:
            df: DataFrame original
            filters: Dicionário de filtros

        Returns:
            DataFrame filtrado
        """
        df_result = df.copy()

        for key, value in filters.items():
            try:
                if key == 'une_nome' and value:
                    # Normalizar para uppercase
                    value_upper = str(value).upper()
                    df_result = df_result[df_result['une_nome'].str.upper() == value_upper]
                    logger.info(f"  Filtro: une_nome = {value_upper} -> {len(df_result)} registros")

                elif key == 'segmento' and value:
                    value_upper = str(value).upper()
                    df_result = df_result[df_result['nomesegmento'].str.upper().str.contains(value_upper, na=False)]
                    logger.info(f"  Filtro: segmento = {value_upper} -> {len(df_result)} registros")

                elif key == 'categoria' and value:
                    value_upper = str(value).upper()
                    if 'NOMECATEGORIA' in df_result.columns:
                        df_result = df_result[df_result['NOMECATEGORIA'].str.upper().str.contains(value_upper, na=False)]
                        logger.info(f"  Filtro: categoria = {value_upper} -> {len(df_result)} registros")

                elif key == 'codigo' and value:
                    df_result = df_result[df_result['codigo'] == int(value)]
                    logger.info(f"  Filtro: codigo = {value} -> {len(df_result)} registros")

                elif key == 'estoque_maior_que' and value is not None:
                    if 'estoque_atual' in df_result.columns:
                        df_result = df_result[df_result['estoque_atual'] > int(value)]
                        logger.info(f"  Filtro: estoque > {value} -> {len(df_result)} registros")

                elif key == 'estoque_menor_que' and value is not None:
                    if 'estoque_atual' in df_result.columns:
                        df_result = df_result[df_result['estoque_atual'] < int(value)]
                        logger.info(f"  Filtro: estoque < {value} -> {len(df_result)} registros")

                elif key == 'estoque_igual_a' and value is not None:
                    if 'estoque_atual' in df_result.columns:
                        df_result = df_result[df_result['estoque_atual'] == int(value)]
                        logger.info(f"  Filtro: estoque = {value} -> {len(df_result)} registros")

                elif key == 'preco_maior_que' and value is not None:
                    if 'preco_38_percent' in df_result.columns:
                        df_result = df_result[df_result['preco_38_percent'] > float(value)]
                        logger.info(f"  Filtro: preco > {value} -> {len(df_result)} registros")

                elif key == 'preco_menor_que' and value is not None:
                    if 'preco_38_percent' in df_result.columns:
                        df_result = df_result[df_result['preco_38_percent'] < float(value)]
                        logger.info(f"  Filtro: preco < {value} -> {len(df_result)} registros")

            except Exception as e:
                logger.warning(f"[AVISO] Erro ao aplicar filtro {key}={value}: {e}")
                continue

        return df_result

    def _execute_ranking_produtos(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ranking de produtos."""
        limit = intent.get('limit', 10)
        sort_by = intent.get('sort_by', 'vendas_total')

        if sort_by not in df.columns:
            sort_by = 'vendas_total'

        # Agrupar por produto
        produtos = df.groupby('codigo').agg({
            'vendas_total': 'sum',
            'nome_produto': 'first',
            'nomesegmento': 'first',
            'preco_38_percent': 'first'
        }).reset_index()

        # Top N
        top_produtos = produtos.nlargest(limit, 'vendas_total')

        # Preparar dados para gráfico
        chart_data = {
            "x": [p['nome_produto'][:40] for _, p in top_produtos.iterrows()],
            "y": [float(p['vendas_total']) for _, p in top_produtos.iterrows()],
            "type": "bar",
            "show_values": True
        }

        produtos_list = [{
            "codigo": int(p['codigo']),
            "nome": p['nome_produto'],
            "vendas": float(p['vendas_total']),
            "segmento": p['nomesegmento']
        } for _, p in top_produtos.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limit} Produtos Mais Vendidos",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "total_produtos": len(produtos_list)
            },
            "summary": f"Top {len(produtos_list)} produtos. Líder: {produtos_list[0]['nome']} ({produtos_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _execute_ranking_unes(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ranking de UNEs."""
        limit = intent.get('limit', 10)

        # Agrupar por UNE
        unes = df.groupby('une_nome').agg({
            'vendas_total': 'sum',
            'une': 'first'
        }).reset_index()

        # Top N
        top_unes = unes.nlargest(limit, 'vendas_total')

        chart_data = {
            "x": [une['une_nome'] for _, une in top_unes.iterrows()],
            "y": [float(une['vendas_total']) for _, une in top_unes.iterrows()],
            "type": "bar",
            "show_values": True
        }

        unes_list = [{
            "une_nome": une['une_nome'],
            "vendas": float(une['vendas_total'])
        } for _, une in top_unes.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limit} UNEs por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "unes": unes_list,
                "total_unes": len(unes_list)
            },
            "summary": f"Top {len(unes_list)} UNEs. Líder: {unes_list[0]['une_nome']} ({unes_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _execute_ranking_segmentos(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ranking de segmentos."""
        limit = intent.get('limit', 10)

        # Agrupar por segmento
        segmentos = df.groupby('nomesegmento').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'
        }).reset_index()

        segmentos.columns = ['segmento', 'vendas_total', 'produtos_unicos']

        # Top N
        top_segmentos = segmentos.nlargest(limit, 'vendas_total')

        chart_data = {
            "x": [s['segmento'] for _, s in top_segmentos.iterrows()],
            "y": [float(s['vendas_total']) for _, s in top_segmentos.iterrows()],
            "type": "bar",
            "show_values": True
        }

        segmentos_list = [{
            "segmento": s['segmento'],
            "vendas": float(s['vendas_total']),
            "produtos": int(s['produtos_unicos'])
        } for _, s in top_segmentos.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limit} Segmentos por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "segmentos": segmentos_list,
                "total_segmentos": len(segmentos_list)
            },
            "summary": f"Top {len(segmentos_list)} segmentos. Líder: {segmentos_list[0]['segmento']} ({segmentos_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _execute_ranking_categorias(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ranking de categorias."""
        if 'NOMECATEGORIA' not in df.columns:
            return {
                "type": "error",
                "error": "Coluna NOMECATEGORIA não disponível",
                "tokens_used": 0
            }

        limit = intent.get('limit', 10)

        # Agrupar por categoria
        categorias = df.groupby('NOMECATEGORIA').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'
        }).reset_index()

        categorias.columns = ['categoria', 'vendas_total', 'produtos_unicos']

        # Top N
        top_categorias = categorias.nlargest(limit, 'vendas_total')

        chart_data = {
            "x": [c['categoria'] for _, c in top_categorias.iterrows()],
            "y": [float(c['vendas_total']) for _, c in top_categorias.iterrows()],
            "type": "bar",
            "show_values": True
        }

        categorias_list = [{
            "categoria": c['categoria'],
            "vendas": float(c['vendas_total']),
            "produtos": int(c['produtos_unicos'])
        } for _, c in top_categorias.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limit} Categorias por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "categorias": categorias_list,
                "total_categorias": len(categorias_list)
            },
            "summary": f"Top {len(categorias_list)} categorias. Líder: {categorias_list[0]['categoria']} ({categorias_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _execute_distribuicao_categoria(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa distribuição por categoria."""
        if 'NOMECATEGORIA' not in df.columns:
            return {
                "type": "error",
                "error": "Coluna NOMECATEGORIA não disponível",
                "tokens_used": 0
            }

        # Agrupar por categoria
        categorias = df.groupby('NOMECATEGORIA').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'
        }).reset_index()

        categorias.columns = ['categoria', 'vendas_total', 'produtos_unicos']
        categorias = categorias.sort_values('vendas_total', ascending=False)

        # Calcular percentuais
        total_vendas = categorias['vendas_total'].sum()
        categorias['percentual'] = (categorias['vendas_total'] / total_vendas * 100).round(2)

        chart_data = {
            "labels": categorias['categoria'].tolist(),
            "data": categorias['vendas_total'].tolist(),
            "type": "pie",
            "show_percentages": True
        }

        categorias_list = [{
            "categoria": row['categoria'],
            "vendas": float(row['vendas_total']),
            "produtos": int(row['produtos_unicos']),
            "percentual": float(row['percentual'])
        } for _, row in categorias.iterrows()]

        return {
            "type": "chart",
            "title": "Distribuição de Vendas por Categoria",
            "result": {
                "chart_data": chart_data,
                "categorias": categorias_list,
                "total_categorias": len(categorias_list),
                "total_vendas": float(total_vendas)
            },
            "summary": f"{len(categorias_list)} categorias. Líder: {categorias_list[0]['categoria']} ({categorias_list[0]['percentual']:.1f}% das vendas)",
            "tokens_used": 0
        }

    def _execute_consulta_une(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa consulta de informações de uma UNE."""
        # Assumir que já foi filtrado por UNE nos filtros
        total_vendas = df['vendas_total'].sum()
        total_produtos = df['codigo'].nunique()

        une_nome = df['une_nome'].iloc[0] if len(df) > 0 else "N/A"

        return {
            "type": "text",
            "title": f"Informações da UNE {une_nome}",
            "result": {
                "une_nome": une_nome,
                "total_vendas": float(total_vendas),
                "total_produtos": int(total_produtos),
                "registros": len(df)
            },
            "summary": f"UNE {une_nome}: {total_vendas:,.0f} vendas, {total_produtos} produtos únicos",
            "tokens_used": 0
        }

    def _execute_analise_estoque(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise de estoque."""
        if 'estoque_atual' not in df.columns:
            return {
                "type": "error",
                "error": "Coluna estoque_atual não disponível",
                "tokens_used": 0
            }

        produtos_list = [{
            "codigo": int(row['codigo']),
            "nome": row['nome_produto'],
            "estoque": int(row['estoque_atual']),
            "vendas": float(row['vendas_total'])
        } for _, row in df.head(100).iterrows()]

        return {
            "type": "table",
            "title": "Análise de Estoque",
            "result": {
                "produtos": produtos_list,
                "total_produtos": len(produtos_list)
            },
            "summary": f"{len(produtos_list)} produtos encontrados",
            "tokens_used": 0
        }

    def _execute_evolucao_temporal(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise de evolução temporal."""
        # Colunas mensais
        meses_cols = [c for c in df.columns if c.startswith('mes_')]

        if not meses_cols:
            return {
                "type": "error",
                "error": "Colunas mensais não disponíveis",
                "tokens_used": 0
            }

        # Somar vendas por mês
        evolucao = df[meses_cols].sum()

        chart_data = {
            "x": meses_cols,
            "y": evolucao.tolist(),
            "type": "line",
            "show_values": True
        }

        return {
            "type": "chart",
            "title": "Evolução de Vendas Mês a Mês",
            "result": {
                "chart_data": chart_data,
                "total_vendas": float(evolucao.sum())
            },
            "summary": f"Evolução de {len(meses_cols)} meses. Total: {evolucao.sum():,.0f} vendas",
            "tokens_used": 0
        }

    def _execute_comparacao(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa comparação entre entidades."""
        # Implementação básica - pode ser expandida
        return self._execute_ranking_segmentos(df, intent)

    def _execute_agregacao(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa agregação simples."""
        aggregations = intent.get('aggregations', {})

        result = {}
        if 'sum' in aggregations:
            col = aggregations['sum']
            if col in df.columns:
                result['sum'] = float(df[col].sum())

        if 'avg' in aggregations:
            col = aggregations['avg']
            if col in df.columns:
                result['avg'] = float(df[col].mean())

        if 'count' in aggregations:
            result['count'] = len(df)

        return {
            "type": "text",
            "title": "Resultado da Agregação",
            "result": result,
            "summary": f"Agregação calculada com {len(result)} métricas",
            "tokens_used": 0
        }

    def _execute_filtro_complexo(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Executa query com filtros complexos."""
        # DataFrame já está filtrado, retornar contagem
        return {
            "type": "text",
            "title": "Resultado do Filtro",
            "result": {
                "total_registros": len(df),
                "total_produtos": int(df['codigo'].nunique()) if 'codigo' in df.columns else 0
            },
            "summary": f"{len(df)} registros encontrados com os filtros aplicados",
            "tokens_used": 0
        }

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        return {
            "operations_executed": self.operations_executed,
            "total_records_processed": self.total_records_processed
        }
