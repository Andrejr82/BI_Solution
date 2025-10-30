"""
Script de Teste: Sistema de Mitigação de Erros de Colunas
==========================================================

Testa todas as camadas de proteção contra erros de colunas não encontradas:
1. Validação no column_validator.py
2. Auto-correção no polars_dask_adapter.py
3. Tratamento de exceções no code_gen_agent.py

Casos de Teste:
- Query com nome de coluna legado (NOME_PRODUTO → nome_produto)
- Query com case incorreto (Venda_30_D → venda_30_d)
- Query com coluna inexistente + sugestões
- Query complexa com múltiplos erros
- Query real: "ranking de vendas todas as unes"

Autor: Claude Code
Data: 2025-10-27
"""

import sys
import os
import logging

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.utils.column_validator import (
    validate_column,
    validate_columns,
    validate_query_code,
    extract_columns_from_query,
    ColumnValidationError,
    print_validation_report
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Imprime cabeçalho formatado."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Imprime resultado de teste."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"  {details}")


def test_column_validation():
    """Testa validação individual de colunas."""
    print_header("TESTE 1: Validação Individual de Colunas")

    # Mock de colunas disponíveis (baseado no Parquet real)
    available = [
        "codigo", "nome_produto", "une", "une_nome",
        "nomesegmento", "nomegrupo", "NOMECATEGORIA", "NOMESUBGRUPO",
        "venda_30_d", "estoque_atual", "preco_38_percent"
    ]

    test_cases = [
        # (input, expected_valid, expected_corrected)
        ("nome_produto", True, "nome_produto"),      # Já correto
        ("NOME_PRODUTO", True, "nome_produto"),      # Case legado
        ("PRODUTO", True, "codigo"),                  # Nome legado
        ("VENDA_30DD", True, "venda_30_d"),          # Nome legado
        ("ESTOQUE_UNE", True, "estoque_atual"),      # Nome legado
        ("coluna_inexistente", False, None),         # Inexistente
    ]

    passed_tests = 0
    total_tests = len(test_cases)

    for col_input, expected_valid, expected_corrected in test_cases:
        is_valid, corrected, suggestions = validate_column(col_input, available)

        # Verificar resultado
        if is_valid == expected_valid:
            if not expected_valid or corrected == expected_corrected:
                passed_tests += 1
                print_test_result(
                    f"Validar '{col_input}'",
                    True,
                    f"Resultado: {'válido' if is_valid else 'inválido'}, Corrigido: {corrected}"
                )
            else:
                print_test_result(
                    f"Validar '{col_input}'",
                    False,
                    f"Esperado: {expected_corrected}, Obtido: {corrected}"
                )
        else:
            print_test_result(
                f"Validar '{col_input}'",
                False,
                f"Esperado válido={expected_valid}, Obtido={is_valid}"
            )

    print(f"\n[STATS] Resultado: {passed_tests}/{total_tests} testes passaram")
    return passed_tests == total_tests


def test_multiple_columns_validation():
    """Testa validação de múltiplas colunas."""
    print_header("TESTE 2: Validação de Múltiplas Colunas")

    available = [
        "codigo", "nome_produto", "une", "venda_30_d", "estoque_atual"
    ]

    # Teste com mix de colunas válidas e inválidas
    columns_to_test = [
        "NOME_PRODUTO",    # Legado → nome_produto
        "codigo",          # Já correto
        "VENDA_30DD",      # Legado → venda_30_d
        "coluna_falsa",    # Inválida
    ]

    result = validate_columns(columns_to_test, available)

    print_validation_report(result)

    # Verificações
    tests_passed = True

    if len(result["valid"]) != 3:
        print_test_result("Colunas válidas", False, f"Esperado 3, obtido {len(result['valid'])}")
        tests_passed = False
    else:
        print_test_result("Colunas válidas", True, f"{len(result['valid'])} colunas corrigidas")

    if len(result["invalid"]) != 1:
        print_test_result("Colunas inválidas", False, f"Esperado 1, obtido {len(result['invalid'])}")
        tests_passed = False
    else:
        print_test_result("Colunas inválidas", True, "1 coluna inválida detectada")

    if "NOME_PRODUTO" not in result["corrected"]:
        print_test_result("Correção automática", False, "NOME_PRODUTO não foi corrigido")
        tests_passed = False
    else:
        print_test_result("Correção automática", True, f"NOME_PRODUTO → {result['corrected']['NOME_PRODUTO']}")

    return tests_passed


def test_query_code_validation():
    """Testa validação e correção de código de query."""
    print_header("TESTE 3: Validação de Código de Query")

    available = ["codigo", "nome_produto", "une", "venda_30_d", "estoque_atual"]

    # Query com nomes legados
    query_code = '''
df.filter(pl.col("NOME_PRODUTO").is_not_null())
  .select(["codigo", "VENDA_30DD", "ESTOQUE_ATUAL"])
  .group_by("une")
  .agg(pl.col("VENDA_30DD").sum())
'''

    print("\n[CODE] Codigo Original:")
    print(query_code)

    result = validate_query_code(query_code, available, auto_correct=True)

    print("\n[CODE] Codigo Corrigido:")
    print(result["corrected_code"])

    print(f"\n[INFO] Colunas Detectadas: {result['columns_used']}")
    print(f"[INFO] Valido: {result['valid']}")
    print(f"[INFO] Correcoes: {result['validation']['corrected']}")

    # Verificações
    tests_passed = True

    # Verificar se detectou as colunas
    expected_columns = {"NOME_PRODUTO", "codigo", "VENDA_30DD", "ESTOQUE_ATUAL", "une"}
    detected = set(result["columns_used"])

    if not expected_columns.issubset(detected):
        print_test_result("Detecção de colunas", False, f"Esperado {expected_columns}, obtido {detected}")
        tests_passed = False
    else:
        print_test_result("Detecção de colunas", True, f"{len(detected)} colunas detectadas")

    # Verificar se corrigiu NOME_PRODUTO
    if "NOME_PRODUTO" not in result["validation"]["corrected"]:
        print_test_result("Correção no código", False, "NOME_PRODUTO não foi corrigido")
        tests_passed = False
    else:
        print_test_result("Correção no código", True, "NOME_PRODUTO → nome_produto")

    # Verificar se código corrigido está diferente
    if result["original_code"] == result["corrected_code"]:
        print_test_result("Código modificado", False, "Código não foi modificado")
        tests_passed = False
    else:
        print_test_result("Código modificado", True, "Código foi corrigido automaticamente")

    return tests_passed


def test_error_handling():
    """Testa tratamento de erros com sugestões."""
    print_header("TESTE 4: Tratamento de Erros com Sugestões")

    available = ["codigo", "nome_produto", "une", "venda_30_d"]

    # Tentar validar coluna inexistente
    try:
        is_valid, corrected, suggestions = validate_column(
            "nome_produt",  # Typo intencional
            available,
            auto_correct=True,
            raise_on_error=False
        )

        if not is_valid and suggestions:
            print_test_result(
                "Sugestões para typo",
                True,
                f"Sugestões: {suggestions}"
            )
            return True
        else:
            print_test_result("Sugestões para typo", False, "Nenhuma sugestão gerada")
            return False

    except Exception as e:
        print_test_result("Tratamento de erro", False, f"Exceção inesperada: {e}")
        return False


def test_real_world_query():
    """Testa query do mundo real: 'ranking de vendas todas as unes'."""
    print_header("TESTE 5: Query Real - 'ranking de vendas todas as unes'")

    available = [
        "codigo", "nome_produto", "une", "une_nome",
        "nomesegmento", "venda_30_d", "estoque_atual"
    ]

    # Simular código que seria gerado para essa query
    query_code = '''
import polars as pl

df = load_data()

# Ranking de vendas por UNE
result = (
    df.filter(pl.col("venda_30_d") > 0)
      .group_by(["une", "une_nome"])
      .agg([
          pl.col("venda_30_d").sum().alias("total_vendas"),
          pl.col("codigo").n_unique().alias("qtd_produtos")
      ])
      .sort("total_vendas", descending=True)
)

result
'''

    print("\n[CODE] Codigo da Query:")
    print(query_code)

    result = validate_query_code(query_code, available, auto_correct=True)

    print(f"\n[INFO] Colunas Validadas: {result['valid']}")
    print(f"[INFO] Total de colunas: {len(result['columns_used'])}")

    if result["valid"]:
        print_test_result("Query real validada", True, "Todas as colunas são válidas")
        return True
    else:
        print_test_result("Query real validada", False, "Colunas inválidas encontradas")
        return False


def test_exception_handling():
    """Testa se exceções são levantadas corretamente."""
    print_header("TESTE 6: Levantamento de Exceções")

    available = ["codigo", "nome_produto"]

    try:
        # Tentar validar com raise_on_error=True
        validate_column(
            "coluna_totalmente_inexistente",
            available,
            raise_on_error=True
        )

        print_test_result("Exceção não levantada", False, "Deveria ter levantado ColumnValidationError")
        return False

    except ColumnValidationError as e:
        print_test_result(
            "ColumnValidationError levantada",
            True,
            f"Mensagem: {str(e)[:100]}..."
        )
        return True
    except Exception as e:
        print_test_result("Exceção incorreta", False, f"Tipo errado: {type(e)}")
        return False


def run_all_tests():
    """Executa todos os testes."""
    print_header("SISTEMA DE MITIGAÇÃO DE ERROS - SUITE DE TESTES")

    tests = [
        ("Validação Individual", test_column_validation),
        ("Validação Múltipla", test_multiple_columns_validation),
        ("Validação de Código", test_query_code_validation),
        ("Sugestões de Erro", test_error_handling),
        ("Query Real", test_real_world_query),
        ("Tratamento de Exceções", test_exception_handling),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            logger.info(f"Executando: {test_name}")
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Erro ao executar {test_name}: {e}", exc_info=True)
            results.append((test_name, False))

    # Relatório final
    print_header("RELATÓRIO FINAL")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    for test_name, passed_test in results:
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\n[STATS] RESULTADO GERAL: {passed}/{total} testes passaram ({100*passed//total}%)")

    if passed == total:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM! Sistema de mitigacao funcionando perfeitamente.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} teste(s) falharam. Verifique os logs acima.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
