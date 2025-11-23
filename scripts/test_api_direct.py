import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key or api_key == "COLE_SUA_NOVA_CHAVE_AQUI":
    print("❌ API key não configurada corretamente no .env")
    exit(1)

print(f"🔑 Testando API key: {api_key[:10]}...{api_key[-5:]}")
print(f"📊 Modelo: models/gemini-2.5-flash")
print()

try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    print("📡 Fazendo chamada de teste à API...")
    response = client.chat.completions.create(
        model="models/gemini-2.5-flash",
        messages=[{"role": "user", "content": "Diga apenas 'OK'"}],
        max_tokens=10,
        temperature=0.0
    )
    
    content = response.choices[0].message.content
    print(f"✅ SUCESSO! Resposta da API: '{content}'")
    print()
    print("🎉 A chave está funcionando corretamente!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    print()
    print("Possíveis causas:")
    print("1. A chave foi revogada ou expirou")
    print("2. A chave não tem permissões para usar a API Gemini")
    print("3. A API Gemini OpenAI compatibility não está habilitada")
    print()
    print("Solução:")
    print("- Gere uma NOVA chave em: https://aistudio.google.com/app/apikey")
    print("- Certifique-se de que a chave tem acesso à API Gemini")
    print("- Cole a nova chave no arquivo .env")
