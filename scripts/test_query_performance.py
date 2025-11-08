"""
Teste de performance da query: "qual é o estoque do produto 369947 na une nit"

Antes da correção: Timeout (>45s)
Após correção: Deveria ser < 5s
"""

import polars as pl
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query():
    """Testa a query problemática do usuário"""

    logger.info("="*80)
    logger.info("TESTE DE PERFORMANCE - QUERY ESTOQUE")
    logger.info("="*80)

    # Query original: estoque do produto 369947 na une nit
    logger.info("\nQuery: 'qual e o estoque do produto 369947 na une nit'")
    logger.info("Filtros: codigo=369947, une_nome contendo 'NIT'")

    # 1. Teste com Polars (método otimizado)
    logger.info("\n[1/2] Testando com Polars (lazy)...")
    polars_start = time.time()

    try:
        # Lazy scan
        lf = pl.scan_parquet("data/parquet/admmat.parquet")

        # Aplicar filtros
        lf = lf.filter(pl.col("codigo") == 369947)
        lf = lf.filter(pl.col("une_nome").str.contains("(?i)NIT"))  # Case-insensitive

        # Selecionar apenas colunas relevantes
        lf = lf.select([
            "codigo",
            "nome_produto",
            "une",
            "une_nome",
            "estoque_atual",
            "estoque_cd",
            "ultima_entrada_data_une",
            "ultima_venda_data_une"
        ])

        # Collect (executar query)
        df = lf.collect()

        polars_time = time.time() - polars_start

        logger.info(f"Tempo: {polars_time:.3f}s")
        logger.info(f"Linhas retornadas: {len(df)}")

        if len(df) > 0:
            logger.info("\nResultado:")
            print(df)

            # Verificar tipo de estoque_atual
            logger.info(f"\nTipo de estoque_atual: {df['estoque_atual'].dtype}")
        else:
            logger.warning("Nenhum resultado encontrado!")

    except Exception as e:
        logger.error(f"Erro no teste Polars: {e}", exc_info=True)
        polars_time = None

    # 2. Teste alternativo: produto existe?
    logger.info("\n[2/2] Verificando se produto existe...")
    check_start = time.time()

    try:
        lf = pl.scan_parquet("data/parquet/admmat.parquet")
        lf = lf.filter(pl.col("codigo") == 369947)
        lf = lf.select(["codigo", "nome_produto", "une", "une_nome"])
        df_check = lf.collect()

        check_time = time.time() - check_start

        logger.info(f"Tempo: {check_time:.3f}s")
        logger.info(f"Produto encontrado em {len(df_check)} UNEs")

        if len(df_check) > 0:
            logger.info("\nUNEs encontradas:")
            print(df_check[["une", "une_nome"]].unique())

    except Exception as e:
        logger.error(f"Erro na verificacao: {e}", exc_info=True)

    # Resumo
    logger.info("\n" + "="*80)
    logger.info("RESUMO")
    logger.info("="*80)

    if polars_time:
        if polars_time < 5:
            logger.info(f"Performance: EXCELENTE ({polars_time:.3f}s < 5s)")
        elif polars_time < 10:
            logger.info(f"Performance: BOA ({polars_time:.3f}s < 10s)")
        elif polars_time < 45:
            logger.info(f"Performance: ACEITAVEL ({polars_time:.3f}s < 45s)")
        else:
            logger.info(f"Performance: TIMEOUT ({polars_time:.3f}s >= 45s)")

        # Comparação com timeout anterior
        improvement = ((45 - polars_time) / 45) * 100
        logger.info(f"Melhoria: {improvement:.1f}% mais rapido que antes (45s)")

if __name__ == "__main__":
    test_query()
