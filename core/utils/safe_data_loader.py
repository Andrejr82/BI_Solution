"""
Safe Data Loader - Carregamento Seguro de Dados com Validação
==============================================================

Wrapper para carregamento de arquivos Parquet com validação robusta de paths
e tratamento de erros detalhado. Elimina erros de "Load Failed".

Autor: Code Agent
Data: 2025-10-29
Versão: 1.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import polars as pl

from core.utils.path_validator import PathValidator, PathValidationError

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler para arquivo de log dedicado
log_file = Path("data/logs/data_loading.log")
log_file.parent.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class DataLoadError(Exception):
    """
    Exceção customizada para erros de carregamento de dados.

    Atributos:
        message: Mensagem de erro detalhada
        path: Path que falhou ao carregar
        error_type: Tipo do erro (validation_failed, polars_error, etc)
        original_error: Exceção original (se houver)
        validation_info: Informações da validação de path
    """

    def __init__(
        self,
        message: str,
        path: str,
        error_type: str,
        original_error: Optional[Exception] = None,
        validation_info: Optional[Dict] = None
    ):
        self.message = message
        self.path = path
        self.error_type = error_type
        self.original_error = original_error
        self.validation_info = validation_info or {}
        super().__init__(self.message)

    def __str__(self):
        """Formata mensagem de erro completa."""
        msg = f"ERRO DE CARREGAMENTO DE DADOS\n"
        msg += f"{'=' * 60}\n"
        msg += f"Mensagem: {self.message}\n"
        msg += f"Path: {self.path}\n"
        msg += f"Tipo: {self.error_type}\n"

        if self.original_error:
            msg += f"Erro original: {type(self.original_error).__name__}: {str(self.original_error)}\n"

        if self.validation_info:
            msg += f"\nInformações de validação:\n"
            for key, value in self.validation_info.items():
                if key != 'validation_errors':
                    msg += f"  - {key}: {value}\n"

        msg += f"{'=' * 60}\n"
        return msg


class SafeDataLoader:
    """
    Carregador seguro de dados Parquet com validação robusta.

    Características:
    - Validação completa de paths antes de carregar
    - Mensagens de erro claras e acionáveis
    - Logging detalhado de todas as operações
    - Estatísticas de carregamento
    - Cache de validações (opcional)

    Exemplo:
        >>> loader = SafeDataLoader()
        >>> df = loader.load_parquet("data/file.parquet")
        >>> print(f"Carregadas {len(df)} linhas")
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        enable_cache: bool = False,
        validate_on_load: bool = True
    ):
        """
        Inicializa o carregador seguro.

        Args:
            base_path: Path base para resolução de paths relativos
            enable_cache: Se True, mantém cache de validações bem-sucedidas
            validate_on_load: Se True, valida path antes de carregar (recomendado)
        """
        self.base_path = base_path or Path.cwd()
        self.validator = PathValidator(base_path=self.base_path)
        self.enable_cache = enable_cache
        self.validate_on_load = validate_on_load

        # Estatísticas
        self.stats = {
            'total_loads': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'validation_failures': 0,
            'polars_errors': 0,
            'total_rows_loaded': 0,
            'total_bytes_loaded': 0
        }

        # Cache de validações (se habilitado)
        self._validation_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"SafeDataLoader inicializado (base_path={self.base_path}, "
            f"cache={enable_cache}, validate={validate_on_load})"
        )

    def load_parquet(
        self,
        file_path: Union[str, Path],
        validate: Optional[bool] = None,
        polars_kwargs: Optional[Dict] = None,
        raise_on_error: bool = True
    ) -> Optional[pl.DataFrame]:
        """
        Carrega arquivo Parquet com validação robusta.

        Args:
            file_path: Path do arquivo a carregar
            validate: Sobrescreve validate_on_load se fornecido
            polars_kwargs: Argumentos adicionais para pl.read_parquet()
            raise_on_error: Se False, retorna None em caso de erro (sem raise)

        Returns:
            pl.DataFrame: DataFrame carregado
            None: Se raise_on_error=False e ocorrer erro

        Raises:
            DataLoadError: Se validação ou carregamento falhar (raise_on_error=True)

        Exemplo:
            >>> loader = SafeDataLoader()
            >>> df = loader.load_parquet("data/file.parquet")
            >>> if df is not None:
            ...     print(f"Carregadas {len(df)} linhas")
        """
        start_time = datetime.now()
        self.stats['total_loads'] += 1

        path_str = str(file_path)
        polars_kwargs = polars_kwargs or {}

        # Determinar se deve validar
        should_validate = validate if validate is not None else self.validate_on_load

        validation_info = {}

        try:
            # ===== FASE 1: VALIDAÇÃO DE PATH =====
            if should_validate:
                logger.debug(f"Iniciando validação de path: {path_str}")

                # Verificar cache se habilitado
                if self.enable_cache and path_str in self._validation_cache:
                    logger.debug(f"Usando validação em cache para: {path_str}")
                    validation_info = self._validation_cache[path_str]
                else:
                    # Executar validação
                    try:
                        is_valid, validation_info = self.validator.validate_parquet_path(
                            file_path
                        )

                        # Adicionar ao cache se habilitado e válido
                        if self.enable_cache and is_valid:
                            self._validation_cache[path_str] = validation_info
                            logger.debug(f"Validação adicionada ao cache: {path_str}")

                    except PathValidationError as e:
                        self.stats['validation_failures'] += 1
                        self.stats['failed_loads'] += 1

                        error_msg = (
                            f"Validação de path falhou para: {path_str}\n"
                            f"Tipo de erro: {e.error_type}\n"
                            f"Detalhes: {e.message}"
                        )

                        logger.error(error_msg)
                        logger.debug(f"Sugestões: {e.suggestions}")

                        if raise_on_error:
                            raise DataLoadError(
                                message=error_msg,
                                path=path_str,
                                error_type="validation_failed",
                                original_error=e,
                                validation_info=validation_info
                            )
                        else:
                            return None

                # Usar path absoluto validado
                absolute_path = validation_info.get('absolute_path', path_str)
                logger.info(
                    f"Validação bem-sucedida: {absolute_path} "
                    f"({validation_info.get('size_mb', '?')} MB)"
                )
            else:
                # Sem validação - usar path diretamente
                absolute_path = path_str
                logger.warning(
                    f"Carregando sem validação (não recomendado): {absolute_path}"
                )

            # ===== FASE 2: CARREGAMENTO COM POLARS =====
            logger.debug(f"Iniciando carregamento Polars: {absolute_path}")

            try:
                df = pl.read_parquet(absolute_path, **polars_kwargs)

                # Validar DataFrame carregado
                if df is None or len(df) == 0:
                    error_msg = f"DataFrame vazio ou None após carregamento: {absolute_path}"
                    logger.warning(error_msg)

                    if raise_on_error:
                        raise DataLoadError(
                            message=error_msg,
                            path=absolute_path,
                            error_type="empty_dataframe",
                            validation_info=validation_info
                        )
                    else:
                        return None

                # ===== FASE 3: ATUALIZAR ESTATÍSTICAS =====
                load_time = (datetime.now() - start_time).total_seconds()
                row_count = len(df)
                col_count = len(df.columns)

                self.stats['successful_loads'] += 1
                self.stats['total_rows_loaded'] += row_count

                if 'size_bytes' in validation_info:
                    self.stats['total_bytes_loaded'] += validation_info['size_bytes']

                logger.info(
                    f"Carregamento bem-sucedido: {absolute_path}\n"
                    f"  - Linhas: {row_count:,}\n"
                    f"  - Colunas: {col_count}\n"
                    f"  - Tempo: {load_time:.3f}s\n"
                    f"  - Taxa: {row_count / load_time:,.0f} linhas/s"
                )

                return df

            except Exception as e:
                self.stats['polars_errors'] += 1
                self.stats['failed_loads'] += 1

                error_msg = (
                    f"Erro ao carregar arquivo Parquet com Polars: {absolute_path}\n"
                    f"Tipo: {type(e).__name__}\n"
                    f"Mensagem: {str(e)}"
                )

                logger.error(error_msg)
                logger.exception("Stack trace completo:")

                if raise_on_error:
                    raise DataLoadError(
                        message=error_msg,
                        path=absolute_path,
                        error_type="polars_read_error",
                        original_error=e,
                        validation_info=validation_info
                    )
                else:
                    return None

        except DataLoadError:
            # Re-raise DataLoadError sem modificar
            raise

        except Exception as e:
            # Capturar erros inesperados
            self.stats['failed_loads'] += 1

            error_msg = f"Erro inesperado ao carregar dados: {str(e)}"
            logger.exception(error_msg)

            if raise_on_error:
                raise DataLoadError(
                    message=error_msg,
                    path=path_str,
                    error_type="unexpected_error",
                    original_error=e,
                    validation_info=validation_info
                )
            else:
                return None

    def load_multiple_parquet(
        self,
        file_paths: list[Union[str, Path]],
        stop_on_error: bool = False,
        concatenate: bool = False,
        polars_kwargs: Optional[Dict] = None
    ) -> Union[Dict[str, pl.DataFrame], pl.DataFrame, None]:
        """
        Carrega múltiplos arquivos Parquet.

        Args:
            file_paths: Lista de paths para carregar
            stop_on_error: Se True, para no primeiro erro
            concatenate: Se True, concatena todos os DataFrames em um só
            polars_kwargs: Argumentos para pl.read_parquet()

        Returns:
            Dict[str, pl.DataFrame]: Mapeamento path -> DataFrame (concatenate=False)
            pl.DataFrame: DataFrame concatenado (concatenate=True)
            None: Se concatenate=True e nenhum arquivo foi carregado

        Exemplo:
            >>> loader = SafeDataLoader()
            >>> dfs = loader.load_multiple_parquet(["file1.parquet", "file2.parquet"])
            >>> for path, df in dfs.items():
            ...     print(f"{path}: {len(df)} linhas")
        """
        logger.info(f"Carregando {len(file_paths)} arquivos...")

        results = {}
        errors = []

        for file_path in file_paths:
            path_str = str(file_path)
            try:
                df = self.load_parquet(
                    file_path,
                    polars_kwargs=polars_kwargs,
                    raise_on_error=True
                )
                results[path_str] = df
                logger.debug(f"Carregado: {path_str}")

            except DataLoadError as e:
                errors.append((path_str, e))
                logger.error(f"Falha ao carregar {path_str}: {e.error_type}")

                if stop_on_error:
                    logger.error("Parando carregamento múltiplo devido a erro")
                    break

        # Log resumo
        success_count = len(results)
        total_count = len(file_paths)
        logger.info(
            f"Carregamento múltiplo concluído: {success_count}/{total_count} bem-sucedidos"
        )

        if errors:
            logger.warning(f"Erros encontrados em {len(errors)} arquivos:")
            for path, error in errors:
                logger.warning(f"  - {path}: {error.error_type}")

        # Concatenar se solicitado
        if concatenate:
            if not results:
                logger.warning("Nenhum DataFrame para concatenar")
                return None

            logger.info(f"Concatenando {len(results)} DataFrames...")
            try:
                concatenated = pl.concat(list(results.values()))
                logger.info(
                    f"Concatenação bem-sucedida: {len(concatenated):,} linhas totais"
                )
                return concatenated
            except Exception as e:
                logger.error(f"Erro ao concatenar DataFrames: {str(e)}")
                raise

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de carregamento.

        Returns:
            Dict com estatísticas completas:
                - total_loads: Total de tentativas de carregamento
                - successful_loads: Carregamentos bem-sucedidos
                - failed_loads: Carregamentos que falharam
                - success_rate: Taxa de sucesso (%)
                - validation_failures: Falhas na validação de path
                - polars_errors: Erros do Polars
                - total_rows_loaded: Total de linhas carregadas
                - total_bytes_loaded: Total de bytes carregados
                - avg_load_size_mb: Tamanho médio por carregamento (MB)
        """
        stats = self.stats.copy()

        # Calcular métricas derivadas
        if stats['total_loads'] > 0:
            stats['success_rate'] = (
                stats['successful_loads'] / stats['total_loads'] * 100
            )
        else:
            stats['success_rate'] = 0.0

        if stats['successful_loads'] > 0:
            stats['avg_load_size_mb'] = (
                stats['total_bytes_loaded'] / stats['successful_loads'] / (1024 * 1024)
            )
        else:
            stats['avg_load_size_mb'] = 0.0

        return stats

    def clear_cache(self):
        """Limpa o cache de validações."""
        cache_size = len(self._validation_cache)
        self._validation_cache.clear()
        logger.info(f"Cache de validações limpo ({cache_size} entradas removidas)")

    def reset_stats(self):
        """Reseta as estatísticas de carregamento."""
        logger.info("Resetando estatísticas de carregamento")
        self.stats = {
            'total_loads': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'validation_failures': 0,
            'polars_errors': 0,
            'total_rows_loaded': 0,
            'total_bytes_loaded': 0
        }


# Função de conveniência
def load_parquet_safe(
    file_path: Union[str, Path],
    base_path: Optional[Path] = None,
    **kwargs
) -> Optional[pl.DataFrame]:
    """
    Função de conveniência para carregar Parquet com validação.

    Args:
        file_path: Path do arquivo
        base_path: Path base opcional
        **kwargs: Argumentos adicionais para load_parquet()

    Returns:
        pl.DataFrame ou None

    Exemplo:
        >>> df = load_parquet_safe("data/file.parquet")
        >>> if df is not None:
        ...     print(f"Carregadas {len(df)} linhas")
    """
    loader = SafeDataLoader(base_path=base_path)
    return loader.load_parquet(file_path, **kwargs)


# Exemplo de uso
if __name__ == "__main__":
    print("=" * 80)
    print("TESTE DO SAFE DATA LOADER")
    print("=" * 80)

    # Criar loader
    loader = SafeDataLoader(enable_cache=True)

    # Teste 1: Carregar arquivo válido
    print("\n1. Testando carregamento de arquivo válido...")
    try:
        df = loader.load_parquet("data/parquet/Tabelao_qualidade.parquet")
        if df is not None:
            print(f"   Sucesso: {len(df):,} linhas, {len(df.columns)} colunas")
    except DataLoadError as e:
        print(f"   ERRO: {e.error_type}")
        print(f"   {e.message}")

    # Teste 2: Carregar arquivo inexistente
    print("\n2. Testando arquivo inexistente (raise_on_error=False)...")
    df = loader.load_parquet(
        "data/arquivo_inexistente.parquet",
        raise_on_error=False
    )
    print(f"   Resultado: {df}")

    # Teste 3: Estatísticas
    print("\n3. Estatísticas de carregamento:")
    stats = loader.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")

    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)
