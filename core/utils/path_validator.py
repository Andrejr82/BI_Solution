"""
Validador de Paths para Carregamento de Arquivos Parquet
=========================================================

Este módulo fornece validação robusta de paths antes de tentar carregar arquivos,
eliminando erros de "Load Failed" com mensagens claras e diagnóstico completo.

Autor: Code Agent
Data: 2025-10-29
Versão: 1.0.0
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

# Configurar logger específico para validação de paths
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler para arquivo de log dedicado
log_file = Path("data/logs/path_validation.log")
log_file.parent.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class PathValidationError(Exception):
    """
    Exceção customizada para erros de validação de path.

    Atributos:
        message: Mensagem de erro clara para o usuário
        path: Path que falhou na validação
        error_type: Tipo específico do erro (not_found, no_permission, invalid_extension, etc)
        suggestions: Lista de sugestões para resolver o problema
    """

    def __init__(
        self,
        message: str,
        path: str,
        error_type: str,
        suggestions: list = None
    ):
        self.message = message
        self.path = path
        self.error_type = error_type
        self.suggestions = suggestions or []
        super().__init__(self.message)

    def __str__(self):
        """Formata mensagem de erro com sugestões."""
        msg = f"{self.message}\n"
        msg += f"Path: {self.path}\n"
        msg += f"Tipo de erro: {self.error_type}\n"
        if self.suggestions:
            msg += "\nSugestões:\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                msg += f"  {i}. {suggestion}\n"
        return msg


class PathValidator:
    """
    Validador robusto de paths para arquivos Parquet.

    Realiza validações completas antes de tentar carregar arquivos:
    - Existência do arquivo
    - Permissões de leitura
    - Extensão válida (.parquet)
    - Tamanho do arquivo
    - Último acesso/modificação

    Exemplo:
        >>> validator = PathValidator()
        >>> is_valid, info = validator.validate_parquet_path("data/file.parquet")
        >>> if is_valid:
        ...     df = pl.read_parquet(info['absolute_path'])
    """

    VALID_EXTENSIONS = {'.parquet', '.parq'}
    MIN_FILE_SIZE = 100  # bytes - arquivo muito pequeno pode estar corrompido

    def __init__(self, base_path: Optional[Path] = None):
        """
        Inicializa o validador.

        Args:
            base_path: Path base para resolução de paths relativos.
                      Se None, usa o diretório de trabalho atual.
        """
        self.base_path = base_path or Path.cwd()
        logger.info(f"PathValidator inicializado com base_path: {self.base_path}")

    def validate_parquet_path(
        self,
        file_path: str | Path,
        check_size: bool = True,
        min_size: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida um path de arquivo Parquet de forma robusta.

        Args:
            file_path: Path do arquivo a validar (pode ser relativo ou absoluto)
            check_size: Se True, valida tamanho mínimo do arquivo
            min_size: Tamanho mínimo em bytes (usa MIN_FILE_SIZE se None)

        Returns:
            Tuple[bool, Dict]: (is_valid, validation_info)
                - is_valid: True se todas as validações passaram
                - validation_info: Dicionário com informações detalhadas:
                    - absolute_path: Path absoluto do arquivo
                    - exists: Se o arquivo existe
                    - readable: Se tem permissão de leitura
                    - valid_extension: Se tem extensão válida
                    - size_bytes: Tamanho do arquivo em bytes
                    - last_modified: Última modificação
                    - validation_errors: Lista de erros encontrados
                    - validation_timestamp: Timestamp da validação

        Raises:
            PathValidationError: Se validação falhar, com detalhes do erro
        """
        start_time = datetime.now()
        validation_info = {
            'validation_timestamp': start_time.isoformat(),
            'original_path': str(file_path),
            'validation_errors': []
        }

        try:
            # 1. Converter para Path e resolver para absoluto
            path_obj = Path(file_path)
            if not path_obj.is_absolute():
                path_obj = self.base_path / path_obj

            absolute_path = path_obj.resolve()
            validation_info['absolute_path'] = str(absolute_path)

            logger.debug(f"Validando path: {absolute_path}")

            # 2. Verificar existência do arquivo
            exists = absolute_path.exists()
            validation_info['exists'] = exists

            if not exists:
                error_msg = f"Arquivo não encontrado: {absolute_path}"
                validation_info['validation_errors'].append(error_msg)
                logger.error(error_msg)

                suggestions = [
                    f"Verifique se o path está correto: {absolute_path}",
                    "Confirme que o arquivo não foi movido ou deletado",
                    f"Verifique a configuração do path base: {self.base_path}",
                    "Execute o script de extração de dados se necessário"
                ]

                raise PathValidationError(
                    message=error_msg,
                    path=str(absolute_path),
                    error_type="file_not_found",
                    suggestions=suggestions
                )

            # 3. Verificar se é um arquivo (não diretório)
            if not absolute_path.is_file():
                error_msg = f"Path não é um arquivo: {absolute_path}"
                validation_info['validation_errors'].append(error_msg)
                logger.error(error_msg)

                raise PathValidationError(
                    message=error_msg,
                    path=str(absolute_path),
                    error_type="not_a_file",
                    suggestions=["Forneça o path completo do arquivo, não um diretório"]
                )

            # 4. Verificar extensão
            valid_extension = absolute_path.suffix.lower() in self.VALID_EXTENSIONS
            validation_info['valid_extension'] = valid_extension
            validation_info['extension'] = absolute_path.suffix

            if not valid_extension:
                error_msg = (
                    f"Extensão inválida: {absolute_path.suffix}. "
                    f"Esperado: {', '.join(self.VALID_EXTENSIONS)}"
                )
                validation_info['validation_errors'].append(error_msg)
                logger.error(error_msg)

                raise PathValidationError(
                    message=error_msg,
                    path=str(absolute_path),
                    error_type="invalid_extension",
                    suggestions=[
                        f"Use arquivos com extensões válidas: {', '.join(self.VALID_EXTENSIONS)}",
                        "Verifique se o arquivo foi salvo no formato correto"
                    ]
                )

            # 5. Verificar permissões de leitura
            readable = os.access(absolute_path, os.R_OK)
            validation_info['readable'] = readable

            if not readable:
                error_msg = f"Sem permissão de leitura para: {absolute_path}"
                validation_info['validation_errors'].append(error_msg)
                logger.error(error_msg)

                suggestions = [
                    "Verifique as permissões do arquivo no sistema operacional",
                    "Execute o aplicativo com privilégios adequados",
                    "Verifique se o arquivo não está aberto em outro programa"
                ]

                # Adicionar informações específicas do Windows
                if os.name == 'nt':
                    suggestions.append("No Windows, verifique se o arquivo não está bloqueado")
                    suggestions.append("Tente executar como Administrador se necessário")

                raise PathValidationError(
                    message=error_msg,
                    path=str(absolute_path),
                    error_type="no_read_permission",
                    suggestions=suggestions
                )

            # 6. Verificar tamanho do arquivo
            file_size = absolute_path.stat().st_size
            validation_info['size_bytes'] = file_size
            validation_info['size_mb'] = round(file_size / (1024 * 1024), 2)

            if check_size:
                min_required_size = min_size or self.MIN_FILE_SIZE
                if file_size < min_required_size:
                    error_msg = (
                        f"Arquivo muito pequeno ({file_size} bytes). "
                        f"Mínimo esperado: {min_required_size} bytes. "
                        f"Arquivo pode estar corrompido."
                    )
                    validation_info['validation_errors'].append(error_msg)
                    logger.warning(error_msg)

                    raise PathValidationError(
                        message=error_msg,
                        path=str(absolute_path),
                        error_type="file_too_small",
                        suggestions=[
                            "Verifique se o arquivo foi gerado corretamente",
                            "Regere o arquivo Parquet se necessário",
                            "Confirme que a exportação foi concluída com sucesso"
                        ]
                    )

            # 7. Coletar metadados adicionais
            stat_info = absolute_path.stat()
            validation_info['last_modified'] = datetime.fromtimestamp(
                stat_info.st_mtime
            ).isoformat()
            validation_info['last_accessed'] = datetime.fromtimestamp(
                stat_info.st_atime
            ).isoformat()

            # 8. Verificar se arquivo pode ser aberto
            try:
                with open(absolute_path, 'rb') as f:
                    # Tentar ler os primeiros bytes para verificar acesso real
                    f.read(1)
                validation_info['can_open'] = True
            except Exception as e:
                error_msg = f"Erro ao tentar abrir arquivo: {str(e)}"
                validation_info['validation_errors'].append(error_msg)
                validation_info['can_open'] = False
                logger.error(error_msg)

                raise PathValidationError(
                    message=error_msg,
                    path=str(absolute_path),
                    error_type="cannot_open_file",
                    suggestions=[
                        "Arquivo pode estar corrompido",
                        "Arquivo pode estar em uso por outro processo",
                        "Verifique integridade do arquivo"
                    ]
                )

            # Validação bem-sucedida
            validation_time = (datetime.now() - start_time).total_seconds()
            validation_info['validation_time_seconds'] = validation_time

            logger.info(
                f"Validação bem-sucedida para {absolute_path} "
                f"({validation_info['size_mb']} MB) em {validation_time:.3f}s"
            )

            return True, validation_info

        except PathValidationError:
            # Re-raise PathValidationError sem modificar
            raise

        except Exception as e:
            # Capturar erros inesperados
            error_msg = f"Erro inesperado durante validação: {str(e)}"
            validation_info['validation_errors'].append(error_msg)
            logger.exception(error_msg)

            raise PathValidationError(
                message=error_msg,
                path=str(file_path),
                error_type="unexpected_error",
                suggestions=[
                    "Verifique os logs para mais detalhes",
                    "Contate o suporte técnico se o problema persistir"
                ]
            )

    def validate_multiple_paths(
        self,
        file_paths: list[str | Path],
        stop_on_first_error: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Valida múltiplos paths de uma vez.

        Args:
            file_paths: Lista de paths para validar
            stop_on_first_error: Se True, para na primeira validação que falhar

        Returns:
            Dict mapeando cada path para seu resultado de validação:
                {
                    "path1": {"valid": True, "info": {...}},
                    "path2": {"valid": False, "error": "...", "info": {...}}
                }
        """
        results = {}

        for file_path in file_paths:
            path_str = str(file_path)
            try:
                is_valid, info = self.validate_parquet_path(file_path)
                results[path_str] = {
                    "valid": True,
                    "info": info
                }
            except PathValidationError as e:
                results[path_str] = {
                    "valid": False,
                    "error": str(e),
                    "error_type": e.error_type,
                    "suggestions": e.suggestions
                }

                if stop_on_first_error:
                    logger.error(f"Parando validação múltipla devido a erro em: {path_str}")
                    break

        # Log resumo
        valid_count = sum(1 for r in results.values() if r["valid"])
        total_count = len(results)
        logger.info(
            f"Validação múltipla concluída: {valid_count}/{total_count} paths válidos"
        )

        return results

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das validações realizadas.

        Returns:
            Dict com estatísticas agregadas das validações
        """
        # Implementação futura: coletar estatísticas de validações
        return {
            "base_path": str(self.base_path),
            "valid_extensions": list(self.VALID_EXTENSIONS),
            "min_file_size": self.MIN_FILE_SIZE
        }


def validate_parquet_path(
    file_path: str | Path,
    base_path: Optional[Path] = None,
    **kwargs
) -> Tuple[bool, Dict[str, Any]]:
    """
    Função de conveniência para validar um path sem criar instância do validador.

    Args:
        file_path: Path do arquivo a validar
        base_path: Path base opcional
        **kwargs: Argumentos adicionais para validate_parquet_path()

    Returns:
        Tuple[bool, Dict]: (is_valid, validation_info)

    Exemplo:
        >>> is_valid, info = validate_parquet_path("data/file.parquet")
        >>> if is_valid:
        ...     print(f"Arquivo OK: {info['size_mb']} MB")
    """
    validator = PathValidator(base_path=base_path)
    return validator.validate_parquet_path(file_path, **kwargs)


# Exemplo de uso
if __name__ == "__main__":
    print("=" * 80)
    print("TESTE DO VALIDADOR DE PATHS")
    print("=" * 80)

    # Teste 1: Path válido
    print("\n1. Testando path válido...")
    try:
        is_valid, info = validate_parquet_path(
            "data/parquet/Tabelao_qualidade.parquet"
        )
        print(f"   Status: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
        print(f"   Tamanho: {info.get('size_mb', 'N/A')} MB")
        print(f"   Última modificação: {info.get('last_modified', 'N/A')}")
    except PathValidationError as e:
        print(f"   ERRO: {e.error_type}")
        print(f"   {e.message}")

    # Teste 2: Path inválido
    print("\n2. Testando path inexistente...")
    try:
        is_valid, info = validate_parquet_path("data/arquivo_inexistente.parquet")
        print(f"   Status: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    except PathValidationError as e:
        print(f"   ERRO (esperado): {e.error_type}")
        print(f"   Sugestões: {len(e.suggestions)} disponíveis")

    # Teste 3: Extensão inválida
    print("\n3. Testando extensão inválida...")
    try:
        is_valid, info = validate_parquet_path("data/arquivo.csv")
        print(f"   Status: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    except PathValidationError as e:
        print(f"   ERRO (esperado): {e.error_type}")

    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)
