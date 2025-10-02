"""
Teste para verificar se o GeminiLLMAdapter está usando a URL correta
"""
import sys
from core.llm_adapter import GeminiLLMAdapter, DeepSeekLLMAdapter

def test_gemini_base_url():
    """Verifica se Gemini usa base_url correta"""
    print("=" * 80)
    print("TESTE: GeminiLLMAdapter Base URL")
    print("=" * 80)

    try:
        # Criar adapter com API key fake (não vai fazer chamada real)
        adapter = GeminiLLMAdapter(
            api_key="AIzaSyDummy_Test_Key",
            model_name="gemini-2.5-flash",
            enable_cache=False
        )

        # Verificar base_url
        base_url = adapter.client.base_url
        print(f"\nBase URL configurada: {base_url}")

        # Verificar se é a URL correta do Gemini
        expected_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        if str(base_url) == expected_url:
            print("\nOK: Gemini usando base_url CORRETA")
            return True
        else:
            print(f"\nERRO: Base URL incorreta!")
            print(f"Esperado: {expected_url}")
            print(f"Obtido:   {base_url}")
            return False

    except Exception as e:
        print(f"\nERRO ao criar adapter: {e}")
        return False

def test_deepseek_base_url():
    """Verifica se DeepSeek usa base_url correta"""
    print("\n" + "=" * 80)
    print("TESTE: DeepSeekLLMAdapter Base URL")
    print("=" * 80)

    try:
        # Criar adapter com API key fake
        adapter = DeepSeekLLMAdapter(
            api_key="sk-dummy_test_key",
            model_name="deepseek-chat",
            enable_cache=False
        )

        # Verificar base_url
        base_url = adapter.client.base_url
        print(f"\nBase URL configurada: {base_url}")

        # Verificar se é a URL correta do DeepSeek (com ou sem trailing slash)
        expected_url = "https://api.deepseek.com/v1"

        if str(base_url).rstrip('/') == expected_url:
            print("\nOK: DeepSeek usando base_url CORRETA")
            return True
        else:
            print(f"\nERRO: Base URL incorreta!")
            print(f"Esperado: {expected_url}")
            print(f"Obtido:   {base_url}")
            return False

    except Exception as e:
        print(f"\nERRO ao criar adapter: {e}")
        return False

if __name__ == "__main__":
    print("\nINICIANDO TESTES DE LLM ADAPTERS\n")

    test1_ok = test_gemini_base_url()
    test2_ok = test_deepseek_base_url()

    print("\n" + "=" * 80)
    print("RESULTADO DOS TESTES")
    print("=" * 80)
    print(f"GeminiLLMAdapter:   {'PASSOU' if test1_ok else 'FALHOU'}")
    print(f"DeepSeekLLMAdapter: {'PASSOU' if test2_ok else 'FALHOU'}")
    print("=" * 80)

    if test1_ok and test2_ok:
        print("\nTODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\nALGUNS TESTES FALHARAM!")
        sys.exit(1)
