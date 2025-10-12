"""
Testes para o FeedbackSystem.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from core.learning.feedback_system import FeedbackSystem


class TestFeedbackSystem:
    """Suite de testes para FeedbackSystem"""

    @pytest.fixture
    def temp_feedback_dir(self, tmp_path):
        """Fixture para criar diretório temporário de feedback"""
        feedback_dir = tmp_path / "feedback"
        feedback_dir.mkdir()
        return str(feedback_dir)

    @pytest.fixture
    def feedback_system(self, temp_feedback_dir):
        """Fixture para criar instância do FeedbackSystem"""
        return FeedbackSystem(feedback_dir=temp_feedback_dir)

    # ==========================================
    # TESTES DE INICIALIZAÇÃO
    # ==========================================

    def test_initialization_creates_directory(self, temp_feedback_dir):
        """Testa que inicialização cria diretório"""
        new_dir = os.path.join(temp_feedback_dir, "subdir")
        feedback = FeedbackSystem(feedback_dir=new_dir)

        assert os.path.exists(new_dir)

    def test_initialization_with_existing_directory(self, temp_feedback_dir):
        """Testa inicialização com diretório existente"""
        feedback = FeedbackSystem(feedback_dir=temp_feedback_dir)

        assert feedback is not None
        assert feedback.feedback_dir == temp_feedback_dir

    # ==========================================
    # TESTES DE RECORD_FEEDBACK
    # ==========================================

    def test_record_positive_feedback(self, feedback_system, temp_feedback_dir):
        """Testa registro de feedback positivo"""
        result = feedback_system.record_feedback(
            query="top 10 produtos",
            code="df.head(10)",
            feedback_type="positive",
            result_rows=10
        )

        assert result == True

        # Verificar que arquivo foi criado
        date_str = datetime.now().strftime('%Y%m%d')
        feedback_file = os.path.join(temp_feedback_dir, f'feedback_{date_str}.jsonl')
        assert os.path.exists(feedback_file)

    def test_record_negative_feedback_with_comment(self, feedback_system, temp_feedback_dir):
        """Testa registro de feedback negativo com comentário"""
        result = feedback_system.record_feedback(
            query="ranking de vendas",
            code="df.sort_values()",
            feedback_type="negative",
            user_comment="Retornou produtos errados",
            result_rows=0
        )

        assert result == True

        # Ler arquivo e verificar conteúdo
        date_str = datetime.now().strftime('%Y%m%d')
        feedback_file = os.path.join(temp_feedback_dir, f'feedback_{date_str}.jsonl')

        with open(feedback_file, 'r', encoding='utf-8') as f:
            line = f.readline()
            entry = json.loads(line)

            assert entry['feedback_type'] == 'negative'
            assert entry['user_comment'] == 'Retornou produtos errados'
            assert entry['query'] == 'ranking de vendas'

    def test_record_partial_feedback(self, feedback_system):
        """Testa registro de feedback parcial"""
        result = feedback_system.record_feedback(
            query="dados de estoque",
            code="df[['ESTOQUE_UNE']]",
            feedback_type="partial",
            result_rows=50
        )

        assert result == True

    def test_record_feedback_with_session_info(self, feedback_system, temp_feedback_dir):
        """Testa registro com informações de sessão"""
        result = feedback_system.record_feedback(
            query="test query",
            code="test code",
            feedback_type="positive",
            session_id="session_123",
            user_id="user_456"
        )

        assert result == True

        # Verificar que session_id e user_id foram salvos
        date_str = datetime.now().strftime('%Y%m%d')
        feedback_file = os.path.join(temp_feedback_dir, f'feedback_{date_str}.jsonl')

        with open(feedback_file, 'r', encoding='utf-8') as f:
            entry = json.loads(f.readline())
            assert entry['session_id'] == 'session_123'
            assert entry['user_id'] == 'user_456'

    def test_multiple_feedbacks_in_same_file(self, feedback_system, temp_feedback_dir):
        """Testa múltiplos feedbacks no mesmo arquivo"""
        feedback_system.record_feedback("query1", "code1", "positive")
        feedback_system.record_feedback("query2", "code2", "negative")
        feedback_system.record_feedback("query3", "code3", "partial")

        # Ler arquivo e contar linhas
        date_str = datetime.now().strftime('%Y%m%d')
        feedback_file = os.path.join(temp_feedback_dir, f'feedback_{date_str}.jsonl')

        with open(feedback_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 3

    # ==========================================
    # TESTES DE GET_FEEDBACK_STATS
    # ==========================================

    def test_get_feedback_stats_empty(self, feedback_system):
        """Testa estatísticas com nenhum feedback"""
        stats = feedback_system.get_feedback_stats(days=7)

        assert stats['total'] == 0
        assert stats['positive'] == 0
        assert stats['negative'] == 0
        assert stats['partial'] == 0

    def test_get_feedback_stats_with_data(self, feedback_system):
        """Testa estatísticas com dados"""
        # Adicionar feedbacks
        feedback_system.record_feedback("q1", "c1", "positive", result_rows=10)
        feedback_system.record_feedback("q2", "c2", "positive", result_rows=20)
        feedback_system.record_feedback("q3", "c3", "negative", user_comment="Erro")
        feedback_system.record_feedback("q4", "c4", "partial", result_rows=5)

        stats = feedback_system.get_feedback_stats(days=7)

        assert stats['total'] == 4
        assert stats['positive'] == 2
        assert stats['negative'] == 1
        assert stats['partial'] == 1

    def test_get_feedback_stats_success_rate_calculation(self, feedback_system):
        """Testa cálculo de taxa de sucesso"""
        # 2 positivos, 1 negativo, 1 parcial
        # Taxa = (2 + 1*0.5) / 4 = 2.5 / 4 = 62.5%
        feedback_system.record_feedback("q1", "c1", "positive")
        feedback_system.record_feedback("q2", "c2", "positive")
        feedback_system.record_feedback("q3", "c3", "negative")
        feedback_system.record_feedback("q4", "c4", "partial")

        stats = feedback_system.get_feedback_stats(days=7)

        expected_rate = (2 + 1 * 0.5) / 4 * 100
        assert abs(stats['success_rate'] - expected_rate) < 0.1

    def test_get_feedback_stats_common_issues(self, feedback_system):
        """Testa coleta de problemas comuns"""
        feedback_system.record_feedback("q1", "c1", "negative", user_comment="Problema 1")
        feedback_system.record_feedback("q2", "c2", "negative", user_comment="Problema 2")
        feedback_system.record_feedback("q3", "c3", "positive")

        stats = feedback_system.get_feedback_stats(days=7)

        assert len(stats['common_issues']) == 2
        assert "Problema 1" in stats['common_issues']
        assert "Problema 2" in stats['common_issues']

    # ==========================================
    # TESTES DE GET_PROBLEMATIC_QUERIES
    # ==========================================

    def test_get_problematic_queries_empty(self, feedback_system):
        """Testa queries problemáticas sem dados"""
        problematic = feedback_system.get_problematic_queries()

        assert isinstance(problematic, list)
        assert len(problematic) == 0

    def test_get_problematic_queries_with_data(self, feedback_system):
        """Testa identificação de queries problemáticas"""
        # Query problemática repetida
        feedback_system.record_feedback("query problematica", "code", "negative")
        feedback_system.record_feedback("query problematica", "code", "negative")
        feedback_system.record_feedback("query problematica", "code", "negative")

        # Query com apenas 1 problema
        feedback_system.record_feedback("outra query", "code", "negative")

        # Query sem problemas
        feedback_system.record_feedback("query boa", "code", "positive")

        problematic = feedback_system.get_problematic_queries(limit=10)

        assert len(problematic) > 0
        # A query mais problemática deve ser a primeira
        assert problematic[0]['query'] == "query problematica"
        assert problematic[0]['negative_count'] == 3

    def test_get_problematic_queries_respects_limit(self, feedback_system):
        """Testa que limit funciona"""
        # Criar 5 queries problemáticas diferentes
        for i in range(5):
            feedback_system.record_feedback(f"query_{i}", "code", "negative")

        problematic = feedback_system.get_problematic_queries(limit=3)

        assert len(problematic) <= 3

    # ==========================================
    # TESTES DE EXPORT_FEEDBACK_FOR_TRAINING
    # ==========================================

    def test_export_feedback_for_training(self, feedback_system, temp_feedback_dir):
        """Testa exportação de feedback positivo"""
        # Adicionar feedback misto
        feedback_system.record_feedback("query1", "code1", "positive", result_rows=10)
        feedback_system.record_feedback("query2", "code2", "negative")
        feedback_system.record_feedback("query3", "code3", "positive", result_rows=20)

        output_file = os.path.join(temp_feedback_dir, "export.json")
        result = feedback_system.export_feedback_for_training(output_file)

        assert result == True
        assert os.path.exists(output_file)

        # Verificar conteúdo
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Deve ter apenas os 2 feedbacks positivos
            assert len(data) == 2
            assert all(item['query'] in ['query1', 'query3'] for item in data)

    def test_export_feedback_only_positive(self, feedback_system, temp_feedback_dir):
        """Testa que apenas feedback positivo é exportado"""
        feedback_system.record_feedback("pos", "code", "positive")
        feedback_system.record_feedback("neg", "code", "negative")
        feedback_system.record_feedback("par", "code", "partial")

        output_file = os.path.join(temp_feedback_dir, "export.json")
        feedback_system.export_feedback_for_training(output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['query'] == 'pos'

    def test_export_feedback_empty(self, feedback_system, temp_feedback_dir):
        """Testa exportação sem feedback positivo"""
        feedback_system.record_feedback("neg", "code", "negative")

        output_file = os.path.join(temp_feedback_dir, "export.json")
        result = feedback_system.export_feedback_for_training(output_file)

        assert result == True

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 0

    # ==========================================
    # TESTES DE EDGE CASES
    # ==========================================

    def test_record_feedback_with_empty_query(self, feedback_system):
        """Testa feedback com query vazia"""
        result = feedback_system.record_feedback(
            query="",
            code="code",
            feedback_type="positive"
        )

        assert result == True

    def test_record_feedback_with_very_long_comment(self, feedback_system):
        """Testa feedback com comentário muito longo"""
        long_comment = "x" * 10000  # 10k caracteres

        result = feedback_system.record_feedback(
            query="query",
            code="code",
            feedback_type="negative",
            user_comment=long_comment
        )

        assert result == True

    def test_get_feedback_stats_future_days(self, feedback_system):
        """Testa estatísticas com dias no futuro (deve tratar gracefully)"""
        stats = feedback_system.get_feedback_stats(days=-1)

        # Não deve crashar
        assert isinstance(stats, dict)

    def test_concurrent_writes(self, feedback_system):
        """Testa escritas concorrentes (simuladas)"""
        # Escrever múltiplos feedbacks rapidamente
        results = []
        for i in range(100):
            result = feedback_system.record_feedback(f"query{i}", f"code{i}", "positive")
            results.append(result)

        # Todos devem ter sucesso
        assert all(results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
