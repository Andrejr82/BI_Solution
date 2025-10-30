"""
Extrair UNEs do arquivo Parquet
"""
import pandas as pd
import sys
import io

# Configurar encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Carregando dados do Parquet...")

try:
    # Carregar apenas as colunas necessárias
    df = pd.read_parquet(
        'data/parquet/admmat.parquet',
        columns=['une', 'une_nome']
    )

    # Obter UNEs únicas
    unes = df[['une', 'une_nome']].drop_duplicates().sort_values('une')

    print(f"\nTotal de UNEs encontradas: {len(unes)}\n")
    print("="*60)

    # Exibir lista
    for _, row in unes.iterrows():
        print(f"{row['une']}: {row['une_nome']}")

    print("\n" + "="*60)

    # Gerar mapeamento Python
    print("\n# CODIGO PYTHON PARA UNE_MAPPING.PY:")
    print("="*60)

    print("\nUNE_MAP = {")
    for _, row in unes.iterrows():
        une_code = str(row['une'])
        une_name = str(row['une_nome'])

        # Extrair sigla (primeiros caracteres antes do hífen)
        if '-' in une_name:
            parts = une_name.split('-', 1)
            sigla = parts[0].strip()
            nome_completo = parts[1].strip() if len(parts) > 1 else une_name
        else:
            sigla = une_name[:3].upper()
            nome_completo = une_name

        # Gerar entradas
        print(f'    "{sigla.lower()}": "{une_code}",')
        print(f'    "{nome_completo.lower()}": "{une_code}",')
        print(f'    "une {sigla.lower()}": "{une_code}",')

    print("}")

    print("\nUNE_NAMES = {")
    for _, row in unes.iterrows():
        une_code = str(row['une'])
        une_name = str(row['une_nome'])
        print(f'    "{une_code}": "{une_name}",')
    print("}")

    # Salvar em arquivo
    with open('data/reports/unes_from_parquet.txt', 'w', encoding='utf-8') as f:
        f.write("UNEs do Parquet\n")
        f.write("="*60 + "\n\n")
        for _, row in unes.iterrows():
            f.write(f"{row['une']}: {row['une_nome']}\n")

    print("\n\nArquivo salvo em: data/reports/unes_from_parquet.txt")

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
