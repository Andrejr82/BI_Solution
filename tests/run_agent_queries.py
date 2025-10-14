import sys
import os
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO)

from core.agents.caculinha_bi_agent import create_caculinha_bi_agent
from core.agents.code_gen_agent import CodeGenAgent
from core.factory.component_factory import ComponentFactory
from langchain_core.messages import HumanMessage

def run_agent_queries():
    """Executa uma série de queries de teste com o agente CaculinhaBI."""

    print("--- Iniciando testes de query com o agente CaculinhaBI ---")

    # Inicializa o agente
    llm_adapter = ComponentFactory.get_llm_adapter()
    code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
    agent_runnable, bi_tools = create_caculinha_bi_agent(
        parquet_dir=parquet_dir,
        code_gen_agent=code_gen_agent,
        llm_adapter=llm_adapter
    )

    queries = [
        "Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 2586?",
        "Calcule a MC do produto 704559 na UNE 2586",
        "Quanto fica uma compra de R$ 600 com ranking 2 pagando em 30 dias?",
        "Quanto fica uma compra de R$ 800 com ranking 0 pagando à vista?",
        "Quais são os produtos com estoque zero no segmento de PAPELARIA na UNE 2586?",
    ]

    for i, query in enumerate(queries):
        print(f"\n--- Teste de Query {i+1}: {query} ---")
        try:
            # Processa a query
            state = {"messages": [HumanMessage(content=query)]}
            result = agent_runnable.invoke(state)

            # Imprime o resultado formatado
            print("Resultado do agente:")
            last_message = result.get('messages', [])[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    print(json.dumps(tool_call, indent=2))
            else:
                print(last_message.content)

        except Exception as e:
            print(f"Falha no teste de query: {e}")
            import traceback
            traceback.print_exc()


    print("\n--- Testes de query com o agente concluídos ---")

if __name__ == "__main__":
    run_agent_queries()