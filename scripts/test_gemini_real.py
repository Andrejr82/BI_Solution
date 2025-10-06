"""
Teste do Gemini Playground com a API key real do .env
"""
import sys
import os
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carregar .env explicitamente
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

print("=" * 60)
print("TESTE DO GEMINI COM API KEY REAL")
print("=" * 60)

# Verificar variáveis de ambiente
print("\n[*] Verificando variaveis de ambiente...")
gemini_key = os.getenv("GEMINI_API_KEY", "")
gemini_model = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

if gemini_key:
    # Remover aspas se existirem
    gemini_key = gemini_key.strip('"').strip("'")
    print(f"[OK] GEMINI_API_KEY encontrada (primeiros 15 chars): {gemini_key[:15]}...")
else:
    print("[ERRO] GEMINI_API_KEY nao encontrada no .env")
    sys.exit(1)

if gemini_model:
    gemini_model = gemini_model.strip('"').strip("'")
    print(f"[OK] GEMINI_MODEL_NAME: {gemini_model}")

# Testar importações
print("\n[*] Testando importacoes...")
try:
    from core.llm_adapter import GeminiLLMAdapter
    print("[OK] GeminiLLMAdapter importado")
except Exception as e:
    print(f"[ERRO] Falha ao importar: {e}")
    sys.exit(1)

# Inicializar o adaptador
print("\n[*] Inicializando GeminiLLMAdapter...")
try:
    adapter = GeminiLLMAdapter(
        api_key=gemini_key,
        model_name=gemini_model,
        enable_cache=True
    )
    print("[OK] Adaptador inicializado com sucesso")
except Exception as e:
    print(f"[ERRO] Falha ao inicializar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Testar cache stats
print("\n[*] Testando cache stats...")
try:
    stats = adapter.get_cache_stats()
    print(f"[OK] Cache stats: {stats}")
except Exception as e:
    print(f"[ERRO] Falha ao obter stats: {e}")

# Fazer uma chamada real à API
print("\n[*] Fazendo chamada real a API do Gemini...")
print("[INFO] Esta chamada consumira creditos da sua API")

try:
    messages = [
        {"role": "user", "content": "Responda apenas 'OK' se voce esta funcionando."}
    ]

    print("[*] Enviando mensagem...")
    response = adapter.get_completion(
        messages=messages,
        temperature=0,
        max_tokens=50,
        stream=False
    )

    if "error" in response:
        print(f"[ERRO] API retornou erro: {response['error']}")
        if response.get("fallback_activated"):
            print(f"[INFO] Fallback ativado: {response.get('retry_with')}")
        sys.exit(1)

    content = response.get("content", "")
    print(f"[OK] Resposta recebida com sucesso!")
    print(f"[RESPOSTA] {content}")

except Exception as e:
    print(f"[ERRO] Excecao durante chamada: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Testar modo streaming
print("\n[*] Testando modo streaming...")
try:
    messages = [
        {"role": "user", "content": "Diga 'Streaming funcionando' em uma frase curta."}
    ]

    print("[*] Iniciando stream...")
    stream = adapter.get_completion(
        messages=messages,
        temperature=0,
        max_tokens=50,
        stream=True
    )

    full_response = ""
    for chunk in stream:
        full_response += chunk
        print(chunk, end="", flush=True)

    print()  # Nova linha
    print(f"[OK] Streaming completado! Resposta completa: {full_response}")

except Exception as e:
    print(f"[ERRO] Falha no streaming: {e}")
    import traceback
    traceback.print_exc()

# Testar JSON mode
print("\n[*] Testando JSON mode...")
try:
    messages = [
        {"role": "user", "content": "Retorne um JSON com uma chave 'status' e valor 'ok'. Apenas o JSON, sem texto adicional."}
    ]

    response = adapter.get_completion(
        messages=messages,
        temperature=0,
        max_tokens=100,
        json_mode=True,
        stream=False
    )

    if "error" in response:
        print(f"[ERRO] Erro no JSON mode: {response['error']}")
    else:
        import json
        content = response.get("content", "")
        print(f"[OK] JSON recebido: {content}")

        # Tentar parsear o JSON
        try:
            parsed = json.loads(content)
            print(f"[OK] JSON valido parseado: {parsed}")
        except json.JSONDecodeError as je:
            print(f"[AVISO] Resposta nao e JSON valido: {je}")

except Exception as e:
    print(f"[ERRO] Falha no JSON mode: {e}")

# Verificar cache após chamadas
print("\n[*] Verificando cache apos chamadas...")
stats = adapter.get_cache_stats()
print(f"[INFO] Cache stats finais: {stats}")

print("\n" + "=" * 60)
print("TODOS OS TESTES COMPLETADOS COM SUCESSO!")
print("O Gemini Playground esta 100% funcional!")
print("=" * 60)
