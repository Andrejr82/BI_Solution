"""
Módulo para tests/test_api_key.py. Fornece as funções: test_gemini_api_key.
"""


import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_adapter import GeminiLLMAdapter

def test_gemini_api_key():
    """Verifica se a chave da API do Gemini é válida."""
    print("=" * 80)
    print("TESTE: Validação da Chave da API do Gemini")
    print("=" * 80)

    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "sua_chave_gemini_aqui":
        print("\nERRO: A chave da API do Gemini não foi encontrada ou não foi alterada no arquivo .env")
        print("Por favor, adicione sua chave de API ao arquivo .env")
        return False

    print(f"\nChave da API encontrada. Iniciando teste de chamada...")

    try:
        adapter = GeminiLLMAdapter(api_key=api_key, model_name="gemini-2.5-flash-lite")
        messages = [{"role": "user", "content": "Olá!"}]
        response = adapter.get_completion(messages)

        if "error" in response:
            print(f"\nERRO ao chamar a API: {response['error']}")
            return False
        else:
            print("\nOK: A chave da API do Gemini é válida e a chamada foi bem-sucedida.")
            print(f"Resposta do modelo: {response['content']}")
            return True

    except Exception as e:
        print(f"\nERRO inesperado ao testar a chave da API: {e}")
        return False

if __name__ == "__main__":
    if test_gemini_api_key():
        sys.exit(0)
    else:
        sys.exit(1)
