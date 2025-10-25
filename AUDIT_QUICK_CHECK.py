#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick check - Verificação rápida dos arquivos críticos"""

from pathlib import Path

base = Path("C:/Users/André/Documents/Agent_Solution_BI")

# 1. Checar logging_config.py
lc = base / "core" / "config" / "logging_config.py"
if lc.exists():
    with open(lc, encoding='utf-8') as f:
        lc_content = f.read()
    print("LOGGING_CONFIG.PY EXISTE")
    print(f"Tem setup_logging: {'def setup_logging' in lc_content}")
    print(f"Tem FileHandler: {'FileHandler' in lc_content}")
    print(f"Linhas: {len(lc_content.splitlines())}")
else:
    print("LOGGING_CONFIG.PY NAO EXISTE")

print("\n" + "="*60)

# 2. Checar streamlit_app.py
sa = base / "streamlit_app.py"
if sa.exists():
    with open(sa, encoding='utf-8') as f:
        sa_content = f.read()
    sa_lines = sa_content.splitlines()
    print("STREAMLIT_APP.PY EXISTE")
    print(f"Tem import setup_logging: {'from core.config.logging_config import' in sa_content}")
    print(f"Tem chamada setup_logging(): {'setup_logging()' in sa_content}")
    print(f"Total linhas: {len(sa_lines)}")

    # Mostrar primeiras 30 linhas
    print("\nPrimeiras 30 linhas:")
    for i, line in enumerate(sa_lines[:30], 1):
        if line.strip():
            print(f"{i:3d}: {line}")
else:
    print("STREAMLIT_APP.PY NAO EXISTE")

print("\n" + "="*60)

# 3. Checar if logs/ directory exists
logs = base / "logs"
print(f"Diretório logs/ existe: {logs.exists()}")
if logs.exists():
    log_files = list(logs.glob("*.log"))
    print(f"Arquivos .log: {len(log_files)}")
    if log_files:
        recent = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        print("Recentes:")
        for f in recent:
            print(f"  - {f.name}")

print("\n" + "="*60)

# 4. Checar direct_query_engine.py
dqe = base / "core" / "business_intelligence" / "direct_query_engine.py"
if dqe.exists():
    with open(dqe, encoding='utf-8') as f:
        dqe_content = f.read()
    print("DIRECT_QUERY_ENGINE.PY EXISTE")
    print(f"Tem função load_data: {'def load_data' in dqe_content}")
    print(f"Tem logger: {'logger' in dqe_content}")
    print(f"Linhas: {len(dqe_content.splitlines())}")
else:
    print("DIRECT_QUERY_ENGINE.PY NAO EXISTE")
