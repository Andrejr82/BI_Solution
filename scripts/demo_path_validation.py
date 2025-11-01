"""
Demonstração do Sistema de Validação de Paths - FASE 1.3
=========================================================

Script de demonstração prática do PathValidator e SafeDataLoader.

Autor: Code Agent
Data: 2025-10-29
Versão: 1.0.0
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.utils.path_validator import PathValidator, PathValidationError
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError


def print_section(title: str):
    """Imprime cabeçalho de seção."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def demo_path_validator():
    """Demonstra uso do PathValidator."""
    print_section("DEMONSTRAÇÃO: PathValidator")

    validator = PathValidator()

    # Exemplo 1: Validar arquivo existente
    print("\n1. Validando arquivo Parquet existente:")
    print("   Path: data/parquet/Tabelao_qualidade.parquet")

    try:
        is_valid, info = validator.validate_parquet_path(
            "data/parquet/Tabelao_qualidade.parquet"
        )

        print(f"\n   Status: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")
        print(f"   Path absoluto: {info['absolute_path']}")
        print(f"   Tamanho: {info['size_mb']:.2f} MB")
        print(f"   Última modificação: {info['last_modified']}")
        print(f"   Tempo de validação: {info['validation_time_seconds']:.4f}s")

    except PathValidationError as e:
        print(f"\n   ✗ ERRO: {e.error_type}")
        print(f"   Mensagem: {e.message}")
        print(f"\n   Sugestões:")
        for i, sugg in enumerate(e.suggestions, 1):
            print(f"   {i}. {sugg}")

    # Exemplo 2: Validar arquivo inexistente
    print("\n2. Validando arquivo inexistente (demonstração de erro):")
    print("   Path: data/arquivo_que_nao_existe.parquet")

    try:
        is_valid, info = validator.validate_parquet_path(
            "data/arquivo_que_nao_existe.parquet"
        )
        print(f"   Status: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")

    except PathValidationError as e:
        print(f"\n   ✗ ERRO ESPERADO: {e.error_type}")
        print(f"   Path tentado: {e.path}")
        print(f"\n   Sugestões fornecidas:")
        for i, sugg in enumerate(e.suggestions, 1):
            print(f"   {i}. {sugg}")

    # Exemplo 3: Validar extensão inválida
    print("\n3. Validando arquivo com extensão inválida:")
    print("   Path: README.md")

    try:
        is_valid, info = validator.validate_parquet_path("README.md")
        print(f"   Status: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")

    except PathValidationError as e:
        print(f"\n   ✗ ERRO ESPERADO: {e.error_type}")
        print(f"   Extensão fornecida: {Path('README.md').suffix}")
        print(f"   Extensões válidas: .parquet, .parq")

    # Exemplo 4: Validar arquivo com permissão de leitura negada
    print("\n4. Validando arquivo com permissão de leitura negada:")
    restricted_file = Path("data/restricted_file.parquet")
    try:
        restricted_file.touch()
        os.chmod(restricted_file, 0o000)  # Sem permissão de leitura/escrita/execução
        print(f"   Path: {restricted_file}")
        is_valid, info = validator.validate_parquet_path(restricted_file)
        print(f"   Status: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")

    except PathValidationError as e:
        print(f"\n   ✗ ERRO ESPERADO: {e.error_type}")
        print(f"   Path tentado: {e.path}")
        print(f"\n   Sugestões fornecidas:")
        for i, sugg in enumerate(e.suggestions, 1):
            print(f"   {i}. {sugg}")
    finally:
        if restricted_file.exists():
            os.chmod(restricted_file, 0o666)
            restricted_file.unlink()


def demo_safe_data_loader():
    """Demonstra uso do SafeDataLoader."""
    print_section("DEMONSTRAÇÃO: SafeDataLoader")

    loader = SafeDataLoader(enable_cache=True)

    # Exemplo 1: Carregar arquivo válido
    print("\n1. Carregando arquivo Parquet válido:")
    print("   Path: data/parquet/Tabelao_qualidade.parquet")

    try:
        df = loader.load_parquet("data/parquet/Tabelao_qualidade.parquet")

        if df is not None:
            print(f"\n   ✓ CARREGAMENTO BEM-SUCEDIDO")
            print(f"   Linhas: {len(df):,}")
            print(f"   Colunas: {len(df.columns)}")
            print(f"   Primeiras colunas: {', '.join(df.columns[:5])}")

            # Mostrar estatísticas
            stats = loader.get_stats()
            print(f"\n   Estatísticas do loader:")
            print(f"   - Total de carregamentos: {stats['total_loads']}")
            print(f"   - Bem-sucedidos: {stats['successful_loads']}")
            print(f"   - Taxa de sucesso: {stats['success_rate']:.1f}%")
            print(f"   - Total de linhas carregadas: {stats['total_rows_loaded']:,}")

    except DataLoadError as e:
        print(f"\n   ✗ ERRO: {e.error_type}")
        print(f"   {e.message}")

    # Exemplo 2: Tentar carregar arquivo inexistente com raise_on_error=False
    print("\n2. Tentando carregar arquivo inexistente (raise_on_error=False):")
    print("   Path: data/arquivo_inexistente.parquet")

    df = loader.load_parquet(
        "data/arquivo_inexistente.parquet",
        raise_on_error=False
    )

    if df is None:
        print(f"\n   ✓ COMPORTAMENTO ESPERADO: Retornou None")
        print(f"   Não lançou exceção (raise_on_error=False)")

    # Exemplo 3: Tentar carregar com raise_on_error=True
    print("\n3. Tentando carregar arquivo inexistente (raise_on_error=True):")
    print("   Path: data/outro_arquivo_inexistente.parquet")

    try:
        df = loader.load_parquet(
            "data/outro_arquivo_inexistente.parquet",
            raise_on_error=True
        )
        print(f"   Carregado: {df is not None}")

    except DataLoadError as e:
        print(f"\n   ✗ ERRO ESPERADO: {e.error_type}")
        print(f"   Path: {e.path}")
        print(f"\n   Informações de validação:")
        for key, value in e.validation_info.items():
            if key not in ['validation_errors', 'validation_timestamp']:
                print(f"   - {key}: {value}")

    # Exemplo 4: Estatísticas finais
    print("\n4. Estatísticas finais do loader:")
    stats = loader.get_stats()

    print(f"\n   Total de tentativas: {stats['total_loads']}")
    print(f"   Bem-sucedidas: {stats['successful_loads']}")
    print(f"   Falhadas: {stats['failed_loads']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"   Falhas de validação: {stats['validation_failures']}")
    print(f"   Erros do Polars: {stats['polars_errors']}")

    if stats['successful_loads'] > 0:
        print(f"   Tamanho médio por arquivo: {stats['avg_load_size_mb']:.2f} MB")


def demo_error_messages():
    """Demonstra mensagens de erro claras."""
    print_section("DEMONSTRAÇÃO: Mensagens de Erro Claras")

    print("\nEste sistema fornece mensagens de erro detalhadas e acionáveis:")

    # Exemplo 1: Arquivo não encontrado
    print("\n1. ERRO: Arquivo não encontrado")
    print("   " + "-" * 70)

    try:
        validator = PathValidator()
        validator.validate_parquet_path("C:/caminho/inexistente/arquivo.parquet")
    except PathValidationError as e:
        error_str = str(e)
        for line in error_str.split('\n'):
            print(f"   {line}")

    # Exemplo 2: Extensão inválida
    print("\n2. ERRO: Extensão inválida")
    print("   " + "-" * 70)

    try:
        validator = PathValidator()
        validator.validate_parquet_path("requirements.txt")
    except PathValidationError as e:
        error_str = str(e)
        for line in error_str.split('\n'):
            print(f"   {line}")


def demo_logging():
    """Demonstra sistema de logging."""
    print_section("DEMONSTRAÇÃO: Sistema de Logging")

    print("\nO sistema registra todas as operações em logs detalhados:")
    print("\n1. Log de validação de paths:")
    print("   Arquivo: data/logs/path_validation.log")
    print("   Conteúdo: Todas as tentativas de validação, sucessos e falhas")

    print("\n2. Log de carregamento de dados:")
    print("   Arquivo: data/logs/data_loading.log")
    print("   Conteúdo: Todas as operações de carregamento, performance, erros")

    print("\n3. Formato dos logs:")
    print("   2025-10-29 10:30:45 - path_validator - INFO - Validação bem-sucedida: ...")
    print("   2025-10-29 10:30:46 - safe_data_loader - ERROR - Erro ao carregar: ...")

    # Tentar mostrar últimas linhas do log se existir
    log_file = Path("data/logs/path_validation.log")
    if log_file.exists():
        print(f"\n4. Últimas entradas em {log_file}:")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"   {line.rstrip()}")


def demo_best_practices():
    """Demonstra melhores práticas de uso."""
    print_section("DEMONSTRAÇÃO: Melhores Práticas")

    print("\n1. SEMPRE validar antes de carregar em produção:")
    print("""
    # ✓ BOM
    loader = SafeDataLoader(validate_on_load=True)
    df = loader.load_parquet("data/file.parquet")

    # ✗ RUIM (não recomendado)
    loader = SafeDataLoader(validate_on_load=False)
    df = loader.load_parquet("data/file.parquet")
    """)

    print("\n2. Usar raise_on_error=False para operações não críticas:")
    print("""
    # Para operações onde falha é aceitável
    df = loader.load_parquet("data/optional_file.parquet", raise_on_error=False)
    if df is None:
        print("Arquivo não disponível, usando dados padrão")
        df = get_default_data()
    """)

    print("\n3. Habilitar cache para múltiplos carregamentos:")
    print("""
    # Se vai carregar os mesmos arquivos múltiplas vezes
    loader = SafeDataLoader(enable_cache=True)

    # Primeira carga - validação completa
    df1 = loader.load_parquet("data/file.parquet")

    # Segunda carga - usa validação em cache (mais rápido)
    df2 = loader.load_parquet("data/file.parquet")
    """)

    print("\n4. Capturar e tratar erros específicos:")
    print("""
    try:
        df = loader.load_parquet("data/file.parquet")
    except DataLoadError as e:
        if e.error_type == "file_not_found":
            # Tratar arquivo não encontrado
            handle_missing_file()
        elif e.error_type == "no_read_permission":
            # Tratar problema de permissão
            handle_permission_error()
        else:
            # Erro genérico
            handle_generic_error(e)
    """)

    print("\n5. Monitorar estatísticas em aplicações de longo prazo:")
    print("""
    # Verificar periodicamente
    stats = loader.get_stats()
    if stats['success_rate'] < 90:
        alert_admin("Taxa de sucesso baixa: {}%".format(stats['success_rate']))

    # Resetar estatísticas periodicamente
    loader.reset_stats()
    """)


def main():
    """Executa todas as demonstrações."""
    print("=" * 80)
    print("SISTEMA DE VALIDAÇÃO DE PATHS - FASE 1.3")
    print("Demonstração Interativa")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        # Executar demonstrações
        demo_path_validator()
        demo_safe_data_loader()
        demo_error_messages()
        demo_logging()
        demo_best_practices()

        # Conclusão
        print_section("CONCLUSÃO")
        print("""
Este sistema elimina erros de "Load Failed" através de:

1. ✓ Validação robusta de paths ANTES de tentar carregar
2. ✓ Mensagens de erro claras com sugestões acionáveis
3. ✓ Logging detalhado de todas as operações
4. ✓ Estatísticas de carregamento para monitoramento
5. ✓ Tratamento de erros específicos e granular
6. ✓ Cache opcional para melhor performance
7. ✓ Suporte a operações em batch (múltiplos arquivos)
8. ✓ API simples e consistente

Para usar em seu código, simplesmente:

    from core.utils.safe_data_loader import SafeDataLoader

    loader = SafeDataLoader()
    df = loader.load_parquet("seu_arquivo.parquet")

TODOS os erros de "Load Failed" agora incluem:
- Path absoluto tentado
- Tipo específico do erro
- Sugestões de como resolver
- Informações de diagnóstico completas
        """)

        print("=" * 80)
        print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 80)

    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"ERRO NA DEMONSTRAÇÃO: {str(e)}")
        print(f"{'=' * 80}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
