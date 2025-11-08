import pandas as pd
import os

def converter_excel_para_csv(excel_file_path, csv_file_path, sheet_name=0):
    """
    Lê uma planilha de um arquivo Excel e a salva como um arquivo CSV.

    Parâmetros:
    - excel_file_path (str): Caminho para o arquivo Excel de entrada (.xlsx).
    - csv_file_path (str): Caminho para o arquivo CSV de saída.
    - sheet_name (str ou int, opcional): Nome ou índice da planilha a ser lida. 
                                        O padrão é 0 (a primeira planilha).
    """
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(excel_file_path):
        print(f"Erro: O arquivo de entrada '{excel_file_path}' não foi encontrado.")
        return

    try:
        # Carrega a planilha específica do arquivo Excel para um DataFrame do pandas
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='xlrd')

        # Salva o DataFrame em um arquivo CSV com codificação UTF-8
        # O parâmetro index=False evita que o índice do DataFrame seja escrito no arquivo CSV
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

        print(f"Sucesso! O arquivo '{excel_file_path}' foi convertido para '{csv_file_path}'.")

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

# --- Exemplo de Uso ---

# 1. Defina o caminho para o seu arquivo Excel.
#    Substitua 'caminho/para/seu/arquivo.xlsx' pelo caminho real do seu arquivo.
caminho_do_arquivo_excel = 'C:\\Users\\André\\Documents\\scripts\\ADMAT_BON_9.3_070524_01h57.xls'

# 2. Defina o caminho para o arquivo CSV que será criado.
#    Você pode usar o mesmo nome do arquivo original, apenas mudando a extensão.
nome_base = os.path.splitext(os.path.basename(caminho_do_arquivo_excel))[0]
caminho_do_arquivo_csv = f"{nome_base}_convertido.csv"

# 3. Chame a função para realizar a conversão.
#    - Se a sua planilha tiver um nome específico (ex: "Vendas_2025"), use:
#      converter_excel_para_csv(caminho_do_arquivo_excel, caminho_do_arquivo_csv, sheet_name="Vendas_2025")
#
#    - Se você quiser converter a primeira planilha, basta chamar a função assim:
converter_excel_para_csv(caminho_do_arquivo_excel, caminho_do_arquivo_csv)
