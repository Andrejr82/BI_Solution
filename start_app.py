#!/usr/bin/env python
"""
Agent_BI - Inicializador Multiplataforma
Inicia Backend (FastAPI) e Frontend (Streamlit) em ordem correta
"""
import subprocess
import sys
import time
import platform
import os
from pathlib import Path

# Cores para terminal (opcional)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Exibe cabeçalho da aplicação."""
    print("\n" + "="*50)
    print("   AGENT_BI - AGENTE DE NEGÓCIOS")
    print("="*50 + "\n")

def check_file_exists(filepath: str) -> bool:
    """Verifica se arquivo existe."""
    return Path(filepath).exists()

def check_backend_health(delay: int = 5) -> bool:
    """Aguarda backend inicializar."""
    time.sleep(delay)
    return True

def start_process(command: list, window_title: str = None) -> subprocess.Popen:
    """Inicia processo em segundo plano."""
    system = platform.system()

    if system == "Windows":
        if window_title:
            # Windows com título de janela
            cmd = ["start", window_title, "cmd", "/k"] + command
            return subprocess.Popen(" ".join(cmd), shell=True)
        else:
            return subprocess.Popen(command, shell=True)
    else:
        # Linux/macOS
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    """Função principal."""
    print_header()

    # Verificar arquivos necessários
    if not check_file_exists("streamlit_app.py"):
        print(f"[ERRO] Arquivo streamlit_app.py não encontrado!")
        print("Execute este script na raiz do projeto.")
        sys.exit(1)

    # Verificar ambiente virtual
    venv_path = ".venv/Scripts/activate" if platform.system() == "Windows" else ".venv/bin/activate"
    if not check_file_exists(venv_path.split('/')[0]):
        print(f"[ERRO] Ambiente virtual não encontrado!")
        print("Execute: python -m venv .venv")
        sys.exit(1)

    # Determinar comandos baseado no sistema
    system = platform.system()
    python_cmd = sys.executable

    # Verificar se backend FastAPI separado existe (modo opcional)
    backend_exists = check_file_exists("main.py")
    backend_process = None

    if backend_exists:
        # Iniciar backend em background (sem nova janela)
        backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Aguardar backend estar pronto
        time.sleep(3)
        check_backend_health()

    # Mensagem de sucesso
    print("\n" + "="*50)
    print("   APLICAÇÃO INICIADA COM SUCESSO!")
    print("")
    print("   Acesse: http://localhost:8501")
    print("")
    print("   Pressione Ctrl+C para encerrar")
    print("="*50 + "\n")

    # Executar Streamlit na mesma janela (foreground)
    try:
        result = subprocess.run(
            [python_cmd, "-m", "streamlit", "run", "streamlit_app.py"],
            check=False,
            capture_output=False,
            text=True
        )

        # Se Streamlit encerrou com erro
        if result.returncode != 0:
            print(f"\n[ERRO] Streamlit encerrou com código: {result.returncode}")
            input("\nPressione ENTER para sair...")
    except KeyboardInterrupt:
        print("\n\nEncerrando aplicação...")
    except Exception as e:
        print(f"\n[ERRO] Falha ao iniciar Streamlit: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")

    # Encerrar backend ao sair
    if backend_process:
        backend_process.terminate()

    print("\nAplicação encerrada com sucesso!")
    sys.exit(0)

if __name__ == "__main__":
    main()
