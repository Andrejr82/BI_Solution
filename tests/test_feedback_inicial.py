"""
Teste do Feedback Inicial - Valida se o agente informa o usuário sobre o que irá fazer.

Este teste verifica se:
1. O nó generate_initial_feedback é executado no modo analítico
2. Uma mensagem de feedback é gerada
3. A mensagem é contextualizada com base na query do usuário

Author: devAndreJr
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agents.bi_agent_nodes import generate_initial_feedback, _create_feedback_message
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage

def test_feedback_message_generation():
    """Testa a geração de mensagens de feedback contextualizadas."""

    print("=" * 60)
    print("TESTE: Geração de Mensagens de Feedback")
    print("=" * 60)

    test_cases = [
        {
            "query": "Estou preocupado com as vendas dos tecidos oxford dos últimos 3 meses",
            "tone": "neutro",
            "expected_keywords": ["analisar", "vendas", "tecidos oxford"]
        },
        {
            "query": "Me mostre o MC do produto 369947 na UNE SCR",
            "tone": "neutro",
            "expected_keywords": ["calcular", "MC"]
        },
        {
            "query": "Preciso urgente do estoque de todos os produtos",
            "tone": "urgente",
            "expected_keywords": ["estoque", "rapidinho"]
        },
        {
            "query": "Gere um gráfico das vendas por segmento",
            "tone": "casual",
            "expected_keywords": ["gráfico", "gerar"]
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTeste {i}: {test_case['query']}")
        print("-" * 60)

        feedback = _create_feedback_message(
            test_case["query"],
            "",  # reasoning não é usado na função
            test_case["tone"]
        )

        print(f"Feedback gerado: {feedback}")

        # Verificar se keywords esperadas estão presentes (case insensitive)
        feedback_lower = feedback.lower()
        missing_keywords = []
        for keyword in test_case["expected_keywords"]:
            if keyword.lower() not in feedback_lower:
                missing_keywords.append(keyword)

        if missing_keywords:
            print(f"❌ FALHOU - Keywords ausentes: {', '.join(missing_keywords)}")
            all_passed = False
        else:
            print(f"✅ PASSOU - Todas as keywords encontradas")

    return all_passed


def test_feedback_node_integration():
    """Testa a integração do nó de feedback com o AgentState."""

    print("\n" + "=" * 60)
    print("TESTE: Integração do Nó generate_initial_feedback")
    print("=" * 60)

    # Criar estado de teste
    state = AgentState(
        messages=[
            HumanMessage(content="Estou preocupado com as vendas dos tecidos oxford")
        ],
        reasoning_mode="analytical",
        reasoning_result={
            "mode": "analytical",
            "reasoning": "Usuário solicitou análise de vendas de tecidos oxford",
            "emotional_tone": "neutro",
            "confidence": 0.9
        }
    )

    print(f"\nQuery: {state['messages'][0].content}")
    print(f"Modo: {state['reasoning_mode']}")
    print(f"Tom emocional: {state['reasoning_result']['emotional_tone']}")

    # Executar nó de feedback
    result = generate_initial_feedback(state)

    print(f"\nResultado do nó:")
    print(f"- initial_feedback: {result.get('initial_feedback', 'N/A')}")

    # Validar resultado
    if "initial_feedback" in result and result["initial_feedback"]:
        print("\n✅ PASSOU - Feedback inicial gerado com sucesso")
        return True
    else:
        print("\n❌ FALHOU - Feedback inicial não foi gerado")
        return False


def main():
    """Executa todos os testes."""

    print("\n" + "=" * 60)
    print("TESTES DE FEEDBACK INICIAL")
    print("=" * 60)

    results = []

    # Teste 1: Geração de mensagens
    results.append(("Geração de Mensagens", test_feedback_message_generation()))

    # Teste 2: Integração do nó
    results.append(("Integração do Nó", test_feedback_node_integration()))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
