#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificação rápida de arquivo de logging_config.py e streamlit_app.py
"""

import os
from pathlib import Path

base_path = Path("C:/Users/André/Documents/Agent_Solution_BI")

print("\n" + "="*70)
print("1. CONTEÚDO INICIAL DE: core/config/logging_config.py")
print("="*70)

logging_config = base_path / "core" / "config" / "logging_config.py"
if logging_config.exists():
    with open(logging_config, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Total de linhas: {len(lines)}")
    print("\nPrimeiras 50 linhas:")
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d}: {line.rstrip()}")
else:
    print("ARQUIVO NÃO ENCONTRADO!")

print("\n" + "="*70)
print("2. PRIMEIRAS 60 LINHAS DE: streamlit_app.py")
print("="*70)

streamlit_app = base_path / "streamlit_app.py"
if streamlit_app.exists():
    with open(streamlit_app, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Total de linhas: {len(lines)}")
    print("\nPrimeiras 60 linhas:")
    for i, line in enumerate(lines[:60], 1):
        print(f"{i:3d}: {line.rstrip()}")
else:
    print("ARQUIVO NÃO ENCONTRADO!")

print("\n" + "="*70)
print("3. VERIFICAÇÃO: setup_logging() presente?")
print("="*70)

if streamlit_app.exists():
    with open(streamlit_app, 'r', encoding='utf-8') as f:
        content = f.read()

    has_import = 'setup_logging' in content
    has_call = 'setup_logging()' in content

    print(f"Importa setup_logging: {has_import}")
    print(f"Chama setup_logging(): {has_call}")

    if not has_call and has_import:
        print("\nAVISO: setup_logging importado mas não chamado!")
    elif not has_import:
        print("\nERRO CRÍTICO: setup_logging nem importado!")

print("\n" + "="*70)
print("4. ESTRUTURA DE DIRETÓRIOS DE LOGS")
print("="*70)

logs_dir = base_path / "logs"
print(f"Diretório logs/ existe: {logs_dir.exists()}")

if logs_dir.exists():
    files = list(logs_dir.glob("*"))
    print(f"Total de arquivos: {len(files)}")
    if files:
        print("\nÚltimos 10 arquivos:")
        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            size = f.stat().st_size
            print(f"  {f.name:40s} ({size} bytes)")
