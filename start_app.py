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
import requests
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
    print("   Inicializando aplicação...")
    print("="*50 + "\n")

def check_file_exists(filepath: str) -> bool:
    """Verifica se arquivo existe."""
    return Path(filepath).exists()

def check_backend_health(max_attempts: int = 30, delay: int = 2) -> bool:
    """Verifica se backend está pronto via health check."""
    print(f"[3/4] Aguardando Backend inicializar...")

    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=1)
            if response.status_code == 200:
                print(f"   - Backend pronto! [OK]")
                return True
        except requests.exceptions.RequestException:
            print(f"   - Tentativa {attempt + 1}/{max_attempts}...", end='\r')
            time.sleep(delay)

    print(f"\n   [AVISO] Backend não respondeu após {max_attempts * delay}s")
    return False

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

    print("[1/4] Ambiente virtual detectado [OK]")

    # Determinar comandos baseado no sistema
    system = platform.system()
    python_cmd = sys.executable

    # Verificar se backend existe
    backend_exists = check_file_exists("main.py")
    backend_process = None

    if backend_exists:
        print("[2/4] Iniciando Backend FastAPI...")

        if system == "Windows":
            backend_cmd = f'"{python_cmd}" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload'
            backend_process = start_process(backend_cmd.split(), "Agent_BI - Backend")
        else:
            backend_process = start_process([
                python_cmd, "-m", "uvicorn",
                "main:app", "--host", "0.0.0.0",
                "--port", "8000", "--reload"
            ])

        # Aguardar backend estar pronto
        time.sleep(3)
        backend_ready = check_backend_health()

        if not backend_ready:
            print("   [AVISO] Continuando sem confirmação do backend...")
    else:
        print("[2/4] Backend FastAPI não encontrado. Pulando...")

    # Iniciar Frontend Streamlit
    print("[4/4] Iniciando Frontend Streamlit...")
    time.sleep(1)

    if system == "Windows":
        frontend_cmd = f'"{python_cmd}" -m streamlit run streamlit_app.py'
        frontend_process = start_process(frontend_cmd.split(), "Agent_BI - Frontend")
    else:
        frontend_process = start_process([
            python_cmd, "-m", "streamlit",
            "run", "streamlit_app.py"
        ])

    # Aguardar um pouco para frontend iniciar
    time.sleep(3)

    # Mensagem de sucesso
    print("\n" + "="*50)
    print("   APLICAÇÃO INICIADA COM SUCESSO!")
    print("")
    if backend_exists:
        print("   Backend:  http://localhost:8000")
        print("   Docs API: http://localhost:8000/docs")
    print("   Frontend: http://localhost:8501")
    print("")
    print("   Para encerrar: Ctrl+C neste terminal")
    print("="*50 + "\n")

    # Manter script rodando
    try:
        print("Pressione Ctrl+C para encerrar a aplicação...\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nEncerrando aplicação...")

        # Encerrar processos
        if backend_process:
            backend_process.terminate()
            print("   - Backend encerrado")

        if frontend_process:
            frontend_process.terminate()
            print("   - Frontend encerrado")

        print("\nAplicação encerrada com sucesso!")
        sys.exit(0)

if __name__ == "__main__":
    main()
