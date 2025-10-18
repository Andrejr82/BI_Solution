"""
Script de Verificação de Instalação - Validadores e Handlers

Este script verifica se todos os componentes de validação foram
instalados e estão funcionando corretamente.

Autor: Code Agent
Data: 2025-10-17
"""

import sys
from pathlib import Path
import importlib

# Configurar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Cores para output (compatível com Windows)
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ""


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(text: str):
    """Imprime mensagem de sucesso."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    """Imprime mensagem de erro."""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    """Imprime mensagem de aviso."""
    print(f"{YELLOW}⚠{RESET} {text}")


def print_info(text: str):
    """Imprime mensagem informativa."""
    print(f"{BLUE}ℹ{RESET} {text}")


def verificar_arquivo(caminho: Path, descricao: str) -> bool:
    """
    Verifica se um arquivo existe.

    Args:
        caminho: Path do arquivo
        descricao: Descrição do arquivo

    Returns:
        True se arquivo existe
    """
    if caminho.exists():
        print_success(f"{descricao}: {caminho.name}")
        return True
    else:
        print_error(f"{descricao}: {caminho.name} - NÃO ENCONTRADO")
        return False


def verificar_import(module_name: str, descricao: str) -> bool:
    """
    Verifica se um módulo pode ser importado.

    Args:
        module_name: Nome do módulo
        descricao: Descrição do módulo

    Returns:
        True se import bem-sucedido
    """
    try:
        importlib.import_module(module_name)
        print_success(f"{descricao}: import {module_name}")
        return True
    except ImportError as e:
        print_error(f"{descricao}: {module_name} - ERRO: {e}")
        return False


def verificar_funcao(module_name: str, function_name: str, descricao: str) -> bool:
    """
    Verifica se uma função existe em um módulo.

    Args:
        module_name: Nome do módulo
        function_name: Nome da função
        descricao: Descrição da função

    Returns:
        True se função existe
    """
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, function_name):
            print_success(f"{descricao}: {function_name}()")
            return True
        else:
            print_error(f"{descricao}: {function_name}() - NÃO ENCONTRADA")
            return False
    except Exception as e:
        print_error(f"{descricao}: Erro ao verificar - {e}")
        return False


def verificar_classe(module_name: str, class_name: str, descricao: str) -> bool:
    """
    Verifica se uma classe existe e pode ser instanciada.

    Args:
        module_name: Nome do módulo
        class_name: Nome da classe
        descricao: Descrição da classe

    Returns:
        True se classe existe e pode ser instanciada
    """
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            instance = cls()  # Tentar instanciar
            print_success(f"{descricao}: {class_name}")
            return True
        else:
            print_error(f"{descricao}: {class_name} - NÃO ENCONTRADA")
            return False
    except Exception as e:
        print_error(f"{descricao}: Erro ao instanciar - {e}")
        return False


def verificar_arquivos():
    """Verifica se todos os arquivos foram criados."""
    print_header("VERIFICANDO ARQUIVOS")

    arquivos = [
        # Validators
        (project_root / "core" / "validators" / "__init__.py", "Validators __init__"),
        (project_root / "core" / "validators" / "schema_validator.py", "SchemaValidator"),

        # Utils
        (project_root / "core" / "utils" / "query_validator.py", "QueryValidator"),
        (project_root / "core" / "utils" / "error_handler.py", "ErrorHandler"),

        # Documentação
        (project_root / "docs" / "CORRECOES_QUERIES_IMPLEMENTADAS.md", "Doc Correções"),
        (project_root / "docs" / "GUIA_USO_VALIDADORES.md", "Guia de Uso"),
        (project_root / "docs" / "RESUMO_CORRECOES_QUERIES.md", "Resumo Executivo"),
        (project_root / "docs" / "QUICK_REFERENCE_VALIDADORES.md", "Quick Reference"),

        # Testes
        (project_root / "tests" / "test_validators_and_handlers.py", "Testes"),

        # Scripts
        (project_root / "scripts" / "demo_validators.py", "Demo Script"),
    ]

    resultados = []
    for caminho, descricao in arquivos:
        resultado = verificar_arquivo(caminho, descricao)
        resultados.append(resultado)

    total = len(resultados)
    sucessos = sum(resultados)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} arquivos encontrados")

    return all(resultados)


def verificar_imports():
    """Verifica se todos os módulos podem ser importados."""
    print_header("VERIFICANDO IMPORTS")

    imports = [
        ("core.validators", "Validators Module"),
        ("core.validators.schema_validator", "SchemaValidator Module"),
        ("core.utils.query_validator", "QueryValidator Module"),
        ("core.utils.error_handler", "ErrorHandler Module"),
    ]

    resultados = []
    for module_name, descricao in imports:
        resultado = verificar_import(module_name, descricao)
        resultados.append(resultado)

    total = len(resultados)
    sucessos = sum(resultados)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} imports bem-sucedidos")

    return all(resultados)


def verificar_classes():
    """Verifica se todas as classes existem e podem ser instanciadas."""
    print_header("VERIFICANDO CLASSES")

    classes = [
        ("core.validators.schema_validator", "SchemaValidator", "SchemaValidator"),
        ("core.utils.query_validator", "QueryValidator", "QueryValidator"),
        ("core.utils.error_handler", "ErrorHandler", "ErrorHandler"),
        ("core.utils.error_handler", "ErrorContext", "ErrorContext (precisa de erro)"),
    ]

    resultados = []
    for module_name, class_name, descricao in classes:
        # ErrorContext precisa de parâmetros, então pulamos a instanciação
        if class_name == "ErrorContext":
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    print_success(f"{descricao}")
                    resultados.append(True)
                else:
                    print_error(f"{descricao} - NÃO ENCONTRADA")
                    resultados.append(False)
            except Exception as e:
                print_error(f"{descricao} - Erro: {e}")
                resultados.append(False)
        else:
            resultado = verificar_classe(module_name, class_name, descricao)
            resultados.append(resultado)

    total = len(resultados)
    sucessos = sum(resultados)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} classes disponíveis")

    return all(resultados)


def verificar_funcoes():
    """Verifica se todas as funções existem."""
    print_header("VERIFICANDO FUNÇÕES")

    funcoes = [
        # SchemaValidator
        ("core.validators.schema_validator", "validate_parquet_schema", "validate_parquet_schema"),

        # QueryValidator
        ("core.utils.query_validator", "validate_columns", "validate_columns"),
        ("core.utils.query_validator", "handle_nulls", "handle_nulls"),
        ("core.utils.query_validator", "safe_filter", "safe_filter"),
        ("core.utils.query_validator", "get_friendly_error", "get_friendly_error"),

        # ErrorHandler
        ("core.utils.error_handler", "handle_error", "handle_error"),
        ("core.utils.error_handler", "get_error_stats", "get_error_stats"),
        ("core.utils.error_handler", "error_handler_decorator", "error_handler_decorator"),
        ("core.utils.error_handler", "create_error_response", "create_error_response"),
    ]

    resultados = []
    for module_name, function_name, descricao in funcoes:
        resultado = verificar_funcao(module_name, function_name, descricao)
        resultados.append(resultado)

    total = len(resultados)
    sucessos = sum(resultados)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} funções disponíveis")

    return all(resultados)


def verificar_dependencias():
    """Verifica se as dependências estão instaladas."""
    print_header("VERIFICANDO DEPENDÊNCIAS")

    dependencias = [
        ("pandas", "Pandas"),
        ("pyarrow", "PyArrow"),
        ("pytest", "Pytest (opcional para testes)"),
    ]

    resultados = []
    for module_name, descricao in dependencias:
        try:
            importlib.import_module(module_name)
            print_success(f"{descricao}: instalado")
            resultados.append(True)
        except ImportError:
            if module_name == "pytest":
                print_warning(f"{descricao}: não instalado (opcional)")
                resultados.append(True)  # Pytest é opcional
            else:
                print_error(f"{descricao}: NÃO INSTALADO")
                resultados.append(False)

    total = len(resultados)
    sucessos = sum(resultados)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} dependências ok")

    return all(resultados)


def teste_funcional_basico():
    """Executa testes funcionais básicos."""
    print_header("TESTES FUNCIONAIS BÁSICOS")

    testes_ok = []

    # Teste 1: SchemaValidator
    print(f"\n{BLUE}Teste 1:{RESET} Instanciar SchemaValidator")
    try:
        from core.validators import SchemaValidator
        validator = SchemaValidator()
        print_success("SchemaValidator instanciado com sucesso")
        testes_ok.append(True)
    except Exception as e:
        print_error(f"Erro ao instanciar SchemaValidator: {e}")
        testes_ok.append(False)

    # Teste 2: QueryValidator
    print(f"\n{BLUE}Teste 2:{RESET} Instanciar QueryValidator")
    try:
        from core.utils.query_validator import QueryValidator
        validator = QueryValidator()
        print_success("QueryValidator instanciado com sucesso")
        testes_ok.append(True)
    except Exception as e:
        print_error(f"Erro ao instanciar QueryValidator: {e}")
        testes_ok.append(False)

    # Teste 3: Validar colunas
    print(f"\n{BLUE}Teste 3:{RESET} Validar colunas em DataFrame")
    try:
        import pandas as pd
        from core.utils.query_validator import validate_columns

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        is_valid, missing = validate_columns(df, ["col1", "col2"])

        if is_valid:
            print_success("Validação de colunas funcionou")
            testes_ok.append(True)
        else:
            print_error(f"Validação falhou: {missing}")
            testes_ok.append(False)
    except Exception as e:
        print_error(f"Erro ao validar colunas: {e}")
        testes_ok.append(False)

    # Teste 4: Tratamento de nulos
    print(f"\n{BLUE}Teste 4:{RESET} Tratamento de valores nulos")
    try:
        import pandas as pd
        from core.utils.query_validator import handle_nulls

        df = pd.DataFrame({"col1": [1, None, 3]})
        df_clean = handle_nulls(df, "col1", strategy="fill", fill_value=0)

        if df_clean["col1"].isna().sum() == 0:
            print_success("Tratamento de nulos funcionou")
            testes_ok.append(True)
        else:
            print_error("Ainda há valores nulos após tratamento")
            testes_ok.append(False)
    except Exception as e:
        print_error(f"Erro ao tratar nulos: {e}")
        testes_ok.append(False)

    # Teste 5: Error handling
    print(f"\n{BLUE}Teste 5:{RESET} Error handling")
    try:
        from core.utils.error_handler import handle_error

        try:
            raise ValueError("Teste de erro")
        except Exception as e:
            error_ctx = handle_error(e, context={"test": True})

            if error_ctx.user_message:
                print_success("Error handling funcionou")
                testes_ok.append(True)
            else:
                print_error("Error context sem mensagem")
                testes_ok.append(False)
    except Exception as e:
        print_error(f"Erro no error handling: {e}")
        testes_ok.append(False)

    total = len(testes_ok)
    sucessos = sum(testes_ok)

    print(f"\n{BLUE}Resultado:{RESET} {sucessos}/{total} testes funcionais passaram")

    return all(testes_ok)


def gerar_relatorio():
    """Gera relatório final da verificação."""
    print_header("RELATÓRIO FINAL")

    print(f"{BLUE}Instalação dos Validadores e Handlers{RESET}\n")

    resultados = []

    # Verificar arquivos
    print("1. Arquivos...")
    arquivos_ok = verificar_arquivos()
    resultados.append(("Arquivos", arquivos_ok))

    # Verificar imports
    print("\n2. Imports...")
    imports_ok = verificar_imports()
    resultados.append(("Imports", imports_ok))

    # Verificar classes
    print("\n3. Classes...")
    classes_ok = verificar_classes()
    resultados.append(("Classes", classes_ok))

    # Verificar funções
    print("\n4. Funções...")
    funcoes_ok = verificar_funcoes()
    resultados.append(("Funções", funcoes_ok))

    # Verificar dependências
    print("\n5. Dependências...")
    deps_ok = verificar_dependencias()
    resultados.append(("Dependências", deps_ok))

    # Testes funcionais
    print("\n6. Testes Funcionais...")
    testes_ok = teste_funcional_basico()
    resultados.append(("Testes Funcionais", testes_ok))

    # Resumo
    print_header("RESUMO")

    for componente, status in resultados:
        if status:
            print_success(f"{componente}: OK")
        else:
            print_error(f"{componente}: FALHOU")

    total = len(resultados)
    sucessos = sum(1 for _, status in resultados if status)

    print(f"\n{BLUE}Status Geral:{RESET} {sucessos}/{total} componentes OK")

    if all(status for _, status in resultados):
        print(f"\n{GREEN}✓ INSTALAÇÃO COMPLETA E FUNCIONAL{RESET}\n")
        return True
    else:
        print(f"\n{RED}✗ INSTALAÇÃO INCOMPLETA OU COM PROBLEMAS{RESET}\n")
        print_info("Verifique os erros acima e corrija os problemas.")
        return False


def main():
    """Função principal."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{'VERIFICAÇÃO DE INSTALAÇÃO - VALIDADORES E HANDLERS':^70}{RESET}")
    print(f"{BLUE}{'Agent Solution BI v2.2':^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

    sucesso = gerar_relatorio()

    if sucesso:
        print(f"\n{GREEN}Próximos passos:{RESET}")
        print("  1. Execute os testes: python -m pytest tests/test_validators_and_handlers.py -v")
        print("  2. Veja a demo: python scripts/demo_validators.py")
        print("  3. Leia a documentação: docs/GUIA_USO_VALIDADORES.md")

    return 0 if sucesso else 1


if __name__ == "__main__":
    sys.exit(main())
