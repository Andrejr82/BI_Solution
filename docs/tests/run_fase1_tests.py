"""
Script para executar todos os testes da Fase 1.

Usage:
    python run_fase1_tests.py              # Executar todos os testes
    python run_fase1_tests.py --verbose    # Output verboso
    python run_fase1_tests.py --coverage   # Com coverage
    python run_fase1_tests.py --fast       # Apenas smoke tests
"""

import sys
import subprocess
import argparse
from pathlib import Path


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_tests(args):
    """Executa testes com pytest"""

    test_files = [
        "tests/test_code_validator.py",
        "tests/test_pattern_matcher.py",
        "tests/test_feedback_system.py",
        "tests/test_error_analyzer.py",
        "tests/test_integration_fase1.py"
    ]

    # Verificar se arquivos existem
    missing = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing.append(test_file)

    if missing:
        print("❌ Arquivos de teste não encontrados:")
        for f in missing:
            print(f"   - {f}")
        return False

    # Construir comando pytest
    pytest_args = ["pytest"]

    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-q")

    if args.coverage:
        pytest_args.extend([
            "--cov=core.validation",
            "--cov=core.learning",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])

    if args.fast:
        # Apenas smoke tests (testes mais rápidos)
        pytest_args.extend(["-k", "test_initialization or test_valid_code"])

    if args.markers:
        pytest_args.extend(["-m", args.markers])

    if args.failed:
        pytest_args.append("--lf")  # Last failed

    # Adicionar arquivos de teste
    pytest_args.extend(test_files)

    # Executar
    print_header("EXECUTANDO TESTES DA FASE 1")

    print(f"Comando: {' '.join(pytest_args)}\n")

    try:
        result = subprocess.run(pytest_args, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instale com: pip install pytest")
        return False


def run_specific_module(module_name):
    """Executa testes de um módulo específico"""

    module_map = {
        "validator": "tests/test_code_validator.py",
        "pattern": "tests/test_pattern_matcher.py",
        "feedback": "tests/test_feedback_system.py",
        "error": "tests/test_error_analyzer.py",
        "integration": "tests/test_integration_fase1.py"
    }

    if module_name not in module_map:
        print(f"❌ Módulo '{module_name}' não encontrado.")
        print(f"Módulos disponíveis: {', '.join(module_map.keys())}")
        return False

    test_file = module_map[module_name]

    print_header(f"TESTANDO: {module_name.upper()}")

    result = subprocess.run(["pytest", test_file, "-v"], check=False)
    return result.returncode == 0


def show_test_summary():
    """Mostra resumo dos testes disponíveis"""

    print_header("RESUMO DOS TESTES DA FASE 1")

    tests_info = [
        ("CodeValidator", "test_code_validator.py", "30+ testes", "Validacao de codigo Python"),
        ("PatternMatcher", "test_pattern_matcher.py", "40+ testes", "Identificacao de padroes de queries"),
        ("FeedbackSystem", "test_feedback_system.py", "25+ testes", "Sistema de coleta de feedback"),
        ("ErrorAnalyzer", "test_error_analyzer.py", "25+ testes", "Analise de padroes de erro"),
        ("Integracao", "test_integration_fase1.py", "10+ testes", "Testes end-to-end")
    ]

    total_tests = 0

    for component, file, count, description in tests_info:
        test_count = int(count.split("+")[0])
        total_tests += test_count

        print(f"[*] {component}")
        print(f"   Arquivo: {file}")
        print(f"   Testes: {count}")
        print(f"   Descricao: {description}")
        print()

    print(f"[OK] Total: ~{total_tests}+ testes implementados\n")


def main():
    parser = argparse.ArgumentParser(
        description="Executar testes da Fase 1 do treinamento LLM"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Output verboso"
    )

    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Executar com coverage"
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Executar apenas smoke tests (testes rápidos)"
    )

    parser.add_argument(
        "-m", "--markers",
        type=str,
        help="Executar apenas testes com markers específicos"
    )

    parser.add_argument(
        "--failed",
        action="store_true",
        help="Re-executar apenas testes que falharam anteriormente"
    )

    parser.add_argument(
        "--module",
        type=str,
        choices=["validator", "pattern", "feedback", "error", "integration"],
        help="Executar apenas testes de um módulo específico"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Mostrar resumo dos testes disponíveis"
    )

    args = parser.parse_args()

    # Mostrar resumo se solicitado
    if args.summary:
        show_test_summary()
        return 0

    # Executar módulo específico se solicitado
    if args.module:
        success = run_specific_module(args.module)
        return 0 if success else 1

    # Executar todos os testes
    success = run_tests(args)

    # Print resultado final
    print("\n" + "=" * 70)
    if success:
        print("[OK] TODOS OS TESTES PASSARAM!")
    else:
        print("[ERRO] ALGUNS TESTES FALHARAM")
    print("=" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
