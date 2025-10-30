"""
Script para Limpar Cache Python
=================================

Remove arquivos .pyc e __pycache__ para forçar reload de módulos.

Uso:
    python scripts/clear_python_cache.py

Autor: Claude Code
Data: 2025-10-27
"""

import os
import shutil
import sys

def clear_cache(root_dir="."):
    """Remove cache Python recursivamente."""
    removed_files = 0
    removed_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remover arquivos .pyc
        for filename in filenames:
            if filename.endswith('.pyc'):
                filepath = os.path.join(dirpath, filename)
                try:
                    os.remove(filepath)
                    removed_files += 1
                    print(f"[REMOVED] {filepath}")
                except Exception as e:
                    print(f"[ERROR] {filepath}: {e}")

        # Remover diretórios __pycache__
        if '__pycache__' in dirnames:
            cache_dir = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                removed_dirs += 1
                print(f"[REMOVED DIR] {cache_dir}")
            except Exception as e:
                print(f"[ERROR] {cache_dir}: {e}")

    return removed_files, removed_dirs

def main():
    """Função principal."""
    print("=" * 60)
    print("LIMPEZA DE CACHE PYTHON")
    print("=" * 60)

    # Limpar cache
    print("\n[1/2] Removendo arquivos .pyc e diretórios __pycache__...")
    removed_files, removed_dirs = clear_cache()

    print(f"\n[2/2] Limpeza concluída:")
    print(f"  - Arquivos .pyc removidos: {removed_files}")
    print(f"  - Diretórios __pycache__ removidos: {removed_dirs}")

    print("\n" + "=" * 60)
    print("[OK] Cache Python limpo com sucesso!")
    print("=" * 60)

    print("\nPróximos passos:")
    print("  1. Reiniciar Streamlit: streamlit run streamlit_app.py")
    print("  2. Testar query novamente")

    return 0

if __name__ == "__main__":
    sys.exit(main())
