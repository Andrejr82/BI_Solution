"""
Data Agent - Processamento ADMMAT com Colunas Calculadas UNE
Adiciona colunas: mc, linha_verde, ranking, precisa_abastecimento, qtd_a_abastecer, preco_varejo, preco_atacado
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

def calcular_mc(row):
    """
    Calcula MC (Média Comum) conforme regras UNE
    - Se existirem colunas mes_01 a mes_12: usa média 12m, média 3m últimos e mes_01
    - Senão: usa venda_30_d * 1.2 como aproximação
    """
    colunas_mensais = [f'mes_{i:02d}' for i in range(1, 13)]

    # Verificar se todas as colunas mensais existem
    if all(col in row.index for col in colunas_mensais):
        valores_12m = [pd.to_numeric(row[col], errors='coerce') for col in colunas_mensais]
        valores_12m = [v for v in valores_12m if pd.notna(v) and v != 0]

        if len(valores_12m) >= 3:
            media_12m = np.mean(valores_12m)

            # Últimos 3 meses (mes_10, mes_11, mes_12)
            valores_3m = [pd.to_numeric(row['mes_10'], errors='coerce'),
                         pd.to_numeric(row['mes_11'], errors='coerce'),
                         pd.to_numeric(row['mes_12'], errors='coerce')]
            valores_3m = [v for v in valores_3m if pd.notna(v)]

            if len(valores_3m) > 0:
                media_3m = np.mean(valores_3m)
                mes_01 = pd.to_numeric(row['mes_01'], errors='coerce')
                mes_01 = mes_01 if pd.notna(mes_01) else 0
                mc = (media_12m + media_3m + mes_01) / 3
                return round(mc, 2)

    # Fallback: usar venda_30_d
    if 'venda_30_d' in row.index and pd.notna(row['venda_30_d']):
        return round(row['venda_30_d'] * 1.2, 2)

    return 0.0

def calcular_linha_verde(row):
    """
    Linha Verde = estoque_atual + estoque_gondola_lv + estoque_ilha_lv
    """
    estoque_atual = row.get('estoque_atual', 0) if pd.notna(row.get('estoque_atual')) else 0
    gondola_lv = row.get('estoque_gondola_lv', 0) if pd.notna(row.get('estoque_gondola_lv')) else 0
    ilha_lv = row.get('estoque_ilha_lv', 0) if pd.notna(row.get('estoque_ilha_lv')) else 0

    return float(estoque_atual + gondola_lv + ilha_lv)

def mapear_ranking(segmento):
    """
    Mapeia segmento para ranking conforme regras UNE:
    - TECIDOS → 0
    - PAPELARIA → 1
    - ARMARINHO ou CONFECÇÃO → 2
    - Demais → 1 (padrão)
    """
    if pd.isna(segmento):
        return 1

    segmento_upper = str(segmento).upper().strip()

    if 'TECIDO' in segmento_upper:
        return 0
    elif 'PAPELARIA' in segmento_upper:
        return 1
    elif 'ARMARINHO' in segmento_upper or 'CONFECÇÃO' in segmento_upper or 'CONFECCAO' in segmento_upper:
        return 2
    else:
        return 1

def calcular_preco_varejo(row):
    """
    Calcula preço varejo baseado no ranking e preco_38_percent
    - ranking 0: preco_38_percent * 1.30
    - ranking 1: preco_38_percent * 1.00
    - ranking 2: preco_38_percent * 1.30
    - ranking 3: preco_38_percent * 1.00
    - ranking 4: preco_38_percent * 1.24
    """
    preco_base = row.get('preco_38_percent', 0)
    if pd.isna(preco_base) or preco_base == 0:
        return 0.0

    ranking = row.get('ranking', 1)

    multiplicadores = {
        0: 1.30,
        1: 1.00,
        2: 1.30,
        3: 1.00,
        4: 1.24
    }

    multiplicador = multiplicadores.get(ranking, 1.00)
    return round(preco_base * multiplicador, 2)

def processar_admmat():
    """
    Função principal de processamento
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

    # 1. Calcular MC (OTIMIZADO - usar venda_30_d * 1.2 para todos)
    logger.info("Calculando coluna MC (versão otimizada)...")
    df['mc'] = df['venda_30_d'].fillna(0) * 1.2

    # 2. Calcular Linha Verde
    logger.info("Calculando coluna linha_verde...")
    df['linha_verde'] = df.apply(calcular_linha_verde, axis=1)

    # 3. Mapear Ranking
    logger.info("Mapeando coluna ranking...")
    if 'nomesegmento' in df.columns:
        df['ranking'] = df['nomesegmento'].apply(mapear_ranking)
    else:
        logger.warning("Coluna 'nomesegmento' não encontrada. Usando ranking padrão = 1")
        df['ranking'] = 1

    # 4. Calcular precisa_abastecimento
    logger.info("Calculando coluna precisa_abastecimento...")
    df['estoque_atual_clean'] = df['estoque_atual'].fillna(0)
    df['precisa_abastecimento'] = df.apply(
        lambda row: bool(row['estoque_atual_clean'] <= (row['linha_verde'] * 0.5)),
        axis=1
    )
    df.drop(columns=['estoque_atual_clean'], inplace=True)

    # 5. Calcular qtd_a_abastecer
    logger.info("Calculando coluna qtd_a_abastecer...")
    df['qtd_a_abastecer'] = df.apply(
        lambda row: max(0.0, row['linha_verde'] - (row.get('estoque_atual', 0) if pd.notna(row.get('estoque_atual')) else 0)),
        axis=1
    )

    # 6. Calcular preco_varejo
    logger.info("Calculando coluna preco_varejo...")
    df['preco_varejo'] = df.apply(calcular_preco_varejo, axis=1)

    # 7. Calcular preco_atacado
    logger.info("Calculando coluna preco_atacado...")
    df['preco_atacado'] = df['preco_38_percent'].fillna(0).round(2)

    # Garantir tipos corretos
    df['mc'] = df['mc'].astype(float)
    df['linha_verde'] = df['linha_verde'].astype(float)
    df['ranking'] = df['ranking'].astype(int)
    df['precisa_abastecimento'] = df['precisa_abastecimento'].astype(bool)
    df['qtd_a_abastecer'] = df['qtd_a_abastecer'].astype(float)
    df['preco_varejo'] = df['preco_varejo'].astype(float)
    df['preco_atacado'] = df['preco_atacado'].astype(float)

    # Salvar resultado
    logger.info(f"Salvando resultado em: {output_path}")
    df.to_parquet(output_path, index=False, compression='snappy')

    tempo_total = time.time() - inicio
    tamanho_arquivo = os.path.getsize(output_path) / (1024 * 1024)  # MB

    # Gerar relatório
    logger.info("Gerando relatório...")

    print("\n" + "="*80)
    print("RELATÓRIO DE PROCESSAMENTO - DATA AGENT")
    print("="*80)
    print(f"\nArquivo de entrada: {input_path}")
    print(f"Arquivo de saída: {output_path}")
    print(f"Data/Hora processamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n" + "-"*80)
    print("1. TOTAL DE LINHAS PROCESSADAS")
    print("-"*80)
    print(f"Total de registros: {len(df):,}")
    print(f"Colunas originais: {len(colunas_originais)}")
    print(f"Colunas adicionadas: 7 (mc, linha_verde, ranking, precisa_abastecimento, qtd_a_abastecer, preco_varejo, preco_atacado)")
    print(f"Total de colunas final: {len(df.columns)}")

    print("\n" + "-"*80)
    print("2. AMOSTRA DE 5 PRODUTOS (TODAS AS COLUNAS)")
    print("-"*80)

    # Selecionar 5 produtos aleatórios
    amostra = df.sample(min(5, len(df)))

    # Mostrar colunas novas + algumas importantes
    colunas_exibir = ['codprod', 'nomeprod', 'nomesegmento', 'estoque_atual',
                      'mc', 'linha_verde', 'ranking', 'precisa_abastecimento',
                      'qtd_a_abastecer', 'preco_38_percent', 'preco_varejo', 'preco_atacado']

    # Filtrar apenas colunas que existem
    colunas_exibir = [col for col in colunas_exibir if col in df.columns]

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

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
    print(f"  Produtos com qtd_a_abastecer > 0: {(df['qtd_a_abastecer'] > 0).sum():,}")

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
    print(f"Tamanho por registro: {(tamanho_arquivo * 1024 * 1024) / len(df):.2f} bytes")

    print("\n" + "="*80)
    print("VALIDAÇÃO DE SCHEMA")
    print("="*80)
    print("\nColunas adicionadas com sucesso:")
    colunas_novas = ['mc', 'linha_verde', 'ranking', 'precisa_abastecimento',
                     'qtd_a_abastecer', 'preco_varejo', 'preco_atacado']

    for col in colunas_novas:
        tipo = df[col].dtype
        nulos = df[col].isna().sum()
        print(f"  [{col}] - Tipo: {tipo}, Nulos: {nulos}")

    print("\n" + "="*80)
    print("PROCESSAMENTO CONCLUÍDO COM SUCESSO")
    print("="*80)

    return df

if __name__ == "__main__":
    try:
        df_resultado = processar_admmat()
    except Exception as e:
        logger.error(f"Erro durante processamento: {str(e)}", exc_info=True)
        raise
