"""
Test Frontend - Testa apenas o frontend na porta 8080
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def test_frontend():
    """Testa o frontend"""
    print("="*60)
    print("TEST FRONTEND - Porta 8080")
    print("="*60)

    frontend_path = Path("frontend")
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"

    print(f"\n[1/3] Verificando frontend path: {frontend_path.absolute()}")
    if not frontend_path.exists():
        print(f"[ERRO] Diretorio frontend nao encontrado!")
        return False

    print(f"[OK] Diretorio frontend encontrado")

    print(f"\n[2/3] Verificando node_modules...")
    if not (frontend_path / "node_modules").exists():
        print("[AVISO] node_modules nao encontrado. Instalando...")
        result = subprocess.run(
            [npm_cmd, "install"],
            cwd=str(frontend_path),
            shell=True
        )
        if result.returncode != 0:
            print("[ERRO] Falha ao instalar dependencias!")
            return False

    print("[OK] node_modules encontrado")

    print(f"\n[3/3] Iniciando servidor dev na porta 8080...")
    print("Aguarde... (isso pode levar alguns segundos)")
    print("\nAcesse: http://localhost:8080")
    print("\nPressione Ctrl+C para parar o servidor\n")

    # Iniciar servidor
    try:
        process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_path),
            shell=True
        )

        # Aguardar
        process.wait()

    except KeyboardInterrupt:
        print("\n\n[OK] Encerrando servidor...")
        process.terminate()
        print("[OK] Servidor encerrado!")

    return True

if __name__ == "__main__":
    test_frontend()
