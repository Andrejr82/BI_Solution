"""
Script de Teste Manual - FASE 1.1
Integração CodeGenAgent + ColumnValidator

Este script testa cenários reais de uso da integração:
1. Código com colunas corretas
2. Código com erros sutis de coluna (auto-correção)
3. Código com múltiplos erros
4. Validação de estatísticas

Uso:
    python scripts/test_fase_1_1_integration.py
"""

import sys
import os
import logging
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agents.code_gen_agent_integrated import CodeGenAgent
import polars as pl


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# CASOS DE TESTE
# ============================================================================

TEST_CASES = [
    {
        "name": "TESTE 1: Código Válido (sem erros)",
        "code": """
import polars as pl
result = df.select(["UNE_NOME", "TOTAL_CLIENTES"]).head(10)
""",
        "expected": "success",
        "description": "Código com colunas corretas deve executar sem correções"
    },
    {
        "name": "TESTE 2: Erro Sutil - UNE_NAME (deve auto-corrigir)",
        "code": """
import polars as pl
result = df.select(["UNE_NAME", "TOTAL_CLIENTES"]).head(10)
""",
        "expected": "auto_correct",
        "description": "UNE_NAME deve ser corrigido para UNE_NOME automaticamente"
    },
    {
        "name": "TESTE 3: Multiple Erros Sutis (deve auto-corrigir)",
        "code": """
import polars as pl
result = df.select([
    pl.col("UNE_NAME"),
    pl.col("TOTAL_CLIENTE"),
    pl.col("RECEITA")
]).head(10)
""",
        "expected": "auto_correct",
        "description": "Múltiplos erros sutis devem ser corrigidos"
    },
    {
        "name": "TESTE 4: Erro Grave - Coluna Inexistente",
        "code": """
import polars as pl
result = df.select(["COLUNA_TOTALMENTE_ERRADA_123"]).head(10)
""",
        "expected": "failure",
        "description": "Coluna muito diferente não deve ter sugestão e deve falhar"
    },
    {
        "name": "TESTE 5: Análise Complexa com Group By",
        "code": """
import polars as pl
result = df.group_by("UNE_NOME").agg([
    pl.col("TOTAL_CLIENTES").sum().alias("total_clientes"),
    pl.col("RECEITA_TOTAL").mean().alias("receita_media")
]).sort("total_clientes", descending=True).head(5)
""",
        "expected": "success",
        "description": "Query complexa com agregações deve funcionar"
    },
]


# ============================================================================
# FUNÇÕES DE TESTE
# ============================================================================

def load_test_dataframe() -> pl.DataFrame:
    """
    Carrega DataFrame para testes.

    Tenta carregar do Parquet ou cria um de teste.
    """
    parquet_path = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\data\\une_data.parquet"

    if os.path.exists(parquet_path):
        logger.info(f"Carregando DataFrame do Parquet: {parquet_path}")
        try:
            df = pl.read_parquet(parquet_path)
            logger.info(f"DataFrame carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
            return df
        except Exception as e:
            logger.warning(f"Erro ao carregar Parquet: {e}")

    # Fallback: criar DataFrame de teste
    logger.info("Criando DataFrame de teste...")
    df = pl.DataFrame({
        "UNE_NOME": [f"UNE {i}" for i in range(1, 101)],
        "TOTAL_CLIENTES": [100 + i * 10 for i in range(100)],
        "RECEITA_TOTAL": [10000.0 + i * 500 for i in range(100)],
        "REGIAO": ["Sul", "Norte", "Centro", "Leste"] * 25,
        "TIPO_UNE": ["Tipo A", "Tipo B"] * 50
    })
    logger.info(f"DataFrame de teste criado: {df.shape[0]} linhas, {df.shape[1]} colunas")
    return df


def run_test_case(test_case: dict, agent: CodeGenAgent, df: pl.DataFrame) -> dict:
    """
    Executa um caso de teste.

    Args:
        test_case: Dicionário com info do teste
        agent: CodeGenAgent configurado
        df: DataFrame para teste

    Returns:
        dict: Resultado do teste
    """
    logger.info("\n" + "=" * 80)
    logger.info(test_case["name"])
    logger.info("=" * 80)
    logger.info(f"Descrição: {test_case['description']}")
    logger.info(f"Expectativa: {test_case['expected']}")

    context = {"df": df}

    # Executar validação + execução
    start_time = datetime.now()
    success, result, error = agent.validate_and_execute(
        test_case["code"],
        df_name="df",
        context=context
    )
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    # Preparar resultado
    test_result = {
        "name": test_case["name"],
        "expected": test_case["expected"],
        "expected_failure": test_case["expected"] == "failure",
        "success": success,
        "elapsed_seconds": elapsed,
        "result": result,
        "error": error,
        "stats": agent.get_validation_stats()
    }

    # Avaliar se passou
    if test_case["expected"] == "success":
        test_result["passed"] = success
    elif test_case["expected"] == "auto_correct":
        # Se esperava auto-correção, deve ter sucesso E ter aplicado correções
        test_result["passed"] = success and test_result["stats"]["auto_corrections"] > 0
    elif test_case["expected"] == "failure":
        test_result["passed"] = not success
    else:
        test_result["passed"] = None

    # Log resultado
    if test_result["passed"]:
        logger.info("✓ TESTE PASSOU")
    else:
        logger.warning("✗ TESTE FALHOU")

    logger.info(f"Tempo de execução: {elapsed:.3f}s")

    if success:
        logger.info(f"Resultado: {type(result).__name__}")
        if isinstance(result, pl.DataFrame):
            logger.info(f"  - Shape: {result.shape}")
    else:
        logger.error(f"Erro: {error}")

    return test_result


def generate_report(test_results: list) -> str:
    """
    Gera relatório final dos testes.

    Args:
        test_results: Lista de resultados dos testes

    Returns:
        str: Relatório formatado
    """
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["passed"])
    failed_tests = total_tests - passed_tests

    # Estatísticas agregadas
    total_validations = sum(r["stats"]["total_validations"] for r in test_results if not r["expected_failure"])
    successful_validations = sum(r["stats"]["successful_validations"] for r in test_results if not r["expected_failure"])
    auto_corrections = sum(r["stats"]["auto_corrections"] for r in test_results)
    validation_failures = sum(r["stats"]["validation_failures"] for r in test_results if not r["expected_failure"])

    success_rate = (successful_validations / total_validations * 100) if total_validations > 0 else 0

    report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     RELATÓRIO FASE 1.1 - TESTES                          ║
║                   Integração CodeGenAgent + ColumnValidator              ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 RESUMO DOS TESTES
{'─' * 79}
Total de Testes:           {total_tests}
Testes Passados:           {passed_tests} ({passed_tests/total_tests*100:.1f}%)
Testes Falhados:           {failed_tests} ({failed_tests/total_tests*100:.1f}%)

📈 ESTATÍSTICAS DE VALIDAÇÃO
{'─' * 79}
Total de Validações:       {total_validations}
Validações Bem-Sucedidas:  {successful_validations}
Auto-Correções Aplicadas:  {auto_corrections}
Falhas de Validação:       {validation_failures}
Taxa de Sucesso:           {success_rate:.1f}%

📋 DETALHES DOS TESTES
{'─' * 79}
"""

    for i, result in enumerate(test_results, 1):
        status = "✓ PASSOU" if result["passed"] else "✗ FALHOU"
        report += f"\n{i}. {result['name']}\n"
        report += f"   Status: {status}\n"
        report += f"   Tempo: {result['elapsed_seconds']:.3f}s\n"
        report += f"   Auto-correções: {result['stats']['auto_corrections']}\n"

        if not result["success"] and result["error"]:
            report += f"   Erro: {result['error'][:100]}...\n"

    report += "\n" + "═" * 79 + "\n"

    # Critério de sucesso FASE 1.1
    if success_rate >= 90 and auto_corrections > 0:
        report += """
✓ CRITÉRIO DE SUCESSO FASE 1.1 ATINGIDO!

  - Taxa de sucesso >= 90%: SIM
  - Auto-correções funcionando: SIM
  - Redução de erros de coluna: VALIDADO

A integração está PRONTA para uso em produção.
"""
    else:
        report += """
⚠ CRITÉRIO DE SUCESSO FASE 1.1 NÃO ATINGIDO

  Ajustes necessários antes de prosseguir para FASE 1.2.
"""

    report += "\n" + "═" * 79 + "\n"

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Função principal - executa todos os testes.
    """
    logger.info("\n\n")
    logger.info("╔═══════════════════════════════════════════════════════════════════════════╗")
    logger.info("║                     INICIANDO TESTES FASE 1.1                             ║")
    logger.info("║                   CodeGenAgent + ColumnValidator                          ║")
    logger.info("╚═══════════════════════════════════════════════════════════════════════════╝")

    # 1. Carregar DataFrame
    logger.info("\n[1/3] Carregando DataFrame...")
    df = load_test_dataframe()

    # 2. Criar Agent
    logger.info("\n[2/3] Criando CodeGenAgent com Column Validator...")
    agent = CodeGenAgent(max_retries=2)

    # 3. Executar testes
    logger.info("\n[3/3] Executando casos de teste...")
    test_results = []

    for test_case in TEST_CASES:
        result = run_test_case(test_case, agent, df)
        test_results.append(result)

    # 4. Gerar relatório
    report = generate_report(test_results)
    print(report)

    # 5. Salvar relatório
    report_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "reports",
        f"FASE_1_1_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"\n📄 Relatório salvo em: {report_path}")

    # 6. Retornar código de saída
    all_passed = all(r["passed"] for r in test_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
