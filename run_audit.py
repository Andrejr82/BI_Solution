#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script executável para auditoria de logs
Execute com: python run_audit.py
"""

import sys
import os

# Garantir que estamos no diretório correto
os.chdir(r"C:\Users\André\Documents\Agent_Solution_BI")

# Importar e executar analisador
if __name__ == "__main__":
    # Tentar importar e executar analisador
    try:
        from ANALISADOR_ARQUIVOS import main
        print("Iniciando auditoria de logs...\n")
        resultados = main()
        print("\nAuditoria concluída com sucesso!")
        sys.exit(0)
    except ImportError as e:
        print(f"Erro ao importar: {e}")
        print("\nExecutando análise inline...\n")

    # Análise inline se ImportError
    from pathlib import Path
    import json

    BASE = Path(".")

    print("="*80)
    print("AUDITORIA DE SISTEMA DE LOGS")
    print("="*80)
    print()

    # Verificar logging_config.py
    lc_path = BASE / "core" / "config" / "logging_config.py"
    print(f"[1] logging_config.py: {lc_path}")
    print(f"    Existe: {lc_path.exists()}")

    if lc_path.exists():
        with open(lc_path, encoding='utf-8') as f:
            lc_content = f.read()
        print(f"    Tem setup_logging: {'def setup_logging' in lc_content}")
        print(f"    Tem FileHandler: {'FileHandler' in lc_content}")
        print(f"    Tamanho: {len(lc_content)} bytes")
    print()

    # Verificar streamlit_app.py
    sa_path = BASE / "streamlit_app.py"
    print(f"[2] streamlit_app.py: {sa_path}")
    print(f"    Existe: {sa_path.exists()}")

    if sa_path.exists():
        with open(sa_path, encoding='utf-8') as f:
            sa_content = f.read()
        print(f"    Chama setup_logging(): {'setup_logging()' in sa_content}")
        print(f"    Importa logging: {'logging_config import' in sa_content}")
        print(f"    Tamanho: {len(sa_content)} bytes")
    print()

    # Verificar diretório logs/
    logs_dir = BASE / "logs"
    print(f"[3] Diretório logs/: {logs_dir}")
    print(f"    Existe: {logs_dir.exists()}")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"    Arquivos .log: {len(log_files)}")
    print()

    # Verificar direct_query_engine.py
    dqe_path = BASE / "core" / "business_intelligence" / "direct_query_engine.py"
    print(f"[4] direct_query_engine.py: {dqe_path}")
    print(f"    Existe: {dqe_path.exists()}")
    if dqe_path.exists():
        with open(dqe_path, encoding='utf-8') as f:
            dqe_content = f.read()
        print(f"    Tem logger: {'logger' in dqe_content}")
        print(f"    Tem load_data: {'def load_data' in dqe_content}")
    print()

    print("="*80)
    print("FIM DA AUDITORIA")
    print("="*80)
