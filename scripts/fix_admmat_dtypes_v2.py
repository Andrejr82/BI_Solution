"""
Script otimizado para corrigir tipos de dados do admmat.parquet.
Versão 2: Salva diretamente substituindo o original.
"""

import polars as pl
import logging
from pathlib import Path
import time
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho do arquivo
INPUT_FILE = "data/parquet/admmat.parquet"
BACKUP_FILE = "data/parquet/admmat_backup_v2.parquet"
TEMP_FILE = "data/parquet/admmat_temp.parquet"

# Definir tipos de dados corretos (apenas os que precisam de conversão)
DTYPE_CONVERSIONS = {
    # Preço e quantidades
    'preco_38_percent': pl.Float64,
    'qtde_emb_master': pl.Int64,
    'qtde_emb_multiplo': pl.Int64,

    # Vendas mensais (String -> Float64)
    'mes_12': pl.Float64,
    'mes_11': pl.Float64,
    'mes_10': pl.Float64,
    'mes_09': pl.Float64,
    'mes_08': pl.Float64,
    'mes_07': pl.Float64,
    'mes_06': pl.Float64,
    'mes_05': pl.Float64,
    'mes_04': pl.Float64,

    # Médias semanais
    'media_semana_anterior_5': pl.Float64,
    'media_semana_anterior_4': pl.Float64,
    'media_semana_anterior_3': pl.Float64,
    'media_semana_anterior_2': pl.Float64,
    'qtde_semana_atual': pl.Float64,
    'media_semana_atual': pl.Float64,

    # Estoque CD
    'estoque_cd': pl.Float64,
    'ultima_entrada_qtde_cd': pl.Float64,
    'ultima_entrada_custo_cd': pl.Float64,

    # Estoque UNE - CRÍTICO
    'estoque_atual': pl.Float64,
    'estoque_lv': pl.Float64,
    'estoque_gondola_lv': pl.Float64,
    'estoque_ilha_lv': pl.Float64,

    # Exposição
    'exposicao_minima': pl.Float64,
    'exposicao_minima_une': pl.Float64,
    'exposicao_maxima_une': pl.Float64,
    'media_travada': pl.Float64,

    # Solicitações
    'solicitacao_pendente_qtde': pl.Float64,

    # Volumes
    'volume_qtde': pl.Float64,
}

def fix_and_replace():
    """Corrige tipos e substitui arquivo original"""

    logger.info("="*80)
    logger.info("CORRECAO DE TIPOS - ADMMAT.PARQUET v2")
    logger.info("="*80)

    total_start = time.time()

    # 1. Criar backup
    logger.info("\n[1/4] Criando backup...")
    if not Path(BACKUP_FILE).exists():
        shutil.copy2(INPUT_FILE, BACKUP_FILE)
        logger.info(f"Backup criado: {BACKUP_FILE}")
    else:
        logger.info(f"Backup ja existe: {BACKUP_FILE}")

    # 2. Ler e converter
    logger.info(f"\n[2/4] Lendo e convertendo: {INPUT_FILE}")
    read_start = time.time()

    df = pl.read_parquet(INPUT_FILE)
    read_time = time.time() - read_start

    logger.info(f"Lido em {read_time:.2f}s - Shape: {df.shape}")

    # 3. Aplicar conversões
    logger.info(f"\n[3/4] Aplicando {len(DTYPE_CONVERSIONS)} conversoes...")
    convert_start = time.time()

    conversions = []
    for col, target_dtype in DTYPE_CONVERSIONS.items():
        if col not in df.columns:
            continue

        current_dtype = df[col].dtype
        if str(current_dtype) == str(target_dtype):
            continue

        # Converter
        if target_dtype in [pl.Float64, pl.Int64]:
            df = df.with_columns(
                pl.col(col).cast(target_dtype, strict=False).fill_null(0).alias(col)
            )
        else:
            df = df.with_columns(
                pl.col(col).cast(target_dtype, strict=False).alias(col)
            )

        conversions.append(f"{col}: {current_dtype} -> {target_dtype}")
        logger.info(f"  OK: {col}")

    convert_time = time.time() - convert_start
    logger.info(f"Conversoes aplicadas: {len(conversions)} em {convert_time:.2f}s")

    # 4. Salvar substituindo original
    logger.info(f"\n[4/4] Salvando: {TEMP_FILE}")
    save_start = time.time()

    df.write_parquet(TEMP_FILE, compression="snappy", use_pyarrow=True)
    save_time = time.time() - save_start
    logger.info(f"Salvo em {save_time:.2f}s")

    # Substituir original
    logger.info("\nSubstituindo arquivo original...")
    Path(INPUT_FILE).unlink()
    shutil.move(TEMP_FILE, INPUT_FILE)

    total_time = time.time() - total_start

    # Validar
    logger.info("\nValidando...")
    df_new = pl.read_parquet(INPUT_FILE)

    logger.info(f"\n{'='*80}")
    logger.info("CONCLUIDO COM SUCESSO!")
    logger.info(f"{'='*80}")
    logger.info(f"Tempo total: {total_time:.2f}s")
    logger.info(f"Tamanho: {Path(INPUT_FILE).stat().st_size / 1024**2:.1f} MB")
    logger.info(f"Backup: {BACKUP_FILE}")
    logger.info(f"\nTipos criticos:")
    logger.info(f"  codigo: {df_new['codigo'].dtype}")
    logger.info(f"  estoque_atual: {df_new['estoque_atual'].dtype}")
    logger.info(f"  mes_01: {df_new['mes_01'].dtype}")

    return True

if __name__ == "__main__":
    fix_and_replace()
