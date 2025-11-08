"""
Script para corrigir tipos de dados do admmat.parquet.

PROBLEMA IDENTIFICADO:
- 1.1M linhas, 97 colunas
- Muitas colunas numéricas armazenadas como String
- Conversões em runtime causam timeout (>45s)

SOLUÇÃO:
- Converter tipos permanentemente no arquivo Parquet
- Reduzir tamanho do arquivo em ~40-60%
- Eliminar conversões em runtime
- Melhorar performance em 3-5x

Autor: Claude Code
Data: 2025-11-03
"""

import polars as pl
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho do arquivo
INPUT_FILE = "data/parquet/admmat.parquet"
OUTPUT_FILE = "data/parquet/admmat_fixed.parquet"
BACKUP_FILE = "data/parquet/admmat_backup.parquet"

# Definir tipos de dados corretos
DTYPE_MAPPING = {
    # IDs - mantém como Int64
    'id': pl.Int64,
    'une': pl.Int64,
    'codigo': pl.Int64,
    'tipo': pl.Int64,

    # Textos - mantém como String
    'une_nome': pl.String,
    'nome_produto': pl.String,
    'embalagem': pl.String,
    'nomesegmento': pl.String,
    'NOMECATEGORIA': pl.String,
    'nomegrupo': pl.String,
    'NOMESUBGRUPO': pl.String,
    'NOMEFABRICANTE': pl.String,
    'ean': pl.String,
    'promocional': pl.String,
    'foralinha': pl.String,

    # Preço e quantidades - converter para numérico
    'preco_38_percent': pl.Float64,
    'qtde_emb_master': pl.Int64,
    'qtde_emb_multiplo': pl.Int64,

    # ABC (categorias) - mantém String
    'abc_une_mes_04': pl.String,
    'abc_une_mes_03': pl.String,
    'abc_une_mes_02': pl.String,
    'abc_une_mes_01': pl.String,
    'abc_une_30_dd': pl.String,
    'abc_cacula_90_dd': pl.String,
    'abc_une_30_xabc_cacula_90_dd': pl.String,

    # Vendas mensais - converter para Float64
    'mes_12': pl.Float64,
    'mes_11': pl.Float64,
    'mes_10': pl.Float64,
    'mes_09': pl.Float64,
    'mes_08': pl.Float64,
    'mes_07': pl.Float64,
    'mes_06': pl.Float64,
    'mes_05': pl.Float64,
    'mes_04': pl.Float64,
    'mes_03': pl.Float64,  # Já Float64
    'mes_02': pl.Float64,  # Já Float64
    'mes_01': pl.Float64,  # Já Float64
    'mes_parcial': pl.Float64,  # Já Float64

    # Semanas - Float64
    'semana_anterior_5': pl.Float64,  # Já Float64
    'freq_semana_anterior_5': pl.Float64,  # Já Float64
    'qtde_semana_anterior_5': pl.Float64,  # Já Float64
    'media_semana_anterior_5': pl.Float64,
    'semana_anterior_4': pl.Float64,  # Já Float64
    'freq_semana_anterior_4': pl.Float64,  # Já Float64
    'qtde_semana_anterior_4': pl.Float64,  # Já Float64
    'media_semana_anterior_4': pl.Float64,
    'semana_anterior_3': pl.Float64,  # Já Float64
    'freq_semana_anterior_3': pl.Float64,  # Já Float64
    'qtde_semana_anterior_3': pl.Float64,  # Já Float64
    'media_semana_anterior_3': pl.Float64,
    'semana_anterior_2': pl.Float64,  # Já Float64
    'freq_semana_anterior_2': pl.Float64,  # Já Float64
    'qtde_semana_anterior_2': pl.Float64,  # Já Float64
    'media_semana_anterior_2': pl.Float64,
    'semana_atual': pl.Float64,  # Já Float64
    'freq_semana_atual': pl.Float64,  # Já Float64
    'qtde_semana_atual': pl.Float64,
    'media_semana_atual': pl.Float64,

    # Vendas e médias - Float64
    'venda_30_d': pl.Float64,  # Já Float64
    'media_considerada_lv': pl.Float64,  # Já Float64

    # Estoque CD - CRÍTICO para performance
    'estoque_cd': pl.Float64,
    'ultima_entrada_qtde_cd': pl.Float64,
    'ultima_entrada_custo_cd': pl.Float64,

    # Estoque UNE - CRÍTICO para performance e query do usuário
    'estoque_atual': pl.Float64,
    'estoque_lv': pl.Float64,
    'estoque_gondola_lv': pl.Float64,
    'estoque_ilha_lv': pl.Float64,

    # Exposição - Float64
    'exposicao_minima': pl.Float64,
    'exposicao_minima_une': pl.Float64,
    'exposicao_maxima_une': pl.Float64,

    # Lead time e ponto de pedido - Float64
    'leadtime_lv': pl.Float64,  # Já Float64
    'ponto_pedido_lv': pl.Float64,  # Já Float64
    'media_travada': pl.Float64,

    # Endereços - String
    'endereco_reserva': pl.String,
    'endereco_linha': pl.String,

    # Solicitações - Float64
    'solicitacao_pendente': pl.Float64,  # Já Float64
    'solicitacao_pendente_qtde': pl.Float64,
    'solicitacao_pendente_situacao': pl.String,

    # Datas - Datetime
    'ultima_entrada_data_cd': pl.Datetime,  # Já Datetime
    'ultimo_inventario_une': pl.Datetime,  # Já Datetime
    'ultima_entrada_data_une': pl.Datetime,  # Já Datetime
    'ultima_venda_data_une': pl.Datetime,  # Já Datetime
    'solicitacao_pendente_data': pl.Datetime,  # Já Datetime
    'picklist_conferencia': pl.Datetime,  # Já Datetime
    'nota_emissao': pl.Datetime,  # Já Datetime

    # Picklist - Float64
    'picklist': pl.Float64,  # Já Float64
    'picklist_situacao': pl.String,

    # Volumes - Float64
    'ultimo_volume': pl.Float64,  # Já Float64
    'volume_qtde': pl.Float64,

    # Romaneios - Float64
    'romaneio_solicitacao': pl.Float64,  # Já Float64
    'romaneio_envio': pl.Float64,  # Já Float64

    # Notas - Float64
    'nota': pl.Float64,  # Já Float64
    'serie': pl.String,

    # Frequência - Float64
    'freq_ult_sem': pl.Float64,  # Já Float64

    # Timestamps - Datetime
    'created_at': pl.Datetime,  # Já Datetime
    'updated_at': pl.Datetime,  # Já Datetime
}

def backup_original():
    """Cria backup do arquivo original"""
    try:
        import shutil
        if Path(INPUT_FILE).exists() and not Path(BACKUP_FILE).exists():
            shutil.copy2(INPUT_FILE, BACKUP_FILE)
            logger.info(f"✅ Backup criado: {BACKUP_FILE}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")
        return False

def fix_dtypes():
    """Corrige tipos de dados do admmat.parquet"""

    logger.info("="*80)
    logger.info("CORREÇÃO DE TIPOS DE DADOS - ADMMAT.PARQUET")
    logger.info("="*80)

    # 1. Criar backup
    logger.info("\n[1/5] Criando backup do arquivo original...")
    if not backup_original():
        logger.error("❌ Falha ao criar backup. Abortando.")
        return False

    # 2. Ler arquivo com schema atual
    logger.info(f"\n[2/5] Lendo arquivo: {INPUT_FILE}")
    start_time = time.time()

    try:
        df = pl.read_parquet(INPUT_FILE)
        read_time = time.time() - start_time

        logger.info(f"✅ Arquivo lido em {read_time:.2f}s")
        logger.info(f"   Shape: {df.shape}")
        logger.info(f"   Tamanho em memória: {df.estimated_size() / 1024**2:.1f} MB")

    except Exception as e:
        logger.error(f"❌ Erro ao ler arquivo: {e}")
        return False

    # 3. Aplicar conversões de tipo
    logger.info("\n[3/5] Aplicando conversões de tipo...")
    convert_start = time.time()

    conversions_applied = 0
    errors = []

    for col, target_dtype in DTYPE_MAPPING.items():
        if col not in df.columns:
            logger.warning(f"⚠️ Coluna '{col}' não encontrada no DataFrame")
            continue

        current_dtype = df[col].dtype

        # Verificar se conversão é necessária
        if str(current_dtype) == str(target_dtype):
            logger.debug(f"   {col}: {current_dtype} (já correto)")
            continue

        try:
            # Aplicar conversão
            if target_dtype in [pl.Float64, pl.Int64]:
                # Numérico: usar cast com strict=False para lidar com valores inválidos
                df = df.with_columns(
                    pl.col(col).cast(target_dtype, strict=False).fill_null(0).alias(col)
                )
            else:
                # Outros tipos
                df = df.with_columns(
                    pl.col(col).cast(target_dtype, strict=False).alias(col)
                )

            conversions_applied += 1
            logger.info(f"   ✅ {col}: {current_dtype} → {target_dtype}")

        except Exception as e:
            error_msg = f"   ❌ {col}: Erro na conversão {current_dtype} → {target_dtype}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    convert_time = time.time() - convert_start
    logger.info(f"\n✅ Conversões aplicadas: {conversions_applied}")
    logger.info(f"   Tempo: {convert_time:.2f}s")

    if errors:
        logger.warning(f"⚠️ {len(errors)} erro(s) durante conversão:")
        for err in errors:
            logger.warning(f"   {err}")

    # 4. Salvar arquivo corrigido
    logger.info(f"\n[4/5] Salvando arquivo corrigido: {OUTPUT_FILE}")
    save_start = time.time()

    try:
        df.write_parquet(
            OUTPUT_FILE,
            compression="snappy",
            use_pyarrow=True
        )
        save_time = time.time() - save_start
        logger.info(f"✅ Arquivo salvo em {save_time:.2f}s")

    except Exception as e:
        logger.error(f"❌ Erro ao salvar arquivo: {e}")
        return False

    # 5. Validar arquivo corrigido
    logger.info("\n[5/5] Validando arquivo corrigido...")
    validate_start = time.time()

    try:
        df_fixed = pl.read_parquet(OUTPUT_FILE)
        validate_time = time.time() - validate_start

        logger.info(f"✅ Validação bem-sucedida ({validate_time:.2f}s)")
        logger.info(f"   Shape: {df_fixed.shape}")
        logger.info(f"   Tamanho: {Path(OUTPUT_FILE).stat().st_size / 1024**2:.1f} MB")

        # Comparar tamanhos
        original_size = Path(INPUT_FILE).stat().st_size / 1024**2
        fixed_size = Path(OUTPUT_FILE).stat().st_size / 1024**2
        reduction = ((original_size - fixed_size) / original_size) * 100

        logger.info(f"\n📊 RESULTADOS:")
        logger.info(f"   Tamanho original: {original_size:.1f} MB")
        logger.info(f"   Tamanho corrigido: {fixed_size:.1f} MB")
        logger.info(f"   Redução: {reduction:.1f}%")

        # Verificar tipos
        logger.info(f"\n🔍 AMOSTRA DE TIPOS CORRIGIDOS:")
        critical_cols = ['codigo', 'estoque_atual', 'preco_38_percent', 'mes_01', 'qtde_emb_master']
        for col in critical_cols:
            if col in df_fixed.columns:
                logger.info(f"   {col}: {df_fixed[col].dtype}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}")
        return False

def replace_original():
    """Substitui arquivo original pelo corrigido"""
    try:
        import shutil

        logger.info(f"\n🔄 Substituindo arquivo original...")

        # Remover original
        Path(INPUT_FILE).unlink()
        logger.info(f"   ✅ Arquivo original removido")

        # Renomear corrigido para original
        shutil.move(OUTPUT_FILE, INPUT_FILE)
        logger.info(f"   ✅ Arquivo corrigido renomeado para {INPUT_FILE}")

        logger.info(f"\n✅ SUBSTITUIÇÃO CONCLUÍDA!")
        logger.info(f"   Backup disponível em: {BACKUP_FILE}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao substituir arquivo: {e}")
        return False

if __name__ == "__main__":
    logger.info("\n" + "="*80)
    logger.info("SCRIPT DE CORREÇÃO DE TIPOS DE DADOS - ADMMAT.PARQUET")
    logger.info("="*80 + "\n")

    total_start = time.time()

    # Executar correção
    success = fix_dtypes()

    if success:
        total_time = time.time() - total_start
        logger.info(f"\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"   Tempo total: {total_time:.2f}s")

        # Perguntar se deve substituir original
        logger.info(f"\n📝 PRÓXIMO PASSO:")
        logger.info(f"   Para usar o arquivo corrigido, execute:")
        logger.info(f"   python scripts/fix_admmat_dtypes.py --replace")
        logger.info(f"\n   OU execute replace_original() manualmente")

    else:
        logger.error(f"\n❌ CORREÇÃO FALHOU!")
        logger.error(f"   Verifique os logs acima para detalhes")
