import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.graph.graph_builder import GraphBuilder
from core.factory.component_factory import ComponentFactory
from core.agents.code_gen_agent import CodeGenAgent
from langchain_core.messages import HumanMessage

@pytest.fixture(scope="module")
def agent_graph():
    """
    Fixture to initialize the agent graph.
    """
    llm_adapter = ComponentFactory.get_llm_adapter()
    code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
    from core.connectivity.hybrid_adapter import HybridDataAdapter
    data_adapter = HybridDataAdapter()
    
    graph_builder = GraphBuilder(
        llm_adapter=llm_adapter,
        parquet_adapter=data_adapter,
        code_gen_agent=code_gen_agent
    )
    return graph_builder.build()

def test_query_abastecimento(agent_graph):
    """
    Tests the agent's ability to answer a query about product replenishment.
    """
    query = "Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 2586?"
    graph_input = {"messages": [HumanMessage(content=query)]}
    
    final_state = agent_graph.invoke(graph_input)
    
    final_response = final_state.get("final_response", {})
    assert final_response.get("type") == "data"
    assert isinstance(final_response.get("content"), list)
    assert len(final_response.get("content")) > 0

def test_query_mc_produto(agent_graph):
    """
    Tests the agent's ability to calculate the average cost of a product.
    """
    query = "Calcule a MC do produto 704559 na UNE 2586"
    graph_input = {"messages": [HumanMessage(content=query)]}
    
    final_state = agent_graph.invoke(graph_input)
    
    final_response = final_state.get("final_response", {})
    assert final_response.get("type") == "text"
    assert "Média de Custo" in final_response.get("content")

def test_query_preco_final(agent_graph):
    """
    Tests the agent's ability to calculate the final price of a product.
    """
    query = "Quanto fica uma compra de R$ 600 com ranking 2 pagando em 30 dias?"
    graph_input = {"messages": [HumanMessage(content=query)]}
    
    final_state = agent_graph.invoke(graph_input)
    
    final_response = final_state.get("final_response", {})
    assert final_response.get("type") == "text"
    assert "Preço Final" in final_response.get("content")

def test_query_estoque_zero(agent_graph):
    """
    Tests the agent's ability to list products with zero stock.
    """
    query = "Quais são os produtos com estoque zero no segmento de PAPELARIA na UNE 2586?"
    graph_input = {"messages": [HumanMessage(content=query)]}
    
    final_state = agent_graph.invoke(graph_input)
    
    final_response = final_state.get("final_response", {})
    assert final_response.get("type") == "data"
    assert isinstance(final_response.get("content"), list)
    assert len(final_response.get("content")) > 0
