"""
Teste de correção de conversações casuais (sem emojis)
"""
import logging
from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage

# Configurar logging
logging.basicConfig(level=logging.WARNING)  # Apenas warnings e errors
logger = logging.getLogger(__name__)

def test_conversational_greetings():
    """Testa se saudações são processadas corretamente"""

    output = []
    output.append("=" * 80)
    output.append("TESTE DE CONVERSACOES CASUAIS")
    output.append("=" * 80)

    # Inicializar LLM
    llm_adapter = ComponentFactory.get_llm_adapter("gemini")

    # Criar engine de raciocínio
    reasoning_engine = ConversationalReasoningEngine(llm_adapter)

    # Teste 1: Saudação simples
    output.append("\nTESTE 1: Saudacao simples")
    output.append("-" * 80)

    state1: AgentState = {
        "messages": [
            HumanMessage(content="oi tudo bem")
        ],
        "query": "oi tudo bem"
    }

    try:
        mode, reasoning = reasoning_engine.reason_about_user_intent(state1)
        output.append(f"OK Mode detectado: {mode}")
        output.append(f"OK Emotional tone: {reasoning.get('emotional_tone')}")
        output.append(f"OK Reasoning: {reasoning.get('reasoning', '')[:150]}...")

        if mode == "conversational":
            response = reasoning_engine.generate_conversational_response(reasoning, state1)
            output.append(f"\nResposta gerada:")
            output.append(f"{response}")
            output.append(f"\nOK TESTE 1 PASSOU!")
        else:
            output.append(f"\nERRO TESTE 1: Mode deveria ser 'conversational' mas foi '{mode}'")

    except Exception as e:
        output.append(f"\nERRO TESTE 1: {e}")
        import traceback
        output.append(traceback.format_exc())

    # Teste 2: Conversa casual
    output.append("\n" + "=" * 80)
    output.append("TESTE 2: Conversa casual")
    output.append("-" * 80)

    state2: AgentState = {
        "messages": [
            HumanMessage(content="ola caçulinha"),
            AIMessage(content="Oi! Tudo joia por aqui! Como posso te ajudar?"),
            HumanMessage(content="opa tudo bem caçulinha")
        ],
        "query": "opa tudo bem caçulinha"
    }

    try:
        mode, reasoning = reasoning_engine.reason_about_user_intent(state2)
        output.append(f"OK Mode detectado: {mode}")
        output.append(f"OK Emotional tone: {reasoning.get('emotional_tone')}")
        output.append(f"OK Reasoning: {reasoning.get('reasoning', '')[:150]}...")

        if mode == "conversational":
            response = reasoning_engine.generate_conversational_response(reasoning, state2)
            output.append(f"\nResposta gerada:")
            output.append(f"{response}")
            output.append(f"\nOK TESTE 2 PASSOU!")
        else:
            output.append(f"\nERRO TESTE 2: Mode deveria ser 'conversational' mas foi '{mode}'")

    except Exception as e:
        output.append(f"\nERRO TESTE 2: {e}")
        import traceback
        output.append(traceback.format_exc())

    output.append("\n" + "=" * 80)
    output.append("TESTES CONCLUIDOS")
    output.append("=" * 80)

    # Salvar output em arquivo
    with open("test_conversational_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("OK - Resultados salvos em test_conversational_output.txt")

if __name__ == "__main__":
    test_conversational_greetings()
