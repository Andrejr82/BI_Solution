import pandas as pd
import os

# --- Configurações ---
# O arquivo Excel que você quer converter
caminho_excel = r"C:\Users\André\Documents\scripts\ferramenta_Admat.xlsx"

# A pasta onde os arquivos CSV serão salvos (dentro do nosso projeto)
pasta_saida = r"C:\Users\André\Documents\Agent_Solution_BI\data\input"

# As abas que você quer converter
abas_para_converter = ['ADMAT', 'SEMVENDAS']

print(f"Iniciando a conversão do arquivo: {os.path.basename(caminho_excel)}")

# Garante que a pasta de saída exista
os.makedirs(pasta_saida, exist_ok=True)

try:
    for aba in abas_para_converter:
        print(f"Lendo a aba '{aba}'...")
        # Lê a aba específica do arquivo Excel
        # O engine 'openpyxl' é necessário para arquivos .xlsx
        df = pd.read_excel(caminho_excel, sheet_name=aba, engine='openpyxl')
        
        # Define o caminho do arquivo CSV de saída
        caminho_csv_saida = os.path.join(pasta_saida, f"{aba}.csv")
        
        print(f"Salvando como '{caminho_csv_saida}'...")
        # Salva o DataFrame para um arquivo CSV
        df.to_csv(caminho_csv_saida, index=False, encoding='utf-8')
        
    print("\nConversão concluída com sucesso!")
    print(f"Os arquivos CSV foram salvos em: {pasta_saida}")

except FileNotFoundError:
    print(f"ERRO: O arquivo de entrada '{caminho_excel}' não foi encontrado.")
except ValueError as e:
    # Erro comum se a aba não existir
    print(f"ERRO: {e}. Verifique se os nomes das abas '{', '.join(abas_para_converter)}' estão corretos no arquivo Excel.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
