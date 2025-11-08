import pandas as pd
import os

# --- Configurações ---
caminho_csv = r"C:\Users\André\Documents\scripts\ADMAT_BON_9.3_070524_01h57_convertido.csv"
# Colunas que parecem mais relevantes para descrever as rotinas
coluna_rotina = 'Unnamed: 107'
coluna_instrucao = 'Unnamed: 108'
coluna_status_lv = 'Unnamed: 91'

# --- Início da Análise de Rotinas ---
try:
    # Tentar ler com encoding padrão, se falhar, tentar outros
    try:
        df = pd.read_csv(caminho_csv, low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin1', low_memory=False)

    # Limpeza básica: remover linhas onde a coluna de rotina está vazia
    df_rotinas = df.dropna(subset=[coluna_rotina])

    # --- Início do Relatório Markdown ---
    print("# Treinamento sobre Rotinas e Etapas")
    print("\n---\n")
    print("Este documento descreve as diferentes rotinas identificadas no arquivo e as etapas ou instruções associadas a cada uma.\n")

    # Encontrar os nomes únicos das rotinas
    nomes_rotinas = df_rotinas[coluna_rotina].unique()

    for rotina in nomes_rotinas:
        if pd.isna(rotina) or str(rotina).strip() == '':
            continue

        print(f"## Rotina: {rotina.strip()}")
        
        # Filtrar o dataframe para a rotina atual
        df_subset = df_rotinas[df_rotinas[coluna_rotina] == rotina]

        # Encontrar as instruções únicas para esta rotina
        instrucoes = df_subset[coluna_instrucao].dropna().unique()
        if len(instrucoes) > 0:
            print("\n### Possíveis Etapas / Instruções:")
            for i, instrucao in enumerate(instrucoes):
                # Limpa a instrução para melhor leitura
                instrucao_limpa = str(instrucao).strip()
                print(f"- **{instrucao_limpa}**")
        else:
            print("\n- Nenhuma instrução detalhada encontrada para esta rotina.")

        # Encontrar os status únicos para esta rotina
        status_lv = df_subset[coluna_status_lv].dropna().unique()
        if len(status_lv) > 0:
            print("\n### Status Associados (Coluna 'Unnamed: 91'):")
            for status in status_lv:
                print(f"- {str(status).strip()}")
        
        print("\n---\n")

except FileNotFoundError:
    print(f"ERRO: O arquivo '{caminho_csv}' não foi encontrado.")
except KeyError as e:
    print(f"ERRO: Uma coluna chave para a análise não foi encontrada: {e}. O arquivo pode ter mudado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a análise: {e}")
