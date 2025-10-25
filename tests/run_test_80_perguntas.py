"""
Script auxiliar para rodar o teste de 80 perguntas
Executa o teste e mostra um resumo dos resultados
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def main():
    """Executa o teste de 80 perguntas"""
    print("=" * 80)
    print("SCRIPT AUXILIAR - TESTE DE 80 PERGUNTAS")
    print("=" * 80)
    print(f"\nDiretório raiz: {root_dir}")
    print(f"Python: {sys.version}")

    # Verificar dependências
    print("\nVerificando dependências...")
    try:
        import pandas as pd
        print(f"[OK] pandas {pd.__version__}")
    except ImportError as e:
        print(f"[ERRO] pandas não encontrado: {e}")
        return 1

    try:
        import dask
        print(f"[OK] dask {dask.__version__}")
    except ImportError as e:
        print(f"[ERRO] dask não encontrado: {e}")
        return 1

    try:
        import pyarrow as pa
        print(f"[OK] pyarrow {pa.__version__}")
    except ImportError as e:
        print(f"[ERRO] pyarrow não encontrado: {e}")
        return 1

    # Verificar arquivos parquet
    print("\nVerificando arquivos parquet...")
    parquet_dir = root_dir / 'data' / 'parquet'

    if not parquet_dir.exists():
        print(f"[ERRO] Diretório não encontrado: {parquet_dir}")
        return 1

    admmat_extended = parquet_dir / 'admmat_extended.parquet'
    admmat = parquet_dir / 'admmat.parquet'

    if admmat_extended.exists():
        print(f"[OK] Usando: {admmat_extended.name}")
        parquet_file = admmat_extended
    elif admmat.exists():
        print(f"[OK] Usando: {admmat.name}")
        parquet_file = admmat
    else:
        print(f"[ERRO] Nenhum arquivo parquet encontrado em {parquet_dir}")
        return 1

    # Verificar tamanho do arquivo
    file_size_mb = parquet_file.stat().st_size / (1024 * 1024)
    print(f"   Tamanho: {file_size_mb:.2f} MB")

    # Importar e executar o teste
    print("\nImportando módulo de teste...")
    try:
        from test_80_perguntas_completo import executar_teste
        print("[OK] Módulo importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Falha ao importar módulo de teste: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Executar teste
    print("\n" + "=" * 80)
    print("INICIANDO TESTE")
    print("=" * 80 + "\n")

    try:
        relatorio = executar_teste()

        if relatorio:
            print("\n" + "=" * 80)
            print("TESTE CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            return 0
        else:
            print("\n" + "=" * 80)
            print("TESTE FALHOU - Verifique os logs acima")
            print("=" * 80)
            return 1

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Exceção durante execução: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
