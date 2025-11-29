#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import polars as pl

# Carregar dados
df = pl.read_parquet('data/parquet/admmat.parquet')

print("="*80)
print("ANALISE DO PARQUET - admmat.parquet")
print("="*80)

print(f"\nTotal de produtos: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n" + "="*80)
print("COLUNAS RELACIONADAS A PRECO/CUSTO/VALOR:")
print("="*80)
preco_cols = [col for col in df.columns if any(x in col.upper() for x in ['PRECO', 'CUSTO', 'VALOR', 'LIQUIDO', 'VENDA'])]
for col in preco_cols:
    print(f"  - {col}")

print("\n" + "="*80)
print("BUSCANDO PRODUTO 59294:")
print("="*80)

produto = df.filter(pl.col('PRODUTO') == 59294)

if len(produto) > 0:
    print(f"\nProduto encontrado! Total de registros: {len(produto)}")
    print("\nDADOS DO PRODUTO:")

    # Colunas principais
    colunas_principais = ['PRODUTO', 'NOME', 'UNE', 'UNE_NOME', 'LIQUIDO_38',
                          'ULTIMA_ENTRADA_CUSTO_CD', 'ESTOQUE_UNE', 'VENDA_30DD']

    for col in colunas_principais:
        if col in produto.columns:
            valor = produto[col][0]
            print(f"  {col}: {valor}")

    print("\n" + "="*80)
    print("INTERPRETACAO:")
    print("="*80)

    if 'LIQUIDO_38' in produto.columns:
        liquido = produto['LIQUIDO_38'][0]
        print(f"  LIQUIDO_38 (possivel preco): {liquido}")

    if 'ULTIMA_ENTRADA_CUSTO_CD' in produto.columns:
        custo = produto['ULTIMA_ENTRADA_CUSTO_CD'][0]
        print(f"  ULTIMA_ENTRADA_CUSTO_CD (custo): {custo}")

else:
    print("\nProduto 59294 NAO ENCONTRADO!")
    print("\nPrimeiros 5 produtos disponiveis:")
    print(df.select(['PRODUTO', 'NOME']).head(5))

print("\n" + "="*80)
