"""
Teste para verificar a correção de queries de ranking por categoria de produto.
Especificamente, para o bug: "top 10 tecidos une cfr" retornando ranking de UNEs.
"""

import pytest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

@pytest.fixture(scope="module")
def engine():
    """Cria uma instância do DirectQueryEngine para os testes."""
    parquet_path = os.path.join("data", "parquet", "admmat.parquet")
    if not os.path.exists(parquet_path):
        pytest.skip(f"Arquivo de dados não encontrado em {parquet_path}, pulando testes.")
    adapter = ParquetAdapter(file_path=parquet_path)
    return DirectQueryEngine(adapter)

class TestCategoryRankingFix:
    """
    Testa a correção para queries que envolvem ranking de produtos
    dentro de uma categoria específica e uma UNE.
    """

    def test_top_10_tecidos_une_cfr(self, engine):
        """
        Verifica se a query "top 10 tecidos une cfr" é classificada corretamente.
        Este teste deve falhar antes da correção.
        """
        query = "top 10 tecidos une cfr"
        
        # Esperado: uma nova intenção ou uma modificação de uma existente
        # que lida com categorias de produto.
        expected_query_type = "top_produtos_categoria_une"
        
        # Classifica a intenção
        query_type, params = engine.classify_intent_direct(query)

        print(f"\nInput Query: '{query}'")
        print(f"Query Type Retornado: '{query_type}'")
        print(f"Params Retornados: {params}")

        # Asserções que devem passar após a correção
        assert query_type == expected_query_type, \
            f"Esperado query_type '{expected_query_type}', mas recebeu '{query_type}'"
        
        assert int(params.get("limite")) == 10, \
            f"Esperado limite 10, mas recebeu {params.get('limite')}"
            
        assert params.get("une_nome").upper() == "CFR", \
            f"Esperado UNE 'CFR', mas recebeu '{params.get('une_nome')}'"
            
        # Esta é a asserção principal que deve falhar inicialmente
        assert params.get("categoria_produto").upper() == "TECIDOS", \
            f"Esperado categoria_produto 'TECIDOS', mas recebeu '{params.get('categoria_produto')}'"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
