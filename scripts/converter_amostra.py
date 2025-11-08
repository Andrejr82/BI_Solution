import pandas as pd
import os

# --- Configurações ---
caminho_csv = r"C:\Users\André\Documents\scripts\ADMAT_BON_9.3_070524_01h57_convertido.csv"
caminho_md = r"C:\Users\André\Documents\scripts\amostra_dados.md"
numero_de_linhas = 200

print(f"Iniciando a conversão das primeiras {numero_de_linhas} linhas de '{os.path.basename(caminho_csv)}' para Markdown...")

try:
    # Ler apenas as primeiras N linhas do CSV para eficiência
    try:
        df_amostra = pd.read_csv(caminho_csv, nrows=numero_de_linhas)
    except UnicodeDecodeError:
        df_amostra = pd.read_csv(caminho_csv, nrows=numero_de_linhas, encoding='latin1')

    # Converter o DataFrame da amostra para uma tabela Markdown
    markdown_table = df_amostra.to_markdown(index=False)

    # Escrever a tabela no arquivo de saída
    with open(caminho_md, 'w', encoding='utf-8') as f:
        f.write(f"# Amostra de Dados ({numero_de_linhas} linhas)\n\n")
        f.write(markdown_table)

    print(f"Arquivo '{os.path.basename(caminho_md)}' criado com sucesso na pasta 'scripts'.")

except FileNotFoundError:
    print(f"ERRO: O arquivo de entrada '{caminho_csv}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
