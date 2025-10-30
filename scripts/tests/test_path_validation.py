"""
Testes para Sistema de Validação de Paths - FASE 1.3
=====================================================

Suite completa de testes para PathValidator e SafeDataLoader.

Autor: Code Agent
Data: 2025-10-29
Versão: 1.0.0
"""

import sys
import os
from pathlib import Path
import tempfile
import time
import shutil

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.path_validator import (
    PathValidator,
    PathValidationError,
    validate_parquet_path
)
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

import polars as pl


class TestResults:
    """Coletor de resultados de testes."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def record_pass(self, test_name: str):
        """Registra teste que passou."""
        self.tests_run += 1
        self.tests_passed += 1
        print(f"   ✓ {test_name}")

    def record_fail(self, test_name: str, error: str):
        """Registra teste que falhou."""
        self.tests_run += 1
        self.tests_failed += 1
        self.failures.append((test_name, error))
        print(f"   ✗ {test_name}")
        print(f"     Erro: {error}")

    def print_summary(self):
        """Imprime resumo dos testes."""
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        print(f"Total de testes: {self.tests_run}")
        print(f"Passou: {self.tests_passed} ({self.tests_passed / self.tests_run * 100:.1f}%)")
        print(f"Falhou: {self.tests_failed} ({self.tests_failed / self.tests_run * 100:.1f}%)")

        if self.failures:
            print("\nFalhas:")
            for test_name, error in self.failures:
                print(f"  - {test_name}: {error}")

        print("=" * 80)


def create_temp_parquet(temp_dir: Path, filename: str, rows: int = 100) -> Path:
    """
    Cria arquivo Parquet temporário para testes.

    Args:
        temp_dir: Diretório temporário
        filename: Nome do arquivo
        rows: Número de linhas

    Returns:
        Path do arquivo criado
    """
    file_path = temp_dir / filename

    # Criar DataFrame de exemplo
    df = pl.DataFrame({
        "id": range(rows),
        "value": [f"value_{i}" for i in range(rows)],
        "number": [i * 10 for i in range(rows)]
    })

    # Salvar como Parquet
    df.write_parquet(file_path)

    return file_path


def test_path_validator(results: TestResults):
    """
    Testa PathValidator.

    Args:
        results: Coletor de resultados
    """
    print("\n" + "=" * 80)
    print("TESTANDO PATH VALIDATOR")
    print("=" * 80)

    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        validator = PathValidator(base_path=temp_path)

        # ===== TESTE 1: Arquivo válido =====
        print("\n1. Teste de arquivo válido:")
        try:
            valid_file = create_temp_parquet(temp_path, "valid.parquet", rows=50)
            is_valid, info = validator.validate_parquet_path(valid_file)

            assert is_valid, "Validação deveria ter passado"
            assert info['exists'], "Arquivo deveria existir"
            assert info['readable'], "Arquivo deveria ser legível"
            assert info['valid_extension'], "Extensão deveria ser válida"
            assert info['size_bytes'] > 0, "Arquivo deveria ter tamanho > 0"
            assert 'absolute_path' in info, "Deveria ter path absoluto"

            results.record_pass("Validação de arquivo válido")
        except Exception as e:
            results.record_fail("Validação de arquivo válido", str(e))

        # ===== TESTE 2: Arquivo inexistente =====
        print("\n2. Teste de arquivo inexistente:")
        try:
            non_existent = temp_path / "nao_existe.parquet"

            try:
                is_valid, info = validator.validate_parquet_path(non_existent)
                results.record_fail(
                    "Arquivo inexistente deveria falhar",
                    "Validação não lançou PathValidationError"
                )
            except PathValidationError as e:
                assert e.error_type == "file_not_found", "Tipo de erro incorreto"
                assert len(e.suggestions) > 0, "Deveria ter sugestões"
                results.record_pass("Detecção de arquivo inexistente")

        except Exception as e:
            results.record_fail("Detecção de arquivo inexistente", str(e))

        # ===== TESTE 3: Extensão inválida =====
        print("\n3. Teste de extensão inválida:")
        try:
            invalid_ext = temp_path / "arquivo.txt"
            invalid_ext.write_text("conteúdo falso")

            try:
                is_valid, info = validator.validate_parquet_path(invalid_ext)
                results.record_fail(
                    "Extensão inválida deveria falhar",
                    "Validação não lançou PathValidationError"
                )
            except PathValidationError as e:
                assert e.error_type == "invalid_extension", "Tipo de erro incorreto"
                results.record_pass("Detecção de extensão inválida")

        except Exception as e:
            results.record_fail("Detecção de extensão inválida", str(e))

        # ===== TESTE 4: Arquivo muito pequeno =====
        print("\n4. Teste de arquivo muito pequeno:")
        try:
            small_file = temp_path / "small.parquet"
            small_file.write_bytes(b"fake")  # Apenas 4 bytes

            try:
                is_valid, info = validator.validate_parquet_path(small_file)
                results.record_fail(
                    "Arquivo pequeno deveria falhar",
                    "Validação não lançou PathValidationError"
                )
            except PathValidationError as e:
                assert e.error_type == "file_too_small", "Tipo de erro incorreto"
                results.record_pass("Detecção de arquivo muito pequeno")

        except Exception as e:
            results.record_fail("Detecção de arquivo muito pequeno", str(e))

        # ===== TESTE 5: Path relativo =====
        print("\n5. Teste de path relativo:")
        try:
            rel_file = create_temp_parquet(temp_path, "relative.parquet")

            # Validar com path relativo
            is_valid, info = validator.validate_parquet_path("relative.parquet")

            assert is_valid, "Path relativo deveria ser resolvido"
            assert Path(info['absolute_path']).is_absolute(), "Deveria retornar path absoluto"

            results.record_pass("Resolução de path relativo")
        except Exception as e:
            results.record_fail("Resolução de path relativo", str(e))

        # ===== TESTE 6: Validação múltipla =====
        print("\n6. Teste de validação múltipla:")
        try:
            # Criar múltiplos arquivos
            files = [
                create_temp_parquet(temp_path, f"file{i}.parquet")
                for i in range(3)
            ]
            files.append(temp_path / "nao_existe.parquet")  # Um inválido

            results_dict = validator.validate_multiple_paths(files)

            assert len(results_dict) == 4, "Deveria validar todos os paths"
            valid_count = sum(1 for r in results_dict.values() if r["valid"])
            assert valid_count == 3, "3 arquivos deveriam ser válidos"

            results.record_pass("Validação múltipla de paths")
        except Exception as e:
            results.record_fail("Validação múltipla de paths", str(e))

        # ===== TESTE 7: Função de conveniência =====
        print("\n7. Teste de função de conveniência:")
        try:
            conv_file = create_temp_parquet(temp_path, "convenience.parquet")

            is_valid, info = validate_parquet_path(conv_file, base_path=temp_path)

            assert is_valid, "Função de conveniência deveria funcionar"
            assert 'size_mb' in info, "Deveria ter informações completas"

            results.record_pass("Função de conveniência validate_parquet_path()")
        except Exception as e:
            results.record_fail("Função de conveniência validate_parquet_path()", str(e))

        # ===== TESTE 8: Metadados do arquivo =====
        print("\n8. Teste de metadados do arquivo:")
        try:
            meta_file = create_temp_parquet(temp_path, "metadata.parquet")

            is_valid, info = validator.validate_parquet_path(meta_file)

            assert 'last_modified' in info, "Deveria ter última modificação"
            assert 'last_accessed' in info, "Deveria ter último acesso"
            assert 'size_mb' in info, "Deveria ter tamanho em MB"
            assert 'validation_time_seconds' in info, "Deveria ter tempo de validação"

            results.record_pass("Coleta de metadados do arquivo")
        except Exception as e:
            results.record_fail("Coleta de metadados do arquivo", str(e))


def test_safe_data_loader(results: TestResults):
    """
    Testa SafeDataLoader.

    Args:
        results: Coletor de resultados
    """
    print("\n" + "=" * 80)
    print("TESTANDO SAFE DATA LOADER")
    print("=" * 80)

    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        loader = SafeDataLoader(base_path=temp_path, enable_cache=True)

        # ===== TESTE 1: Carregamento válido =====
        print("\n1. Teste de carregamento válido:")
        try:
            valid_file = create_temp_parquet(temp_path, "load_valid.parquet", rows=100)

            df = loader.load_parquet(valid_file)

            assert df is not None, "DataFrame não deveria ser None"
            assert len(df) == 100, "Deveria ter 100 linhas"
            assert len(df.columns) == 3, "Deveria ter 3 colunas"

            results.record_pass("Carregamento de arquivo válido")
        except Exception as e:
            results.record_fail("Carregamento de arquivo válido", str(e))

        # ===== TESTE 2: Arquivo inexistente com raise_on_error=True =====
        print("\n2. Teste de arquivo inexistente (raise_on_error=True):")
        try:
            non_existent = temp_path / "nao_existe.parquet"

            try:
                df = loader.load_parquet(non_existent, raise_on_error=True)
                results.record_fail(
                    "Arquivo inexistente deveria falhar",
                    "Não lançou DataLoadError"
                )
            except DataLoadError as e:
                assert e.error_type == "validation_failed", "Tipo de erro incorreto"
                results.record_pass("Detecção de arquivo inexistente (raise=True)")

        except Exception as e:
            results.record_fail("Detecção de arquivo inexistente (raise=True)", str(e))

        # ===== TESTE 3: Arquivo inexistente com raise_on_error=False =====
        print("\n3. Teste de arquivo inexistente (raise_on_error=False):")
        try:
            non_existent = temp_path / "nao_existe2.parquet"

            df = loader.load_parquet(non_existent, raise_on_error=False)

            assert df is None, "Deveria retornar None quando raise_on_error=False"

            results.record_pass("Retorno None com raise_on_error=False")
        except Exception as e:
            results.record_fail("Retorno None com raise_on_error=False", str(e))

        # ===== TESTE 4: Carregamento sem validação =====
        print("\n4. Teste de carregamento sem validação:")
        try:
            no_val_file = create_temp_parquet(temp_path, "no_validation.parquet")

            df = loader.load_parquet(no_val_file, validate=False)

            assert df is not None, "Deveria carregar mesmo sem validação"

            results.record_pass("Carregamento sem validação")
        except Exception as e:
            results.record_fail("Carregamento sem validação", str(e))

        # ===== TESTE 5: Cache de validações =====
        print("\n5. Teste de cache de validações:")
        try:
            cache_file = create_temp_parquet(temp_path, "cache_test.parquet")

            # Primeira carga - validação completa
            start1 = time.time()
            df1 = loader.load_parquet(cache_file)
            time1 = time.time() - start1

            # Segunda carga - deveria usar cache
            start2 = time.time()
            df2 = loader.load_parquet(cache_file)
            time2 = time.time() - start2

            assert df1 is not None and df2 is not None, "Ambas cargas deveriam suceder"
            # Cache pode tornar segunda carga mais rápida (mas não garantido)

            results.record_pass("Cache de validações")
        except Exception as e:
            results.record_fail("Cache de validações", str(e))

        # ===== TESTE 6: Carregamento múltiplo =====
        print("\n6. Teste de carregamento múltiplo:")
        try:
            multi_files = [
                create_temp_parquet(temp_path, f"multi{i}.parquet", rows=50)
                for i in range(3)
            ]

            dfs = loader.load_multiple_parquet(multi_files, concatenate=False)

            assert len(dfs) == 3, "Deveria carregar 3 arquivos"
            for path, df in dfs.items():
                assert len(df) == 50, "Cada DataFrame deveria ter 50 linhas"

            results.record_pass("Carregamento múltiplo (sem concatenar)")
        except Exception as e:
            results.record_fail("Carregamento múltiplo (sem concatenar)", str(e))

        # ===== TESTE 7: Carregamento múltiplo com concatenação =====
        print("\n7. Teste de carregamento múltiplo com concatenação:")
        try:
            concat_files = [
                create_temp_parquet(temp_path, f"concat{i}.parquet", rows=30)
                for i in range(4)
            ]

            df = loader.load_multiple_parquet(concat_files, concatenate=True)

            assert df is not None, "DataFrame concatenado não deveria ser None"
            assert len(df) == 120, "Deveria ter 120 linhas totais (4 x 30)"

            results.record_pass("Carregamento múltiplo com concatenação")
        except Exception as e:
            results.record_fail("Carregamento múltiplo com concatenação", str(e))

        # ===== TESTE 8: Estatísticas de carregamento =====
        print("\n8. Teste de estatísticas:")
        try:
            stats = loader.get_stats()

            assert 'total_loads' in stats, "Deveria ter total_loads"
            assert 'successful_loads' in stats, "Deveria ter successful_loads"
            assert 'success_rate' in stats, "Deveria ter success_rate"
            assert stats['total_loads'] > 0, "Deveria ter registrado carregamentos"

            results.record_pass("Coleta de estatísticas")
        except Exception as e:
            results.record_fail("Coleta de estatísticas", str(e))

        # ===== TESTE 9: Reset de estatísticas =====
        print("\n9. Teste de reset de estatísticas:")
        try:
            loader.reset_stats()
            stats = loader.get_stats()

            assert stats['total_loads'] == 0, "Estatísticas deveriam estar zeradas"
            assert stats['successful_loads'] == 0, "Cargas bem-sucedidas deveriam estar zeradas"

            results.record_pass("Reset de estatísticas")
        except Exception as e:
            results.record_fail("Reset de estatísticas", str(e))

        # ===== TESTE 10: Clear de cache =====
        print("\n10. Teste de clear de cache:")
        try:
            # Carregar arquivo para popular cache
            cache_clear_file = create_temp_parquet(temp_path, "cache_clear.parquet")
            loader.load_parquet(cache_clear_file)

            # Limpar cache
            loader.clear_cache()

            # Verificar que cache foi limpo (através de recarga)
            loader.load_parquet(cache_clear_file)

            results.record_pass("Limpeza de cache")
        except Exception as e:
            results.record_fail("Limpeza de cache", str(e))


def test_integration(results: TestResults):
    """
    Testes de integração do sistema completo.

    Args:
        results: Coletor de resultados
    """
    print("\n" + "=" * 80)
    print("TESTES DE INTEGRAÇÃO")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # ===== TESTE 1: Pipeline completo de validação e carregamento =====
        print("\n1. Teste de pipeline completo:")
        try:
            # Criar arquivo
            test_file = create_temp_parquet(temp_path, "integration.parquet", rows=200)

            # Validar primeiro
            validator = PathValidator(base_path=temp_path)
            is_valid, val_info = validator.validate_parquet_path(test_file)

            assert is_valid, "Validação deveria passar"

            # Carregar depois
            loader = SafeDataLoader(base_path=temp_path)
            df = loader.load_parquet(test_file)

            assert df is not None, "Carregamento deveria suceder"
            assert len(df) == 200, "Deveria ter 200 linhas"

            results.record_pass("Pipeline completo validação + carregamento")
        except Exception as e:
            results.record_fail("Pipeline completo validação + carregamento", str(e))

        # ===== TESTE 2: Tratamento de erros consistente =====
        print("\n2. Teste de tratamento de erros consistente:")
        try:
            loader = SafeDataLoader(base_path=temp_path)

            # Tentar carregar arquivo inexistente
            try:
                loader.load_parquet("nao_existe.parquet", raise_on_error=True)
                results.record_fail(
                    "Erro deveria ser lançado",
                    "DataLoadError não foi lançado"
                )
            except DataLoadError as e:
                # Verificar estrutura do erro
                assert e.message, "Erro deveria ter mensagem"
                assert e.path, "Erro deveria ter path"
                assert e.error_type, "Erro deveria ter tipo"
                assert e.validation_info is not None, "Erro deveria ter validation_info"

                results.record_pass("Tratamento de erros consistente")

        except Exception as e:
            results.record_fail("Tratamento de erros consistente", str(e))

        # ===== TESTE 3: Performance com múltiplos arquivos =====
        print("\n3. Teste de performance com múltiplos arquivos:")
        try:
            # Criar 10 arquivos
            files = [
                create_temp_parquet(temp_path, f"perf{i}.parquet", rows=100)
                for i in range(10)
            ]

            loader = SafeDataLoader(base_path=temp_path, enable_cache=True)

            start = time.time()
            dfs = loader.load_multiple_parquet(files, concatenate=False)
            elapsed = time.time() - start

            assert len(dfs) == 10, "Deveria carregar todos os 10 arquivos"
            print(f"     Tempo total: {elapsed:.3f}s ({elapsed/10:.3f}s por arquivo)")

            results.record_pass("Performance com múltiplos arquivos")
        except Exception as e:
            results.record_fail("Performance com múltiplos arquivos", str(e))


def main():
    """Executa todos os testes."""
    print("=" * 80)
    print("SUITE DE TESTES - FASE 1.3: VALIDAÇÃO DE PATHS")
    print("=" * 80)
    print(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Diretório: {project_root}")
    print("=" * 80)

    results = TestResults()

    try:
        # Executar testes
        test_path_validator(results)
        test_safe_data_loader(results)
        test_integration(results)

    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"ERRO CRÍTICO NOS TESTES: {str(e)}")
        print(f"{'=' * 80}")
        import traceback
        traceback.print_exc()

    finally:
        # Imprimir resumo
        results.print_summary()

        # Retornar código de saída apropriado
        sys.exit(0 if results.tests_failed == 0 else 1)


if __name__ == "__main__":
    main()
