"""
Script para Limpar Cache do Projeto (RÁPIDO)
=============================================

Remove apenas cache Python do projeto, não das bibliotecas.
Muito mais rápido que limpar todo o cache.

Uso:
    python scripts/clear_project_cache.py

Autor: Claude Code
Data: 2025-10-27
"""

import os
import shutil
import sys

# Apenas diretórios do projeto (não .venv)
PROJECT_DIRS = [
    "core",
    "streamlit_app.py",
    "scripts"
]

def clear_project_cache():
    """Remove cache Python apenas do projeto."""
    removed_files = 0
    removed_dirs = 0

    print("\n[INFO] Limpando cache APENAS do projeto (core/, scripts/)...")
    print("[INFO] .venv será PRESERVADO para inicialização rápida\n")

    for base_dir in PROJECT_DIRS:
        if not os.path.exists(base_dir):
            continue

        # Se for arquivo, pular
        if os.path.isfile(base_dir):
            continue

        for dirpath, dirnames, filenames in os.walk(base_dir):
            # Remover arquivos .pyc
            for filename in filenames:
                if filename.endswith('.pyc'):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        os.remove(filepath)
                        removed_files += 1
                    except Exception as e:
                        print(f"[WARN] {filepath}: {e}")

            # Remover diretórios __pycache__
            if '__pycache__' in dirnames:
                cache_dir = os.path.join(dirpath, '__pycache__')
                try:
                    shutil.rmtree(cache_dir)
                    removed_dirs += 1
                    print(f"[REMOVED] {cache_dir}")
                except Exception as e:
                    print(f"[WARN] {cache_dir}: {e}")

    return removed_files, removed_dirs

def main():
    """Função principal."""
    print("=" * 60)
    print("LIMPEZA DE CACHE DO PROJETO (RÁPIDA)")
    print("=" * 60)

    # Limpar cache
    removed_files, removed_dirs = clear_project_cache()

    print(f"\n[RESUMO]")
    print(f"  - Arquivos .pyc removidos: {removed_files}")
    print(f"  - Diretórios __pycache__ removidos: {removed_dirs}")

    print("\n" + "=" * 60)
    print("[OK] Cache do projeto limpo!")
    print("=" * 60)

    print("\n[INFO] .venv preservado - Inicialização será RÁPIDA")
    print("\nPróximos passos:")
    print("  1. Reiniciar Streamlit: streamlit run streamlit_app.py")
    print("  2. Inicialização em ~10-15s (não 2+ minutos)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
