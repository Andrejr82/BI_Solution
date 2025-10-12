"""
Testes de integração para validar que todos os componentes da Fase 1 funcionam juntos.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock
from core.validation.code_validator import CodeValidator
from core.learning.pattern_matcher import PatternMatcher
from core.learning.feedback_system import FeedbackSystem
from core.learning.error_analyzer import ErrorAnalyzer


class TestFase1Integration:
    """Testes de integração da Fase 1"""

    @pytest.fixture
    def temp_dirs(self, tmp_path):
        """Fixture para criar diretórios temporários"""
        return {
            'learning': str(tmp_path / 'learning'),
            'feedback': str(tmp_path / 'feedback')
        }

    # ==========================================
    # TESTE DE INTEGRAÇÃO COMPLETO
    # ==========================================

    def test_full_workflow_positive_feedback(self, temp_dirs):
        """
        Testa fluxo completo com feedback positivo:
        1. PatternMatcher identifica padrão
        2. CodeValidator valida código
        3. FeedbackSystem registra feedback positivo
        """
        # 1. Identificar padrão
        matcher = PatternMatcher()
        query = "top 10 produtos mais vendidos"
        pattern = matcher.match_pattern(query)

        assert pattern is not None
        assert pattern['pattern_name'] == 'top_n'

        # 2. Validar código
        validator = CodeValidator()
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()
result = ranking
"""
        validation = validator.validate(code, query)

        assert validation['valid'] == True

        # 3. Registrar feedback positivo
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])
        success = feedback.record_feedback(
            query=query,
            code=code,
            feedback_type='positive',
            result_rows=10
        )

        assert success == True

        # 4. Verificar estatísticas
        stats = feedback.get_feedback_stats(days=7)
        assert stats['total'] == 1
        assert stats['positive'] == 1
        assert stats['success_rate'] == 100.0

    def test_full_workflow_with_code_fix(self, temp_dirs):
        """
        Testa fluxo com código que precisa de correção:
        1. PatternMatcher identifica padrão top_n
        2. CodeValidator detecta falta de .head()
        3. Auto-fix corrige o código
        4. FeedbackSystem registra sucesso
        """
        # 1. Identificar padrão
        matcher = PatternMatcher()
        query = "top 5 produtos de tecidos"
        pattern = matcher.match_pattern(query)

        assert pattern['pattern_name'] == 'top_n'

        # 2. Código sem .head()
        validator = CodeValidator()
        code = """
df = load_data()
ranking = df[df['NOMESEGMENTO'] == 'TECIDOS'].groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
result = ranking
"""

        validation = validator.validate(code, query)

        # Deve ter warnings sobre falta de .head()
        assert any('top' in w.lower() or 'head' in w.lower() for w in validation['warnings'])

        # 3. Auto-fix
        if not validation['valid'] or validation['warnings']:
            fix_result = validator.auto_fix(validation, query)
            if fix_result['fixed'] or fix_result['fixes_applied']:
                code = fix_result['code']

        # 4. Registrar feedback
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])
        feedback.record_feedback(
            query=query,
            code=code,
            feedback_type='positive',
            result_rows=5
        )

        stats = feedback.get_feedback_stats(days=7)
        assert stats['positive'] >= 1

    def test_full_workflow_with_error(self, temp_dirs):
        """
        Testa fluxo com erro:
        1. Código inválido é detectado pelo validator
        2. Erro é registrado
        3. ErrorAnalyzer identifica o problema
        4. Feedback negativo é registrado
        """
        # 1. Código inválido
        validator = CodeValidator()
        query = "ranking de produtos"
        code = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum(
result = ranking
"""  # Erro de sintaxe proposital

        validation = validator.validate(code, query)

        assert validation['valid'] == False
        assert any('sintaxe' in e.lower() for e in validation['errors'])

        # 2. Simular registro de erro
        os.makedirs(temp_dirs['learning'], exist_ok=True)
        import json
        from datetime import datetime

        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_dirs['learning'], f'error_log_{date_str}.jsonl')

        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'code': code,
            'error_type': 'SyntaxError',
            'error_message': 'invalid syntax'
        }

        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(error_entry) + '\n')

        # 3. Analisar erro
        analyzer = ErrorAnalyzer(logs_dir=temp_dirs['learning'])
        analysis = analyzer.analyze_errors(days=7)

        assert analysis['total_errors'] == 1
        assert any(e['type'] == 'SyntaxError' for e in analysis['most_common_errors'])

        # 4. Registrar feedback negativo
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])
        feedback.record_feedback(
            query=query,
            code=code,
            feedback_type='negative',
            user_comment='Erro de sintaxe no código gerado'
        )

        stats = feedback.get_feedback_stats(days=7)
        assert stats['negative'] >= 1

    def test_pattern_matcher_provides_context_for_validator(self):
        """
        Testa que PatternMatcher fornece contexto útil para CodeValidator
        """
        matcher = PatternMatcher()
        validator = CodeValidator()

        query = "top 10 produtos"

        # 1. Identificar padrão e obter hints
        pattern = matcher.match_pattern(query)
        hints = matcher.get_validation_hints(query)

        assert pattern is not None
        assert len(hints) > 0
        assert any('head' in h.lower() for h in hints)

        # 2. Validar código que deveria ter .head()
        code_without_head = """
df = load_data()
ranking = df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()
result = ranking
"""

        validation = validator.validate(code_without_head, query)

        # Validator deve detectar o mesmo problema que os hints indicam
        assert any('head' in w.lower() or 'top' in w.lower() for w in validation['warnings'])

    def test_feedback_system_exports_for_future_training(self, temp_dirs):
        """
        Testa que FeedbackSystem exporta dados para treinamento futuro (Fase 2 - RAG)
        """
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])

        # Registrar vários feedbacks positivos
        positive_examples = [
            ("top 10 produtos", "df.head(10)"),
            ("ranking de vendas", "df.groupby('NOME')['VENDA_30DD'].sum()"),
            ("produtos de tecidos", "df[df['NOMESEGMENTO'] == 'TECIDOS']")
        ]

        for query, code in positive_examples:
            feedback.record_feedback(query, code, 'positive', result_rows=10)

        # Exportar para treinamento
        export_file = os.path.join(temp_dirs['feedback'], 'training_data.json')
        success = feedback.export_feedback_for_training(export_file)

        assert success == True
        assert os.path.exists(export_file)

        # Verificar conteúdo
        import json
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 3
            assert all('query' in item and 'code' in item for item in data)

    def test_error_analyzer_generates_actionable_insights(self, temp_dirs):
        """
        Testa que ErrorAnalyzer gera insights acionáveis
        """
        os.makedirs(temp_dirs['learning'], exist_ok=True)

        # Criar múltiplos erros do mesmo tipo
        import json
        from datetime import datetime

        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_dirs['learning'], f'error_log_{date_str}.jsonl')

        errors = [
            {'timestamp': datetime.now().isoformat(), 'query': f'query_{i}',
             'code': 'df["col"]', 'error_type': 'KeyError',
             'error_message': 'Column not found'}
            for i in range(5)
        ]

        with open(error_file, 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(json.dumps(error) + '\n')

        # Analisar
        analyzer = ErrorAnalyzer(logs_dir=temp_dirs['learning'])
        analysis = analyzer.analyze_errors(days=7)

        # Verificar que gerou sugestões
        assert len(analysis['suggested_improvements']) > 0

        # KeyError deve ter sugestão específica
        key_error_suggestion = next(
            (s for s in analysis['suggested_improvements']
             if 'coluna' in s['issue'].lower() or 'keyerror' in s['issue'].lower()),
            None
        )

        assert key_error_suggestion is not None
        assert key_error_suggestion['priority'] in ['HIGH', 'MEDIUM', 'LOW']

    def test_all_components_work_with_unicode(self, temp_dirs):
        """
        Testa que todos os componentes funcionam com Unicode/caracteres especiais
        """
        query = "top 10 produtos de tecidos - análise completa 🎯"

        # PatternMatcher
        matcher = PatternMatcher()
        pattern = matcher.match_pattern(query)
        assert pattern is not None

        # CodeValidator
        validator = CodeValidator()
        code = """
df = load_data()
# Comentário com acentuação
ranking = df[df['NOMESEGMENTO'] == 'TECIDOS'].groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()
result = ranking
"""
        validation = validator.validate(code, query)
        assert isinstance(validation, dict)

        # FeedbackSystem
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])
        success = feedback.record_feedback(
            query=query,
            code=code,
            feedback_type='positive',
            user_comment='Ótima resposta com ç, é, ã!'
        )
        assert success == True

    def test_components_handle_edge_cases_gracefully(self, temp_dirs):
        """
        Testa que componentes lidam gracefully com casos extremos
        """
        # Query vazia
        empty_query = ""

        # PatternMatcher com query vazia
        matcher = PatternMatcher()
        pattern = matcher.match_pattern(empty_query)
        # Não deve crashar

        # CodeValidator com código vazio
        validator = CodeValidator()
        validation = validator.validate("", empty_query)
        assert validation['valid'] == False  # Mas não crashou

        # FeedbackSystem com dados vazios
        os.makedirs(temp_dirs['feedback'], exist_ok=True)
        feedback = FeedbackSystem(feedback_dir=temp_dirs['feedback'])
        success = feedback.record_feedback("", "", "positive")
        assert success == True  # Registrou mesmo com dados vazios

        # ErrorAnalyzer sem erros
        os.makedirs(temp_dirs['learning'], exist_ok=True)
        analyzer = ErrorAnalyzer(logs_dir=temp_dirs['learning'])
        analysis = analyzer.analyze_errors(days=7)
        assert analysis['total_errors'] == 0  # Mas não crashou

    def test_performance_with_many_patterns_and_validations(self):
        """
        Testa performance com múltiplas operações
        """
        import time

        matcher = PatternMatcher()
        validator = CodeValidator()

        queries = [
            "top 10 produtos",
            "ranking completo",
            "compare vendas",
            "total de estoque",
            "distribuição por segmento"
        ] * 20  # 100 queries

        start = time.time()

        for query in queries:
            # Pattern matching
            pattern = matcher.match_pattern(query)

            # Code validation
            code = "df = load_data()\nresult = df"
            validation = validator.validate(code, query)

        elapsed = time.time() - start

        # Deve processar 100 queries em menos de 5 segundos
        assert elapsed < 5.0, f"Processamento muito lento: {elapsed:.2f}s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
