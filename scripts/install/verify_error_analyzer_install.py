"""
Script de verificação da instalação do ErrorAnalyzer.

Verifica se todos os arquivos foram criados corretamente e se
o ErrorAnalyzer está funcionando conforme esperado.
"""

from pathlib import Path
import sys


def check_file_exists(file_path: str, description: str) -> bool:
    """Verifica se arquivo existe"""
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists


def check_import(module_name: str, class_name: str) -> bool:
    """Verifica se módulo pode ser importado"""
    try:
        if module_name == "core.learning.error_analyzer":
            from core.learning.error_analyzer import ErrorAnalyzer
            print(f"✅ Import OK: {module_name}.{class_name}")
            return True
    except ImportError as e:
        print(f"❌ Import FALHOU: {module_name}.{class_name}")
        print(f"   Erro: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def check_basic_functionality() -> bool:
    """Testa funcionalidade básica do ErrorAnalyzer"""
    try:
        from core.learning.error_analyzer import ErrorAnalyzer
        import tempfile
        import shutil

        # Cria diretório temporário
        temp_dir = tempfile.mkdtemp()

        try:
            # Testa inicialização
            analyzer = ErrorAnalyzer(feedback_dir=temp_dir)

            # Testa analyze_errors com diretório vazio
            result = analyzer.analyze_errors(days=7)

            # Verifica estrutura do retorno
            assert "most_common_errors" in result
            assert "suggested_improvements" in result
            assert isinstance(result["most_common_errors"], list)
            assert isinstance(result["suggested_improvements"], list)

            # Testa get_error_types
            error_types = analyzer.get_error_types()
            assert isinstance(error_types, list)

            print("✅ Funcionalidade básica OK")
            return True

        finally:
            # Limpa diretório temporário
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ Teste de funcionalidade FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal de verificação"""

    print("=" * 70)
    print("VERIFICAÇÃO DE INSTALAÇÃO DO ErrorAnalyzer")
    print("=" * 70)
    print()

    checks = []

    # 1. Verifica arquivos de código
    print("1. ARQUIVOS DE CÓDIGO")
    print("-" * 70)
    checks.append(check_file_exists(
        "core/learning/error_analyzer.py",
        "ErrorAnalyzer (código principal)"
    ))
    checks.append(check_file_exists(
        "core/learning/__init__.py",
        "Módulo learning (__init__)"
    ))
    print()

    # 2. Verifica scripts
    print("2. SCRIPTS DE SUPORTE")
    print("-" * 70)
    checks.append(check_file_exists(
        "install_error_analyzer.py",
        "Script de instalação"
    ))
    checks.append(check_file_exists(
        "demo_error_analyzer.py",
        "Script de demonstração"
    ))
    checks.append(check_file_exists(
        "verify_error_analyzer_install.py",
        "Script de verificação (este)"
    ))
    print()

    # 3. Verifica documentação
    print("3. DOCUMENTAÇÃO")
    print("-" * 70)
    checks.append(check_file_exists(
        "ERROR_ANALYZER_README.md",
        "README completo"
    ))
    checks.append(check_file_exists(
        "TAREFA_1_ENTREGA_FINAL.md",
        "Entrega final"
    ))
    checks.append(check_file_exists(
        "QUICK_START_ERROR_ANALYZER.txt",
        "Quick start guide"
    ))
    print()

    # 4. Verifica imports
    print("4. IMPORTS")
    print("-" * 70)
    checks.append(check_import(
        "core.learning.error_analyzer",
        "ErrorAnalyzer"
    ))
    print()

    # 5. Testa funcionalidade
    print("5. FUNCIONALIDADE BÁSICA")
    print("-" * 70)
    checks.append(check_basic_functionality())
    print()

    # Resumo
    print("=" * 70)
    print("RESUMO")
    print("=" * 70)

    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\nVerificações passaram: {passed}/{total} ({percentage:.1f}%)")

    if passed == total:
        print("\n🎉 SUCESSO! Instalação do ErrorAnalyzer está completa e funcional.")
        print("\nPróximos passos:")
        print("  1. Execute: python demo_error_analyzer.py")
        print("  2. Leia: ERROR_ANALYZER_README.md")
        print("  3. Comece a usar: from core.learning.error_analyzer import ErrorAnalyzer")
        return 0
    else:
        print(f"\n⚠️  ATENÇÃO: {total - passed} verificação(ões) falharam.")
        print("\nPara corrigir:")
        print("  1. Execute: python install_error_analyzer.py")
        print("  2. Verifique as mensagens de erro acima")
        print("  3. Execute este script novamente")
        return 1


if __name__ == "__main__":
    sys.exit(main())
