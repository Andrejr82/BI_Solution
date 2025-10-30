#!/usr/bin/env python3
"""
Script de Validação do Sistema Agent BI React
Verifica se todos os componentes estão configurados corretamente
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def check_mark(success: bool) -> str:
    """Retorna check ou X baseado no sucesso"""
    return f"{Colors.GREEN}OK{Colors.END}" if success else f"{Colors.RED}ERRO{Colors.END}"

def validate_python() -> Tuple[bool, str]:
    """Valida instalação do Python"""
    try:
        result = subprocess.run(
            [sys.executable, '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        return True, version
    except Exception as e:
        return False, str(e)

def validate_node() -> Tuple[bool, str]:
    """Valida instalação do Node.js"""
    try:
        result = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        return True, version
    except Exception as e:
        return False, str(e)

def validate_npm() -> Tuple[bool, str]:
    """Valida instalação do npm"""
    try:
        result = subprocess.run(
            ['npm', '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        return True, version
    except Exception as e:
        return False, str(e)

def validate_file_exists(filepath: str) -> bool:
    """Verifica se arquivo existe"""
    return Path(filepath).exists()

def validate_frontend_structure() -> Dict[str, bool]:
    """Valida estrutura do frontend"""
    checks = {
        'package.json': validate_file_exists('frontend/package.json'),
        'vite.config.ts': validate_file_exists('frontend/vite.config.ts'),
        'src/main.tsx': validate_file_exists('frontend/src/main.tsx'),
        'src/App.tsx': validate_file_exists('frontend/src/App.tsx'),
        'src/lib/api.ts': validate_file_exists('frontend/src/lib/api.ts'),
        'public/cacula_logo.png': validate_file_exists('frontend/public/cacula_logo.png'),
        'node_modules': validate_file_exists('frontend/node_modules'),
    }
    return checks

def validate_backend_structure() -> Dict[str, bool]:
    """Valida estrutura do backend"""
    checks = {
        'api_server.py': validate_file_exists('api_server.py'),
        'requirements.txt': validate_file_exists('requirements.txt'),
        'core/': validate_file_exists('core'),
        'data/': validate_file_exists('data'),
    }
    return checks

def validate_scripts() -> Dict[str, bool]:
    """Valida scripts de inicialização"""
    checks = {
        'start_react_system_fixed.bat': validate_file_exists('start_react_system_fixed.bat'),
        'GUIA_REACT_COMPLETO.md': validate_file_exists('GUIA_REACT_COMPLETO.md'),
        'SOLUCOES_IMPLEMENTADAS.md': validate_file_exists('SOLUCOES_IMPLEMENTADAS.md'),
        'INICIAR_AQUI.md': validate_file_exists('INICIAR_AQUI.md'),
    }
    return checks

def validate_package_json() -> Tuple[bool, str]:
    """Valida package.json do frontend"""
    try:
        with open('frontend/package.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_scripts = ['dev', 'build', 'preview']
        missing = [s for s in required_scripts if s not in data.get('scripts', {})]

        if missing:
            return False, f"Scripts faltando: {', '.join(missing)}"

        return True, "Configuração OK"
    except Exception as e:
        return False, str(e)

def validate_vite_config() -> Tuple[bool, str]:
    """Valida configuração do Vite"""
    try:
        with open('frontend/vite.config.ts', 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('proxy' in content, 'Proxy configurado'),
            ('/api' in content, 'Rota /api configurada'),
            ('5000' in content, 'Porta backend correta'),
            ('8080' in content, 'Porta frontend correta'),
        ]

        failed = [msg for check, msg in checks if not check]

        if failed:
            return False, f"Problemas: {', '.join(failed)}"

        return True, "Configuração OK"
    except Exception as e:
        return False, str(e)

def print_results(results: Dict[str, bool], title: str):
    """Imprime resultados formatados"""
    print(f"{Colors.BOLD}{title}{Colors.END}")
    for item, success in results.items():
        status = check_mark(success)
        print(f"  {status} {item}")
    print()

def main():
    """Função principal"""
    print_header("VALIDAÇÃO DO SISTEMA AGENT BI REACT")

    # Validar Python
    print(f"{Colors.BOLD}1. Validando Python...{Colors.END}")
    py_ok, py_version = validate_python()
    print(f"  {check_mark(py_ok)} Python: {py_version}\n")

    # Validar Node.js
    print(f"{Colors.BOLD}2. Validando Node.js...{Colors.END}")
    node_ok, node_version = validate_node()
    print(f"  {check_mark(node_ok)} Node.js: {node_version}\n")

    # Validar npm
    print(f"{Colors.BOLD}3. Validando npm...{Colors.END}")
    npm_ok, npm_version = validate_npm()
    print(f"  {check_mark(npm_ok)} npm: {npm_version}\n")

    # Validar estrutura do frontend
    print(f"{Colors.BOLD}4. Validando Estrutura do Frontend...{Colors.END}")
    frontend_checks = validate_frontend_structure()
    print_results(frontend_checks, "")

    # Validar estrutura do backend
    print(f"{Colors.BOLD}5. Validando Estrutura do Backend...{Colors.END}")
    backend_checks = validate_backend_structure()
    print_results(backend_checks, "")

    # Validar scripts
    print(f"{Colors.BOLD}6. Validando Scripts e Documentação...{Colors.END}")
    script_checks = validate_scripts()
    print_results(script_checks, "")

    # Validar package.json
    print(f"{Colors.BOLD}7. Validando package.json...{Colors.END}")
    pkg_ok, pkg_msg = validate_package_json()
    print(f"  {check_mark(pkg_ok)} {pkg_msg}\n")

    # Validar vite.config.ts
    print(f"{Colors.BOLD}8. Validando vite.config.ts...{Colors.END}")
    vite_ok, vite_msg = validate_vite_config()
    print(f"  {check_mark(vite_ok)} {vite_msg}\n")

    # Resumo final
    all_checks = [
        py_ok,
        node_ok,
        npm_ok,
        all(frontend_checks.values()),
        all(backend_checks.values()),
        all(script_checks.values()),
        pkg_ok,
        vite_ok,
    ]

    total = len(all_checks)
    passed = sum(all_checks)

    print_header("RESUMO DA VALIDAÇÃO")

    if all(all_checks):
        print(f"{Colors.GREEN}{Colors.BOLD}[OK] TODOS OS TESTES PASSARAM! ({passed}/{total}){Colors.END}")
        print(f"\n{Colors.GREEN}O sistema esta pronto para uso!{Colors.END}")
        print(f"\n{Colors.BOLD}Proximo passo:{Colors.END}")
        print(f"  Execute: {Colors.YELLOW}start_react_system_fixed.bat{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}[ERRO] ALGUNS TESTES FALHARAM ({passed}/{total}){Colors.END}")
        print(f"\n{Colors.RED}Por favor, corrija os problemas acima antes de continuar.{Colors.END}\n")

        if not py_ok or not node_ok or not npm_ok:
            print(f"{Colors.YELLOW}Dica: Instale Python 3.9+ e Node.js 18+{Colors.END}\n")

        if not all(frontend_checks.values()):
            print(f"{Colors.YELLOW}Dica Frontend: Execute 'cd frontend && npm install'{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validação interrompida pelo usuário.{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Erro durante validação: {e}{Colors.END}\n")
        sys.exit(1)
