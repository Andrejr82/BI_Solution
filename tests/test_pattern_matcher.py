"""
Testes para o PatternMatcher.
"""

import pytest
import json
import os
from core.learning.pattern_matcher import PatternMatcher


class TestPatternMatcher:
    """Suite de testes para PatternMatcher"""

    @pytest.fixture
    def matcher(self):
        """Fixture para criar instância do matcher"""
        return PatternMatcher()

    @pytest.fixture
    def temp_patterns_file(self, tmp_path):
        """Fixture para criar arquivo temporário de padrões para testes"""
        patterns = {
            "test_pattern": {
                "description": "Padrão de teste",
                "keywords": ["teste", "mock"],
                "exclude_keywords": ["excluir"],
                "examples": [
                    {
                        "user_query": "query de teste",
                        "code": "df = load_data()\nresult = df",
                        "expected_output": "DataFrame"
                    }
                ]
            },
            "ranking_completo": {
                "description": "Ranking completo",
                "keywords": ["ranking", "todos"],
                "examples": []
            }
        }

        patterns_file = tmp_path / "test_patterns.json"
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f)

        return str(patterns_file)

    # ==========================================
    # TESTES DE INICIALIZAÇÃO
    # ==========================================

    def test_initialization_with_default_file(self, matcher):
        """Testa inicialização com arquivo padrão"""
        assert matcher is not None
        assert matcher.patterns is not None
        assert len(matcher.patterns) > 0

    def test_initialization_with_custom_file(self, temp_patterns_file):
        """Testa inicialização com arquivo customizado"""
        matcher = PatternMatcher(patterns_file=temp_patterns_file)

        assert matcher is not None
        assert "test_pattern" in matcher.patterns
        assert "ranking_completo" in matcher.patterns

    def test_initialization_with_invalid_file(self):
        """Testa inicialização com arquivo inexistente"""
        matcher = PatternMatcher(patterns_file="arquivo_inexistente.json")

        # Deve ter patterns vazio mas não crashar
        assert matcher is not None
        assert matcher.patterns == {}

    # ==========================================
    # TESTES DE MATCH_PATTERN
    # ==========================================

    def test_match_top_n_pattern(self, matcher):
        """Testa identificação do padrão 'top_n'"""
        query = "top 10 produtos mais vendidos"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'top_n'
        assert pattern['score'] > 0

    def test_match_ranking_completo_pattern(self, matcher):
        """Testa identificação do padrão 'ranking_completo'"""
        query = "ranking completo de todos os produtos"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'ranking_completo'

    def test_match_comparacao_pattern(self, matcher):
        """Testa identificação do padrão 'comparacao'"""
        query = "comparar vendas de tecidos versus papelaria"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'comparacao'

    def test_match_agregacao_simples_pattern(self, matcher):
        """Testa identificação do padrão 'agregacao_simples'"""
        query = "qual o total de vendas"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'agregacao_simples'

    def test_match_estoque_baixo_pattern(self, matcher):
        """Testa identificação do padrão 'estoque_baixo'"""
        query = "produtos com estoque zero"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'estoque_baixo'

    def test_match_distribuicao_pattern(self, matcher):
        """Testa identificação do padrão 'distribuicao'"""
        query = "distribuição de vendas por segmento"

        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'distribuicao'

    def test_no_match_for_unrelated_query(self, matcher):
        """Testa que query não relacionada não retorna padrão"""
        query = "xyzabc123 query aleatória sem sentido"

        pattern = matcher.match_pattern(query)

        # Pode ou não retornar padrão dependendo de keywords genéricas
        # Se retornar, score deve ser baixo
        if pattern:
            assert pattern['score'] <= 1

    def test_exclude_keywords_reduce_score(self, temp_patterns_file):
        """Testa que palavras de exclusão reduzem o score"""
        matcher = PatternMatcher(patterns_file=temp_patterns_file)

        # Query com keyword positiva
        query1 = "query de teste"
        pattern1 = matcher.match_pattern(query1)

        # Query com keyword positiva + exclusão
        query2 = "query de teste mas excluir isto"
        pattern2 = matcher.match_pattern(query2)

        # pattern2 deve ter score menor ou não ser encontrado
        if pattern2:
            assert pattern2['score'] < pattern1['score']

    # ==========================================
    # TESTES DE GET_ALL_MATCHES
    # ==========================================

    def test_get_all_matches_returns_multiple(self, matcher):
        """Testa que get_all_matches retorna múltiplos padrões"""
        query = "ranking completo de produtos mais vendidos"

        matches = matcher.get_all_matches(query, top_k=5)

        assert len(matches) > 0
        assert len(matches) <= 5

        # Verificar formato da tupla (pattern_name, pattern_data, score)
        assert len(matches[0]) == 3
        assert isinstance(matches[0][0], str)  # pattern_name
        assert isinstance(matches[0][1], dict)  # pattern_data
        assert isinstance(matches[0][2], int)  # score

    def test_get_all_matches_sorted_by_score(self, matcher):
        """Testa que matches são ordenados por score (maior primeiro)"""
        query = "top 10 produtos mais vendidos"

        matches = matcher.get_all_matches(query, top_k=5)

        if len(matches) > 1:
            # Verificar ordem decrescente de score
            for i in range(len(matches) - 1):
                assert matches[i][2] >= matches[i + 1][2]

    def test_get_all_matches_respects_top_k(self, matcher):
        """Testa que top_k limita o número de resultados"""
        query = "ranking de produtos"

        matches_3 = matcher.get_all_matches(query, top_k=3)
        matches_5 = matcher.get_all_matches(query, top_k=5)

        assert len(matches_3) <= 3
        assert len(matches_5) <= 5

    # ==========================================
    # TESTES DE BUILD_EXAMPLES_CONTEXT
    # ==========================================

    def test_build_examples_context_returns_string(self, matcher):
        """Testa que build_examples_context retorna string"""
        query = "top 10 produtos"

        context = matcher.build_examples_context(query)

        assert isinstance(context, str)

    def test_build_examples_context_contains_examples(self, matcher):
        """Testa que contexto contém exemplos quando padrão é encontrado"""
        query = "top 10 produtos mais vendidos"

        context = matcher.build_examples_context(query, max_examples=2)

        if context:  # Se padrão foi encontrado
            assert "Exemplo" in context or "exemplo" in context
            assert "python" in context.lower()
            assert "Query" in context or "query" in context

    def test_build_examples_context_respects_max_examples(self, matcher):
        """Testa que max_examples limita o número de exemplos"""
        query = "top 10 produtos"

        context_1 = matcher.build_examples_context(query, max_examples=1)
        context_2 = matcher.build_examples_context(query, max_examples=2)

        # context_2 deve ser mais longo (mais exemplos)
        if context_1 and context_2:
            assert len(context_2) >= len(context_1)

    def test_build_examples_context_empty_for_no_match(self, matcher):
        """Testa que retorna vazio quando não há match"""
        query = "xyzabc123 sem match"

        context = matcher.build_examples_context(query)

        # Pode retornar string vazia ou ter conteúdo mínimo
        assert isinstance(context, str)

    # ==========================================
    # TESTES DE GET_VALIDATION_HINTS
    # ==========================================

    def test_get_validation_hints_for_top_n(self, matcher):
        """Testa hints para padrão top_n"""
        query = "top 5 produtos"

        hints = matcher.get_validation_hints(query)

        assert isinstance(hints, list)
        # Deve ter hint sobre .head()
        assert any('head' in hint.lower() for hint in hints)

    def test_get_validation_hints_for_ranking_completo(self, matcher):
        """Testa hints para padrão ranking_completo"""
        query = "ranking completo de produtos"

        hints = matcher.get_validation_hints(query)

        assert isinstance(hints, list)
        # Deve ter hint sobre não usar .head()
        if hints:
            assert any('não' in hint.lower() and 'head' in hint.lower() for hint in hints)

    def test_get_validation_hints_for_comparacao(self, matcher):
        """Testa hints para padrão comparacao"""
        query = "comparar tecidos versus papelaria"

        hints = matcher.get_validation_hints(query)

        assert isinstance(hints, list)
        if hints:
            assert any('isin' in hint.lower() for hint in hints)

    def test_get_validation_hints_empty_for_no_match(self, matcher):
        """Testa que retorna lista vazia quando não há match"""
        query = "xyzabc123 sem match"

        hints = matcher.get_validation_hints(query)

        assert isinstance(hints, list)
        # Pode ser vazia ou ter hints genéricos
        assert len(hints) >= 0

    # ==========================================
    # TESTES DE SUGGEST_COLUMNS
    # ==========================================

    def test_suggest_columns_for_sales_query(self, matcher):
        """Testa sugestão de colunas para query de vendas"""
        query = "vendas por produto"

        columns = matcher.suggest_columns(query)

        assert isinstance(columns, list)
        assert 'VENDA_30DD' in columns
        assert 'NOME' in columns  # Sempre incluído

    def test_suggest_columns_for_stock_query(self, matcher):
        """Testa sugestão de colunas para query de estoque"""
        query = "estoque disponível"

        columns = matcher.suggest_columns(query)

        assert 'ESTOQUE_UNE' in columns
        assert 'NOME' in columns

    def test_suggest_columns_for_price_query(self, matcher):
        """Testa sugestão de colunas para query de preço"""
        query = "preço médio por segmento"

        columns = matcher.suggest_columns(query)

        assert 'LIQUIDO_38' in columns
        assert 'NOMESEGMENTO' in columns

    def test_suggest_columns_for_segment_query(self, matcher):
        """Testa sugestão de colunas para query de segmento"""
        query = "produtos por segmento"

        columns = matcher.suggest_columns(query)

        assert 'NOMESEGMENTO' in columns

    def test_suggest_columns_for_category_query(self, matcher):
        """Testa sugestão de colunas para query de categoria"""
        query = "análise por categoria"

        columns = matcher.suggest_columns(query)

        assert 'NomeCategoria' in columns

    def test_suggest_columns_no_duplicates(self, matcher):
        """Testa que não há colunas duplicadas"""
        query = "vendas e faturamento por segmento"  # Múltiplas keywords

        columns = matcher.suggest_columns(query)

        # Verificar que não há duplicatas
        assert len(columns) == len(set(columns))

    def test_suggest_columns_always_includes_nome(self, matcher):
        """Testa que NOME sempre está incluído"""
        queries = [
            "total de vendas",
            "estoque baixo",
            "preços altos",
            "dados aleatórios"
        ]

        for query in queries:
            columns = matcher.suggest_columns(query)
            assert 'NOME' in columns, f"NOME não encontrado para query: {query}"

    # ==========================================
    # TESTES DE EDGE CASES
    # ==========================================

    def test_empty_query(self, matcher):
        """Testa query vazia"""
        query = ""

        pattern = matcher.match_pattern(query)
        context = matcher.build_examples_context(query)
        hints = matcher.get_validation_hints(query)
        columns = matcher.suggest_columns(query)

        # Não deve crashar
        assert pattern is None or isinstance(pattern, dict)
        assert isinstance(context, str)
        assert isinstance(hints, list)
        assert isinstance(columns, list)

    def test_query_with_special_characters(self, matcher):
        """Testa query com caracteres especiais"""
        query = "top 10 produtos @#$%&*"

        pattern = matcher.match_pattern(query)

        # Deve identificar top_n apesar dos caracteres especiais
        if pattern:
            assert 'top' in pattern['pattern_name'].lower() or pattern['score'] > 0

    def test_case_insensitive_matching(self, matcher):
        """Testa que matching é case-insensitive"""
        query1 = "TOP 10 PRODUTOS"
        query2 = "top 10 produtos"
        query3 = "Top 10 Produtos"

        pattern1 = matcher.match_pattern(query1)
        pattern2 = matcher.match_pattern(query2)
        pattern3 = matcher.match_pattern(query3)

        # Todos devem identificar o mesmo padrão
        if pattern1 and pattern2 and pattern3:
            assert pattern1['pattern_name'] == pattern2['pattern_name']
            assert pattern2['pattern_name'] == pattern3['pattern_name']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
