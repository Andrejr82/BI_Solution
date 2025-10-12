"""
Teste Rápido - Validar API Key do Gemini

Testa apenas se a chave do Gemini está válida e funcionando.
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def test_gemini_key():
    """Testa se a API Key do Gemini está válida."""
    print("=" * 70)
    print("  TESTE RAPIDO - API KEY GEMINI")
    print("=" * 70)
    print()

    # Verificar se a chave está configurada
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not gemini_key:
        print("[ERRO] Gemini API Key nao esta configurada no .env")
        return False

    print(f"[INFO] Chave encontrada: {gemini_key[:30]}...")
    print()

    # Testar a chave
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        print("[INFO] Enviando teste simples para o Gemini...")

        response = client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=10
        )

        resposta = response.choices[0].message.content

        print()
        print("=" * 70)
        print("[SUCESSO] API KEY VALIDA!")
        print("=" * 70)
        print(f"Resposta do Gemini: '{resposta}'")
        print()
        print("A chave esta funcionando corretamente!")
        print()
        return True

    except Exception as e:
        error_msg = str(e).lower()

        print()
        print("=" * 70)
        print("[ERRO] API KEY INVALIDA OU EXPIRADA")
        print("=" * 70)
        print()

        if "expired" in error_msg or "invalid" in error_msg:
            print("Problema: A chave do Gemini esta EXPIRADA ou INVALIDA")
            print()
            print("Solucao:")
            print("1. Acesse: https://aistudio.google.com/app/apikey")
            print("2. Revogue a chave antiga")
            print("3. Crie uma NOVA chave")
            print("4. Copie a nova chave")
            print("5. Cole no arquivo .env na linha GEMINI_API_KEY")
            print()
        elif "quota" in error_msg or "limit" in error_msg:
            print("Problema: Quota ou limite da API atingido")
            print()
            print("Solucao:")
            print("1. Aguarde alguns minutos")
            print("2. Ou gere uma nova chave em outro projeto")
            print()
        else:
            print(f"Erro desconhecido: {str(e)[:200]}")
            print()

        return False

if __name__ == "__main__":
    try:
        success = test_gemini_key()

        if success:
            print("[INFO] Execute agora o teste completo:")
            print("       python scripts/test_gemini_complete.py")
            sys.exit(0)
        else:
            print("[AVISO] Corrija a chave antes de executar testes completos")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
