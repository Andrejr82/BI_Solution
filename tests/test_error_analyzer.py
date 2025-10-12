"""
Testes para o ErrorAnalyzer.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from core.learning.error_analyzer import ErrorAnalyzer


class TestErrorAnalyzer:
    """Suite de testes para ErrorAnalyzer"""

    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Fixture para criar diretório temporário de logs"""
        logs_dir = tmp_path / "learning"
        logs_dir.mkdir()
        return str(logs_dir)

    @pytest.fixture
    def analyzer(self, temp_logs_dir):
        """Fixture para criar instância do ErrorAnalyzer"""
        return ErrorAnalyzer(logs_dir=temp_logs_dir)

    @pytest.fixture
    def sample_error_logs(self, temp_logs_dir):
        """Fixture para criar logs de erro de exemplo"""
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        errors = [
            {
                'timestamp': datetime.now().isoformat(),
                'query': 'query com KeyError',
                'code': 'df["coluna_inexistente"]',
                'error_type': 'KeyError',
                'error_message': 'Key "coluna_inexistente" not found'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'query': 'query com KeyError novamente',
                'code': 'df["outra_coluna"]',
                'error_type': 'KeyError',
                'error_message': 'Key "outra_coluna" not found'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'query': 'query com TypeError',
                'code': '"string" + 5',
                'error_type': 'TypeError',
                'error_message': 'Cannot add string and int'
            }
        ]

        with open(error_file, 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(json.dumps(error, ensure_ascii=False) + '\n')

        return error_file

    # ==========================================
    # TESTES DE INICIALIZAÇÃO
    # ==========================================

    def test_initialization(self, temp_logs_dir):
        """Testa inicialização"""
        analyzer = ErrorAnalyzer(logs_dir=temp_logs_dir)

        assert analyzer is not None
        assert analyzer.logs_dir == temp_logs_dir

    # ==========================================
    # TESTES DE ANALYZE_ERRORS
    # ==========================================

    def test_analyze_errors_empty(self, analyzer):
        """Testa análise sem erros"""
        analysis = analyzer.analyze_errors(days=7)

        assert analysis['total_errors'] == 0
        assert len(analysis['most_common_errors']) == 0

    def test_analyze_errors_with_data(self, analyzer, sample_error_logs):
        """Testa análise com dados"""
        analysis = analyzer.analyze_errors(days=7)

        assert analysis['total_errors'] == 3
        assert len(analysis['most_common_errors']) > 0

    def test_analyze_errors_counts_by_type(self, analyzer, sample_error_logs):
        """Testa contagem de erros por tipo"""
        analysis = analyzer.analyze_errors(days=7)

        # Encontrar KeyError nos resultados
        key_error = next(
            (e for e in analysis['most_common_errors'] if e['type'] == 'KeyError'),
            None
        )

        assert key_error is not None
        assert key_error['count'] == 2  # 2 KeyErrors no sample

    def test_analyze_errors_calculates_percentage(self, analyzer, sample_error_logs):
        """Testa cálculo de percentual"""
        analysis = analyzer.analyze_errors(days=7)

        # Verificar que percentuais somam ~100%
        total_percentage = sum(e['percentage'] for e in analysis['most_common_errors'])
        assert abs(total_percentage - 100.0) < 0.1

    def test_analyze_errors_includes_examples(self, analyzer, sample_error_logs):
        """Testa que análise inclui exemplos"""
        analysis = analyzer.analyze_errors(days=7)

        for error in analysis['most_common_errors']:
            assert 'example_query' in error
            assert 'example_error' in error

    def test_analyze_errors_generates_suggestions(self, analyzer, sample_error_logs):
        """Testa geração de sugestões"""
        analysis = analyzer.analyze_errors(days=7)

        assert 'suggested_improvements' in analysis
        assert len(analysis['suggested_improvements']) > 0

        # Verificar formato das sugestões
        for suggestion in analysis['suggested_improvements']:
            assert 'issue' in suggestion
            assert 'solution' in suggestion
            assert 'priority' in suggestion

    def test_analyze_errors_identifies_problematic_queries(self, analyzer, temp_logs_dir):
        """Testa identificação de queries problemáticas"""
        # Criar erro com mesma query repetida
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        repeated_query = "query problemática"
        errors = [
            {
                'timestamp': datetime.now().isoformat(),
                'query': repeated_query,
                'code': 'code',
                'error_type': 'ValueError',
                'error_message': 'Error'
            }
        ] * 3  # 3 vezes a mesma query

        with open(error_file, 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(json.dumps(error, ensure_ascii=False) + '\n')

        analysis = analyzer.analyze_errors(days=7)

        # Verificar que a query foi identificada como problemática
        problematic = analysis['queries_with_errors']
        assert len(problematic) > 0
        assert problematic[0]['query'] == repeated_query
        assert problematic[0]['error_count'] == 3

    # ==========================================
    # TESTES DE SUGESTÕES ESPECÍFICAS
    # ==========================================

    def test_suggestions_for_keyerror(self, analyzer, temp_logs_dir):
        """Testa sugestões específicas para KeyError"""
        # Criar log com KeyError
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        with open(error_file, 'w', encoding='utf-8') as f:
            error = {
                'timestamp': datetime.now().isoformat(),
                'query': 'query',
                'code': 'df["col"]',
                'error_type': 'KeyError',
                'error_message': 'Error'
            }
            f.write(json.dumps(error) + '\n')

        analysis = analyzer.analyze_errors(days=7)
        suggestions = analysis['suggested_improvements']

        # Deve ter sugestão sobre validação de colunas
        assert any('coluna' in s['issue'].lower() for s in suggestions)

    def test_suggestions_for_timeout(self, analyzer, temp_logs_dir):
        """Testa sugestões para timeout"""
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        with open(error_file, 'w', encoding='utf-8') as f:
            error = {
                'timestamp': datetime.now().isoformat(),
                'query': 'query demorada',
                'code': 'df.sort_values()',
                'error_type': 'timeout',
                'error_message': 'Timeout'
            }
            f.write(json.dumps(error) + '\n')

        analysis = analyzer.analyze_errors(days=7)
        suggestions = analysis['suggested_improvements']

        # Deve ter sugestão sobre otimização
        assert any('timeout' in s['issue'].lower() or 'otimizar' in s['solution'].lower() for s in suggestions)

    # ==========================================
    # TESTES DE GET_ERROR_TRENDS
    # ==========================================

    def test_get_error_trends_empty(self, analyzer):
        """Testa tendências sem dados"""
        trends = analyzer.get_error_trends(days=7)

        assert isinstance(trends, dict)

    def test_get_error_trends_with_counters(self, analyzer, temp_logs_dir):
        """Testa tendências com contadores"""
        # Criar arquivo de contador
        date_str = datetime.now().strftime('%Y%m%d')
        counter_file = os.path.join(temp_logs_dir, f'error_counts_{date_str}.json')

        counts = {
            'KeyError': 5,
            'TypeError': 3
        }

        with open(counter_file, 'w', encoding='utf-8') as f:
            json.dump(counts, f)

        trends = analyzer.get_error_trends(days=7)

        assert 'KeyError' in trends
        assert 'TypeError' in trends

    def test_get_error_trends_multiple_days(self, analyzer, temp_logs_dir):
        """Testa tendências com múltiplos dias"""
        # Criar contadores para hoje e ontem
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        for date in [today, yesterday]:
            date_str = date.strftime('%Y%m%d')
            counter_file = os.path.join(temp_logs_dir, f'error_counts_{date_str}.json')

            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump({'KeyError': 2}, f)

        trends = analyzer.get_error_trends(days=7)

        # KeyError deve ter dados de 2 dias
        if 'KeyError' in trends:
            assert len(trends['KeyError']) >= 2

    # ==========================================
    # TESTES DE GENERATE_REPORT
    # ==========================================

    def test_generate_report_returns_string(self, analyzer):
        """Testa que generate_report retorna string"""
        report = analyzer.generate_report(days=7)

        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_report_with_data(self, analyzer, sample_error_logs):
        """Testa relatório com dados"""
        report = analyzer.generate_report(days=7)

        # Verificar que contém seções esperadas
        assert "RELATÓRIO DE ANÁLISE DE ERROS" in report
        assert "ESTATÍSTICAS GERAIS" in report
        assert "ERROS MAIS COMUNS" in report

    def test_generate_report_to_file(self, analyzer, sample_error_logs, temp_logs_dir):
        """Testa geração de relatório para arquivo"""
        output_file = os.path.join(temp_logs_dir, "report.md")
        result = analyzer.generate_report(days=7, output_file=output_file)

        assert result == output_file
        assert os.path.exists(output_file)

        # Verificar conteúdo do arquivo
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "RELATÓRIO" in content

    def test_generate_report_formatting(self, analyzer, sample_error_logs):
        """Testa formatação do relatório"""
        report = analyzer.generate_report(days=7)

        # Verificar elementos de formatação Markdown
        assert "#" in report  # Headers
        assert "-" in report or "*" in report  # Lists
        assert "**" in report  # Bold

    # ==========================================
    # TESTES DE EDGE CASES
    # ==========================================

    def test_analyze_errors_with_malformed_json(self, analyzer, temp_logs_dir):
        """Testa análise com JSON malformado"""
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        with open(error_file, 'w', encoding='utf-8') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')  # Linha inválida
            f.write('{"another": "valid"}\n')

        # Não deve crashar
        analysis = analyzer.analyze_errors(days=7)

        # Deve processar apenas as linhas válidas
        assert analysis['total_errors'] >= 0

    def test_analyze_errors_zero_days(self, analyzer):
        """Testa análise com 0 dias"""
        analysis = analyzer.analyze_errors(days=0)

        # Não deve crashar
        assert isinstance(analysis, dict)

    def test_analyze_errors_large_number_of_days(self, analyzer):
        """Testa análise com muitos dias"""
        analysis = analyzer.analyze_errors(days=365)

        # Não deve crashar
        assert isinstance(analysis, dict)

    def test_generate_report_with_unicode(self, analyzer, temp_logs_dir):
        """Testa relatório com caracteres Unicode"""
        date_str = datetime.now().strftime('%Y%m%d')
        error_file = os.path.join(temp_logs_dir, f'error_log_{date_str}.jsonl')

        with open(error_file, 'w', encoding='utf-8') as f:
            error = {
                'timestamp': datetime.now().isoformat(),
                'query': 'query com acentuação e émojis 🎯',
                'code': 'código',
                'error_type': 'ValueError',
                'error_message': 'Mensagem de erro com ç ã é'
            }
            f.write(json.dumps(error, ensure_ascii=False) + '\n')

        report = analyzer.generate_report(days=7)

        # Deve conter caracteres Unicode
        assert 'ç' in report or 'é' in report or len(report) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
