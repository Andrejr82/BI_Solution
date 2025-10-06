"""
Script de teste para verificar se o Gemini Playground está funcionando
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("[*] Testando imports...")
    try:
        from core.llm_adapter import GeminiLLMAdapter
        print("[OK] GeminiLLMAdapter importado com sucesso")

        from core.config.safe_settings import get_safe_settings
        print("[OK] get_safe_settings importado com sucesso")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao importar: {e}")
        return False

def test_settings():
    """Testa se as configurações estão carregadas"""
    print("\n[*] Testando configuracoes...")
    try:
        from core.config.safe_settings import get_safe_settings
        settings = get_safe_settings()

        if settings.GEMINI_API_KEY:
            print(f"[OK] GEMINI_API_KEY configurada (primeiros 10 chars: {settings.GEMINI_API_KEY[:10]}...)")
        else:
            print("[AVISO] GEMINI_API_KEY nao configurada")
            return False

        print(f"[OK] Modelo configurado: {settings.LLM_MODEL_NAME}")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar settings: {e}")
        return False

def test_gemini_adapter():
    """Testa se o GeminiLLMAdapter funciona"""
    print("\n[*] Testando GeminiLLMAdapter...")
    try:
        from core.llm_adapter import GeminiLLMAdapter
        from core.config.safe_settings import get_safe_settings

        settings = get_safe_settings()

        if not settings.GEMINI_API_KEY:
            print("[AVISO] Pulando teste do adaptador - API key nao configurada")
            return False

        # Inicializar o adaptador
        adapter = GeminiLLMAdapter(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            enable_cache=True
        )
        print("[OK] GeminiLLMAdapter inicializado com sucesso")

        # Testar cache stats
        stats = adapter.get_cache_stats()
        print(f"[OK] Cache stats: {stats}")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao testar GeminiLLMAdapter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_completion():
    """Testa uma completion simples"""
    print("\n[*] Testando completion simples...")
    try:
        from core.llm_adapter import GeminiLLMAdapter
        from core.config.safe_settings import get_safe_settings

        settings = get_safe_settings()

        if not settings.GEMINI_API_KEY:
            print("[AVISO] Pulando teste de completion - API key nao configurada")
            return False

        adapter = GeminiLLMAdapter(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            enable_cache=True
        )

        # Fazer uma pergunta simples
        messages = [
            {"role": "user", "content": "Responda apenas com a palavra 'OK' se voce esta funcionando."}
        ]

        print("[*] Enviando mensagem de teste...")
        response = adapter.get_completion(
            messages=messages,
            temperature=0,
            max_tokens=10,
            stream=False
        )

        if "error" in response:
            print(f"[ERRO] Erro na resposta: {response['error']}")
            if response.get("fallback_activated"):
                print(f"[INFO] Fallback ativado: {response.get('retry_with')}")
            return False

        content = response.get("content", "")
        print(f"[OK] Resposta recebida: {content}")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao testar completion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_page_syntax():
    """Testa se a página tem erros de sintaxe"""
    print("\n[*] Testando sintaxe da pagina...")
    try:
        page_path = os.path.join(os.path.dirname(__file__), '..', 'pages', '10_🤖_Gemini_Playground.py')

        with open(page_path, 'r', encoding='utf-8') as f:
            code = f.read()

        compile(code, page_path, 'exec')
        print("[OK] Pagina sem erros de sintaxe")

        return True
    except SyntaxError as e:
        print(f"[ERRO] Erro de sintaxe na pagina: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao verificar pagina: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DO GEMINI PLAYGROUND")
    print("=" * 60)

    results = []

    # Teste 1: Imports
    results.append(("Imports", test_imports()))

    # Teste 2: Settings
    results.append(("Settings", test_settings()))

    # Teste 3: Sintaxe da página
    results.append(("Sintaxe da Pagina", test_page_syntax()))

    # Teste 4: Adapter
    results.append(("GeminiLLMAdapter", test_gemini_adapter()))

    # Teste 5: Completion (opcional - pode consumir créditos)
    print("\n[AVISO] O proximo teste fara uma chamada real a API do Gemini.")
    user_input = input("Deseja executar o teste de completion? (s/n): ")

    if user_input.lower() == 's':
        results.append(("Completion Simples", test_simple_completion()))
    else:
        print("[INFO] Teste de completion pulado")
        results.append(("Completion Simples", None))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for name, result in results:
        if result is True:
            status = "[OK] PASSOU"
        elif result is False:
            status = "[ERRO] FALHOU"
        else:
            status = "[INFO] PULADO"

        print(f"{name:.<30} {status}")

    # Resultado final
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)

    print("\n" + "=" * 60)
    print(f"Passou: {passed} | Falhou: {failed} | Pulado: {skipped}")

    if failed == 0 and passed > 0:
        print("\nTODOS OS TESTES PASSARAM! O Playground esta pronto para uso.")
    elif failed > 0:
        print("\nAlguns testes falharam. Verifique os erros acima.")

    print("=" * 60)

if __name__ == "__main__":
    main()
