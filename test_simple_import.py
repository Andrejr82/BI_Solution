#!/usr/bin/env python3
"""
Teste simples de importação para verificar se streamlit_app.py funciona
"""

import os
import sys

def test_import():
    print("TESTE DE IMPORTACAO STREAMLIT_APP")
    print("=" * 40)

    # Limpar env vars para simular Streamlit Cloud
    env_vars = ['DB_SERVER', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'OPENAI_API_KEY']
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    print("Variaveis de ambiente limpas")

    try:
        print("Tentando importar streamlit_app...")
        import streamlit_app
        print("SUCESSO: streamlit_app importado!")
        return True

    except Exception as e:
        print(f"ERRO: {e}")
        print(f"Tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import()
    sys.exit(0 if success else 1)