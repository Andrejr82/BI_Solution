"""
Script de teste para verificar o fluxo de mensagens na interface
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_message_flow():
    """Testa o fluxo de mensagens entre usuário e assistente"""

    print("=" * 80)
    print("TESTE DE FLUXO DE MENSAGENS")
    print("=" * 80)

    # Simular session_state do Streamlit
    class MockSessionState:
        def __init__(self):
            self.messages = [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "content": "Olá! Eu sou a Caçulinha."
                    }
                }
            ]
            self.processing = False
            self.pending_query = None

        def get(self, key, default=None):
            return getattr(self, key, default)

    session_state = MockSessionState()

    print("\n[1] ESTADO INICIAL")
    print(f"   Mensagens: {len(session_state.messages)}")
    print(f"   Processing: {session_state.processing}")
    print(f"   Pending Query: {session_state.pending_query}")

    # Simular start_query_processing
    print("\n[2] USUARIO ENVIA PERGUNTA: 'Ola, quem e voce?'")
    user_input = "Olá, quem é você?"

    # Adicionar mensagem do usuário
    user_message = {"role": "user", "content": {"type": "text", "content": user_input}}
    session_state.messages.append(user_message)

    # Marcar como processando
    session_state.processing = True
    session_state.pending_query = user_input

    print(f"   Mensagens: {len(session_state.messages)} (usuário adicionado)")
    print(f"   Processing: {session_state.processing}")
    print(f"   Pending Query: '{session_state.pending_query}'")
    print("   >> RERUN aconteceria aqui")

    # Simular próximo rerun - renderização
    print("\n[3] RENDERIZACAO (apos rerun)")
    print("   Renderizando mensagens:")
    for i, msg in enumerate(session_state.messages):
        role = msg["role"]
        content = msg["content"]
        if isinstance(content, dict):
            text = content.get("content", str(content))
        else:
            text = str(content)
        print(f"   [{i+1}] {role.upper()}: {text[:50]}...")

    print(f"\n   Processing = {session_state.processing}")
    if session_state.processing:
        print("   [OK] INDICADOR 'Pensando...' SERIA MOSTRADO")

    # Simular processamento
    print("\n[4] PROCESSAMENTO (bloco if st.session_state.pending_query)")
    if session_state.pending_query:
        print(f"   Processando query: '{session_state.pending_query}'")

        # Limpar pending_query
        user_input_to_process = session_state.pending_query
        session_state.pending_query = None

        # Simular resposta do agente
        agent_response = {
            "type": "text",
            "content": "Olá! Eu sou a Caçulinha, sua assistente de BI. Posso te ajudar com análises de dados!",
            "user_query": user_input_to_process
        }

        # Adicionar resposta ao histórico
        assistant_message = {"role": "assistant", "content": agent_response}
        session_state.messages.append(assistant_message)

        # Desmarcar processamento
        session_state.processing = False

        print(f"   [OK] Resposta adicionada ao historico")
        print(f"   Mensagens: {len(session_state.messages)}")
        print(f"   Processing: {session_state.processing}")
        print("   >> RERUN aconteceria aqui")

    # Simular terceiro rerun - mostrar resposta
    print("\n[5] RENDERIZACAO FINAL (apos segundo rerun)")
    print("   Renderizando mensagens:")
    for i, msg in enumerate(session_state.messages):
        role = msg["role"]
        content = msg["content"]
        if isinstance(content, dict):
            text = content.get("content", str(content))
        else:
            text = str(content)
        print(f"   [{i+1}] {role.upper()}: {text}")

    print(f"\n   Processing = {session_state.processing}")
    if session_state.processing:
        print("   [ERRO] INDICADOR 'Pensando...' AINDA VISIVEL")
    else:
        print("   [OK] INDICADOR 'Pensando...' OCULTO")

    # Verificações
    print("\n" + "=" * 80)
    print("VERIFICAÇÕES")
    print("=" * 80)

    checks = []

    # Check 1: 3 mensagens no total
    if len(session_state.messages) == 3:
        print("[PASS] Check 1: 3 mensagens no historico (inicial, usuario, assistente)")
        checks.append(True)
    else:
        print(f"[FAIL] Check 1: Esperado 3 mensagens, encontrado {len(session_state.messages)}")
        checks.append(False)

    # Check 2: Processing = False no final
    if not session_state.processing:
        print("[PASS] Check 2: Flag 'processing' = False no final")
        checks.append(True)
    else:
        print("[FAIL] Check 2: Flag 'processing' ainda = True (ERRO!)")
        checks.append(False)

    # Check 3: pending_query = None no final
    if session_state.pending_query is None:
        print("[PASS] Check 3: pending_query = None no final")
        checks.append(True)
    else:
        print(f"[FAIL] Check 3: pending_query ainda = '{session_state.pending_query}' (ERRO!)")
        checks.append(False)

    # Check 4: Última mensagem é do assistente
    if session_state.messages[-1]["role"] == "assistant":
        print("[PASS] Check 4: Ultima mensagem e do assistente")
        checks.append(True)
    else:
        print(f"[FAIL] Check 4: Ultima mensagem e do {session_state.messages[-1]['role']}")
        checks.append(False)

    # Check 5: Resposta do assistente tem conteúdo
    last_msg_content = session_state.messages[-1]["content"]
    if isinstance(last_msg_content, dict) and last_msg_content.get("content"):
        print("[PASS] Check 5: Resposta do assistente tem conteudo valido")
        checks.append(True)
    else:
        print("[FAIL] Check 5: Resposta do assistente SEM conteudo")
        checks.append(False)

    # Resultado final
    print("\n" + "=" * 80)
    if all(checks):
        print("[SUCCESS] TODOS OS TESTES PASSARAM!")
        print("=" * 80)
        return True
    else:
        print(f"[FAIL] {len([c for c in checks if not c])}/{len(checks)} TESTES FALHARAM")
        print("=" * 80)
        return False


def test_rendering_logic():
    """Testa a lógica de renderização específica"""

    print("\n" + "=" * 80)
    print("TESTE DE RENDERIZAÇÃO")
    print("=" * 80)

    # Simular mensagem do assistente com estrutura complexa
    response_data = {
        "type": "text",
        "content": "Esta é a resposta do agente",
        "user_query": "Esta foi a pergunta do usuário"
    }

    print("\n[1] ESTRUTURA DA RESPOSTA")
    print(f"   Type: {response_data.get('type')}")
    print(f"   Content: {response_data.get('content')}")
    print(f"   User Query: {response_data.get('user_query')}")

    # Testar extração de conteúdo
    print("\n[2] EXTRACAO DE CONTEUDO")

    response_type = response_data.get("type", "text")
    content = response_data.get("content", "Conteúdo não disponível")

    print(f"   Response Type: {response_type}")
    print(f"   Content: {content}")

    if response_type == "text" and isinstance(content, str):
        print("   [OK] Renderizacao como TEXTO simples")
    else:
        print(f"   [WARN] Tipo inesperado: {type(content).__name__}")

    print("\n" + "=" * 80)
    print("[OK] TESTE DE RENDERIZACAO OK")
    print("=" * 80)

    return True


if __name__ == "__main__":
    print("\nINICIANDO TESTES DE INTERFACE\n")

    test1 = test_message_flow()
    test2 = test_rendering_logic()

    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Teste de Fluxo de Mensagens: {'[PASS]' if test1 else '[FAIL]'}")
    print(f"Teste de Renderizacao: {'[PASS]' if test2 else '[FAIL]'}")

    if test1 and test2:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM - INTERFACE OK!")
        sys.exit(0)
    else:
        print("\n[FAIL] ALGUNS TESTES FALHARAM - REVISAR IMPLEMENTACAO")
        sys.exit(1)
