"""
Teste rápido de API do Gemini
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TESTE RAPIDO - API GEMINI")
print("=" * 70)

# 1. Testar import de configurações
print("\n[1] Testando imports...")
try:
    from core.config.settings import get_settings
    print("    [OK] Modulo de configuracoes")
except Exception as e:
    print(f"    [ERRO] {e}")
    sys.exit(1)

# 2. Carregar API key
print("\n[2] Carregando API key...")
try:
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY
    if api_key and len(api_key) > 10:
        masked = api_key[:10] + "..." + api_key[-4:]
        print(f"    [OK] Chave encontrada: {masked}")
    else:
        print("    [ERRO] Chave nao encontrada ou invalida!")
        sys.exit(1)
except Exception as e:
    print(f"    [ERRO] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Criar adaptador
print("\n[3] Criando adaptador LLM...")
try:
    from core.llm_adapter import GeminiLLMAdapter
    adapter = GeminiLLMAdapter(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp",
        temperature=0.7,
        enable_cache=False
    )
    print("    [OK] Adaptador criado")
except Exception as e:
    print(f"    [ERRO] {e}")
    sys.exit(1)

# 4. Testar chamada simples
print("\n[4] Testando API...")
print("    Enviando: 'Ola! Responda apenas: API OK'")

try:
    response = adapter.get_completion(
        messages=[{"role": "user", "content": "Ola! Responda apenas: API OK"}],
        temperature=0.0,
        max_tokens=50
    )

    # Verificar erro
    if response.get("error"):
        print(f"\n    [ERRO] API retornou erro:")
        print(f"    Tipo: {response.get('error')}")

        if response.get("user_message"):
            print(f"\n    Mensagem para usuario:")
            print("    " + "-" * 60)
            for line in response.get("user_message").split("\n"):
                print(f"    {line}")
            print("    " + "-" * 60)
        sys.exit(1)

    # Verificar resposta
    content = response.get("content", "")
    if content:
        print(f"\n    [OK] Resposta recebida ({len(content)} caracteres)")
        print(f"    Conteudo: '{content}'")
    else:
        print("\n    [ERRO] Resposta vazia!")
        sys.exit(1)

except Exception as e:
    print(f"\n    [ERRO] Excecao: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Sucesso!
print("\n" + "=" * 70)
print("[SUCESSO] API DO GEMINI FUNCIONANDO!")
print("=" * 70)
print("\nA interface esta pronta para uso.")
print("Execute: streamlit run streamlit_app.py")
sys.exit(0)
