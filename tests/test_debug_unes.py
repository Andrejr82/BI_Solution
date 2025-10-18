"""
Script de debug: Investigar por que nenhuma UNE retorna produtos
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("DEBUG: Problema 'Nenhum produto com estoque' em TODAS as UNEs")
print("=" * 80)

# 1. Verificar arquivo Parquet
print("\n[1] Verificando arquivo Parquet...")
parquet_path = Path('data/parquet')
if (parquet_path / 'admmat_extended.parquet').exists():
    parquet_file = parquet_path / 'admmat_extended.parquet'
    print(f"OK Usando: {parquet_file}")
elif (parquet_path / 'admmat.parquet').exists():
    parquet_file = parquet_path / 'admmat.parquet'
    print(f"OK Usando: {parquet_file}")
else:
    print("ERRO: Nenhum arquivo Parquet encontrado!")
    sys.exit(1)

# 2. Carregar dados
print("\n[2] Carregando dados...")
df = pd.read_parquet(parquet_file)
print(f"OK Total de registros: {len(df):,}")
print(f"OK Colunas disponiveis: {len(df.columns)}")

# 3. Verificar UNEs
print("\n[3] UNEs disponiveis:")
unes = sorted(df['une'].unique())
print(f"OK Total de UNEs: {len(unes)}")
print(f"OK UNEs: {unes[:10]}...")

# 4. Verificar colunas de estoque
print("\n[4] Colunas relacionadas a estoque:")
colunas_estoque = [col for col in df.columns if 'estoque' in col.lower()]
print(f"Colunas encontradas: {colunas_estoque}")

for col in colunas_estoque:
    print(f"\n  - {col}:")
    print(f"    Tipo: {df[col].dtype}")
    print(f"    Valores únicos: {df[col].nunique():,}")
    print(f"    Nulos: {df[col].isna().sum():,}")
    print(f"    Amostra: {df[col].head(3).tolist()}")

# 5. Testar UNE especifica
print("\n[5] Testando UNE 3 (exemplo)...")
df_une3 = df[df['une'] == 3].copy()
print(f"OK Registros UNE 3: {len(df_une3):,}")

if 'estoque_atual' in df_une3.columns:
    print(f"\n  Análise estoque_atual:")
    print(f"  - Tipo original: {df_une3['estoque_atual'].dtype}")
    print(f"  - Amostra (5 primeiros): {df_une3['estoque_atual'].head().tolist()}")

    # Tentar conversão
    print(f"\n  Tentando conversão numérica...")
    df_une3['estoque_num'] = pd.to_numeric(df_une3['estoque_atual'], errors='coerce')
    print(f"  - Tipo após conversão: {df_une3['estoque_num'].dtype}")
    print(f"  - Amostra convertida: {df_une3['estoque_num'].head().tolist()}")

    # Filtrar > 0
    print(f"\n  Filtrando estoque > 0...")
    antes = len(df_une3)
    df_une3_filtrado = df_une3[df_une3['estoque_num'] > 0]
    depois = len(df_une3_filtrado)

    print(f"  - Antes do filtro: {antes:,} registros")
    print(f"  - Depois do filtro: {depois:,} registros")
    print(f"  - Taxa: {(depois/antes*100):.1f}%")

    if depois > 0:
        print(f"\n  OK SUCESSO! {depois:,} produtos com estoque encontrados na UNE 3")
        print(f"\n  Top 5 produtos com maior estoque:")
        top5 = df_une3_filtrado.nlargest(5, 'estoque_num')[['codigo', 'nome_produto', 'estoque_num']]
        print(top5.to_string(index=False))
    else:
        print(f"\n  ERRO: Nenhum produto com estoque > 0 apos conversao!")
        print(f"  Valores unicos de estoque_num: {df_une3['estoque_num'].unique()[:20]}")
else:
    print(f"  ERRO: Coluna 'estoque_atual' nao encontrada!")
    print(f"  Colunas disponiveis: {df_une3.columns.tolist()}")

# 6. Testar HybridAdapter
print("\n" + "=" * 80)
print("[6] Testando HybridAdapter...")
print("=" * 80)

try:
    from core.connectivity.hybrid_adapter import HybridDataAdapter

    adapter = HybridDataAdapter()
    print(f"OK Adapter criado")
    print(f"OK Status: {adapter.get_status()}")

    print(f"\n  Executando query: {{'une': 3}}")
    result = adapter.execute_query({'une': 3})

    if isinstance(result, dict) and 'error' in result:
        print(f"  ERRO retornado: {result['error']}")
    elif isinstance(result, list):
        print(f"  OK Resultado: lista com {len(result):,} registros")

        if len(result) > 0:
            df_result = pd.DataFrame(result)
            print(f"\n  Colunas retornadas: {list(df_result.columns)}")

            if 'estoque_atual' in df_result.columns:
                print(f"\n  Tipo de 'estoque_atual': {df_result['estoque_atual'].dtype}")
                print(f"  Amostra: {df_result['estoque_atual'].head(3).tolist()}")

                # Verificar se precisa conversao
                if df_result['estoque_atual'].dtype == 'object':
                    print(f"\n  ALERTA: estoque_atual eh STRING (object)!")
                    print(f"  Isso explica por que o filtro > 0 nao funciona!")
            else:
                print(f"  ERRO: Coluna 'estoque_atual' nao existe no resultado!")
        else:
            print(f"  ALERTA: Resultado vazio!")
    else:
        print(f"  ERRO: Tipo inesperado: {type(result)}")

except Exception as e:
    print(f"  ERRO ao testar adapter: {e}")
    import traceback
    print(traceback.format_exc())

print("\n" + "=" * 80)
print("FIM DO DEBUG")
print("=" * 80)
