"""
Data Agent - Processamento ADMMAT com Colunas UNE (VERSÃO OTIMIZADA)
Usa operações vetorizadas do pandas para máxima performance
"""

import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def processar_admmat():
    """
    Função principal de processamento - VERSÃO VETORIZADA
    """
    inicio = time.time()

    # Caminhos
    input_path = r"C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet"
    output_path = r"C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat_extended.parquet"

    logger.info(f"Iniciando leitura de: {input_path}")

    # Verificar se arquivo existe
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    # Ler Parquet
    df = pd.read_parquet(input_path)
    logger.info(f"Arquivo lido com sucesso: {len(df)} linhas, {len(df.columns)} colunas")

    # Backup das colunas originais
    colunas_originais = df.columns.tolist()

    # 1. Calcular MC (VETORIZADO)
    logger.info("Calculando coluna MC...")
    df['mc'] = pd.to_numeric(df.get('venda_30_d', 0), errors='coerce').fillna(0) * 1.2

    # 2. Calcular Linha Verde (VETORIZADO)
    logger.info("Calculando coluna linha_verde...")
    estoque_atual = pd.to_numeric(df.get('estoque_atual', 0), errors='coerce').fillna(0)
    estoque_gondola = pd.to_numeric(df.get('estoque_gondola_lv', 0), errors='coerce').fillna(0)
    estoque_ilha = pd.to_numeric(df.get('estoque_ilha_lv', 0), errors='coerce').fillna(0)
    df['linha_verde'] = estoque_atual + estoque_gondola + estoque_ilha

    # 3. Mapear Ranking (VETORIZADO)
    logger.info("Mapeando coluna ranking...")
    if 'nomesegmento' in df.columns:
        df['ranking'] = 1  # Padrão
        df.loc[df['nomesegmento'].str.contains('TECIDO', case=False, na=False), 'ranking'] = 0
        df.loc[df['nomesegmento'].str.contains('PAPELARIA', case=False, na=False), 'ranking'] = 1
        df.loc[df['nomesegmento'].str.contains('ARMARINHO|CONFEC', case=False, na=False), 'ranking'] = 2
    else:
        logger.warning("Coluna 'nomesegmento' não encontrada. Usando ranking padrão = 1")
        df['ranking'] = 1

    # 4. Calcular precisa_abastecimento (VETORIZADO)
    logger.info("Calculando coluna precisa_abastecimento...")
    df['precisa_abastecimento'] = estoque_atual <= (df['linha_verde'] * 0.5)

    # 5. Calcular qtd_a_abastecer (VETORIZADO)
    logger.info("Calculando coluna qtd_a_abastecer...")
    df['qtd_a_abastecer'] = np.maximum(0, df['linha_verde'] - estoque_atual)

    # 6. Calcular preco_varejo (VETORIZADO)
    logger.info("Calculando coluna preco_varejo...")
    preco_base = pd.to_numeric(df.get('preco_38_percent', 0), errors='coerce').fillna(0)

    # Multiplicadores por ranking
    df['preco_varejo'] = preco_base  # Padrão
    df.loc[df['ranking'] == 0, 'preco_varejo'] = preco_base * 1.30
    df.loc[df['ranking'] == 1, 'preco_varejo'] = preco_base * 1.00
    df.loc[df['ranking'] == 2, 'preco_varejo'] = preco_base * 1.30
    df.loc[df['ranking'] == 3, 'preco_varejo'] = preco_base * 1.00
    df.loc[df['ranking'] == 4, 'preco_varejo'] = preco_base * 1.24

    # 7. Calcular preco_atacado (VETORIZADO)
    logger.info("Calculando coluna preco_atacado...")
    df['preco_atacado'] = preco_base

    # Garantir tipos corretos
    df['mc'] = df['mc'].astype(float).round(2)
    df['linha_verde'] = df['linha_verde'].astype(float).round(2)
    df['ranking'] = df['ranking'].astype(int)
    df['precisa_abastecimento'] = df['precisa_abastecimento'].astype(bool)
    df['qtd_a_abastecer'] = df['qtd_a_abastecer'].astype(float).round(2)
    df['preco_varejo'] = df['preco_varejo'].astype(float).round(2)
    df['preco_atacado'] = df['preco_atacado'].astype(float).round(2)

    # Salvar resultado
    logger.info(f"Salvando resultado em: {output_path}")
    df.to_parquet(output_path, index=False, compression='snappy')

    tempo_total = time.time() - inicio
    tamanho_arquivo = os.path.getsize(output_path) / (1024 * 1024)  # MB

    # Gerar relatório
    logger.info("Gerando relatório...")

    print("\n" + "="*80)
    print("RELATÓRIO DE PROCESSAMENTO - DATA AGENT (VERSÃO OTIMIZADA)")
    print("="*80)
    print(f"\nArquivo de entrada: {input_path}")
    print(f"Arquivo de saída: {output_path}")
    print(f"Data/Hora processamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n" + "-"*80)
    print("1. TOTAL DE LINHAS PROCESSADAS")
    print("-"*80)
    print(f"Total de registros: {len(df):,}")
    print(f"Colunas originais: {len(colunas_originais)}")
    print(f"Colunas adicionadas: 7")
    print(f"Total de colunas final: {len(df.columns)}")

    print("\n" + "-"*80)
    print("2. AMOSTRA DE 5 PRODUTOS")
    print("-"*80)

    # Selecionar 5 produtos aleatórios
    amostra = df.sample(min(5, len(df)))

    # Colunas para exibir
    colunas_exibir = ['codigo', 'nome_produto', 'nomesegmento', 'estoque_atual',
                      'mc', 'linha_verde', 'ranking', 'precisa_abastecimento',
                      'qtd_a_abastecer', 'preco_38_percent', 'preco_varejo', 'preco_atacado']

    # Filtrar apenas colunas que existem
    colunas_exibir = [col for col in colunas_exibir if col in df.columns]

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 40)

    print(amostra[colunas_exibir].to_string(index=False))

    print("\n" + "-"*80)
    print("3. ESTATÍSTICAS")
    print("-"*80)

    # Média de MC
    media_mc = df['mc'].mean()
    print(f"\nMédia de MC: {media_mc:.2f}")
    print(f"MC Mínimo: {df['mc'].min():.2f}")
    print(f"MC Máximo: {df['mc'].max():.2f}")
    print(f"MC Mediana: {df['mc'].median():.2f}")

    # Produtos que precisam abastecimento
    total_precisa = df['precisa_abastecimento'].sum()
    percentual_precisa = (total_precisa / len(df)) * 100
    print(f"\nTotal de produtos que precisam abastecimento: {total_precisa:,} ({percentual_precisa:.1f}%)")

    # Distribuição de ranking
    print("\nDistribuição de Ranking:")
    ranking_dist = df['ranking'].value_counts().sort_index()
    ranking_labels = {
        0: "TECIDOS",
        1: "PAPELARIA/PADRÃO",
        2: "ARMARINHO/CONFECÇÃO",
        3: "SEM DESCONTO",
        4: "ESPECIAL"
    }

    for ranking_val, count in ranking_dist.items():
        label = ranking_labels.get(ranking_val, f"Ranking {ranking_val}")
        percentual = (count / len(df)) * 100
        print(f"  {label} (ranking={ranking_val}): {count:,} produtos ({percentual:.1f}%)")

    # Estatísticas de abastecimento
    print("\nEstatísticas de Abastecimento:")
    print(f"  Quantidade média a abastecer: {df['qtd_a_abastecer'].mean():.2f}")
    print(f"  Quantidade total a abastecer: {df['qtd_a_abastecer'].sum():.2f}")
    print(f"  Produtos com qtd > 0: {(df['qtd_a_abastecer'] > 0).sum():,}")

    # Estatísticas de preços
    print("\nEstatísticas de Preços:")
    print(f"  Preço varejo médio: R$ {df['preco_varejo'].mean():.2f}")
    print(f"  Preço atacado médio: R$ {df['preco_atacado'].mean():.2f}")
    print(f"  Diferença média (varejo - atacado): R$ {(df['preco_varejo'] - df['preco_atacado']).mean():.2f}")

    print("\n" + "-"*80)
    print("4. TEMPO DE PROCESSAMENTO")
    print("-"*80)
    print(f"Tempo total: {tempo_total:.2f} segundos")
    print(f"Registros por segundo: {len(df)/tempo_total:.0f}")

    print("\n" + "-"*80)
    print("5. TAMANHO DO ARQUIVO GERADO")
    print("-"*80)
    print(f"Tamanho: {tamanho_arquivo:.2f} MB")

    print("\n" + "="*80)
    print("COLUNAS ADICIONADAS:")
    print("="*80)
    colunas_novas = ['mc', 'linha_verde', 'ranking', 'precisa_abastecimento',
                     'qtd_a_abastecer', 'preco_varejo', 'preco_atacado']

    for col in colunas_novas:
        tipo = df[col].dtype
        nulos = df[col].isna().sum()
        print(f"  ✅ [{col}] - Tipo: {tipo}, Nulos: {nulos}")

    print("\n" + "="*80)
    print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print("="*80)

    return df

if __name__ == "__main__":
    try:
        df_resultado = processar_admmat()
    except Exception as e:
        logger.error(f"Erro durante processamento: {str(e)}", exc_info=True)
        raise
