import pandas as pd
import os

# --- Configurações ---
caminho_csv = r"C:\Users\André\Documents\Agent_Solution_BI\data\input\SEMVENDAS.csv"
caminho_md = r"C:\Users\André\Documents\Agent_Solution_BI\scripts\descricao_SEMVENDAS.md" # Salvar dentro do projeto
numero_exemplos = 5

print("Iniciando a descrição detalhada de cada coluna...")

try:
    try:
        df = pd.read_csv(caminho_csv, low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin1', low_memory=False)

    with open(caminho_md, 'w', encoding='utf-8') as f:
        f.write("# Descrição Detalhada das Colunas\n\n")
        f.write("A seguir, uma análise de cada coluna, com uma descrição do conteúdo inferido e exemplos de dados presentes.\n\n---\n\n")

        for col in df.columns:
            f.write(f"## Coluna: `{col}`\n\n")
            
            # Analisa apenas os valores não nulos
            col_data = df[col].dropna().unique()

            if len(col_data) == 0:
                f.write("- **Conteúdo:** A coluna parece estar vazia ou conter apenas valores nulos.\n")
                f.write("\n---\n")
                continue

            # Tenta inferir o tipo de conteúdo
            is_numeric = False
            try:
                pd.to_numeric(pd.Series(col_data))
                is_numeric = True
            except (ValueError, TypeError):
                pass
            
            description = ""
            if is_numeric:
                description = "Parece conter apenas valores numéricos."
            elif pd.api.types.is_string_dtype(pd.Series(col_data)):
                # Check for date-like strings
                try:
                    pd.to_datetime(pd.Series(col_data), errors='raise')
                    description = "Parece conter datas ou data/hora."
                except (ValueError, TypeError):
                    if len(col_data) < 20:
                        description = "Parece ser uma coluna categórica com um conjunto limitado de textos."
                    else:
                        description = "Contém textos variados, possivelmente códigos, descrições ou identificadores."
            else:
                description = "Contém tipos de dados mistos (números, textos, etc.)."

            f.write(f"- **Descrição Inferida:** {description}\n")

            # Pega exemplos
            exemplos = col_data[:numero_exemplos]
            f.write("- **Exemplos de Valores:**\n")
            for ex in exemplos:
                f.write(f"  - `{ex}`\n")
            
            f.write("\n---\n")

    print(f"Arquivo '{os.path.basename(caminho_md)}' criado com sucesso.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
