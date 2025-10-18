"""
Testes para Pilar 4: Análise de Logs e Métricas
Autor: Claude Code
Data: 2025-10-18
"""

import pytest
import os
from pathlib import Path

# Imports dos componentes do Pilar 4
from core.learning.error_analyzer import ErrorAnalyzer
from core.learning.dynamic_prompt import DynamicPrompt
from core.monitoring.metrics_dashboard import MetricsDashboard


class TestErrorAnalyzer:
    """Testes para ErrorAnalyzer"""

    def test_error_analyzer_init(self):
        """Testa inicialização do ErrorAnalyzer"""
        analyzer = ErrorAnalyzer()
        assert analyzer is not None
        # Verificar se tem os métodos principais
        assert hasattr(analyzer, 'analyze_errors')

    def test_analyze_errors_structure(self):
        """Testa estrutura do retorno de analyze_errors"""
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze_errors(days=7)

        assert isinstance(result, dict)
        assert "most_common_errors" in result
        assert "suggested_improvements" in result
        assert isinstance(result["most_common_errors"], list)
        assert isinstance(result["suggested_improvements"], list)

    def test_analyzer_has_methods(self):
        """Testa se analyzer tem métodos essenciais"""
        analyzer = ErrorAnalyzer()

        assert hasattr(analyzer, 'analyze_errors')
        assert callable(analyzer.analyze_errors)


class TestDynamicPrompt:
    """Testes para DynamicPrompt"""

    def test_dynamic_prompt_init(self):
        """Testa inicialização do DynamicPrompt"""
        dp = DynamicPrompt()
        assert dp is not None
        assert hasattr(dp, 'base_prompt')
        assert hasattr(dp, 'error_analyzer')

    def test_get_enhanced_prompt(self):
        """Testa get_enhanced_prompt retorna string"""
        dp = DynamicPrompt()
        prompt = dp.get_enhanced_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_update_prompt(self):
        """Testa update_prompt retorna bool"""
        dp = DynamicPrompt()
        result = dp.update_prompt()

        assert isinstance(result, bool)


class TestMetricsDashboard:
    """Testes para MetricsDashboard"""

    def test_metrics_dashboard_init(self):
        """Testa inicialização do MetricsDashboard"""
        dashboard = MetricsDashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'learning_dir')

    def test_get_metrics_structure(self):
        """Testa estrutura do retorno de get_metrics"""
        dashboard = MetricsDashboard()
        metrics = dashboard.get_metrics(days=7)

        assert isinstance(metrics, dict)
        assert "success_rate" in metrics
        assert "avg_response_time" in metrics
        assert "cache_hit_rate" in metrics
        assert "total_queries" in metrics
        assert "top_queries" in metrics
        assert "error_trend" in metrics

    def test_get_success_rate(self):
        """Testa get_success_rate retorna float válido"""
        dashboard = MetricsDashboard()
        rate = dashboard.get_success_rate()

        assert isinstance(rate, float)
        assert 0.0 <= rate <= 1.0

    def test_get_top_queries(self):
        """Testa get_top_queries retorna lista"""
        dashboard = MetricsDashboard()
        top = dashboard.get_top_queries(limit=10)

        assert isinstance(top, list)
        # Pode estar vazia se não houver dados
        if len(top) > 0:
            assert isinstance(top[0], dict)


class TestIntegration:
    """Testes de integração entre componentes"""

    def test_dynamic_prompt_uses_error_analyzer(self):
        """Testa se DynamicPrompt usa ErrorAnalyzer"""
        dp = DynamicPrompt()
        assert dp.error_analyzer is not None
        assert isinstance(dp.error_analyzer, ErrorAnalyzer)

    def test_all_components_work_together(self):
        """Testa se todos os componentes funcionam juntos"""
        # ErrorAnalyzer
        analyzer = ErrorAnalyzer()
        errors = analyzer.analyze_errors(days=7)
        assert errors is not None

        # DynamicPrompt
        dp = DynamicPrompt()
        prompt = dp.get_enhanced_prompt()
        assert prompt is not None

        # MetricsDashboard
        dashboard = MetricsDashboard()
        metrics = dashboard.get_metrics(days=7)
        assert metrics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
