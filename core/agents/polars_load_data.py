"""
FUNÇÃO LOAD_DATA OTIMIZADA COM POLARS
======================================

Substitui Pandas/Dask por Polars para eliminar erros de memória e KeyError.

Baseado em:
- Context7 Polars Documentation
- Best practices de lazy evaluation
- Sistema de validação de colunas

Autor: Claude Code
Data: 2025-10-27
"""

import logging
import os
from typing import Dict, Any, Optional
import pandas as pd

# Import condicional do Polars
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

from core.config.column_mapping import normalize_column_name, COLUMN_MAP, ESSENTIAL_COLUMNS
from core.utils.column_validator import validate_columns, get_available_columns_cached

logger = logging.getLogger(__name__)

# ✅ CACHE SIMPLES EM MEMÓRIA (evita reprocessar mesma query)
_load_data_cache = {}
_cache_hits = 0
_cache_misses = 0


def create_optimized_load_data(parquet_path: str, data_adapter=None):
    """
    Factory que cria função load_data() otimizada com Polars.

    Args:
        parquet_path: Caminho do arquivo Parquet
        data_adapter: Adapter de dados (opcional, para compatibilidade)

    Returns:
        Função load_data() pronta para ser injetada no escopo
    """

    def load_data_polars(filters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Carrega dados do Parquet usando POLARS (lazy + memory-efficient).

        ✅ VANTAGENS SOBRE PANDAS/DASK:
        - 10x mais rápido em aggregations
        - Lazy evaluation (não carrega tudo na memória)
        - Validação automática de colunas
        - Streaming mode para datasets grandes
        - Cache em memória para queries repetidas

        Args:
            filters: Filtros opcionais (ex: {'une': '2586', 'nomesegmento': 'TECIDOS'})

        Returns:
            pandas.DataFrame (para compatibilidade com código existente)

        Examples:
            >>> df = load_data()  # Carrega top 10K linhas
            >>> df = load_data({'une': '2586'})  # Filtra por UNE
        """
        # ✅ CACHE: Verificar se já processamos essa query antes
        global _load_data_cache, _cache_hits, _cache_misses

        # Criar chave de cache baseada nos filtros
        cache_key = str(sorted(filters.items())) if filters else "no_filters"

        if cache_key in _load_data_cache:
            _cache_hits += 1
            hit_rate = (_cache_hits / (_cache_hits + _cache_misses)) * 100
            logger.info(f"✅ CACHE HIT! Retornando resultado cached (hit rate: {hit_rate:.1f}%)")
            return _load_data_cache[cache_key].copy()  # Retornar cópia para evitar mutações

        _cache_misses += 1

        if not POLARS_AVAILABLE:
            logger.error("❌ Polars não disponível! Usando fallback Pandas (LENTO)")
            return _load_data_pandas_fallback(parquet_path, filters)

        try:
            logger.info(f"🚀 load_data() usando POLARS - Lazy evaluation")
            logger.info(f"📂 Parquet path: {parquet_path}")

            # Verificar se path existe (glob pattern ou arquivo direto)
            import glob
            if '*' in parquet_path:
                matched_files = glob.glob(parquet_path)
                logger.info(f"🔍 Glob pattern encontrou {len(matched_files)} arquivo(s): {matched_files}")
                if not matched_files:
                    raise FileNotFoundError(f"Nenhum arquivo encontrado para pattern: {parquet_path}")
            elif not os.path.exists(parquet_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {parquet_path}")

            # 1. SCAN PARQUET (lazy - 0 memória até collect)
            # ✅ CORREÇÃO: Ler múltiplos arquivos com schemas diferentes
            import glob

            # Se for pattern com *, processar cada arquivo separadamente
            if '*' in parquet_path:
                matched_files = glob.glob(parquet_path)
                logger.info(f"🔍 Glob pattern encontrou {len(matched_files)} arquivo(s): {matched_files}")

                if not matched_files:
                    raise FileNotFoundError(f"Nenhum arquivo encontrado para pattern: {parquet_path}")

                # Ler cada arquivo e selecionar apenas colunas essenciais
                lazy_frames = []
                for file in matched_files:
                    try:
                        # Scan arquivo individual
                        lf_single = pl.scan_parquet(
                            file,
                            low_memory=True,
                            rechunk=False
                        )

                        # Selecionar apenas colunas essenciais (que existem em todos os arquivos)
                        schema_single = lf_single.collect_schema()
                        available_cols = [col for col in ESSENTIAL_COLUMNS if col in schema_single.names()]

                        lf_single = lf_single.select(available_cols)
                        lazy_frames.append(lf_single)

                        logger.info(f"   ✅ {file}: {len(available_cols)} colunas selecionadas")

                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao ler {file}: {e}. Pulando...")

                # Concatenar todos os LazyFrames
                if lazy_frames:
                    lf = pl.concat(lazy_frames)
                    logger.info(f"📚 Concatenados {len(lazy_frames)} arquivo(s)")
                else:
                    raise FileNotFoundError("Nenhum arquivo válido encontrado")

            else:
                # Arquivo único
                lf = pl.scan_parquet(
                    parquet_path,
                    low_memory=True,
                    rechunk=False
                )

            # 2. VALIDAR SCHEMA
            try:
                schema = lf.collect_schema()
                available_columns = list(schema.names())
                logger.info(f"📊 Schema carregado: {len(available_columns)} colunas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler schema: {e}. Continuando...")
                available_columns = ESSENTIAL_COLUMNS

            # 3. APLICAR FILTROS (se fornecidos)
            # ✅ OTIMIZAÇÃO: Push-down filtering ANTES de qualquer processamento
            has_filters = filters and len(filters) > 0

            if has_filters:
                logger.info(f"🔍 Aplicando {len(filters)} filtro(s) - PUSH-DOWN mode")

                # Validar colunas dos filtros
                filter_cols = list(filters.keys())
                validation = validate_columns(filter_cols, available_columns, auto_correct=True)

                if not validation["all_valid"]:
                    logger.warning(f"⚠️ Colunas inválidas nos filtros: {validation['invalid']}")
                    # Remover filtros inválidos
                    filters = {validation["corrected"].get(k, k): v
                              for k, v in filters.items()
                              if k not in validation["invalid"]}

                # Aplicar filtros
                for col, value in filters.items():
                    col_corrected = validation["corrected"].get(col, col)

                    if isinstance(value, (list, tuple)):
                        lf = lf.filter(pl.col(col_corrected).is_in(value))
                    else:
                        lf = lf.filter(pl.col(col_corrected) == value)

                    logger.info(f"   ✅ Filtro aplicado: {col_corrected} == {value}")

            # 4. SELECIONAR COLUNAS ESSENCIAIS (reduz memória)
            try:
                # Validar quais colunas essenciais existem
                validation = validate_columns(
                    ESSENTIAL_COLUMNS,
                    available_columns,
                    auto_correct=True
                )

                cols_to_select = validation["valid"]

                if cols_to_select:
                    lf = lf.select(cols_to_select)
                    logger.info(f"📋 Selecionadas {len(cols_to_select)} colunas essenciais")

            except Exception as e:
                logger.warning(f"⚠️ Erro ao selecionar colunas: {e}. Usando todas.")

            # 5. AMOSTRAGEM ESTRATIFICADA POR UNE (proteção contra OOM + representatividade)
            # ✅ OTIMIZAÇÃO: Se já tem filtros (ex: UNE específica), aumentar limite
            if has_filters:
                # Com filtros: dataset já reduzido, pode carregar mais linhas
                MAX_ROWS = 500000  # 500K linhas para queries filtradas
                logger.info(f"📊 Query com filtros - limite aumentado para {MAX_ROWS:,} linhas")
            else:
                # Sem filtros: aplicar amostragem conservadora
                MAX_ROWS = 200000  # 200K linhas para queries genéricas
                logger.info(f"📊 Query sem filtros - amostragem estratificada ({MAX_ROWS:,} linhas)")

            # ✅ CORREÇÃO: Garantir que todas as UNEs estejam representadas
            # Estratégia: Amostrar N linhas por UNE ao invés de limitar globalmente
            #
            # ANTES: lf.limit(50000) → pegava primeiros 50K (apenas ITA e NIG)
            # DEPOIS: Amostragem distribuída entre todas as UNEs

            # Coletar metadados das UNEs antes de limitar
            try:
                # Contar UNEs únicas
                unes_count = lf.select(pl.col("une_nome")).unique().collect()
                num_unes = len(unes_count)

                if num_unes > 0:
                    # Calcular linhas por UNE (distribuição equitativa)
                    rows_per_une = MAX_ROWS // num_unes
                    logger.info(f"   📍 {num_unes} UNEs detectadas")
                    logger.info(f"   ⚖️  Amostrando ~{rows_per_une} linhas por UNE")

                    # Aplicar amostragem estratificada
                    lf = (lf
                          .filter(pl.col("une_nome") != "")  # Remover UNE vazia
                          .group_by("une_nome")
                          .head(rows_per_une)  # Top N por UNE
                         )
                else:
                    # Fallback: limite simples
                    logger.warning(f"   ⚠️  Não foi possível detectar UNEs. Usando limite simples.")
                    lf = lf.limit(MAX_ROWS)

            except Exception as e:
                # Se amostragem estratificada falhar, usar limite simples
                logger.warning(f"⚠️ Erro na amostragem estratificada: {e}. Usando limite simples.")
                lf = lf.limit(MAX_ROWS)

            # 6. COLLECT (executar query)
            logger.info(f"⚡ Executando query (lazy → collect)...")

            try:
                # Tentar collect normal
                df_polars = lf.collect()
                logger.info(f"✅ Carregados {len(df_polars)} registros com {len(df_polars.columns)} colunas")

            except MemoryError as e:
                # Fallback: streaming mode
                logger.warning(f"⚠️ MemoryError no collect. Usando streaming mode...")

                df_polars = lf.collect(streaming=True)
                logger.info(f"✅ [STREAMING] Carregados {len(df_polars)} registros")

            # 7. CONVERTER PARA PANDAS (compatibilidade)
            df_pandas = df_polars.to_pandas()

            # 8. NORMALIZAR NOMES DE COLUNAS (para código legado)
            # Garantir que nomes estejam corretos
            logger.info(f"📝 DataFrame final: {df_pandas.shape}")
            logger.info(f"   Colunas: {list(df_pandas.columns)[:10]}...")

            # ✅ CACHE: Salvar resultado para próximas execuções
            # Limitar cache a 10 queries (evitar OOM)
            if len(_load_data_cache) >= 10:
                # Remover entrada mais antiga (FIFO)
                oldest_key = next(iter(_load_data_cache))
                del _load_data_cache[oldest_key]
                logger.debug(f"🗑️  Cache cheio - removido: {oldest_key}")

            _load_data_cache[cache_key] = df_pandas.copy()
            logger.info(f"💾 Resultado salvo no cache (total: {len(_load_data_cache)} queries)")

            return df_pandas

        except Exception as e:
            logger.error(f"❌ Erro no load_data_polars: {e}", exc_info=True)
            logger.warning("🔄 Fallback para Pandas...")
            return _load_data_pandas_fallback(parquet_path, filters)

    return load_data_polars


def _load_data_pandas_fallback(parquet_path: str, filters: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Fallback usando Pandas puro (mais lento mas sempre funciona).

    Args:
        parquet_path: Caminho do Parquet
        filters: Filtros opcionais

    Returns:
        pandas.DataFrame
    """
    logger.warning("⚠️ Usando Pandas fallback (LENTO)")

    try:
        # Carregar apenas colunas essenciais
        df = pd.read_parquet(
            parquet_path,
            engine='pyarrow',
            columns=ESSENTIAL_COLUMNS
        ).head(10000)  # Limitar a 10K linhas

        # Aplicar filtros se fornecidos
        if filters:
            for col, value in filters.items():
                col_normalized = normalize_column_name(col)

                if col_normalized in df.columns:
                    if isinstance(value, (list, tuple)):
                        df = df[df[col_normalized].isin(value)]
                    else:
                        df = df[df[col_normalized] == value]

        logger.info(f"✅ [FALLBACK] Carregados {len(df)} registros")
        return df

    except Exception as e:
        logger.error(f"❌ Fallback Pandas também falhou: {e}")
        raise RuntimeError(
            "❌ **Erro ao Carregar Dados**\n\n"
            "Não foi possível carregar o dataset.\n\n"
            "**Sugestões:**\n"
            "- Verifique se o arquivo Parquet existe\n"
            "- Tente reiniciar o sistema\n"
            "- Entre em contato com o suporte"
        )


# ==================== TESTES ====================

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Mock path
    parquet_path = "data/parquet/admmat_une.parquet"

    if not os.path.exists(parquet_path):
        print(f"❌ Arquivo não encontrado: {parquet_path}")
        sys.exit(1)

    # Teste 1: Sem filtros
    print("\n" + "="*60)
    print("TESTE 1: Carregar sem filtros")
    print("="*60)

    load_data = create_optimized_load_data(parquet_path)
    df = load_data()

    print(f"✅ Shape: {df.shape}")
    print(f"✅ Colunas: {list(df.columns)}")
    print(f"✅ Primeiras linhas:")
    print(df.head())

    # Teste 2: Com filtros
    print("\n" + "="*60)
    print("TESTE 2: Carregar com filtros (UNE=2586)")
    print("="*60)

    df_filtered = load_data({'une': 2586})

    print(f"✅ Shape: {df_filtered.shape}")
    print(f"✅ UNEs únicas: {df_filtered['une'].unique()}")

    print("\n✅ TESTES CONCLUÍDOS!")
