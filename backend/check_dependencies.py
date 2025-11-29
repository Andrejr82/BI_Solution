#!/usr/bin/env python3
"""
Verificador de Dependências - Agent Solution BI Backend
========================================================

Este script verifica TODAS as dependências do projeto e gera um relatório
detalhado do status de cada pacote.

Uso:
    python check_dependencies.py
"""

import sys
import importlib
from typing import Dict, List, Tuple

# Códigos ANSI para cores (Windows 10+)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def check_package(package_name: str) -> Tuple[bool, str]:
    """
    Verifica se um pacote está instalado e retorna sua versão.

    Args:
        package_name: Nome do pacote a verificar

    Returns:
        Tupla (instalado: bool, versão: str)
    """
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, 'N/A'


def main():
    """Função principal de verificação."""

    print(f"{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}Verificador de Dependências - Agent Solution BI Backend{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    # Definir dependências críticas por categoria
    dependencies: Dict[str, List[Tuple[str, str, str]]] = {
        "Core Framework (FastAPI + Backend)": [
            ('fastapi', '^0.115.0', 'CRÍTICO'),
            ('uvicorn', '^0.35.0', 'CRÍTICO'),
            ('pydantic', '^2.11.0', 'CRÍTICO'),
            ('pydantic_settings', '^2.10.0', 'CRÍTICO'),
            ('dotenv', '^1.1.0', 'CRÍTICO'),
            ('python_multipart', '^0.0.20', 'IMPORTANTE'),
            ('jinja2', '^3.1.6', 'IMPORTANTE'),
            ('email_validator', '^2.0.0', 'IMPORTANTE'),
        ],

        "Database & Data Processing": [
            ('sqlalchemy', '^2.0.43', 'CRÍTICO'),
            ('alembic', '^1.16.4', 'IMPORTANTE'),
            ('aioodbc', '^0.5.0', 'IMPORTANTE'),
            ('aiosqlite', '^0.21.0', 'IMPORTANTE'),
            ('pyodbc', '^5.2.0', 'IMPORTANTE'),
            ('pandas', '^2.2.2', 'CRÍTICO'),
            ('polars', '^1.35.2', 'CRÍTICO'),
            ('pyarrow', '^16.1.0', 'CRÍTICO'),
            ('numpy', '^1.26.4', 'CRÍTICO'),
            ('dask', '^2025.11.0', 'IMPORTANTE'),
        ],

        "LLM & Agents (LangChain + Gemini)": [
            ('langchain', '^0.3.13', 'CRÍTICO'),
            ('langchain_core', 'latest', 'CRÍTICO'),
            ('langchain_community', '^0.3.13', 'CRÍTICO'),
            ('langchain_openai', '^1.0.3', 'IMPORTANTE'),
            ('langgraph', '^0.2.55', 'CRÍTICO'),
            ('google.generativeai', '^0.8.5', 'CRÍTICO'),
        ],

        "Visualização de Dados (Gráficos)": [
            ('plotly', '^6.5.0', 'CRÍTICO'),
            ('kaleido', '^1.2.0', 'IMPORTANTE'),
            ('matplotlib', '^3.10.7', 'IMPORTANTE'),
            ('seaborn', '^0.13.2', 'IMPORTANTE'),
        ],

        "Security & Authentication": [
            ('jose', '^3.5.0', 'CRÍTICO'),
            ('passlib', '^1.7.4', 'CRÍTICO'),
        ],

        "Monitoring & Performance": [
            ('structlog', '^25.5.0', 'IMPORTANTE'),
            ('sentry_sdk', '^2.35.0', 'IMPORTANTE'),
            ('prometheus_client', '^0.22.0', 'IMPORTANTE'),
            ('slowapi', '^0.1.9', 'IMPORTANTE'),
        ],

        "HTTP & Utilities": [
            ('httpx', '^0.28.0', 'IMPORTANTE'),
            ('redis', '^5.2.0', 'IMPORTANTE'),
            ('orjson', 'latest', 'OPCIONAL'),
        ],
    }

    # Estatísticas
    total_packages = 0
    installed_count = 0
    missing_count = 0
    critical_missing = []
    important_missing = []

    # Verificar cada categoria
    for category, packages in dependencies.items():
        print(f"{BOLD}{BLUE}{category}{RESET}")
        print(f"{'-'*80}")

        for package_name, required_version, priority in packages:
            total_packages += 1
            installed, version = check_package(package_name)

            status_icon = f"{GREEN}✓{RESET}" if installed else f"{RED}✗{RESET}"
            priority_color = RED if priority == 'CRÍTICO' else YELLOW if priority == 'IMPORTANTE' else ''

            if installed:
                installed_count += 1
                print(f"{status_icon} {package_name:30s} v{version:15s} [{priority_color}{priority}{RESET}]")
            else:
                missing_count += 1
                print(f"{status_icon} {package_name:30s} {'FALTANDO':15s} [{priority_color}{priority}{RESET}]")

                if priority == 'CRÍTICO':
                    critical_missing.append(package_name)
                elif priority == 'IMPORTANTE':
                    important_missing.append(package_name)

        print()

    # Resumo Final
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}Resumo da Verificação{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    print(f"Total de pacotes verificados: {BOLD}{total_packages}{RESET}")
    print(f"{GREEN}Instalados: {installed_count}{RESET}")
    print(f"{RED}Faltando: {missing_count}{RESET}\n")

    # Pacotes críticos faltando
    if critical_missing:
        print(f"{RED}{BOLD}⚠️  PACOTES CRÍTICOS FALTANDO ({len(critical_missing)}):{RESET}")
        for pkg in critical_missing:
            print(f"   {RED}●{RESET} {pkg}")
        print()

    # Pacotes importantes faltando
    if important_missing:
        print(f"{YELLOW}{BOLD}⚠️  PACOTES IMPORTANTES FALTANDO ({len(important_missing)}):{RESET}")
        for pkg in important_missing:
            print(f"   {YELLOW}●{RESET} {pkg}")
        print()

    # Comandos de instalação
    if missing_count > 0:
        all_missing = critical_missing + important_missing

        print(f"{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}{BLUE}Comandos para Instalar Pacotes Faltantes{RESET}")
        print(f"{BOLD}{'='*80}{RESET}\n")

        print(f"{YELLOW}Poetry (Recomendado):{RESET}")
        print(f"poetry add {' '.join(all_missing)}\n")

        print(f"{YELLOW}Pip (Alternativa):{RESET}")
        print(f"pip install {' '.join(all_missing)}\n")

        print(f"{YELLOW}Script Automatizado:{RESET}")
        print(f"python install_missing_deps.bat\n")
    else:
        print(f"{GREEN}{BOLD}✓ Todas as dependências estão instaladas!{RESET}\n")

    # Código de saída
    exit_code = 1 if critical_missing else 0

    print(f"{BOLD}{'='*80}{RESET}\n")

    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verificação interrompida pelo usuário.{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}ERRO: {e}{RESET}")
        sys.exit(1)
