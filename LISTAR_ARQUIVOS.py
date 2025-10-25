#!/usr/bin/env python3
import os
import sys
from pathlib import Path

os.chdir(r"C:\Users\André\Documents\Agent_Solution_BI")

# Listar arquivos críticos
base = Path(".")

print("\n" + "="*80)
print("LISTAGEM DE ARQUIVOS CRÍTICOS")
print("="*80 + "\n")

arquivos = [
    "core/config/logging_config.py",
    "streamlit_app.py",
    "core/business_intelligence/direct_query_engine.py",
    "core/connectivity/parquet_adapter.py",
    "logs/",
    "data/learning/"
]

for arquivo in arquivos:
    caminho = base / arquivo
    if caminho.is_dir():
        existe = caminho.exists()
        print(f"[DIR]  {arquivo}")
        print(f"       Existe: {existe}")
        if existe:
            files = list(caminho.glob("*"))
            print(f"       Arquivos: {len(files)}")
            if files:
                for f in sorted(files)[-5:]:
                    print(f"         - {f.name}")
    else:
        existe = caminho.exists()
        print(f"[FILE] {arquivo}")
        print(f"       Existe: {existe}")
        if existe:
            size = caminho.stat().st_size
            lines = len(caminho.read_text(encoding='utf-8').splitlines())
            print(f"       Tamanho: {size} bytes")
            print(f"       Linhas: {lines}")
    print()

print("="*80)
