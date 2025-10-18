"""Teste rápido e correção da página Transferências"""
import pandas as pd
from pathlib import Path

# Testar ParquetAdapter
from core.connectivity.parquet_adapter import ParquetAdapter

adapter = ParquetAdapter('data/parquet/admmat_extended.parquet')
result = adapter.execute_query({'une': 1})

df = pd.DataFrame(result)
print(f"✓ {len(result)} registros UNE 1")

# Verificar colunas
print(f"\nColunas disponíveis: {df.columns.tolist()[:15]}")

# Testar conversão
df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
df_com_estoque = df[df['estoque_atual'] > 0]

print(f"\n✓ Tipo após conversão: {df['estoque_atual'].dtype}")
print(f"✓ Produtos com estoque: {len(df_com_estoque)}")
print(f"\nTop 3 produtos:")
print(df_com_estoque.nlargest(3, 'estoque_atual')[['codigo', 'nome_produto', 'estoque_atual']])

# SOLUÇÃO: O problema é que cols_relevantes não encontra as colunas porque estão em formatos diferentes
# Vou criar a versão corrigida da função

codigo_corrigido = '''
def get_produtos_une(une_id):
    try:
        result = adapter.execute_query({'une': une_id})
        if not result:
            return []

        df = pd.DataFrame(result)

        # Garantir que temos as colunas mínimas
        if 'estoque_atual' not in df.columns or 'codigo' not in df.columns:
            return []

        # Converter estoque para numérico
        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)

        # Filtrar produtos com estoque
        df = df[df['estoque_atual'] > 0]

        # Selecionar colunas (usar só as que existem)
        colunas_retorno = ['codigo', 'nome_produto', 'estoque_atual']
        if 'venda_30_d' in df.columns:
            colunas_retorno.append('venda_30_d')
            df['venda_30_d'] = pd.to_numeric(df['venda_30_d'], errors='coerce').fillna(0)
        if 'preco_38_percent' in df.columns:
            colunas_retorno.append('preco_38_percent')
            df['preco_38_percent'] = pd.to_numeric(df['preco_38_percent'], errors='coerce').fillna(0)
        if 'nomesegmento' in df.columns:
            colunas_retorno.append('nomesegmento')
        if 'NOMEFABRICANTE' in df.columns:
            colunas_retorno.append('NOMEFABRICANTE')

        return df[colunas_retorno].to_dict('records')
    except Exception as e:
        st.error(f"Erro: {e}")
        return []
'''

print("\n" + "="*60)
print("CÓDIGO CORRIGIDO PRONTO")
print("="*60)
print(codigo_corrigido)
