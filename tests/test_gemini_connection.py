"""
Teste de conexão com Gemini API
"""
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("=" * 60)
print("TESTE DE CONEXAO GEMINI")
print("=" * 60)

# Verificar variáveis de ambiente
api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

print(f"\nAPI Key presente: {'Sim' if api_key else 'Nao'}")
print(f"Base URL: {base_url}")

if not api_key:
    print("\nERRO: GEMINI_API_KEY nao encontrada no .env")
    exit(1)

# Testar conexão
print("\nTestando conexao com Gemini...")

try:
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    print("Cliente OpenAI criado com sucesso")

    # Fazer requisição simples
    print("\nEnviando requisicao de teste...")
    import time
    start = time.time()

    # Usar modelo configurado no .env
    model = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash-exp")
    print(f"Modelo: {model}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Responda apenas: OK"}
        ],
        max_tokens=10,
        temperature=0
    )

    elapsed = time.time() - start

    print(f"\nResposta recebida em {elapsed:.2f}s:")
    print(f"Modelo: {response.model}")
    print(f"Conteudo: {response.choices[0].message.content}")
    print(f"Tokens usados: {response.usage.total_tokens}")

    print("\n" + "=" * 60)
    print("STATUS: GEMINI FUNCIONANDO!")
    print("=" * 60)

except Exception as e:
    print(f"\nERRO ao conectar com Gemini:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")

    if "503" in str(e):
        print("\nSTATUS: GEMINI SOBRECARREGADO (503)")
        print("Aguarde alguns minutos e tente novamente.")
    elif "401" in str(e):
        print("\nSTATUS: API KEY INVALIDA (401)")
    elif "429" in str(e):
        print("\nSTATUS: RATE LIMIT (429)")
    else:
        print(f"\nSTATUS: ERRO DESCONHECIDO")

    print("=" * 60)
