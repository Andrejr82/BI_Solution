"""
Diagnóstico do problema de sugestões automáticas limitadas à UNE 1
Autor: UNE Operations Agent
Data: 2025-10-16
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from core.tools.une_tools import sugerir_transferencias_automaticas
import json

def diagnosticar_sugestoes():
    """Diagnostica o problema de sugestões automáticas"""

    print("=" * 80)
    print("DIAGNÓSTICO: SUGESTÕES AUTOMÁTICAS - PROBLEMA UNE 1")
    print("=" * 80)

    # Teste 1: Sem filtros
    print("\n[TESTE 1] Sugestões sem filtros:")
    resultado1 = sugerir_transferencias_automaticas(
        une_destino_id=1,
        limite=5
    )

    if resultado1['status'] == 'success':
        print(f"Total sugestões: {len(resultado1['sugestoes'])}")
        for sug in resultado1['sugestoes']:
            print(f"  - Produto: {sug['produto_nome'][:50]}")
            print(f"    Origem: UNE {sug['une_origem_id']} | Destino: UNE {sug['une_destino_id']}")
            print(f"    Estoque origem: {sug['estoque_origem']} | Deficit destino: {sug['deficit_destino']}")

    # Teste 2: Com filtro de segmento
    print("\n[TESTE 2] Sugestões com filtro segmento='MOVEIS':")
    resultado2 = sugerir_transferencias_automaticas(
        une_destino_id=1,
        segmento='MOVEIS',
        limite=5
    )

    if resultado2['status'] == 'success':
        print(f"Total sugestões: {len(resultado2['sugestoes'])}")
        for sug in resultado2['sugestoes']:
            print(f"  - Produto: {sug['produto_nome'][:50]}")
            print(f"    Origem: UNE {sug['une_origem_id']} | Segmento: {sug.get('segmento', 'N/A')}")

    # Teste 3: Verificar distribuição de UNEs origem
    print("\n[TESTE 3] Distribuição de UNEs de origem:")
    resultado3 = sugerir_transferencias_automaticas(
        une_destino_id=1,
        limite=50  # Pegar mais sugestões
    )

    if resultado3['status'] == 'success':
        unes_origem = {}
        for sug in resultado3['sugestoes']:
            une_id = sug['une_origem_id']
            unes_origem[une_id] = unes_origem.get(une_id, 0) + 1

        print("Contagem por UNE origem:")
        for une_id, count in sorted(unes_origem.items()):
            print(f"  UNE {une_id}: {count} sugestões")

    # Teste 4: Verificar dados brutos do Parquet
    print("\n[TESTE 4] Verificando dados brutos do Parquet:")
    try:
        caminho_parquet = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'parquet',
            'admmat.parquet'
        )
        df = pd.read_parquet(caminho_parquet)

        print(f"Total produtos no Parquet: {len(df)}")
        print(f"Colunas: {list(df.columns)}")

        # Verificar distribuição de produtos por UNE
        if 'une_id' in df.columns:
            print("\nDistribuição de produtos por UNE:")
            dist_une = df['une_id'].value_counts().sort_index()
            for une_id, count in dist_une.items():
                print(f"  UNE {une_id}: {count} produtos")

        # Verificar se existe coluna de estoque
        colunas_estoque = [col for col in df.columns if 'estoque' in col.lower()]
        print(f"\nColunas de estoque encontradas: {colunas_estoque}")

        # Verificar produtos com estoque > 0
        if 'estoque' in df.columns:
            df_estoque = df[df['estoque'] > 0]
            print(f"\nProdutos com estoque > 0: {len(df_estoque)}")
            dist_estoque_une = df_estoque['une_id'].value_counts().sort_index()
            print("Distribuição de produtos com estoque por UNE:")
            for une_id, count in dist_estoque_une.items():
                print(f"  UNE {une_id}: {count} produtos")

    except Exception as e:
        print(f"Erro ao carregar Parquet: {e}")

    # Teste 5: Verificar lógica de cálculo de deficit/superavit
    print("\n[TESTE 5] Análise de deficit/superavit:")
    try:
        df = pd.read_parquet(caminho_parquet)

        # Produtos com linha_verde > 0
        if 'linha_verde' in df.columns and 'estoque' in df.columns:
            df['deficit'] = df['linha_verde'] - df['estoque']

            # Produtos com deficit (precisam receber)
            df_deficit = df[df['deficit'] > 0]
            print(f"Produtos com deficit: {len(df_deficit)}")

            # Produtos com superavit (podem doar)
            df_superavit = df[df['deficit'] < 0]
            print(f"Produtos com superavit: {len(df_superavit)}")

            # Verificar distribuição por UNE
            print("\nDistribuição de deficit por UNE:")
            dist_deficit = df_deficit.groupby('une_id').size()
            for une_id, count in dist_deficit.items():
                print(f"  UNE {une_id}: {count} produtos em deficit")

            print("\nDistribuição de superavit por UNE:")
            dist_superavit = df_superavit.groupby('une_id').size()
            for une_id, count in dist_superavit.items():
                print(f"  UNE {une_id}: {count} produtos em superavit")

    except Exception as e:
        print(f"Erro na análise: {e}")

    print("\n" + "=" * 80)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    diagnosticar_sugestoes()
