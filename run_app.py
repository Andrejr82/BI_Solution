#!/usr/bin/env python3
"""
Script de Inicialização - Agent Solution BI
Inicia a aplicação Streamlit (com backend integrado)
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Função principal"""
    print("=" * 70)
    print("  Agent Solution BI - Sistema de Análise Inteligente")
    print("=" * 70)
    print()

    # Verificar se streamlit_app.py existe
    if not Path("streamlit_app.py").exists():
        print("ERRO: Arquivo streamlit_app.py nao encontrado!")
        sys.exit(1)

    # Verificar se .env existe
    if not Path(".env").exists():
        print("AVISO: Arquivo .env nao encontrado")
        print("       Copie .env.example para .env e configure suas chaves de API")
        print()

    print("Iniciando aplicacao...")
    print()
    print("  Acesse: http://localhost:8501")
    print("  Pressione Ctrl+C para encerrar")
    print()
    print("=" * 70)
    print()

    try:
        # Executar Streamlit
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nAplicacao encerrada pelo usuario")
    except subprocess.CalledProcessError as e:
        print(f"\nERRO ao executar Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nERRO: Streamlit nao esta instalado")
        print("Instale com: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
