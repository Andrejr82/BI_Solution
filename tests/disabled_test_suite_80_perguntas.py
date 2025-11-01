"""
Suite Completa de Testes para as 80 Perguntas de Negócio
Testes automatizados end-to-end
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter


class TestSuite80Perguntas:
    """Suite de testes para as 80 perguntas de negócio"""

    @pytest.fixture(scope="class")
    def engine(self):
        """Fixture para criar engine compartilhado"""
        parquet_path = os.path.join("data", "parquet", "admmat.parquet")
        adapter = ParquetAdapter(file_path=parquet_path)
        return DirectQueryEngine(adapter)

    # ===== VENDAS POR PRODUTO =====

    def test_vendas_produto_une(self, engine):
        """Test: Gráfico de vendas do produto na UNE"""
        query_type, params = engine.classify_intent_direct(
            "Gere um gráfico de vendas do produto 369947 na UNE SCR"
        )
        assert query_type == "vendas_produto_une"
        assert params.get("produto") == "369947"

    def test_evolucao_vendas(self, engine):
        """Test: Evolução mensal de vendas"""
        query_type, _ = engine.classify_intent_direct(
            "Mostre a evolução de vendas mensais do produto 369947"
        )
        assert query_type in ["evolucao_vendas_produto", "evolucao_mes_a_mes"]

    def test_top_produtos_une(self, engine):
        """Test: Top produtos em UNE específica"""
        query_type, params = engine.classify_intent_direct(
            "Quais são os 5 produtos mais vendidos na UNE SCR?"
        )
        assert query_type == "top_produtos_une_especifica"
        assert params.get("limite") in ["5", 5]

    # ===== ANÁLISES POR SEGMENTO =====

    def test_top_produtos_segmento(self, engine):
        """Test: Top produtos em segmento"""
        query_type, params = engine.classify_intent_direct(
            "Quais são os 10 produtos que mais vendem no segmento TECIDOS?"
        )
        # Pode ser top_produtos_por_segmento ou analise_geral (mas não fallback)
        assert query_type != "fallback"

    def test_comparacao_segmentos(self, engine):
        """Test: Comparação entre segmentos"""
        query_type, _ = engine.classify_intent_direct(
            "Compare vendas entre segmentos ARMARINHO e TECIDOS"
        )
        assert query_type == "comparacao_segmentos"

    def test_ranking_segmentos(self, engine):
        """Test: Ranking de segmentos"""
        query_type, _ = engine.classify_intent_direct(
            "Ranking dos segmentos por volume de vendas"
        )
        assert query_type in ["ranking_geral", "ranking_vendas_unes"]

    def test_crescimento_segmento(self, engine):
        """Test: Crescimento por segmento"""
        query_type, _ = engine.classify_intent_direct(
            "Qual segmento teve maior crescimento?"
        )
        assert query_type == "crescimento_segmento"

    # ===== ANÁLISES POR UNE =====

    def test_ranking_vendas_une(self, engine):
        """Test: Ranking de vendas por UNE"""
        query_type, _ = engine.classify_intent_direct(
            "Ranking de vendas por UNE"
        )
        assert query_type == "ranking_vendas_unes"

    def test_ranking_vendas_na_une_scr(self, engine):
        """Test: Ranking de vendas NA une específica"""
        query_type, params = engine.classify_intent_direct(
            "Ranking de vendas na une scr"
        )
        assert query_type == "top_produtos_une_especifica"
        assert params.get("une_nome") == "SCR"

    # ===== ANÁLISES TEMPORAIS =====

    def test_sazonalidade(self, engine):
        """Test: Análise de sazonalidade"""
        query_type, _ = engine.classify_intent_direct(
            "Análise de sazonalidade no segmento FESTAS"
        )
        assert query_type == "sazonalidade"

    def test_tendencia_vendas(self, engine):
        """Test: Tendência de vendas"""
        query_type, _ = engine.classify_intent_direct(
            "Tendência de vendas dos últimos 6 meses"
        )
        assert query_type == "tendencia_vendas"

    def test_evolucao_12_meses(self, engine):
        """Test: Evolução de vendas"""
        query_type, _ = engine.classify_intent_direct(
            "Evolução de vendas dos últimos 12 meses"
        )
        assert query_type == "evolucao_mes_a_mes"

    def test_pico_vendas(self, engine):
        """Test: Produtos com pico de vendas"""
        query_type, _ = engine.classify_intent_direct(
            "Quais produtos tiveram pico no último mês?"
        )
        assert query_type == "pico_vendas"

    # ===== PERFORMANCE E ABC =====

    def test_analise_abc_classe_a(self, engine):
        """Test: Produtos ABC classe A"""
        query_type, params = engine.classify_intent_direct(
            "Produtos classificados como ABC A no segmento TECIDOS"
        )
        assert query_type == "analise_abc"
        assert params.get("classe_abc") == "a"

    def test_analise_abc_geral(self, engine):
        """Test: Análise ABC distribuição"""
        query_type, _ = engine.classify_intent_direct(
            "Análise ABC: distribuição de produtos"
        )
        assert query_type == "analise_abc"

    def test_abc_classe_c(self, engine):
        """Test: Produtos ABC C com potencial"""
        query_type, params = engine.classify_intent_direct(
            "Produtos ABC C com potencial para B"
        )
        assert query_type == "analise_abc"
        assert params.get("classe_abc") == "c"

    # ===== ESTOQUE E LOGÍSTICA =====

    def test_estoque_baixo(self, engine):
        """Test: Produtos com estoque baixo"""
        query_type, _ = engine.classify_intent_direct(
            "Produtos com estoque baixo vs alta demanda"
        )
        # Pode ser produtos_reposicao ou estoque_baixo
        assert query_type in ["produtos_reposicao", "estoque_baixo"]

    def test_estoque_excesso(self, engine):
        """Test: Produtos com excesso de estoque"""
        query_type, _ = engine.classify_intent_direct(
            "Identificar produtos com excesso de estoque"
        )
        assert query_type == "estoque_alto"

    def test_rotacao_estoque(self, engine):
        """Test: Rotação de estoque"""
        query_type, _ = engine.classify_intent_direct(
            "Produtos com maior rotação de estoque"
        )
        assert query_type == "rotacao_estoque"

    def test_produtos_sem_movimento(self, engine):
        """Test: Produtos sem movimento"""
        query_type, _ = engine.classify_intent_direct(
            "Produtos sem movimento"
        )
        assert query_type == "produtos_sem_movimento"

    # ===== ANÁLISES POR FABRICANTE =====

    def test_ranking_fabricantes(self, engine):
        """Test: Ranking de fabricantes"""
        query_type, _ = engine.classify_intent_direct(
            "Ranking de fabricantes por volume de vendas"
        )
        assert query_type == "ranking_fabricantes"

    def test_fabricantes_diversidade(self, engine):
        """Test: Fabricantes com maior diversidade"""
        query_type, _ = engine.classify_intent_direct(
            "Fabricantes com maior diversidade de produtos"
        )
        assert query_type == "ranking_fabricantes"

    # ===== CATEGORIA/GRUPO =====

    def test_performance_categoria(self, engine):
        """Test: Performance por categoria"""
        query_type, _ = engine.classify_intent_direct(
            "Performance por categoria no segmento ARMARINHO"
        )
        assert query_type == "performance_categoria"


# Executar todos os testes
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
