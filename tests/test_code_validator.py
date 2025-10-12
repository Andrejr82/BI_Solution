"""
Testes para o CodeValidator.
"""

import pytest
from core.validation.code_validator import CodeValidator


class TestCodeValidator:
    """Suite de testes para CodeValidator"""

    @pytest.fixture
    def validator(self):
        """Fixture para criar instância do validador"""
        return CodeValidator()

    # ==========================================
    # TESTES DE VALIDAÇÃO BÁSICA
    # ==========================================

    def test_valid_code_with_all_requirements(self, validator):
        """Testa código válido com todos os requisitos"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()
result = ranking
"""
        query = "top 10 produtos mais vendidos"

        result = validator.validate(code, query)

        assert result['valid'] == True
        assert len(result['errors']) == 0

    def test_missing_load_data(self, validator):
        """Testa código sem load_data()"""
        code = """
ranking = df.groupby('NOME')['VENDA_30DD'].sum()
result = ranking
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('load_data' in error for error in result['errors'])

    def test_missing_result_assignment(self, validator):
        """Testa código sem atribuição a result"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum()
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('result' in error for error in result['errors'])

    def test_syntax_error_detection(self, validator):
        """Testa detecção de erro de sintaxe"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum(
result = ranking
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('sintaxe' in error.lower() for error in result['errors'])

    # ==========================================
    # TESTES DE RANKING E TOP N
    # ==========================================

    def test_ranking_query_without_groupby(self, validator):
        """Testa query de ranking sem groupby"""
        code = """
df = load_data()
result = df.sort_values('VENDA_30DD', ascending=False)
"""
        query = "ranking de produtos mais vendidos"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('groupby' in error for error in result['errors'])

    def test_top_n_without_head(self, validator):
        """Testa query 'top N' sem .head()"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
result = ranking
"""
        query = "top 10 produtos"

        result = validator.validate(code, query)

        # Deve ter warning sobre falta de .head()
        assert len(result['warnings']) > 0
        assert any('top' in warning.lower() for warning in result['warnings'])

    def test_top_n_with_correct_head(self, validator):
        """Testa query 'top N' com .head() correto"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()
result = ranking
"""
        query = "top 10 produtos"

        result = validator.validate(code, query)

        # Não deve ter warning sobre .head()
        warnings_about_head = [w for w in result['warnings'] if 'top' in w.lower() or 'head' in w.lower()]
        assert len(warnings_about_head) == 0

    # ==========================================
    # TESTES DE SEGMENTOS
    # ==========================================

    def test_segment_mapping_warning(self, validator):
        """Testa warning quando query menciona segmento mas código pode não usar valor correto"""
        code = """
df = load_data()
result = df[df['NOMESEGMENTO'] == 'tecido']
"""
        query = "produtos de tecido"

        result = validator.validate(code, query)

        # Deve ter warning sobre mapeamento de segmento
        assert len(result['warnings']) > 0
        assert any('TECIDOS' in warning for warning in result['warnings'])

    def test_correct_segment_value(self, validator):
        """Testa código com valor correto de segmento"""
        code = """
df = load_data()
result = df[df['NOMESEGMENTO'] == 'TECIDOS']
"""
        query = "produtos de tecido"

        result = validator.validate(code, query)

        # Não deve ter warning sobre segmento
        segment_warnings = [w for w in result['warnings'] if 'TECIDOS' in w and 'tecido' in w.lower()]
        assert len(segment_warnings) == 0

    # ==========================================
    # TESTES DE MÉTRICAS
    # ==========================================

    def test_sales_metric_validation(self, validator):
        """Testa warning quando query sobre vendas não usa VENDA_30DD"""
        code = """
df = load_data()
result = df.groupby('NOME')['venda'].sum()
"""
        query = "total de vendas por produto"

        result = validator.validate(code, query)

        # Deve ter warning sobre métrica de vendas
        assert any('VENDA_30DD' in warning for warning in result['warnings'])

    def test_stock_metric_validation(self, validator):
        """Testa warning quando query sobre estoque não usa ESTOQUE_UNE"""
        code = """
df = load_data()
result = df.groupby('NOME')['estoque'].sum()
"""
        query = "estoque por produto"

        result = validator.validate(code, query)

        # Deve ter warning sobre métrica de estoque
        assert any('ESTOQUE_UNE' in warning for warning in result['warnings'])

    # ==========================================
    # TESTES DE SEGURANÇA
    # ==========================================

    def test_blocked_operation_import_os(self, validator):
        """Testa bloqueio de import os"""
        code = """
import os
df = load_data()
result = df
"""
        query = "dados"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('import os' in error for error in result['errors'])

    def test_blocked_operation_eval(self, validator):
        """Testa bloqueio de eval()"""
        code = """
df = load_data()
result = eval('df.head()')
"""
        query = "dados"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert any('eval' in error for error in result['errors'])

    # ==========================================
    # TESTES DE AUTO-FIX
    # ==========================================

    def test_auto_fix_missing_load_data(self, validator):
        """Testa correção automática de load_data() faltando"""
        code = """
ranking = df.groupby('NOME')['VENDA_30DD'].sum()
result = ranking
"""
        query = "ranking de vendas"

        validation_result = validator.validate(code, query)
        fix_result = validator.auto_fix(validation_result, query)

        assert fix_result['fixed'] or len(fix_result['fixes_applied']) > 0
        assert 'load_data' in fix_result['code']

    def test_auto_fix_missing_result(self, validator):
        """Testa correção automática de result faltando"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
"""
        query = "ranking de vendas"

        validation_result = validator.validate(code, query)
        fix_result = validator.auto_fix(validation_result, query)

        assert len(fix_result['fixes_applied']) > 0
        assert 'result' in fix_result['code']

    def test_auto_fix_top_n(self, validator):
        """Testa correção automática de .head() para top N"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
result = ranking
"""
        query = "top 5 produtos"

        validation_result = validator.validate(code, query)
        fix_result = validator.auto_fix(validation_result, query)

        # Deve adicionar .head(5)
        if not validation_result['valid']:
            assert '.head(5)' in fix_result['code'] or len(fix_result['fixes_applied']) > 0

    def test_auto_fix_does_not_break_valid_code(self, validator):
        """Testa que auto_fix não quebra código já válido"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()
result = ranking
"""
        query = "top 10 produtos"

        validation_result = validator.validate(code, query)
        fix_result = validator.auto_fix(validation_result, query)

        # Código já é válido, não deve aplicar fixes
        assert fix_result['fixed'] == False
        assert len(fix_result['fixes_applied']) == 0

    # ==========================================
    # TESTES DE AGREGAÇÃO
    # ==========================================

    def test_aggregation_without_reset_index(self, validator):
        """Testa warning quando agregação não tem reset_index()"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False)
result = ranking
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        # Deve ter warning sobre reset_index
        assert any('reset_index' in warning for warning in result['warnings'])

    def test_aggregation_with_reset_index(self, validator):
        """Testa que agregação com reset_index() não gera warning"""
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
result = ranking
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        # Não deve ter warning sobre reset_index
        warnings_about_reset = [w for w in result['warnings'] if 'reset_index' in w]
        assert len(warnings_about_reset) == 0

    # ==========================================
    # TESTES DE EDGE CASES
    # ==========================================

    def test_empty_code(self, validator):
        """Testa código vazio"""
        code = ""
        query = "dados"

        result = validator.validate(code, query)

        assert result['valid'] == False
        assert len(result['errors']) > 0

    def test_code_with_comments_only(self, validator):
        """Testa código com apenas comentários"""
        code = """
# Este é um comentário
# Outro comentário
"""
        query = "dados"

        result = validator.validate(code, query)

        assert result['valid'] == False

    def test_multiple_result_assignments(self, validator):
        """Testa código com múltiplas atribuições a result (deve aceitar)"""
        code = """
df = load_data()
result = df.groupby('NOME')['VENDA_30DD'].sum()
result = result.sort_values(ascending=False).reset_index()
"""
        query = "ranking de vendas"

        result = validator.validate(code, query)

        # Deve aceitar, pois tem pelo menos uma atribuição a result
        result_errors = [e for e in result['errors'] if 'result' in e.lower()]
        assert len(result_errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
