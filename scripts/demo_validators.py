"""
Demonstração de uso dos Validadores e Handlers.

Este script demonstra como usar os novos componentes de validação
e tratamento de erros implementados no projeto.

Autor: Code Agent
Data: 2025-10-17
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Configurar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.validators.schema_validator import SchemaValidator
from core.utils.query_validator import (
    QueryValidator,
    validate_columns,
    handle_nulls,
    safe_filter,
    get_friendly_error
)
from core.utils.error_handler import (
    handle_error,
    get_error_stats,
    error_handler_decorator,
    create_error_response,
    ParquetErrorHandler
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Imprime cabeçalho de seção."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_schema_validator():
    """Demonstração do SchemaValidator."""
    print_section("1. SCHEMA VALIDATOR - Validação de Schemas Parquet")

    validator = SchemaValidator()

    # Verificar se existem arquivos Parquet
    parquet_dir = project_root / "data" / "parquet"

    if not parquet_dir.exists():
        print(f"❌ Diretório de dados Parquet não encontrado: {parquet_dir}")
        print("   Criando dados de exemplo...")

        # Criar diretório e dados de exemplo
        parquet_dir.mkdir(parents=True, exist_ok=True)

        # Criar DataFrame de exemplo
        df_example = pd.DataFrame({
            'produto_id': ['P001', 'P002', 'P003'],
            'descricao': ['Produto 1', 'Produto 2', 'Produto 3'],
            'preco': [10.5, 20.0, 30.5],
            'estoque': [5, 10, 15]
        })

        example_file = parquet_dir / "produtos_une1.parquet"
        df_example.to_parquet(example_file, index=False)
        print(f"✅ Arquivo de exemplo criado: {example_file}")

    # Validar arquivos Parquet
    print("\n📋 Validando arquivos Parquet...")

    for parquet_file in parquet_dir.glob("*.parquet"):
        print(f"\n  Arquivo: {parquet_file.name}")

        is_valid, errors = validator.validate_parquet_file(str(parquet_file))

        if is_valid:
            print(f"  ✅ Schema válido")
        else:
            print(f"  ❌ Schema inválido ({len(errors)} erros)")
            for error in errors:
                print(f"     - {error}")

    # Demonstrar validação de colunas de query
    print("\n\n🔍 Validando colunas para query...")

    table_name = 'produtos'
    query_columns = ['produto_id', 'preco', 'estoque', 'coluna_inexistente']

    is_valid, invalid_cols = validator.validate_query_columns(table_name, query_columns)

    if is_valid:
        print(f"  ✅ Todas as colunas são válidas")
    else:
        print(f"  ❌ Colunas inválidas encontradas: {invalid_cols}")


def demo_query_validator():
    """Demonstração do QueryValidator."""
    print_section("2. QUERY VALIDATOR - Validação e Tratamento de Queries")

    # Criar DataFrame de teste
    print("📊 Criando DataFrame de teste...")

    df = pd.DataFrame({
        'produto_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'descricao': ['Produto 1', 'Produto 2', None, 'Produto 4', 'Produto 5'],
        'preco': [10.5, None, 30.0, '45.50', 'invalid'],
        'estoque': ['5', '10', None, '15', '20'],
        'categoria': ['A', 'B', 'A', 'C', 'B']
    })

    print(f"\nDataFrame original ({len(df)} linhas):")
    print(df)

    # 1. Validar colunas
    print("\n\n1️⃣  VALIDAÇÃO DE COLUNAS")

    required_cols = ['produto_id', 'preco', 'estoque']
    is_valid, missing = validate_columns(df, required_cols, "produtos")

    if is_valid:
        print(f"  ✅ Todas as colunas obrigatórias presentes")
    else:
        print(f"  ❌ Colunas faltantes: {missing}")

    # Tentar validar com coluna inexistente
    is_valid, missing = validate_columns(df, ['produto_id', 'coluna_falsa'], "produtos")
    if not is_valid:
        print(f"  ℹ️  Exemplo de coluna faltante: {missing}")

    # 2. Tratar valores nulos
    print("\n\n2️⃣  TRATAMENTO DE VALORES NULOS")

    print(f"  Valores nulos em 'descricao': {df['descricao'].isna().sum()}")
    df = handle_nulls(df, 'descricao', strategy='fill', fill_value='Sem descrição')
    print(f"  Após preenchimento: {df['descricao'].isna().sum()} nulos")

    print(f"\n  Valores nulos em 'preco': {df['preco'].isna().sum()}")
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=0)
    print(f"  Após preenchimento: {df['preco'].isna().sum()} nulos")

    # 3. Converter tipos
    print("\n\n3️⃣  CONVERSÃO DE TIPOS")

    validator = QueryValidator()

    print("  Convertendo tipos de dados...")
    df = validator.validate_and_convert_types(df, {
        'preco': 'float',
        'estoque': 'int',
        'produto_id': 'str'
    })

    print(f"  ✅ Tipos após conversão:")
    print(f"     - preco: {df['preco'].dtype}")
    print(f"     - estoque: {df['estoque'].dtype}")
    print(f"     - produto_id: {df['produto_id'].dtype}")

    # 4. Filtro seguro
    print("\n\n4️⃣  FILTRO SEGURO")

    print("  Aplicando filtro: preco > 0")
    df_filtered = safe_filter(
        df,
        filter_func=lambda df: df[df['preco'] > 0],
        error_msg="Erro ao filtrar por preço"
    )
    print(f"  ✅ Resultados após filtro: {len(df_filtered)} linhas")

    # Tentar filtro inválido
    print("\n  Tentando filtro com coluna inexistente...")
    df_invalid = safe_filter(
        df,
        filter_func=lambda df: df[df['coluna_inexistente'] > 0],
        error_msg="Erro ao filtrar por coluna inexistente"
    )
    print(f"  ℹ️  DataFrame retornado com {len(df_invalid)} linhas (original)")

    # 5. Mensagens amigáveis
    print("\n\n5️⃣  MENSAGENS USER-FRIENDLY")

    test_errors = [
        FileNotFoundError("arquivo.parquet"),
        KeyError("campo_inexistente"),
        ValueError("Valor inválido"),
        TypeError("Tipo incompatível")
    ]

    for error in test_errors:
        message = get_friendly_error(error)
        print(f"  {type(error).__name__}: {message}")


def demo_error_handler():
    """Demonstração do ErrorHandler."""
    print_section("3. ERROR HANDLER - Tratamento Centralizado de Erros")

    # 1. Tratamento básico de erro
    print("1️⃣  TRATAMENTO BÁSICO DE ERRO\n")

    try:
        # Simular erro
        raise ValueError("Valor fora do intervalo permitido")

    except Exception as e:
        error_ctx = handle_error(
            e,
            context={
                'function': 'validar_valor',
                'param': 'idade',
                'value': -5
            },
            user_message="A idade deve ser um número positivo"
        )

        print(f"  Mensagem para usuário: {error_ctx.user_message}")
        print(f"  Tipo de erro: {error_ctx.error_type}")
        print(f"  Timestamp: {error_ctx.timestamp}")

    # 2. Decorador de error handling
    print("\n\n2️⃣  DECORADOR DE ERROR HANDLING\n")

    @error_handler_decorator(
        context_func=lambda une: {'une': une},
        return_on_error={'success': False, 'data': [], 'count': 0}
    )
    def buscar_produtos(une: int):
        """Função que pode falhar."""
        if une < 1 or une > 9:
            raise ValueError(f"UNE inválida: {une}")

        return {
            'success': True,
            'data': [{'id': 'P001', 'nome': 'Produto 1'}],
            'count': 1
        }

    # Teste com sucesso
    print("  Teste com UNE válida (une=1):")
    result = buscar_produtos(1)
    print(f"    Success: {result['success']}")
    print(f"    Count: {result['count']}")

    # Teste com erro
    print("\n  Teste com UNE inválida (une=99):")
    result = buscar_produtos(99)
    print(f"    Success: {result['success']}")
    print(f"    Error: {result.get('error', 'N/A')}")

    # 3. Resposta padronizada de erro
    print("\n\n3️⃣  RESPOSTA PADRONIZADA DE ERRO\n")

    try:
        # Simular erro de arquivo
        df = pd.read_parquet("arquivo_inexistente.parquet")

    except Exception as e:
        response = create_error_response(
            error=e,
            context={'operation': 'read_parquet', 'file': 'arquivo_inexistente.parquet'},
            include_details=True
        )

        print(f"  Response:")
        print(f"    success: {response['success']}")
        print(f"    message: {response['message']}")
        print(f"    error_type: {response['error_type']}")
        print(f"    timestamp: {response['timestamp']}")

    # 4. Estatísticas de erros
    print("\n\n4️⃣  ESTATÍSTICAS DE ERROS\n")

    # Gerar alguns erros para estatísticas
    test_errors = [
        ValueError("Erro 1"),
        ValueError("Erro 2"),
        KeyError("Erro 3"),
        FileNotFoundError("Erro 4")
    ]

    for error in test_errors:
        handle_error(error, {'test': True})

    stats = get_error_stats()

    print(f"  Total de erros: {stats['total_errors']}")
    print(f"  Erro mais comum: {stats['most_common_error']}")
    print(f"\n  Contadores por tipo:")
    for error_type, count in stats['error_counts'].items():
        print(f"    {error_type}: {count}")


def demo_integration():
    """Demonstração de integração completa."""
    print_section("4. INTEGRAÇÃO - Fluxo Completo de Validação")

    print("🔄 Simulando fluxo completo de query com validação...\n")

    # 1. Criar dados de teste
    print("1. Criar dados de teste")
    df = pd.DataFrame({
        'produto_id': ['P001', 'P002', 'P003', 'P004'],
        'descricao': ['Produto 1', None, 'Produto 3', 'Produto 4'],
        'preco': [10.5, 20.0, None, '30.5'],
        'estoque': ['5', '10', '15', 'invalid'],
        'une': [1, 1, 2, 2]
    })
    print(f"   ✅ DataFrame criado com {len(df)} linhas\n")

    # 2. Validar colunas
    print("2. Validar colunas obrigatórias")
    is_valid, missing = validate_columns(df, ['produto_id', 'preco', 'estoque'], 'produtos')
    if is_valid:
        print(f"   ✅ Todas as colunas presentes\n")
    else:
        print(f"   ❌ Colunas faltantes: {missing}\n")
        return

    # 3. Tratar nulos
    print("3. Tratar valores nulos")
    df = handle_nulls(df, 'descricao', strategy='fill', fill_value='Sem descrição')
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
    print(f"   ✅ Valores nulos tratados\n")

    # 4. Converter tipos
    print("4. Converter tipos de dados")
    validator = QueryValidator()
    df = validator.validate_and_convert_types(df, {
        'preco': 'float',
        'estoque': 'int'
    })
    print(f"   ✅ Tipos convertidos\n")

    # 5. Aplicar filtros
    print("5. Aplicar filtros")
    df_filtered = safe_filter(
        df,
        filter_func=lambda df: df[(df['preco'] > 0) & (df['estoque'] > 0)],
        error_msg="Erro ao filtrar produtos"
    )
    print(f"   ✅ Filtro aplicado: {len(df_filtered)} resultados\n")

    # 6. Resultado final
    print("6. Resultado final")
    print(df_filtered[['produto_id', 'descricao', 'preco', 'estoque']])

    print(f"\n✅ Fluxo completo executado com sucesso!")


def main():
    """Função principal."""
    print("\n" + "🎯"*35)
    print("  DEMONSTRAÇÃO: VALIDADORES E HANDLERS")
    print("  Agent Solution BI - v2.2")
    print("🎯"*35)

    try:
        # Executar demonstrações
        demo_schema_validator()
        demo_query_validator()
        demo_error_handler()
        demo_integration()

        print("\n\n" + "✅"*35)
        print("  DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅"*35 + "\n")

    except Exception as e:
        print(f"\n\n❌ Erro durante demonstração: {e}")
        logger.error("Erro na demonstração", exc_info=True)


if __name__ == "__main__":
    main()
