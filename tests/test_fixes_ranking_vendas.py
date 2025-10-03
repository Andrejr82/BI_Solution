"""
Testes para verificar correções de:
1. Salvamento de gráficos
2. Reconhecimento de 'ranking de vendas na une X'
"""

import pytest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter


class TestRankingVendasFixes:
    """Testes para verificar correções de ranking de vendas"""

    @pytest.fixture
    def engine(self):
        """Fixture para criar engine de teste com dados reais"""
        import os
        # Caminho para o arquivo parquet real
        parquet_path = os.path.join("data", "parquet", "admmat.parquet")
        adapter = ParquetAdapter(file_path=parquet_path)
        return DirectQueryEngine(adapter)

    def test_ranking_vendas_na_une_scr(self, engine):
        """Teste: 'ranking de vendas na une scr' deve ser reconhecido"""
        query_type, params = engine.classify_intent_direct("ranking de vendas na une scr")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_une_especifica", f"Esperado 'top_produtos_une_especifica', recebeu '{query_type}'"
        assert params.get("une_nome") == "SCR", f"Esperado UNE 'SCR', recebeu '{params.get('une_nome')}'"
        assert params.get("limite") == 10, f"Esperado limite 10, recebeu {params.get('limite')}"

    def test_ranking_vendas_da_une_261(self, engine):
        """Teste: 'ranking vendas da une 261' deve ser reconhecido"""
        query_type, params = engine.classify_intent_direct("ranking vendas da une 261")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_une_especifica"
        assert params.get("une_nome") == "261"

    def test_ranking_de_vendas_na_une_mad(self, engine):
        """Teste: 'ranking de vendas na une MAD' deve ser reconhecido"""
        query_type, params = engine.classify_intent_direct("ranking de vendas na une MAD")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_une_especifica"
        assert params.get("une_nome") == "MAD"

    def test_ranking_produtos_geral(self, engine):
        """Teste: 'ranking de produtos' sem UNE específica"""
        query_type, params = engine.classify_intent_direct("ranking de produtos")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_por_segmento"
        assert params.get("segmento") == "todos"

    def test_top_vendas_geral(self, engine):
        """Teste: 'top vendas' deve retornar ranking geral"""
        query_type, params = engine.classify_intent_direct("top vendas")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_por_segmento"

    def test_ranking_10_produtos(self, engine):
        """Teste: 'ranking de 10 produtos' deve capturar o limite"""
        query_type, params = engine.classify_intent_direct("ranking de 10 produtos")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        assert query_type == "top_produtos_por_segmento"
        assert params.get("limit") == 10

    def test_ranking_vendas_unes_todas(self, engine):
        """Teste: 'ranking de vendas totais de cada une' deve manter padrão original"""
        query_type, params = engine.classify_intent_direct("vendas totais de cada une")

        print(f"\n✅ Query Type: {query_type}")
        print(f"✅ Params: {params}")

        # Deve detectar como ranking_vendas_unes (todas as UNEs)
        assert query_type == "ranking_vendas_unes"


if __name__ == "__main__":
    # Executar testes manualmente
    import logging
    logging.basicConfig(level=logging.INFO)

    # Criar engine com dados reais
    parquet_path = os.path.join("data", "parquet", "admmat.parquet")
    adapter = ParquetAdapter(file_path=parquet_path)
    engine = DirectQueryEngine(adapter)

    print("\n" + "="*80)
    print("TESTANDO CORRECOES DE RANKING DE VENDAS")
    print("="*80)

    # Teste 1
    print("\n[Teste 1] 'ranking de vendas na une scr'")
    query_type, params = engine.classify_intent_direct("ranking de vendas na une scr")
    print(f"   OK Query Type: {query_type}")
    print(f"   OK Params: {params}")
    assert query_type == "top_produtos_une_especifica", "FALHOU!"

    # Teste 2
    print("\n[Teste 2] 'ranking vendas da une 261'")
    query_type, params = engine.classify_intent_direct("ranking vendas da une 261")
    print(f"   OK Query Type: {query_type}")
    print(f"   OK Params: {params}")
    assert query_type == "top_produtos_une_especifica", "FALHOU!"

    # Teste 3
    print("\n[Teste 3] 'ranking de produtos' (geral)")
    query_type, params = engine.classify_intent_direct("ranking de produtos")
    print(f"   OK Query Type: {query_type}")
    print(f"   OK Params: {params}")
    assert query_type == "top_produtos_por_segmento", "FALHOU!"

    # Teste 4
    print("\n[Teste 4] 'vendas totais de cada une' (todas UNEs)")
    query_type, params = engine.classify_intent_direct("vendas totais de cada une")
    print(f"   OK Query Type: {query_type}")
    print(f"   OK Params: {params}")
    assert query_type == "ranking_vendas_unes", "FALHOU!"

    print("\n" + "="*80)
    print("SUCESSO - TODOS OS TESTES PASSARAM!")
    print("="*80)
