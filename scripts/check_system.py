#!/usr/bin/env python3
"""
Quick System Check - Agent Solution BI
======================================
Verificacao rapida antes de iniciar o sistema
"""

import socket
import sys
from pathlib import Path

def check_port_available(port: int) -> bool:
    """Verifica se uma porta esta livre"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0  # True se porta esta livre
    except:
        return False

def main():
    print("\n" + "=" * 60)
    print("  VERIFICACAO RAPIDA DO SISTEMA")
    print("=" * 60 + "\n")
    
    all_ok = True
    
    # 1. Verifica Python
    print("[1/5] Verificando Python...")
    python_version = sys.version.split()[0]
    print(f"      Python {python_version} - OK")
    
    # 2. Verifica arquivo de usuarios
    print("[2/5] Verificando arquivo de usuarios...")
    users_file = Path(__file__).parent / "data" / "parquet" / "users.parquet"
    if users_file.exists():
        print(f"      {users_file.name} - OK")
    else:
        print(f"      [ERRO] {users_file.name} nao encontrado!")
        all_ok = False
    
    # 3. Verifica porta 8000 (backend)
    print("[3/5] Verificando porta 8000 (backend)...")
    if check_port_available(8000):
        print("      Porta 8000 livre - OK")
    else:
        print("      [AVISO] Porta 8000 em uso - sera liberada automaticamente")
    
    # 4. Verifica porta 3000 (frontend)
    print("[4/5] Verificando porta 3000 (frontend)...")
    if check_port_available(3000):
        print("      Porta 3000 livre - OK")
    else:
        print("      [AVISO] Porta 3000 em uso - sera liberada automaticamente")
    
    # 5. Verifica diretorios
    print("[5/5] Verificando estrutura de diretorios...")
    backend_dir = Path(__file__).parent / "backend"
    frontend_dir = Path(__file__).parent / "frontend-react"
    
    if backend_dir.exists() and frontend_dir.exists():
        print("      Diretorios backend e frontend - OK")
    else:
        print("      [ERRO] Estrutura de diretorios incompleta!")
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("  SISTEMA PRONTO PARA INICIAR")
        print("=" * 60)
        print("\n  Execute: RUN.bat ou python run.py")
        print("\n  Credenciais:")
        print("    Usuario: admin")
        print("    Senha: Admin@2024")
        print("\n" + "=" * 60 + "\n")
        return 0
    else:
        print("  PROBLEMAS DETECTADOS - Verifique os erros acima")
        print("=" * 60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
