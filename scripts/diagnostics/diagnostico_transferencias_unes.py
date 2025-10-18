"""
Script de diagnóstico: Análise de distribuição de produtos por UNE
Objetivo: Investigar por que apenas UNE 1 aparece nas sugestões de transferência
Data: 2025-10-16
"""

import pandas as pd
import pyarrow.parquet as pq
import numpy as np
from datetime import datetime
import json

# Caminho absoluto
PARQUET_PATH = r'C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat_extended.parquet'
OUTPUT_PATH = r'C:\Users\André\Documents\Agent_Solution_BI\data\processed'

def carregar_dados():
    """Carrega e prepara dados do Parquet"""
    print("Carregando dados do Parquet...")
    df = pd.read_parquet(PARQUET_PATH)
    print(f"Total de registros carregados: {len(df)}")
    print(f"Colunas disponíveis: {list(df.columns)}")
    return df

def preparar_dados(df):
    """Normaliza e prepara dados para análise"""
    print("\nPreparando dados...")

    # Normalizar colunas
    if 'estoque_lv' in df.columns and 'linha_verde' not in df.columns:
        df['linha_verde'] = df['estoque_lv']
    if 'media_considerada_lv' in df.columns and 'mc' not in df.columns:
        df['mc'] = df['media_considerada_lv']

    # Converter para numérico
    df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
    df['linha_verde'] = pd.to_numeric(df['linha_verde'], errors='coerce').fillna(0)
    df['mc'] = pd.to_numeric(df.get('mc', 0), errors='coerce').fillna(0)

    # Garantir que 'une' é string
    df['une'] = df['une'].astype(str)

    # Calcular percentual de linha verde
    df['perc_linha_verde'] = 0.0
    mask = df['linha_verde'] > 0
    df.loc[mask, 'perc_linha_verde'] = (df.loc[mask, 'estoque_atual'] / df.loc[mask, 'linha_verde'] * 100)

    # Calcular diferença
    df['diff_linha_verde'] = df['estoque_atual'] - df['linha_verde']

    print(f"Dados preparados: {len(df)} registros válidos")
    return df

def analise_distribuicao_une(df):
    """Analisa distribuição de produtos por UNE"""
    print("\n" + "="*80)
    print("ANÁLISE 1: DISTRIBUIÇÃO POR UNE")
    print("="*80)

    resultado = []

    for une in sorted(df['une'].unique()):
        df_une = df[df['une'] == une]

        # Estatísticas gerais
        total_produtos = len(df_une)
        produtos_com_lv = len(df_une[df_une['linha_verde'] > 0])

        # Produtos com excesso (>100% LV)
        excesso_100 = len(df_une[df_une['perc_linha_verde'] > 100])
        excesso_150 = len(df_une[df_une['perc_linha_verde'] > 150])
        excesso_200 = len(df_une[df_une['perc_linha_verde'] > 200])

        # Produtos com deficit (<75% LV)
        deficit_75 = len(df_une[df_une['perc_linha_verde'] < 75])
        deficit_50 = len(df_une[df_une['perc_linha_verde'] < 50])
        deficit_25 = len(df_une[df_une['perc_linha_verde'] < 25])

        # Produtos na faixa ideal (75-100%)
        ideal = len(df_une[(df_une['perc_linha_verde'] >= 75) & (df_une['perc_linha_verde'] <= 100)])

        resultado.append({
            'UNE': une,
            'Total_Produtos': total_produtos,
            'Com_LV': produtos_com_lv,
            'Excesso_>100%': excesso_100,
            'Excesso_>150%': excesso_150,
            'Excesso_>200%': excesso_200,
            'Ideal_75-100%': ideal,
            'Deficit_<75%': deficit_75,
            'Deficit_<50%': deficit_50,
            'Deficit_<25%': deficit_25
        })

    df_result = pd.DataFrame(resultado)
    print(df_result.to_string(index=False))

    return df_result

def analise_produtos_multiplas_unes(df):
    """Identifica produtos que aparecem em múltiplas UNEs"""
    print("\n" + "="*80)
    print("ANÁLISE 2: PRODUTOS EM MÚLTIPLAS UNEs")
    print("="*80)

    # Agrupar por código de produto
    produtos_por_une = df.groupby('codigo')['une'].apply(lambda x: sorted(x.unique())).reset_index()
    produtos_por_une['num_unes'] = produtos_por_une['une'].apply(len)

    print(f"\nTotal de produtos únicos: {len(produtos_por_une)}")
    print(f"Produtos em 1 UNE: {len(produtos_por_une[produtos_por_une['num_unes'] == 1])}")
    print(f"Produtos em 2+ UNEs: {len(produtos_por_une[produtos_por_une['num_unes'] > 1])}")

    # Produtos em múltiplas UNEs
    mult_unes = produtos_por_une[produtos_por_une['num_unes'] > 1].sort_values('num_unes', ascending=False)

    if len(mult_unes) > 0:
        print(f"\nTop 10 produtos com mais UNEs:")
        print(mult_unes.head(10).to_string(index=False))

    return produtos_por_une

def analise_excesso_deficit(df):
    """Analisa produtos com excesso vs deficit por UNE"""
    print("\n" + "="*80)
    print("ANÁLISE 3: PRODUTOS COM EXCESSO E DEFICIT")
    print("="*80)

    # Produtos com excesso significativo (>150% LV)
    df_excesso = df[df['perc_linha_verde'] > 150].copy()

    if len(df_excesso) > 0:
        print(f"\nProdutos com EXCESSO (>150% LV): {len(df_excesso)}")
        excesso_por_une = df_excesso.groupby('une').size().reset_index(name='count')
        print("\nDistribuição de excesso por UNE:")
        print(excesso_por_une.to_string(index=False))

        # Top produtos com excesso
        df_excesso['excesso_unidades'] = df_excesso['diff_linha_verde']
        top_excesso = df_excesso.nlargest(10, 'excesso_unidades')[
            ['codigo', 'descricao', 'une', 'estoque_atual', 'linha_verde', 'perc_linha_verde', 'excesso_unidades']
        ]
        print("\nTop 10 produtos com maior excesso:")
        print(top_excesso.to_string(index=False))
    else:
        print("\nNenhum produto com excesso >150% encontrado!")

    # Produtos com deficit significativo (<50% LV)
    df_deficit = df[df['perc_linha_verde'] < 50].copy()

    if len(df_deficit) > 0:
        print(f"\n\nProdutos com DEFICIT (<50% LV): {len(df_deficit)}")
        deficit_por_une = df_deficit.groupby('une').size().reset_index(name='count')
        print("\nDistribuição de deficit por UNE:")
        print(deficit_por_une.to_string(index=False))

        # Top produtos com deficit
        df_deficit['deficit_unidades'] = abs(df_deficit['diff_linha_verde'])
        top_deficit = df_deficit.nlargest(10, 'deficit_unidades')[
            ['codigo', 'descricao', 'une', 'estoque_atual', 'linha_verde', 'perc_linha_verde', 'deficit_unidades']
        ]
        print("\nTop 10 produtos com maior deficit:")
        print(top_deficit.to_string(index=False))
    else:
        print("\n\nNenhum produto com deficit <50% encontrado!")

    return df_excesso, df_deficit

def analise_oportunidades_transferencia(df):
    """Identifica oportunidades de transferência entre UNEs"""
    print("\n" + "="*80)
    print("ANÁLISE 4: OPORTUNIDADES DE TRANSFERÊNCIA")
    print("="*80)

    oportunidades = []

    # Agrupar por código de produto
    for codigo in df['codigo'].unique():
        df_produto = df[df['codigo'] == codigo]

        # Precisa estar em pelo menos 2 UNEs
        if len(df_produto) < 2:
            continue

        # Identificar UNEs com excesso e deficit
        unes_excesso = df_produto[df_produto['perc_linha_verde'] > 120]
        unes_deficit = df_produto[df_produto['perc_linha_verde'] < 80]

        if len(unes_excesso) > 0 and len(unes_deficit) > 0:
            for _, row_excesso in unes_excesso.iterrows():
                for _, row_deficit in unes_deficit.iterrows():
                    if row_excesso['une'] != row_deficit['une']:
                        qtd_transferir = min(
                            row_excesso['estoque_atual'] - row_excesso['linha_verde'],
                            row_deficit['linha_verde'] - row_deficit['estoque_atual']
                        )

                        if qtd_transferir > 0:
                            oportunidades.append({
                                'codigo': codigo,
                                'descricao': row_excesso['descricao'],
                                'origem_une': row_excesso['une'],
                                'origem_estoque': row_excesso['estoque_atual'],
                                'origem_lv': row_excesso['linha_verde'],
                                'origem_perc': row_excesso['perc_linha_verde'],
                                'destino_une': row_deficit['une'],
                                'destino_estoque': row_deficit['estoque_atual'],
                                'destino_lv': row_deficit['linha_verde'],
                                'destino_perc': row_deficit['perc_linha_verde'],
                                'qtd_transferir': qtd_transferir
                            })

    if len(oportunidades) > 0:
        df_oportunidades = pd.DataFrame(oportunidades)
        df_oportunidades = df_oportunidades.sort_values('qtd_transferir', ascending=False)

        print(f"\nTotal de oportunidades identificadas: {len(df_oportunidades)}")

        # Distribuição por UNE de origem
        print("\nUNEs de ORIGEM (com excesso):")
        origem_dist = df_oportunidades.groupby('origem_une').size().reset_index(name='count')
        print(origem_dist.to_string(index=False))

        # Distribuição por UNE de destino
        print("\nUNEs de DESTINO (com deficit):")
        destino_dist = df_oportunidades.groupby('destino_une').size().reset_index(name='count')
        print(destino_dist.to_string(index=False))

        # Top 20 oportunidades
        print("\nTop 20 oportunidades de transferência:")
        print(df_oportunidades.head(20).to_string(index=False))

        return df_oportunidades
    else:
        print("\nNENHUMA OPORTUNIDADE DE TRANSFERÊNCIA IDENTIFICADA!")
        print("Possíveis causas:")
        print("1. Nenhum produto aparece em múltiplas UNEs")
        print("2. Não há combinação de excesso/deficit nos mesmos produtos")
        print("3. Thresholds muito restritivos (>120% e <80%)")
        return None

def salvar_relatorio(df_dist, df_oportunidades):
    """Salva relatório em JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_PATH}/diagnostico_transferencias_{timestamp}.json"

    relatorio = {
        'timestamp': timestamp,
        'distribuicao_une': df_dist.to_dict(orient='records'),
        'oportunidades': df_oportunidades.to_dict(orient='records') if df_oportunidades is not None else []
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório salvo em: {output_file}")
    return output_file

def main():
    """Execução principal"""
    print("DIAGNÓSTICO DE TRANSFERÊNCIAS - ANÁLISE POR UNE")
    print("="*80)

    # Carregar e preparar dados
    df = carregar_dados()
    df = preparar_dados(df)

    # Executar análises
    df_dist = analise_distribuicao_une(df)
    produtos_unes = analise_produtos_multiplas_unes(df)
    df_excesso, df_deficit = analise_excesso_deficit(df)
    df_oportunidades = analise_oportunidades_transferencia(df)

    # Salvar relatório
    salvar_relatorio(df_dist, df_oportunidades)

    # Diagnóstico final
    print("\n" + "="*80)
    print("DIAGNÓSTICO FINAL")
    print("="*80)

    if df_oportunidades is None or len(df_oportunidades) == 0:
        print("\nPROBLEMA IDENTIFICADO: Nenhuma oportunidade de transferência encontrada!")
        print("\nPossíveis causas:")
        print("1. Produtos não estão duplicados em múltiplas UNEs")
        print("2. Não há padrão de excesso em uma UNE e deficit em outra")
        print("3. Dados de linha_verde podem estar incorretos ou zerados")
        print("4. Thresholds de excesso/deficit muito restritivos")
    else:
        origem_unes = df_oportunidades['origem_une'].unique()
        print(f"\nUNEs com produtos em EXCESSO: {sorted(origem_unes)}")

        if len(origem_unes) == 1 and '1' in origem_unes:
            print("\nPROBLEMA IDENTIFICADO: Apenas UNE 1 tem produtos com excesso!")
            print("Isso explica por que apenas UNE 1 aparece nas sugestões.")
            print("\nVerificar:")
            print("- Por que outras UNEs não têm estoque acima da linha verde?")
            print("- Os dados de estoque estão corretos para outras UNEs?")
            print("- A linha verde está calibrada corretamente?")

if __name__ == "__main__":
    main()
