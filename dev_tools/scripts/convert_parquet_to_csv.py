# dev_tools/scripts/convert_data_format.py
"""
Módulo para converter ficheiros Parquet de grande volume para CSV ou XLSX.

Utiliza Dask para processar os dados em chunks, evitando o consumo excessivo de memória RAM.
Aceita um argumento de linha de comando `--format` para especificar o tipo de saída.

Exemplos de uso:
  python dev_tools/scripts/convert_data_format.py --format csv
  python dev_tools/scripts/convert_data_format.py --format xlsx
"""

import os
import argparse
import time
from pathlib import Path

import dask.dataframe as dd
import pandas as pd
# CORREÇÃO: Importar ProgressBar do submódulo correto.
from dask.diagnostics.progress import ProgressBar

# --- Configuração ---
INPUT_PARQUET_PATH = r"C:\Users\André\Documents\Daddos_Projetos\admmat.parquet"


def convert_to_csv(ddf: dd.DataFrame, output_path: str):
    """Processa e salva o Dask DataFrame como um único ficheiro CSV."""
    print("\n⏳ Iniciando a escrita para o ficheiro CSV. Isto pode demorar...")
    with ProgressBar():
        ddf.to_csv(output_path, single_file=True, index=False)


def convert_to_xlsx(ddf: dd.DataFrame, output_path: str):
    """
    Processa e salva o Dask DataFrame como um único ficheiro XLSX, partição por partição.
    Aviso: Este processo é mais lento e consome mais memória por chunk do que o CSV.
    """
    print("\n⏳ Iniciando a escrita para o ficheiro XLSX. Este processo é mais lento...")

    try:
        import openpyxl
    except ImportError:
        print("❌ ERRO: A biblioteca 'openpyxl' é necessária para a conversão para XLSX.")
        print("Por favor, instale-a executando: pip install openpyxl")
        return

    # Escreve o ficheiro Excel em modo de 'append' por chunks
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
        # Escreve o primeiro chunk com o cabeçalho
        print("  - Processando partição 1...")
        first_partition = ddf.partitions[0].compute()
        first_partition.to_excel(
            writer, sheet_name='data', index=False, header=True)

        # Escreve os chunks restantes sem o cabeçalho
        if ddf.npartitions > 1:
            # Usar ProgressBar aqui pode ser muito verboso, então vamos iterar diretamente
            # e imprimir o progresso manualmente.
            total_partitions = ddf.npartitions
            for i in range(1, total_partitions):
                print(f"  - Processando partição {i+1}/{total_partitions}...")
                partition_df = ddf.partitions[i].compute()
                partition_df.to_excel(
                    writer,
                    sheet_name='data',
                    index=False,
                    header=False,
                    startrow=writer.sheets['data'].max_row
                )
    print("  - Finalizando a escrita do ficheiro XLSX.")


def main():
    """
    Função principal que parseia os argumentos e orquestra a conversão.
    """
    parser = argparse.ArgumentParser(
        description="Converte um ficheiro Parquet grande para CSV ou XLSX usando Dask.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=["csv", "xlsx"],
        help="O formato de saída desejado.\n  'csv': Rápido e eficiente para grandes ficheiros.\n  'xlsx': Mais lento e consome mais memória, mas gera um ficheiro Excel."
    )
    args = parser.parse_args()
    output_format = args.format

    print("--- Início da Conversão de Formato de Dados ---")

    # 1. Validação do Ficheiro de Entrada
    if not os.path.exists(INPUT_PARQUET_PATH):
        print(
            f"❌ ERRO: O ficheiro de entrada não foi encontrado em: {INPUT_PARQUET_PATH}")
        return

    output_path = str(
        Path(INPUT_PARQUET_PATH).with_suffix(f".{output_format}"))

    print(f"📖 Lendo ficheiro Parquet de: {INPUT_PARQUET_PATH}")
    print(f"💾 O ficheiro de saída será: {output_path}")

    start_time = time.time()

    try:
        # 2. Leitura Lazy com Dask
        ddf = dd.read_parquet(INPUT_PARQUET_PATH, blocksize="256MB")
        print(f"\n📊 DataFrame Dask criado com {ddf.npartitions} partições.")

        # 3. Executa a conversão apropriada
        if output_format == "csv":
            convert_to_csv(ddf, output_path)
        elif output_format == "xlsx":
            convert_to_xlsx(ddf, output_path)

        end_time = time.time()
        duration = end_time - start_time

        print("\n--- Conversão Concluída com Sucesso! ---")
        print(f"✅ Ficheiro gerado em: {output_path}")
        print(f"⏱️ Tempo total de execução: {duration:.2f} segundos.")

    except Exception as e:
        print(f"\n❌ ERRO: Ocorreu um erro inesperado durante a conversão.")
        print(f"Detalhes do erro: {e}")


if __name__ == "__main__":
    main()
