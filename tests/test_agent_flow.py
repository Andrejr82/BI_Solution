'''
Testes de fumaça (smoke tests) para o fluxo principal do agente de BI.
Estes testes garantem que os principais caminhos de execução não quebram.
'''
import pytest
import os
from dotenv import load_dotenv
import logging

# Configuração de logging para arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_debug.log',
    filemode='w'
)

# Carregar variáveis de ambiente para os testes
load_dotenv(override=True)

# Mock para st.secrets, já que não estamos em um ambiente Streamlit
class MockSecrets(dict):
    def get(self, key, default=None):
        return self.get(key, default)

# Injetar o mock antes de importar os módulos do app
import streamlit as st
st.secrets = MockSecrets(
    GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY"),
    DEEPSEEK_API_KEY=os.environ.get("DEEPSEEK_API_KEY")
)

# Importar os componentes necessários após o mock
from core.graph.graph_builder import GraphBuilder
from core.factory.component_factory import ComponentFactory
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.agents.code_gen_agent import CodeGenAgent

import pandas as pd

@pytest.fixture(scope="module")
def agent_app():
    '''Cria uma instância do aplicativo do agente para ser usada nos testes.'''
    try:
        llm_adapter = ComponentFactory.get_llm_adapter("gemini")
        data_adapter = HybridDataAdapter()
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
        
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=data_adapter,
            code_gen_agent=code_gen_agent
        )
        app = graph_builder.build()
        return app
    except Exception as e:
        pytest.fail(f"Falha ao inicializar o backend para os testes: {e}")

def test_simple_query_is_correct(agent_app):
    """Verifica se uma consulta de filtro simples retorna o dado correto."""
    query = "qual o estoque do produto 369947?"
    initial_state = {"messages": [{"role": "user", "content": query}]}
    
    try:
        final_state = agent_app.invoke(initial_state)
        response = final_state["final_response"]
        
        assert response.get("type") == "data", "O tipo da resposta deveria ser 'data'"
        output_data = response.get("content")
        assert isinstance(output_data, list), "A saída deveria ser uma lista"
        assert len(output_data) > 0, "Deveria haver pelo menos um resultado"
        
        # Verifica se o código do produto está no resultado
        found_product = any(str(item.get('codigo', item.get('PRODUTO'))) == '369947' for item in output_data)
        assert found_product, "O produto 369947 não foi encontrado na resposta"

    except Exception as e:
        pytest.fail(f"Invocação do agente para consulta simples falhou com a exceção: {e}")

def test_complex_query_is_correct(agent_app):
    """Verifica se uma consulta complexa retorna a análise correta."""
    query = "gere o ranking de vendas do segmento tecidos"
    initial_state = {"messages": [{"role": "user", "content": query}]}
    
    try:
        final_state = agent_app.invoke(initial_state)
        response = final_state["final_response"]

        assert response.get("type") == "dataframe", "O tipo da resposta deveria ser 'dataframe'"
        output_df = pd.DataFrame(response.get("output"))
        assert not output_df.empty, "O DataFrame de saída não pode estar vazio"
        
        # Verifica se todos os resultados são do segmento correto
        assert 'nomesegmento' in output_df.columns, "A coluna 'nomesegmento' é esperada no resultado"
        assert all(output_df['nomesegmento'].str.upper() == 'TECIDO'), "Todos os produtos no ranking deveriam ser do segmento TECIDO"

    except Exception as e:
        pytest.fail(f"Invocação do agente para consulta complexa falhou com a exceção: {e}")
