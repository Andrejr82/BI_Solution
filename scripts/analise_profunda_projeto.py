"""
Script de Análise Profunda do Projeto Agent_Solution_BI
Verifica imports, dependências, erros potenciais, código duplicado, etc.
"""
import os
import sys
import re
import ast
import json
from pathlib import Path
from collections import defaultdict
import importlib.util

# Configurar encoding
sys.stdout = sys.__stdout__
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Cores para output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}## {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

# Diretório base do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Diretórios a ignorar
IGNORE_DIRS = {'.venv', '__pycache__', '.git', 'node_modules', 'dist', 'build', '.pytest_cache', 'htmlcov'}

def get_python_files():
    """Retorna lista de todos arquivos Python do projeto."""
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Remover diretórios a ignorar
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files

def extract_imports(file_path):
    """Extrai todos os imports de um arquivo Python."""
    imports = {
        'standard': [],
        'third_party': [],
        'local': [],
        'errors': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module.startswith('core') or module.startswith('ui') or module.startswith('dev_tools'):
                        imports['local'].append(alias.name)
                    else:
                        imports['third_party'].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    full_import = node.module
                    if module in ['core', 'ui', 'dev_tools', 'config']:
                        imports['local'].append(full_import)
                    else:
                        imports['third_party'].append(full_import)

    except SyntaxError as e:
        imports['errors'].append(f"Syntax error: {e}")
    except Exception as e:
        imports['errors'].append(f"Error parsing: {e}")

    return imports

def check_missing_imports():
    """Verifica imports que não podem ser resolvidos."""
    print_section("1. ANÁLISE DE IMPORTS E DEPENDÊNCIAS")

    all_files = get_python_files()
    print_info(f"Total de arquivos Python: {len(all_files)}")

    missing_imports = defaultdict(list)
    syntax_errors = []

    for file_path in all_files:
        imports = extract_imports(file_path)

        if imports['errors']:
            syntax_errors.append((file_path, imports['errors']))

        # Verificar imports locais
        for imp in imports['local']:
            # Converter import para caminho de arquivo
            module_path = PROJECT_ROOT / imp.replace('.', os.sep)
            py_file = module_path.with_suffix('.py')
            init_file = module_path / '__init__.py'

            if not py_file.exists() and not init_file.exists():
                missing_imports[str(file_path.relative_to(PROJECT_ROOT))].append(imp)

    # Reportar erros de sintaxe
    if syntax_errors:
        print_error(f"Encontrados {len(syntax_errors)} arquivos com erros de sintaxe:")
        for file_path, errors in syntax_errors:
            print(f"  📄 {file_path.relative_to(PROJECT_ROOT)}")
            for error in errors:
                print(f"     {error}")
    else:
        print_success("Nenhum erro de sintaxe encontrado")

    print()

    # Reportar imports faltando
    if missing_imports:
        print_warning(f"Encontrados {len(missing_imports)} arquivos com imports potencialmente quebrados:")
        for file_path, imports in list(missing_imports.items())[:10]:  # Mostrar primeiros 10
            print(f"  📄 {file_path}")
            for imp in imports:
                print(f"     ❌ from {imp} import ...")
    else:
        print_success("Todos os imports locais parecem válidos")

    return len(syntax_errors), len(missing_imports)

def check_env_variables():
    """Verifica variáveis de ambiente necessárias."""
    print_section("2. ANÁLISE DE VARIÁVEIS DE AMBIENTE")

    required_vars = [
        'OPENAI_API_KEY',
        'SQL_SERVER_HOST',
        'SQL_SERVER_DATABASE',
        'SQL_SERVER_USER',
        'SQL_SERVER_PASSWORD',
    ]

    optional_vars = [
        'SQL_SERVER_PORT',
        'SQL_SERVER_DRIVER',
        'LANGCHAIN_API_KEY',
        'LANGCHAIN_TRACING_V2',
    ]

    # Verificar se .env existe
    env_file = PROJECT_ROOT / '.env'
    if env_file.exists():
        print_success(f"Arquivo .env encontrado: {env_file}")

        # Ler variáveis do .env
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()

        missing_required = []
        for var in required_vars:
            if var not in env_content:
                missing_required.append(var)

        if missing_required:
            print_warning(f"Variáveis OBRIGATÓRIAS faltando no .env:")
            for var in missing_required:
                print(f"  ❌ {var}")
        else:
            print_success("Todas as variáveis obrigatórias presentes")

        print_info(f"\nVariáveis opcionais:")
        for var in optional_vars:
            if var in env_content:
                print(f"  ✅ {var}")
            else:
                print(f"  ⚪ {var} (não configurada)")
    else:
        print_error(f"Arquivo .env NÃO encontrado em: {env_file}")
        print_info("Verifique se existe .env.example para copiar")

def check_config_files():
    """Verifica arquivos de configuração."""
    print_section("3. ANÁLISE DE ARQUIVOS DE CONFIGURAÇÃO")

    config_files = {
        'requirements.txt': 'Dependências Python',
        '.env': 'Variáveis de ambiente',
        '.env.example': 'Template de variáveis',
        'streamlit_app.py': 'Aplicação Streamlit principal',
        'core/config/settings.py': 'Configurações gerais',
        'core/config/une_mapping.py': 'Mapeamento de UNEs',
        'core/config/column_mapping.py': 'Mapeamento de colunas',
    }

    for file_path, description in config_files.items():
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print_success(f"{file_path} - {description} ({size} bytes)")
        else:
            print_error(f"{file_path} - {description} (NÃO ENCONTRADO)")

def check_data_files():
    """Verifica arquivos de dados essenciais."""
    print_section("4. ANÁLISE DE ARQUIVOS DE DADOS")

    data_dir = PROJECT_ROOT / 'data'

    critical_files = {
        'data/query_examples.json': 'Exemplos RAG (102 exemplos)',
        'data/catalog_focused.json': 'Catálogo de colunas',
        'data/parquet/*.parquet': 'Dados Parquet',
    }

    for file_pattern, description in critical_files.items():
        if '*' in file_pattern:
            # Glob pattern
            import glob
            files = glob.glob(str(PROJECT_ROOT / file_pattern))
            if files:
                total_size = sum(Path(f).stat().st_size for f in files)
                print_success(f"{file_pattern} - {description} ({len(files)} arquivos, {total_size / 1024 / 1024:.1f} MB)")
            else:
                print_error(f"{file_pattern} - {description} (NENHUM ARQUIVO)")
        else:
            full_path = PROJECT_ROOT / file_pattern
            if full_path.exists():
                size = full_path.stat().st_size
                print_success(f"{file_pattern} - {description} ({size / 1024:.1f} KB)")
            else:
                print_warning(f"{file_pattern} - {description} (NÃO ENCONTRADO)")

def check_code_quality():
    """Verifica qualidade do código."""
    print_section("5. ANÁLISE DE QUALIDADE DE CÓDIGO")

    all_files = get_python_files()

    # Estatísticas
    total_lines = 0
    total_comments = 0
    total_docstrings = 0
    files_without_docstring = []
    long_functions = []

    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            total_lines += len(lines)

            # Contar comentários
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    total_comments += 1

            # Parse AST para análise mais profunda
            try:
                tree = ast.parse(content)

                # Verificar docstring do módulo
                if not (tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)):
                    if 'test' not in str(file_path) and '__init__' not in str(file_path):
                        files_without_docstring.append(file_path)

                # Contar docstrings e funções longas
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if ast.get_docstring(node):
                            total_docstrings += 1

                        # Verificar tamanho de funções
                        if isinstance(node, ast.FunctionDef):
                            if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                                func_lines = node.end_lineno - node.lineno
                                if func_lines > 100:
                                    long_functions.append((file_path, node.name, func_lines))

            except:
                pass

        except Exception as e:
            pass

    print_info(f"Linhas totais de código: {total_lines:,}")
    print_info(f"Comentários: {total_comments:,}")
    print_info(f"Docstrings: {total_docstrings:,}")

    if files_without_docstring:
        print_warning(f"\nArquivos sem docstring de módulo: {len(files_without_docstring)}")
        for f in files_without_docstring[:5]:
            print(f"  📄 {f.relative_to(PROJECT_ROOT)}")

    if long_functions:
        print_warning(f"\nFunções muito longas (>100 linhas): {len(long_functions)}")
        for file_path, func_name, lines in long_functions[:5]:
            print(f"  📄 {file_path.relative_to(PROJECT_ROOT)}:{func_name} ({lines} linhas)")

def check_potential_bugs():
    """Verifica bugs potenciais no código."""
    print_section("6. ANÁLISE DE BUGS POTENCIAIS")

    all_files = get_python_files()

    issues = {
        'bare_except': [],
        'mutable_defaults': [],
        'print_statements': [],
        'todo_comments': [],
    }

    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.split('\n')

            # Verificar bare except
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues['bare_except'].append((file_path, node.lineno))

                # Verificar defaults mutáveis
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues['mutable_defaults'].append((file_path, node.lineno, node.name))

                # Verificar print statements (fora de debug)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'print':
                        if 'test' not in str(file_path) and 'debug' not in str(file_path):
                            issues['print_statements'].append((file_path, node.lineno))

            # Verificar TODOs
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    issues['todo_comments'].append((file_path, i, line.strip()))

        except:
            pass

    # Reportar
    if issues['bare_except']:
        print_warning(f"Bare except encontrados: {len(issues['bare_except'])}")
        for file_path, lineno in issues['bare_except'][:5]:
            print(f"  📄 {file_path.relative_to(PROJECT_ROOT)}:{lineno}")

    if issues['mutable_defaults']:
        print_warning(f"Defaults mutáveis encontrados: {len(issues['mutable_defaults'])}")
        for file_path, lineno, func_name in issues['mutable_defaults'][:5]:
            print(f"  📄 {file_path.relative_to(PROJECT_ROOT)}:{lineno} (função: {func_name})")

    if issues['print_statements']:
        print_info(f"Print statements encontrados: {len(issues['print_statements'])} (considere usar logging)")

    if issues['todo_comments']:
        print_info(f"TODOs/FIXMEs encontrados: {len(issues['todo_comments'])}")
        for file_path, lineno, comment in issues['todo_comments'][:10]:
            print(f"  📄 {file_path.relative_to(PROJECT_ROOT)}:{lineno}")
            print(f"     {comment[:80]}")

def main():
    """Executa análise profunda do projeto."""
    print_header("ANÁLISE PROFUNDA DO PROJETO AGENT_SOLUTION_BI")

    print_info(f"Diretório do projeto: {PROJECT_ROOT}")
    print_info(f"Data da análise: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Executar análises
    syntax_errors, import_errors = check_missing_imports()
    check_env_variables()
    check_config_files()
    check_data_files()
    check_code_quality()
    check_potential_bugs()

    # Resumo final
    print_section("RESUMO DA ANÁLISE")

    if syntax_errors > 0:
        print_error(f"Erros de sintaxe: {syntax_errors}")
    else:
        print_success("Sem erros de sintaxe")

    if import_errors > 0:
        print_warning(f"Imports possivelmente quebrados: {import_errors}")
    else:
        print_success("Imports OK")

    print("\n" + "="*70)
    print_info("Análise completa! Verifique os warnings acima.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
