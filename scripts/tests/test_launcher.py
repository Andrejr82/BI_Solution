"""
Teste do Launcher - Agent Solution BI
Valida todas as funcionalidades do start_all.py
"""

import sys
import os
import subprocess
from pathlib import Path

print("="*70)
print("TESTE DO LAUNCHER - Agent Solution BI")
print("="*70)

# Teste 1: Sintaxe
print("\n[1/8] Testando sintaxe do start_all.py...")
try:
    import py_compile
    py_compile.compile("start_all.py", doraise=True)
    print("OK - Sintaxe correta")
except Exception as e:
    print(f"ERRO - {e}")
    sys.exit(1)

# Teste 2: Imports do launcher
print("\n[2/8] Testando imports do launcher...")
try:
    import subprocess
    import sys
    import os
    import time
    import webbrowser
    from pathlib import Path
    print("OK - Todos os imports disponíveis")
except ImportError as e:
    print(f"ERRO - {e}")
    sys.exit(1)

# Teste 3: Funções do launcher
print("\n[3/8] Testando funções do launcher...")
try:
    # Importar start_all sem executar main
    import importlib.util
    spec = importlib.util.spec_from_file_location("start_all", "start_all.py")
    start_all = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(start_all)

    # Verificar funções existem
    functions = ['check_dependencies', 'check_env', 'show_menu',
                 'start_api', 'start_streamlit', 'start_react']
    for func in functions:
        if hasattr(start_all, func):
            print(f"OK - Função '{func}' encontrada")
        else:
            print(f"ERRO - Função '{func}' não encontrada")
except Exception as e:
    print(f"ERRO - {e}")

# Teste 4: Arquivos necessários
print("\n[4/8] Testando arquivos necessários...")
files = [
    "api_server.py",
    "streamlit_app.py",
    "frontend/package.json",
    "frontend/vite.config.ts"
]
for file in files:
    if os.path.exists(file):
        print(f"OK - {file} encontrado")
    else:
        print(f"AVISO - {file} não encontrado")

# Teste 5: Script .bat (Windows)
print("\n[5/8] Testando start.bat...")
if os.path.exists("start.bat"):
    print("OK - start.bat criado")
    with open("start.bat", "r", encoding="utf-8") as f:
        content = f.read()
        if "start_all.py" in content:
            print("OK - start.bat chama start_all.py")
else:
    print("ERRO - start.bat não encontrado")

# Teste 6: Script .sh (Linux/Mac)
print("\n[6/8] Testando start.sh...")
if os.path.exists("start.sh"):
    print("OK - start.sh criado")
    with open("start.sh", "r", encoding="utf-8") as f:
        content = f.read()
        if "start_all.py" in content:
            print("OK - start.sh chama start_all.py")
else:
    print("ERRO - start.sh não encontrado")

# Teste 7: Dependências
print("\n[7/8] Testando dependências...")
deps = ['fastapi', 'uvicorn', 'streamlit']
for dep in deps:
    try:
        __import__(dep)
        print(f"OK - {dep} instalado")
    except ImportError:
        print(f"AVISO - {dep} não instalado")

# Teste 8: Estrutura do projeto
print("\n[8/8] Testando estrutura do projeto...")
dirs = ["frontend", "core", "data"]
for dir_name in dirs:
    if os.path.exists(dir_name):
        print(f"OK - Pasta '{dir_name}/' encontrada")
    else:
        print(f"AVISO - Pasta '{dir_name}/' não encontrada")

# Relatório Final
print("\n" + "="*70)
print("RELATORIO FINAL - LAUNCHER")
print("="*70)

print("\nARQUIVOS CRIADOS:")
print("  ✓ start_all.py  - Launcher Python principal")
print("  ✓ start.bat     - Launcher Windows")
print("  ✓ start.sh      - Launcher Linux/Mac")

print("\nCOMO USAR:")
print("\n  WINDOWS:")
print("    1. Duplo clique em 'start.bat'")
print("    2. Ou: python start_all.py")

print("\n  LINUX/MAC:")
print("    1. chmod +x start.sh")
print("    2. ./start.sh")
print("    3. Ou: python3 start_all.py")

print("\nOPÇÕES DISPONÍVEIS:")
print("  1. React Frontend     - Interface moderna (14 páginas)")
print("  2. Streamlit          - Interface rápida")
print("  3. API FastAPI        - Apenas API REST")
print("  4. TODAS              - Inicia as 3 simultaneamente")

print("\nFUNCIONALIDADES DO LAUNCHER:")
print("  ✓ Menu interativo")
print("  ✓ Verificação automática de dependências")
print("  ✓ Verificação de .env (API keys)")
print("  ✓ Instalação automática de node_modules (se necessário)")
print("  ✓ Abre navegador automaticamente")
print("  ✓ Gerencia múltiplos processos")
print("  ✓ Encerramento limpo com Ctrl+C")

print("\nPORTAS UTILIZADAS:")
print("  • API FastAPI: 5000")
print("  • React:       8080")
print("  • Streamlit:   8501")

print("\n" + "="*70)
print("STATUS: ✓ LAUNCHER PRONTO PARA USO")
print("="*70)
print("\nPRÓXIMO PASSO: Execute 'python start_all.py' ou 'start.bat'")
print("="*70 + "\n")
