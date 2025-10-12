"""
Script para testar diferentes modelos do Gemini
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_gemini_model(model_name):
    """Testa um modelo específico do Gemini"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip('"').strip("'")

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=10
        )

        content = response.choices[0].message.content
        return {
            "valid": True,
            "model": model_name,
            "response": content,
            "message": f"✅ Modelo {model_name} funcionando"
        }
    except Exception as e:
        error_msg = str(e)
        return {
            "valid": False,
            "model": model_name,
            "error": error_msg,
            "message": f"❌ Modelo {model_name} FALHOU"
        }

if __name__ == "__main__":
    models_to_test = [
        "gemini-2.5-flash",        # Modelo configurado no .env
        "gemini-2.5-flash-lite",   # Modelo usado no log de erro
        "gemini-1.5-flash",        # Modelo alternativo
        "gemini-1.5-pro"           # Modelo mais potente
    ]

    print("=" * 60)
    print("TESTANDO MODELOS GEMINI DISPONÍVEIS")
    print("=" * 60)

    results = []
    for model in models_to_test:
        print(f"\n[TESTE] {model}...")
        result = test_gemini_model(model)
        results.append(result)

        if result["valid"]:
            print(f"  {result['message']}")
            print(f"  Resposta: {result['response']}")
        else:
            print(f"  {result['message']}")
            print(f"  Erro: {result['error'][:100]}")

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)

    valid_models = [r for r in results if r["valid"]]
    invalid_models = [r for r in results if not r["valid"]]

    if valid_models:
        print(f"\n✅ Modelos funcionando ({len(valid_models)}):")
        for r in valid_models:
            print(f"  - {r['model']}")

    if invalid_models:
        print(f"\n❌ Modelos com erro ({len(invalid_models)}):")
        for r in invalid_models:
            print(f"  - {r['model']}")

    print("\n" + "=" * 60)
