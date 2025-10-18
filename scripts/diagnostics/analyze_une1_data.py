"""
Data Agent - Análise de dados UNE 1
Verifica qualidade dos dados no arquivo Parquet
"""
import pandas as pd
import os
from datetime import datetime
import json

def analyze_une1_data():
    """Analisa dados da UNE 1 no arquivo Parquet"""

    # Definir caminhos
    base_path = r"C:\Users\André\Documents\Agent_Solution_BI"
    parquet_extended = os.path.join(base_path, "data", "parquet", "admmat_extended.parquet")
    parquet_basic = os.path.join(base_path, "data", "parquet", "admmat.parquet")

    # Tentar ler arquivo extended primeiro
    if os.path.exists(parquet_extended):
        print(f"[INFO] Lendo arquivo: {parquet_extended}")
        df = pd.read_parquet(parquet_extended)
        source_file = "admmat_extended.parquet"
    elif os.path.exists(parquet_basic):
        print(f"[INFO] Lendo arquivo: {parquet_basic}")
        df = pd.read_parquet(parquet_basic)
        source_file = "admmat.parquet"
    else:
        print("[ERRO] Nenhum arquivo Parquet encontrado!")
        return None

    print(f"\n{'='*80}")
    print(f"ANÁLISE DE DADOS - UNE 1")
    print(f"{'='*80}")
    print(f"Fonte: {source_file}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # 1. INFO GERAL DO DATASET
    print(f"[1] INFORMAÇÕES GERAIS DO DATASET")
    print(f"    Total de registros: {len(df):,}")
    print(f"    Total de colunas: {len(df.columns)}")
    print(f"    Colunas disponíveis: {', '.join(df.columns.tolist())}\n")

    # 2. FILTRAR UNE 1
    print(f"[2] FILTRANDO DADOS DA UNE 1")

    # Identificar coluna de UNE
    une_col = None
    for col in ['UNE', 'une', 'cod_une', 'COD_UNE']:
        if col in df.columns:
            une_col = col
            break

    if une_col is None:
        print("    [ERRO] Coluna de UNE não encontrada!")
        return None

    print(f"    Coluna UNE identificada: '{une_col}'")
    print(f"    Valores únicos de UNE: {df[une_col].unique().tolist()}")

    # Filtrar UNE 1
    df_une1 = df[df[une_col] == 1].copy()
    print(f"    Total de registros UNE 1: {len(df_une1):,}")

    if len(df_une1) == 0:
        print("    [AVISO] Nenhum registro encontrado para UNE 1!")
        return None

    # 3. ANÁLISE DE COLUNAS DE ESTOQUE
    print(f"\n[3] ANÁLISE DE COLUNAS DE ESTOQUE")

    estoque_cols = [col for col in df_une1.columns if 'estoque' in col.lower() or 'ESTOQUE' in col]
    print(f"    Colunas de estoque encontradas: {len(estoque_cols)}")

    for col in estoque_cols:
        dtype = df_une1[col].dtype
        non_null = df_une1[col].notna().sum()
        null_count = df_une1[col].isna().sum()

        print(f"\n    Coluna: '{col}'")
        print(f"      - Tipo de dado: {dtype}")
        print(f"      - Não nulos: {non_null:,} ({non_null/len(df_une1)*100:.1f}%)")
        print(f"      - Nulos: {null_count:,} ({null_count/len(df_une1)*100:.1f}%)")

        # Se for numérico, mostrar estatísticas
        try:
            if pd.api.types.is_numeric_dtype(df_une1[col]):
                values = df_une1[col].dropna()
                if len(values) > 0:
                    print(f"      - Min: {values.min():.2f}")
                    print(f"      - Max: {values.max():.2f}")
                    print(f"      - Média: {values.mean():.2f}")
                    print(f"      - Total > 0: {(values > 0).sum():,}")
            else:
                # Tentar converter para numérico
                print(f"      - [AVISO] Tipo não numérico! Tentando converter...")
                converted = pd.to_numeric(df_une1[col], errors='coerce')
                numeric_count = converted.notna().sum()
                print(f"      - Conversíveis para número: {numeric_count:,} ({numeric_count/len(df_une1)*100:.1f}%)")
                if numeric_count > 0:
                    print(f"      - Total > 0 após conversão: {(converted > 0).sum():,}")
        except Exception as e:
            print(f"      - [ERRO] Não foi possível analisar valores: {str(e)}")

    # 4. PRODUTOS COM ESTOQUE > 0
    print(f"\n[4] PRODUTOS COM ESTOQUE > 0")

    # Identificar coluna principal de estoque
    main_estoque_col = None
    for col in ['estoque_atual', 'ESTOQUE_UNE', 'estoque_lv', 'ESTOQUE']:
        if col in df_une1.columns:
            main_estoque_col = col
            break

    if main_estoque_col is None and estoque_cols:
        main_estoque_col = estoque_cols[0]

    if main_estoque_col:
        print(f"    Usando coluna: '{main_estoque_col}'")

        # Converter para numérico se necessário
        estoque_numeric = pd.to_numeric(df_une1[main_estoque_col], errors='coerce')
        df_une1['estoque_numeric'] = estoque_numeric

        df_with_stock = df_une1[df_une1['estoque_numeric'] > 0].copy()
        print(f"    Total com estoque > 0: {len(df_with_stock):,}")
        print(f"    Percentual: {len(df_with_stock)/len(df_une1)*100:.1f}%")
    else:
        print("    [ERRO] Nenhuma coluna de estoque identificada!")
        df_with_stock = pd.DataFrame()

    # 5. EXEMPLOS DE PRODUTOS
    print(f"\n[5] EXEMPLOS DE PRODUTOS COM ESTOQUE NA UNE 1")

    if len(df_with_stock) > 0:
        # Identificar colunas de código e nome
        cod_col = None
        for col in ['codigo', 'CODIGO', 'cod_produto', 'COD_PRODUTO']:
            if col in df_with_stock.columns:
                cod_col = col
                break

        nome_col = None
        for col in ['nome', 'NOME', 'descricao', 'DESCRICAO', 'produto', 'PRODUTO']:
            if col in df_with_stock.columns:
                nome_col = col
                break

        # Selecionar colunas para exibir
        display_cols = []
        if cod_col:
            display_cols.append(cod_col)
        if nome_col:
            display_cols.append(nome_col)
        display_cols.append(main_estoque_col)
        display_cols.append('estoque_numeric')

        # Adicionar outras colunas de estoque se existirem
        for col in estoque_cols[:3]:  # Máximo 3 colunas adicionais
            if col != main_estoque_col and col in df_with_stock.columns:
                display_cols.append(col)

        # Mostrar 5 exemplos
        sample = df_with_stock.nlargest(5, 'estoque_numeric')[display_cols]

        print(f"\n    Top 5 produtos com maior estoque:")
        print(f"    {'-'*80}")
        for idx, row in sample.iterrows():
            print(f"\n    Produto #{idx}")
            for col in display_cols:
                print(f"      {col}: {row[col]}")
    else:
        print("    [AVISO] Nenhum produto com estoque > 0 encontrado!")

    # 6. INCONSISTÊNCIAS DETECTADAS
    print(f"\n[6] INCONSISTÊNCIAS DETECTADAS")

    issues = []

    # Verificar tipos de dados incorretos
    for col in estoque_cols:
        if not pd.api.types.is_numeric_dtype(df_une1[col]):
            issues.append(f"Coluna '{col}' tem tipo {df_une1[col].dtype} (esperado: numérico)")

    # Verificar valores nulos em colunas críticas
    for col in estoque_cols:
        null_pct = df_une1[col].isna().sum() / len(df_une1) * 100
        if null_pct > 50:
            issues.append(f"Coluna '{col}' tem {null_pct:.1f}% de valores nulos")

    # Verificar valores negativos
    for col in estoque_cols:
        try:
            numeric_vals = pd.to_numeric(df_une1[col], errors='coerce')
            negative_count = (numeric_vals < 0).sum()
            if negative_count > 0:
                issues.append(f"Coluna '{col}' tem {negative_count} valores negativos")
        except:
            pass

    if issues:
        print(f"    Total de inconsistências: {len(issues)}")
        for i, issue in enumerate(issues, 1):
            print(f"    [{i}] {issue}")
    else:
        print("    Nenhuma inconsistência crítica detectada!")

    # 7. SALVAR RELATÓRIO
    print(f"\n[7] SALVANDO RELATÓRIO")

    output_dir = os.path.join(base_path, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Salvar amostra de produtos
    if len(df_with_stock) > 0:
        sample_file = os.path.join(output_dir, f"une1_produtos_amostra_{timestamp}.csv")
        sample_data = df_with_stock.nlargest(20, 'estoque_numeric')
        sample_data.to_csv(sample_file, index=False, encoding='utf-8-sig')
        print(f"    Amostra de produtos salva: {sample_file}")

    # Salvar relatório JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_file": source_file,
        "total_records": len(df),
        "une1_records": len(df_une1),
        "une1_with_stock": len(df_with_stock) if len(df_with_stock) > 0 else 0,
        "stock_percentage": f"{len(df_with_stock)/len(df_une1)*100:.1f}%" if len(df_une1) > 0 else "0%",
        "estoque_columns": estoque_cols,
        "column_types": {col: str(df_une1[col].dtype) for col in estoque_cols},
        "inconsistencies": issues
    }

    report_file = os.path.join(output_dir, f"une1_data_report_{timestamp}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"    Relatório JSON salvo: {report_file}")

    print(f"\n{'='*80}")
    print(f"ANÁLISE CONCLUÍDA")
    print(f"{'='*80}\n")

    return report

if __name__ == "__main__":
    analyze_une1_data()
