#!/usr/bin/env python3
"""
Script de Inicialização - Agent Solution BI
Inicia Backend (FastAPI) e Frontend (Streamlit)
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# Processos em execução
processes = []

def signal_handler(sig, frame):
    """Handler para Ctrl+C - encerra todos os processos"""
    print("\n\n🛑 Encerrando aplicação...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_port(port):
    """Verifica se uma porta está disponível"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True se porta está livre

def start_backend():
    """Inicia o backend FastAPI"""
    print("🔧 Iniciando Backend (FastAPI)...")

    if not check_port(8000):
        print("⚠️  Porta 8000 já está em uso")
        response = input("Tentar iniciar mesmo assim? (s/n): ")
        if response.lower() != 's':
            return None

    try:
        # Executar FastAPI (uvicorn)
        proc = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Aguardar backend inicializar
        print("   Aguardando backend inicializar...", end='', flush=True)
        time.sleep(3)

        if proc.poll() is None:
            print(" ✅")
            print("   Backend rodando em http://localhost:8000")
            return proc
        else:
            print(" ❌")
            print("   Erro ao iniciar backend")
            return None

    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o frontend Streamlit"""
    print("\n🎨 Iniciando Frontend (Streamlit)...")

    if not check_port(8501):
        print("⚠️  Porta 8501 já está em uso")
        response = input("Tentar iniciar mesmo assim? (s/n): ")
        if response.lower() != 's':
            return None

    try:
        # Executar Streamlit
        proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
             "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print("   Aguardando frontend inicializar...", end='', flush=True)
        time.sleep(5)

        if proc.poll() is None:
            print(" ✅")
            print("   Frontend rodando em http://localhost:8501")
            return proc
        else:
            print(" ❌")
            print("   Erro ao iniciar frontend")
            return None

    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def main():
    """Função principal"""
    print("=" * 70)
    print("  🚀 Agent Solution BI - Sistema de Análise Inteligente")
    print("=" * 70)
    print()

    # Verificar se arquivos existem
    if not Path("main.py").exists():
        print("❌ Arquivo main.py não encontrado!")
        sys.exit(1)

    if not Path("streamlit_app.py").exists():
        print("❌ Arquivo streamlit_app.py não encontrado!")
        sys.exit(1)

    # Iniciar backend
    backend = start_backend()
    if backend:
        processes.append(backend)
    else:
        print("\n❌ Não foi possível iniciar o backend")
        sys.exit(1)

    # Iniciar frontend
    frontend = start_frontend()
    if frontend:
        processes.append(frontend)
    else:
        print("\n❌ Não foi possível iniciar o frontend")
        if backend:
            backend.terminate()
        sys.exit(1)

    # Aplicação rodando
    print("\n" + "=" * 70)
    print("✅ APLICAÇÃO RODANDO")
    print("=" * 70)
    print()
    print("  📊 Frontend (Streamlit): http://localhost:8501")
    print("  🔧 Backend (FastAPI):    http://localhost:8000")
    print("  📚 API Docs:             http://localhost:8000/docs")
    print()
    print("  Pressione Ctrl+C para encerrar")
    print("=" * 70)

    # Manter rodando
    try:
        while True:
            # Verificar se processos ainda estão rodando
            if backend.poll() is not None:
                print("\n❌ Backend parou inesperadamente")
                break
            if frontend.poll() is not None:
                print("\n❌ Frontend parou inesperadamente")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Encerrando processos...")
        for proc in processes:
            proc.terminate()
        print("✅ Aplicação encerrada")

if __name__ == "__main__":
    main()
