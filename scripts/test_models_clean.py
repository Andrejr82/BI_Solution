import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("[ERROR] API key nao encontrada")
    exit(1)

print(f"[KEY] Testando: {api_key[:10]}...{api_key[-5:]}")
print()

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Modelos que o usuario quer testar
desired_models = [
    "models/gemini-2.5-flash",
    "models/gemini-3-pro",
]

# Modelos alternativos
alternative_models = [
    "gemini-2.5-flash",
    "gemini-3-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

working_models = []

print("=" * 70)
print("TESTANDO MODELOS DESEJADOS")
print("=" * 70)

for model in desired_models:
    print(f"\n[TEST] {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "OK"}],
            max_tokens=10,
            temperature=0.0
        )
        content = response.choices[0].message.content
        print(f"   [OK] Funciona! Resposta: {content}")
        working_models.append(model)
    except Exception as e:
        if "404" in str(e):
            print(f"   [FAIL] Modelo nao encontrado (404)")
        elif "400" in str(e):
            print(f"   [FAIL] Erro 400: {str(e)[:100]}")
        else:
            print(f"   [FAIL] {str(e)[:100]}")

print("\n" + "=" * 70)
print("TESTANDO MODELOS ALTERNATIVOS")
print("=" * 70)

for model in alternative_models:
    print(f"\n[TEST] {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "OK"}],
            max_tokens=10,
            temperature=0.0
        )
        content = response.choices[0].message.content
        print(f"   [OK] Funciona! Resposta: {content}")
        if model not in working_models:
            working_models.append(model)
    except Exception as e:
        if "404" in str(e):
            print(f"   [FAIL] Modelo nao encontrado (404)")
        elif "400" in str(e):
            print(f"   [FAIL] Erro 400")
        else:
            print(f"   [FAIL] Erro")

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)

if working_models:
    print(f"\n[INFO] Modelos funcionando: {len(working_models)}")
    for m in working_models:
        if m in desired_models:
            print(f"   [DESIRED] {m}")
        else:
            print(f"   [ALTERNATIVE] {m}")
    
    print("\n[RECOMENDACAO]:")
    if "models/gemini-2.5-flash" in working_models and "models/gemini-3-pro" in working_models:
        print("   [OK] Use os modelos desejados!")
        print("   INTENT_CLASSIFICATION_MODEL=models/gemini-2.5-flash")
        print("   CODE_GENERATION_MODEL=models/gemini-3-pro")
    elif working_models:
        print(f"   INTENT_CLASSIFICATION_MODEL={working_models[0]}")
        print(f"   CODE_GENERATION_MODEL={working_models[0]}")
else:
    print("\n[ERROR] Nenhum modelo funcionou!")
