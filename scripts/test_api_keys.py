"""
Script para testar e validar API keys do Gemini e DeepSeek
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_gemini_key():
    """Testa se a chave do Gemini é válida"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip('"').strip("'")

    if not api_key or api_key == "sua_chave_gemini_aqui":
        return {"valid": False, "error": "Chave não configurada", "api_key": "***"}

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=10
        )

        return {
            "valid": True,
            "message": "✅ Chave Gemini VÁLIDA",
            "model": "gemini-2.5-flash",
            "api_key": api_key[:10] + "***"
        }
    except Exception as e:
        error_msg = str(e)

        if "expired" in error_msg.lower():
            return {
                "valid": False,
                "error": "❌ Chave EXPIRADA - Gere nova chave em https://aistudio.google.com/apikey",
                "api_key": api_key[:10] + "***"
            }
        elif "invalid" in error_msg.lower() or "400" in error_msg:
            return {
                "valid": False,
                "error": f"❌ Chave INVÁLIDA: {error_msg}",
                "api_key": api_key[:10] + "***"
            }
        else:
            return {
                "valid": False,
                "error": f"❌ Erro ao validar: {error_msg}",
                "api_key": api_key[:10] + "***"
            }

def test_deepseek_key():
    """Testa se a chave do DeepSeek é válida"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip('"').strip("'")

    if not api_key or api_key == "sua_chave_deepseek_aqui":
        return {"valid": False, "error": "Chave não configurada", "api_key": "***"}

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=10
        )

        return {
            "valid": True,
            "message": "✅ Chave DeepSeek VÁLIDA",
            "model": "deepseek-chat",
            "api_key": api_key[:10] + "***"
        }
    except Exception as e:
        error_msg = str(e)

        if "invalid" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            return {
                "valid": False,
                "error": f"❌ Chave INVÁLIDA: {error_msg}",
                "api_key": api_key[:10] + "***"
            }
        else:
            return {
                "valid": False,
                "error": f"❌ Erro ao validar: {error_msg}",
                "api_key": api_key[:10] + "***"
            }

if __name__ == "__main__":
    print("=" * 60)
    print("🔑 VALIDAÇÃO DE API KEYS")
    print("=" * 60)

    print("\n[1/2] Testando Gemini...")
    gemini_result = test_gemini_key()
    if gemini_result["valid"]:
        print(f"  {gemini_result['message']}")
        print(f"  Modelo: {gemini_result['model']}")
    else:
        print(f"  {gemini_result['error']}")
    print(f"  Chave: {gemini_result['api_key']}")

    print("\n[2/2] Testando DeepSeek...")
    deepseek_result = test_deepseek_key()
    if deepseek_result["valid"]:
        print(f"  {deepseek_result['message']}")
        print(f"  Modelo: {deepseek_result['model']}")
    else:
        print(f"  {deepseek_result['error']}")
    print(f"  Chave: {deepseek_result['api_key']}")

    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)

    gemini_ok = gemini_result["valid"]
    deepseek_ok = deepseek_result["valid"]

    if gemini_ok and deepseek_ok:
        print("✅ Ambas as chaves estão VÁLIDAS - Sistema operacional!")
    elif deepseek_ok:
        print("⚠️  Apenas DeepSeek válida - Sistema funcionará com fallback")
    elif gemini_ok:
        print("⚠️  Apenas Gemini válida - Sem fallback disponível")
    else:
        print("❌ NENHUMA chave válida - Sistema NÃO funcionará!")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        if not gemini_ok:
            print("  1. Gere nova chave Gemini em: https://aistudio.google.com/apikey")
        if not deepseek_ok:
            print("  2. Gere nova chave DeepSeek em: https://platform.deepseek.com/api_keys")
        print("  3. Atualize o arquivo .env com as novas chaves")

    print("=" * 60)
