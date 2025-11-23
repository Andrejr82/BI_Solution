# Modelos Gemini Disponiveis - Janeiro 2025
# Baseado em pesquisa oficial do Google

GEMINI_MODELS = {
    "Gemini 2.5": [
        "gemini-2.5-pro",           # Modelo avancado de raciocínio
        "gemini-2.5-flash",          # Rapido e eficiente
        "models/gemini-2.5-pro",
        "models/gemini-2.5-flash",
    ],
    
    "Gemini 2.0": [
        "gemini-2.0-flash",          # Disponivel geralmente
        "gemini-2.0-flash-exp",      # Experimental (gratuito)
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-exp",
    ],
    
    "Gemini 1.5": [
        "gemini-1.5-pro",            # Mid-size multimodal
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",          # Rapido e eficiente
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",       # Variante menor
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
    ],
    
    "Gemini 1.0": [
        "gemini-pro",                # Modelo base
        "gemini-pro-vision",         # Com visao
        "models/gemini-pro",
    ]
}

# Testar todos
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    print("[ERROR] No API key")
    exit(1)

print(f"[INFO] Testing with key: {api_key[:10]}...{api_key[-5:]}")
print(f"[INFO] Total models to test: {sum(len(v) for v in GEMINI_MODELS.values())}")
print()

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

working = []
failed = {}

for category, models in GEMINI_MODELS.items():
    print(f"\n{'='*60}")
    print(f"{category}")
    print(f"{'='*60}")
    
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "OK"}],
                max_tokens=5,
                temperature=0.0
            )
            content = response.choices[0].message.content
            print(f"  [OK] {model}")
            working.append(model)
        except Exception as e:
            error_str = str(e)
            if "404" in error_str:
                failed[model] = "NOT_FOUND"
                print(f"  [404] {model}")
            elif "400" in error_str:
                failed[model] = "BAD_REQUEST"
                print(f"  [400] {model}")
            else:
                failed[model] = "ERROR"
                print(f"  [ERR] {model}")

print(f"\n{'='*60}")
print("RESUMO")
print(f"{'='*60}")
print(f"\n[INFO] Modelos funcionando: {len(working)}")
for m in working:
    print(f"  - {m}")

print(f"\n[INFO] Modelos com erro: {len(failed)}")
if len(failed) <= 10:
    for m, err in failed.items():
        print(f"  - {m} ({err})")

print(f"\n[RECOMENDACAO] Use um destes modelos:")
if working:
    for m in working[:3]:
        print(f"  {m}")
