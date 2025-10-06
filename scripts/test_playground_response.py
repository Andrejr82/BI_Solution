"""
Teste para validar se o Gemini Playground retorna respostas corretamente
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 60)
print("TESTE DE RESPOSTA DO GEMINI PLAYGROUND")
print("=" * 60)

# Importar componentes
print("\n[*] Importando componentes...")
try:
    from core.llm_adapter import GeminiLLMAdapter
    from core.config.safe_settings import get_safe_settings
    print("[OK] Componentes importados")
except Exception as e:
    print(f"[ERRO] Falha ao importar: {e}")
    sys.exit(1)

# Carregar configurações
print("\n[*] Carregando configurações...")
try:
    settings = get_safe_settings()
    gemini_model = getattr(settings, 'GEMINI_MODEL_NAME', settings.LLM_MODEL_NAME)
    print(f"[OK] Modelo: {gemini_model}")
except Exception as e:
    print(f"[ERRO] Falha ao carregar settings: {e}")
    sys.exit(1)

# Inicializar adaptador
print("\n[*] Inicializando adaptador...")
try:
    gemini = GeminiLLMAdapter(
        api_key=settings.GEMINI_API_KEY,
        model_name=gemini_model,
        enable_cache=True
    )
    print("[OK] Adaptador inicializado")
except Exception as e:
    print(f"[ERRO] Falha ao inicializar: {e}")
    sys.exit(1)

# Teste 1: Resposta simples
print("\n[*] Teste 1: Resposta simples")
print("-" * 60)
try:
    messages = [
        {"role": "user", "content": "Responda apenas 'Funcionando' se você consegue me ouvir."}
    ]

    response = gemini.get_completion(
        messages=messages,
        temperature=0,
        max_tokens=50,
        json_mode=False,
        stream=False
    )

    print(f"Response type: {type(response)}")
    print(f"Response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")

    if "error" in response:
        print(f"[ERRO] API retornou erro: {response['error']}")
    else:
        content = response.get("content", "")
        print(f"[OK] Resposta recebida: '{content}'")

        if not content:
            print("[AVISO] Conteúdo está vazio!")
        elif content == "None":
            print("[ERRO] Conteúdo é a string 'None'!")
        else:
            print("[OK] Conteúdo válido recebido")

except Exception as e:
    print(f"[ERRO] Exceção durante teste: {e}")
    import traceback
    traceback.print_exc()

# Teste 2: Query SQL (como no exemplo do usuário)
print("\n[*] Teste 2: Query SQL")
print("-" * 60)
try:
    messages = [
        {"role": "user", "content": "Crie uma query SQL para calcular o total de vendas por categoria nos últimos 30 dias."}
    ]

    response = gemini.get_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
        json_mode=False,
        stream=False
    )

    print(f"Response type: {type(response)}")

    if "error" in response:
        print(f"[ERRO] API retornou erro: {response['error']}")
    else:
        content = response.get("content", "")

        if not content:
            print("[ERRO] Resposta vazia!")
        else:
            print(f"[OK] Resposta recebida ({len(content)} caracteres)")
            print("\n--- PREVIEW DA RESPOSTA ---")
            print(content[:200] + "..." if len(content) > 200 else content)
            print("--- FIM DO PREVIEW ---\n")

except Exception as e:
    print(f"[ERRO] Exceção durante teste: {e}")
    import traceback
    traceback.print_exc()

# Teste 3: Verificar se None está sendo retornado
print("\n[*] Teste 3: Verificar valor None")
print("-" * 60)
try:
    messages = [
        {"role": "user", "content": "Diga 'teste' apenas."}
    ]

    response = gemini.get_completion(
        messages=messages,
        temperature=0,
        max_tokens=10,
        json_mode=False,
        stream=False
    )

    content = response.get("content", "")

    print(f"Tipo de content: {type(content)}")
    print(f"Valor de content: {repr(content)}")
    print(f"Content is None: {content is None}")
    print(f"Content == 'None': {content == 'None'}")
    print(f"Content vazio: {not content}")

    if content is None:
        print("[ERRO] content é None (objeto Python)")
    elif content == "None":
        print("[ERRO] content é 'None' (string)")
    elif not content:
        print("[ERRO] content está vazio")
    else:
        print(f"[OK] content válido: '{content}'")

except Exception as e:
    print(f"[ERRO] Exceção: {e}")

print("\n" + "=" * 60)
print("TESTES CONCLUÍDOS")
print("=" * 60)
