import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key or api_key == "COLE_SUA_NOVA_CHAVE_AQUI":
    print("❌ API key não configurada corretamente no .env")
    exit(1)

print(f"🔑 Testando API key: {api_key[:10]}...{api_key[-5:]}\n")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Try different model names
models_to_try = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

working_model = None

for model in models_to_try:
    print(f"📡 Testando modelo: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=50,
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ SUCESSO! Resposta: '{content}'")
        working_model = model
        break
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"   ❌ Modelo não encontrado")
        elif "400" in error_msg:
            print(f"   ❌ Requisição inválida: {error_msg[:80]}")
        else:
            print(f"   ❌ Erro: {error_msg[:80]}")

if working_model:
    print(f"\n🎉 Modelo funcionando: {working_model}")
    print(f"\n💡 Atualize o .env com:")
    print(f"   INTENT_CLASSIFICATION_MODEL={working_model}")
    print(f"   CODE_GENERATION_MODEL={working_model}")
else:
    print("\n❌ Nenhum modelo funcionou")
    print("\nPossíveis soluções:")
    print("1. Verifique se a chave tem acesso à API Gemini")
    print("2. Gere uma nova chave em: https://aistudio.google.com/app/apikey")
    print("3. Certifique-se de habilitar 'Gemini API' para a chave")
