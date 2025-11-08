
import pandas as pd
import io
import sys
import os

# --- Configurações ---
caminho_csv = r"C:\Users\André\Documents\scripts\ADMAT_BON_9.3_070524_01h57_convertido.csv"
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# --- Início da Análise ---
try:
    # Tentar ler com encoding padrão, se falhar, tentar outros
    try:
        df = pd.read_csv(caminho_csv)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin1')

    num_linhas, num_colunas = df.shape

    # --- Início do Relatório Markdown ---
    print(f"# Análise Detalhada do Arquivo: {os.path.basename(caminho_csv)}")
    print("\n---\n")

    # 1. Visão Geral
    print("## 1. Visão Geral do Arquivo")
    print(f"- **Número de Linhas:** {num_linhas}")
    print(f"- **Número de Colunas:** {num_colunas}")
    print("\n")

    # 2. Estrutura e Tipos de Dados
    print("## 2. Estrutura e Tipos de Dados (Inferidos pelo Pandas)")
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    print("```")
    print(info_str)
    print("```")
    print("\n")

    # 3. Contagem de Valores Faltantes (NaN)")
    print("## 3. Contagem de Valores Faltantes (NaN)")
    missing_values = df.isnull().sum()
    missing_df = missing_values[missing_values > 0].sort_values(ascending=False).to_frame('Valores Faltantes')
    if not missing_df.empty:
        print(missing_df.to_markdown())
    else:
        print("Nenhum valor faltante encontrado no conjunto de dados.")
    print("\n---\n")

    # 4. Amostra dos Dados (Primeiras 5 Linhas)
    print("## 4. Amostra dos Dados (Primeiras 5 Linhas)")
    print(df.head(5).to_markdown(index=False))
    print("\n---\n")

    # 5. Análise Descritiva (Colunas Numéricas)
    print("## 5. Análise Descritiva (Colunas Numéricas)")

    # Tenta converter todas as colunas para numérico, tratando erros
    df_numeric = df.apply(pd.to_numeric, errors='coerce')

    # Filtra apenas as colunas que foram convertidas com sucesso (pelo menos um valor numérico)
    df_numeric = df_numeric.dropna(axis=1, how='all')

    if not df_numeric.empty:
        print("- **Nota:** As estatísticas abaixo são calculadas após uma tentativa de conversão forçada para o tipo numérico. Valores não numéricos foram transformados em 'NaN' (Não é um Número) para permitir o cálculo.")
        descritivo_numerico = df_numeric.describe()
        print(descritivo_numerico.to_markdown())
    else:
        print("Nenhuma coluna pôde ser convertida para um tipo numérico para análise.")
    print("\n---\n")

    # 6. Análise de Colunas Categóricas/Texto
    print("## 6. Análise de Colunas Categóricas/Texto")
    object_cols = df.select_dtypes(include=['object']).columns
    if len(object_cols) > 0:
        for col in object_cols:
            num_unicos = df[col].nunique()
            print(f"### Coluna: `{col}`")
            print(f"- **Valores Únicos:** {num_unicos}")
            if num_unicos > 0:
                # Se houver muitos valores únicos, mostre apenas os mais comuns
                if num_unicos > 20:
                    print("- **Top 10 Valores Mais Comuns:**")
                    print("```")
                    print(df[col].value_counts().head(10))
                    print("```")
                else:
                    print("- **Distribuição de Valores:**")
                    print("```")
                    print(df[col].value_counts())
                    print("```")
            else:
                 print("- A coluna não contém valores únicos (pode estar vazia ou ter apenas NaN).")
            print("\n")
    else:
        print("Nenhuma coluna de texto/categórica encontrada.")

except FileNotFoundError:
    print(f"ERRO: O arquivo '{caminho_csv}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a análise: {e}")
