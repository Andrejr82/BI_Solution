"""
Testar função get_produtos_une() isoladamente
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from core.connectivity.hybrid_adapter import HybridDataAdapter

print("=" * 80)
print("TESTE: Função get_produtos_une()")
print("=" * 80)

def get_produtos_une(une_id, adapter):
    """Cópia exata da função da página de Transferências"""
    try:
        result = adapter.execute_query({'une': une_id})
        if result:
            df = pd.DataFrame(result)

            print(f"\n[1] DataFrame criado:")
            print(f"  - Shape: {df.shape}")
            print(f"  - Colunas: {list(df.columns)[:10]}...")

            # Selecionar colunas relevantes
            cols_relevantes = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d',
                             'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE']
            cols_existentes = [c for c in cols_relevantes if c in df.columns]

            print(f"\n[2] Colunas selecionadas: {cols_existentes}")

            if cols_existentes:
                df_produtos = df[cols_existentes].copy()

                print(f"\n[3] ANTES da conversão:")
                print(f"  - Tipo estoque_atual: {df_produtos['estoque_atual'].dtype}")
                print(f"  - Amostra: {df_produtos['estoque_atual'].head(3).tolist()}")

                # Converter TODAS as colunas numéricas para garantir
                colunas_numericas = ['estoque_atual', 'venda_30_d', 'preco_38_percent']
                for col in colunas_numericas:
                    if col in df_produtos.columns:
                        df_produtos[col] = pd.to_numeric(df_produtos[col], errors='coerce').fillna(0)

                print(f"\n[4] DEPOIS da conversão:")
                print(f"  - Tipo estoque_atual: {df_produtos['estoque_atual'].dtype}")
                print(f"  - Amostra: {df_produtos['estoque_atual'].head(3).tolist()}")

                # Garantir que estoque_atual existe
                if 'estoque_atual' not in df_produtos.columns:
                    df_produtos['estoque_atual'] = 0

                print(f"\n[5] Filtrando estoque > 0...")
                antes = len(df_produtos)

                # Filtrar apenas produtos com estoque > 0
                df_produtos = df_produtos[df_produtos['estoque_atual'] > 0]

                depois = len(df_produtos)
                print(f"  - Antes: {antes:,} registros")
                print(f"  - Depois: {depois:,} registros")
                print(f"  - Taxa: {(depois/antes*100):.1f}%")

                if depois > 0:
                    print(f"\n[6] OK! {depois:,} produtos retornados")
                    print(f"\n  Top 3 produtos:")
                    top3 = df_produtos.nlargest(3, 'estoque_atual')[['codigo', 'nome_produto', 'estoque_atual']]
                    print(top3.to_string(index=False))

                    return df_produtos.to_dict('records')
                else:
                    print(f"\n[6] ERRO: Nenhum produto após filtro!")
                    return []
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        print(traceback.format_exc())
    return []

# Criar adapter
print("\n[SETUP] Criando adapter...")
adapter = HybridDataAdapter()
print(f"Status: {adapter.get_status()}")

# Testar com UNE 3
print("\n" + "=" * 80)
print("TESTANDO: UNE 3")
print("=" * 80)

produtos = get_produtos_une(3, adapter)

print("\n" + "=" * 80)
print(f"RESULTADO FINAL: {len(produtos)} produtos")
print("=" * 80)

if produtos:
    print("\nSUCESSO! Função está funcionando corretamente.")
else:
    print("\nFALHA! Nenhum produto retornado.")
