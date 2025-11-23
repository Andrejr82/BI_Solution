import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("❌ API key não encontrada")
    exit(1)

print(f"🔑 Testando com chave: {api_key[:10]}...{api_key[-5:]}\n")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Modelos que o usuário quer testar
desired_models = [
    "models/gemini-2.5-flash",
    "models/gemini-3-pro",
]

# Modelos alternativos para testar
alternative_models = [
    "gemini-2.5-flash",
    "gemini-3-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
]

all_models = desired_models + alternative_models

working_models = []

print("=" * 70)
print("TESTANDO MODELOS DESEJADOS")
print("=" * 70)

for model in desired_models:
    print(f"\n📡 Testando: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=50,
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ FUNCIONANDO! Resposta: '{content}'")
        working_models.append(model)
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            print(f"   ❌ Modelo não encontrado (404)")
        elif "400" in error_str:
            if "expired" in error_str.lower():
                print(f"   ❌ Erro 400: API key issue")
            else:
                print(f"   ❌ Erro 400: {error_str[:80]}")
        else:
            print(f"   ❌ Erro: {error_str[:80]}")

print("\n" + "=" * 70)
print("TESTANDO MODELOS ALTERNATIVOS")
print("=" * 70)

for model in alternative_models:
    print(f"\n📡 Testando: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=50,
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ FUNCIONANDO! Resposta: '{content}'")
        if model not in working_models:
            working_models.append(model)
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            print(f"   ❌ Modelo não encontrado (404)")
        elif "400" in error_str:
            print(f"   ❌ Erro 400: {error_str[:80]}")
        else:
            print(f"   ❌ Erro: {error_str[:80]}")

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)

if working_models:
    print(f"\n✅ Modelos funcionando ({len(working_models)}):")
    for m in working_models:
        if m in desired_models:
            print(f"   🎯 {m} (DESEJADO)")
        else:
            print(f"   📌 {m}")
    
    print("\n💡 RECOMENDAÇÃO:")
    if "models/gemini-2.5-flash" in working_models and "models/gemini-3-pro" in working_models:
        print("   ✅ Use os modelos desejados!")
        print("   INTENT_CLASSIFICATION_MODEL=models/gemini-2.5-flash")
        print("   CODE_GENERATION_MODEL=models/gemini-3-pro")
    elif working_models:
        print(f"   Use: INTENT_CLASSIFICATION_MODEL={working_models[0]}")
        print(f"   Use: CODE_GENERATION_MODEL={working_models[0]}")
else:
    print("\n❌ Nenhum modelo funcionou!")
    print("   Verifique a chave de API")
