"""
Teste de conexão com API do Gemini
Verifica se a nova API key está funcionando
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gemini_api():
    """Testa conexão com API do Gemini"""
    print("=" * 80)
    print("TESTE DE CONEXAO COM API DO GEMINI")
    print("=" * 80)

    # Importar dependências
    try:
        from core.config.settings import get_settings
        print("\n[OK] Modulo de configuracoes importado")
    except Exception as e:
        print(f"\n[ERRO] Falha ao importar configuracoes: {e}")
        return False

    # Carregar configurações
    try:
        settings = get_settings()
        print("[OK] Configuracoes carregadas")

        # Verificar se API key existe (não mostrar a chave completa por segurança)
        api_key = settings.GEMINI_API_KEY  # Acessar como atributo, não dicionário
        if api_key:
            masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
            print(f"[OK] API Key encontrada: {masked_key}")
        else:
            print("[ERRO] API Key NAO encontrada!")
            return False

    except Exception as e:
        print(f"[ERRO] Falha ao carregar configuracoes: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Criar adaptador LLM
    try:
        from core.llm_adapter import GeminiLLMAdapter

        adapter = GeminiLLMAdapter(
            api_key=api_key,
            model_name="gemini-2.0-flash-exp",
            temperature=0.7,
            enable_cache=False  # Desabilitar cache para teste limpo
        )
        print("[OK] Adaptador Gemini criado")
    except Exception as e:
        print(f"[ERRO] Falha ao criar adaptador: {e}")
        return False

    # Testar chamada simples
    print("\n" + "-" * 80)
    print("TESTE 1: Pergunta Simples")
    print("-" * 80)

    try:
        test_message = "Ola! Responda apenas: 'API funcionando'"
        print(f"Enviando: '{test_message}'")

        response = adapter.get_completion(
            messages=[{"role": "user", "content": test_message}],
            temperature=0.0,
            max_tokens=50
        )

        # Verificar resposta
        if response.get("error"):
            print(f"\n[ERRO] API retornou erro:")
            print(f"  Tipo: {response.get('error')}")
            if response.get("user_message"):
                print(f"  Mensagem: {response.get('user_message')[:200]}...")
            return False

        content = response.get("content", "")
        if content:
            print(f"\n[OK] Resposta recebida ({len(content)} caracteres)")
            print(f"  Conteudo: '{content[:100]}...'")
        else:
            print("\n[ERRO] Resposta vazia!")
            return False

    except Exception as e:
        print(f"\n[ERRO] Falha na chamada da API: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Testar modo conversacional
    print("\n" + "-" * 80)
    print("TESTE 2: Modo Conversacional")
    print("-" * 80)

    try:
        conversational_message = "Ola, quem e voce?"
        print(f"Enviando: '{conversational_message}'")

        response = adapter.get_completion(
            messages=[{"role": "user", "content": conversational_message}],
            temperature=0.7,
            max_tokens=200
        )

        if response.get("error"):
            print(f"\n[ERRO] API retornou erro no modo conversacional")
            return False

        content = response.get("content", "")
        if content and len(content) > 10:
            print(f"\n[OK] Resposta conversacional recebida ({len(content)} caracteres)")
            print(f"  Conteudo: '{content[:150]}...'")
        else:
            print(f"\n[AVISO] Resposta muito curta: '{content}'")

    except Exception as e:
        print(f"\n[ERRO] Falha no teste conversacional: {e}")
        return False

    # Teste final
    print("\n" + "=" * 80)
    print("[SUCESSO] TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print("\nA API do Gemini esta funcionando corretamente.")
    print("A interface deveria estar respondendo normalmente agora.")
    return True


def test_agent_graph():
    """Testa o fluxo completo do agente"""
    print("\n" + "=" * 80)
    print("TESTE DE FLUXO COMPLETO DO AGENTE")
    print("=" * 80)

    try:
        # Importar módulo de inicialização do backend (simular streamlit_app)
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        from langchain_core.messages import HumanMessage
        from core.graph.graph_builder import GraphBuilder
        from core.factory.component_factory import ComponentFactory

        print("\n[OK] Importacoes realizadas")

        # Inicializar componentes (como no streamlit_app)
        factory = ComponentFactory()
        llm_adapter = factory.get_reasoning_llm()
        parquet_adapter = factory.get_parquet_adapter()
        code_gen_agent = factory.get_code_gen_agent()

        # Criar graph builder
        graph_builder = GraphBuilder(llm_adapter, parquet_adapter, code_gen_agent)
        agent_graph = graph_builder.build()

        if not agent_graph:
            print("[ERRO] Nao foi possivel obter agent_graph")
            return False

        print("[OK] Agent graph construido")

        # Criar mensagem de teste
        test_query = "Ola, bom dia!"
        print(f"\nTestando query: '{test_query}'")

        initial_state = {
            "messages": [HumanMessage(content=test_query)],
            "query": test_query
        }

        print("[...] Processando (isso pode demorar ~5-10s)...")

        # Invocar agente
        result = agent_graph.invoke(initial_state)

        # Verificar resultado
        if not result:
            print("[ERRO] Resultado vazio")
            return False

        print("[OK] Agente processou a query")

        # Verificar final_response
        final_response = result.get("final_response")
        if not final_response:
            print("[AVISO] Nenhuma final_response no resultado")
            print(f"  Chaves disponiveis: {list(result.keys())}")
            return False

        print(f"[OK] Final response encontrada")
        print(f"  Tipo: {final_response.get('type')}")

        content = final_response.get("content")
        if content:
            if isinstance(content, str):
                print(f"  Conteudo: '{content[:100]}...'")
            else:
                print(f"  Conteudo (tipo {type(content).__name__}): {str(content)[:100]}...")
        else:
            print("[ERRO] Conteudo vazio na resposta!")
            return False

        print("\n[SUCESSO] Fluxo completo do agente funcionando!")
        return True

    except Exception as e:
        print(f"\n[ERRO] Falha no teste do agente: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nINICIANDO TESTES DE VALIDACAO\n")

    # Teste 1: API do Gemini
    api_ok = test_gemini_api()

    # Teste 2: Fluxo do agente (apenas se API estiver OK)
    agent_ok = False
    if api_ok:
        agent_ok = test_agent_graph()

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"1. API do Gemini: {'[PASS]' if api_ok else '[FAIL]'}")
    print(f"2. Fluxo do Agente: {'[PASS]' if agent_ok else '[FAIL]'}")

    if api_ok and agent_ok:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        print("\nA interface esta pronta para uso.")
        print("Execute: streamlit run streamlit_app.py")
        sys.exit(0)
    else:
        print("\n[FALHA] Alguns testes falharam")
        print("\nVerifique os erros acima e corrija antes de usar a interface.")
        sys.exit(1)
