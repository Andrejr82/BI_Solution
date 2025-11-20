"""
Script de Teste: Conversational Reasoning Engine

Testa a nova arquitetura conversacional com diferentes tipos de inputs.

Author: devAndreJr
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.config.settings import get_safe_settings

def test_conversational_reasoning():
    """Testa o motor de raciocínio conversacional"""

    print("=" * 80)
    print("TESTE: Conversational Reasoning Engine")
    print("=" * 80)

    # Configurar
    settings = get_safe_settings()

    # Importar adaptador LLM
    from core.factory.component_factory import ComponentFactory
    llm_adapter = ComponentFactory.create_llm_adapter()

    # Criar engine
    engine = ConversationalReasoningEngine(llm_adapter)

    # Cenários de teste
    test_cases = [
        {
            "name": "Saudação Casual",
            "message": "oi, tudo bem?",
            "expected_mode": "conversational"
        },
        {
            "name": "Query Técnica Clara",
            "message": "qual a MC do produto 369947 na UNE SCR?",
            "expected_mode": "analytical"
        },
        {
            "name": "Pedido Vago (Precisa Clarificação)",
            "message": "quero ver produtos",
            "expected_mode": "conversational"
        },
        {
            "name": "Frustração",
            "message": "já tentei 3 vezes e não funciona!",
            "expected_mode": "conversational"
        },
        {
            "name": "Agradecimento",
            "message": "muito obrigado pela ajuda!",
            "expected_mode": "conversational"
        },
        {
            "name": "Query Analítica - Gráfico",
            "message": "mostre um gráfico de vendas por categoria",
            "expected_mode": "analytical"
        }
    ]

    # Executar testes
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"TESTE {i}/{len(test_cases)}: {test['name']}")
        print(f"{'-' * 80}")
        print(f"Input: \"{test['message']}\"")
        print(f"Modo Esperado: {test['expected_mode']}")

        # Criar estado mock
        state = {
            "messages": [HumanMessage(content=test["message"])]
        }

        try:
            # Executar reasoning
            mode, reasoning_result = engine.reason_about_user_intent(state)

            # Resultados
            print(f"\nRESULTADO:")
            print(f"   - Modo Detectado: {mode}")
            print(f"   - Tom Emocional: {reasoning_result.get('emotional_tone', 'N/A')}")
            print(f"   - Confianca: {reasoning_result.get('confidence', 0):.2f}")
            print(f"   - Raciocinio: {reasoning_result.get('reasoning', 'N/A')[:150]}...")
            print(f"   - Precisa Clarificacao: {reasoning_result.get('needs_clarification', False)}")

            # Validação
            if mode == test["expected_mode"]:
                print(f"\n[OK] PASSOU: Modo correto detectado!")
            else:
                print(f"\n[WARN] Modo diferente do esperado (esperado: {test['expected_mode']}, obtido: {mode})")

            # Se conversacional, testar resposta
            if mode == "conversational":
                print(f"\nGerando resposta conversacional...")
                response = engine.generate_conversational_response(reasoning_result, state)
                print(f"   Resposta: \"{response[:200]}...\"")

        except Exception as e:
            print(f"\n[ERRO]: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("[OK] TESTES CONCLUIDOS")
    print("=" * 80)

if __name__ == "__main__":
    test_conversational_reasoning()
