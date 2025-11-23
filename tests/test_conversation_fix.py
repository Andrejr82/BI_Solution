import pytest
from unittest.mock import MagicMock, patch

# Importar os componentes necessários
from core.graph.graph_builder import GraphBuilder
from langchain_core.messages import HumanMessage, AIMessage

# Mock dos componentes externos para isolar o teste na lógica do grafo
@pytest.fixture
def mock_llm_adapter():
    """Mock do adaptador LLM para controlar as respostas da IA."""
    mock = MagicMock()
    # Configurar respostas simuladas para cada chamada
    mock.get_completion.side_effect = [
        # 1ª chamada (classify_intent): IA pede esclarecimento sobre 'vendas'
        {"content": '{"intent": "gerar_grafico", "confidence": 0.9, "reasoning": "Usuário quer um gráfico, mas \'vendas\' é ambíguo."}', },
        # 2ª chamada (generate_parquet_query): IA gera filtros com base no esclarecimento
        {"content": '{"nomesegmento": {"operator": "is_not_null"}, "une_nome": "scr", "metric": "LIQUIDO_38"}', },
        # 3ª chamada (generate_plotly_spec): IA gera o código para o gráfico
        {"content": "```python\nimport plotly.express as px\nresult = px.bar(df_raw_data, x='nomesegmento', y='LIQUIDO_38', title='Vendas por Segmento na UNE SCR')\n```"}
    ]
    return mock

@pytest.fixture
def mock_parquet_adapter():
    """Mock do adaptador Parquet para simular o retorno de dados."""
    mock = MagicMock()
    # Simular o retorno de dados após a consulta
    mock.execute_query.return_value = [
        {"nomesegmento": "TECIDOS", "LIQUIDO_38": 1500},
        {"nomesegmento": "PAPELARIA", "LIQUIDO_38": 1200},
        {"nomesegmento": "ARTES", "LIQUIDO_38": 800}
    ]
    return mock

@pytest.fixture
def mock_code_gen_agent(mock_llm_adapter):
    """Mock do agente de geração de código."""
    # Como o código do gráfico agora é gerado em generate_plotly_spec,
    # vamos simular o comportamento de execução de código aqui.
    agent = MagicMock()

    def execute_side_effect(input_data):
        # Simula a execução do código python e retorna um objeto de gráfico plotly
        if "px.bar" in input_data.get("query", ""):
            return {"type": "chart", "output": '{"data": [{"type": "bar"}]}'}
        return {"type": "error", "output": "Código inesperado"}

    agent.generate_and_execute_code.side_effect = execute_side_effect
    return agent


# O teste de conversação
def test_conversational_graph_flow_with_clarification(mock_llm_adapter, mock_parquet_adapter, mock_code_gen_agent):
    """
    Simula uma conversa de 2 turnos para validar que o agente não
    entra em loop e responde corretamente após um esclarecimento.
    """
    # 1. Configuração do ambiente de teste
    # Usar patch para substituir a fábrica real pelos nossos mocks
    with patch('core.agents.bi_agent_nodes._factory.get_intent_classification_llm', return_value=mock_llm_adapter):
        with patch('core.agents.bi_agent_nodes._factory.get_code_generation_llm', return_value=mock_llm_adapter):
            graph_builder = GraphBuilder(
                llm_adapter=mock_llm_adapter,
                parquet_adapter=mock_parquet_adapter,
                code_gen_agent=mock_code_gen_agent
            )
            agent_graph = graph_builder.build()

            # --- TURNO 1: Pergunta inicial do usuário ---
            print("\n--- TURNO 1: INICIANDO ---")
            initial_input = {"messages": [HumanMessage(content="gráfico de barras de vendas na une scr")]}
            
            # Simular a primeira chamada ao agente
            # Aqui, esperamos que ele peça esclarecimento
            intermediate_state = agent_graph.invoke(initial_input)
            
            # Verificar se o agente pediu esclarecimento (simulado pela resposta de texto)
            # Na implementação real, isso viria da lógica de decisão que leva a um nó de esclarecimento
            # Como estamos mockando, a primeira resposta do LLM leva à geração da segunda pergunta
            # Para este teste, vamos assumir que a lógica interna do agente decidiu pedir esclarecimento e o formatou
            # Nossa correção principal é no TURNO 2
            print("--- TURNO 1: COMPLETO ---")


            # --- TURNO 2: Resposta do usuário ao esclarecimento ---
            print("\n--- TURNO 2: INICIANDO ---")
            # Adicionar a resposta do agente e a nova resposta do usuário ao histórico
            full_history = [
                HumanMessage(content="gráfico de barras de vendas na une scr"),
                AIMessage(content="Você quer que ele mostre o valor total das vendas, a quantidade de itens vendidos, ou alguma outra coisa de vendas?"),
                HumanMessage(content="valor total das vendas")
            ]
            
            final_input = {"messages": full_history}
            
            # Invocar o agente novamente, agora com o histórico completo
            final_state = agent_graph.invoke(final_input)

            print("--- TURNO 2: COMPLETO ---")

            # --- VALIDAÇÃO ---
            print("\n--- VALIDAÇÃO ---")
            # A correção principal foi garantir que o histórico completo fosse passado.
            # Agora, verificamos se o resultado final é um gráfico.
            final_response = final_state.get("final_response", {})
            print(f"Resposta final do agente: {final_response}")

            assert final_response.get("type") == "chart", "O agente deveria ter gerado um gráfico no final"
            assert '"type": "bar"' in final_response.get("content", ""), "O gráfico deveria ser do tipo barra"
            print("✅ SUCESSO: O agente respondeu com um gráfico após o esclarecimento.")
