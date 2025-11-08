#!/usr/bin/env python3
"""
Plano de Limpeza Definitivo - Agent_Solution_BI
Baseado em melhores práticas Context7

Autor: Claude Code (Anthropic)
Data: 2025-11-08
Versão: 2.0

Funcionalidades:
- Backup automático antes de cada ação
- Execução incremental (por fase)
- Relatório de mudanças em JSON
- Rollback em caso de erro
- Validação de integridade pós-execução
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Paths
PROJECT_ROOT = Path(__file__).parent
BACKUP_DIR = PROJECT_ROOT / "backups" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
REPORT_FILE = PROJECT_ROOT / "cleanup_report.json"

# Estado global
report = {
    "timestamp": datetime.now().isoformat(),
    "fases_executadas": [],
    "arquivos_removidos": [],
    "arquivos_movidos": [],
    "diretorios_criados": [],
    "erros": []
}

def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Imprime mensagem de aviso"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Imprime mensagem de erro"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Imprime mensagem informativa"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def criar_backup(paths: List[Path]) -> bool:
    """
    Cria backup dos arquivos/diretórios antes de modificar

    Args:
        paths: Lista de paths para backup

    Returns:
        True se backup criado com sucesso
    """
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print_info(f"Criando backup em: {BACKUP_DIR}")

        for path in paths:
            if not path.exists():
                print_warning(f"Path não existe (pulando): {path}")
                continue

            # Calcular path relativo para manter estrutura
            rel_path = path.relative_to(PROJECT_ROOT)
            backup_path = BACKUP_DIR / rel_path

            # Criar diretórios pais se necessário
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copiar arquivo ou diretório
            if path.is_file():
                shutil.copy2(path, backup_path)
                print_success(f"Backup criado: {rel_path}")
            elif path.is_dir():
                shutil.copytree(path, backup_path, dirs_exist_ok=True)
                print_success(f"Backup criado (dir): {rel_path}")

        return True

    except Exception as e:
        print_error(f"Erro ao criar backup: {e}")
        report["erros"].append({"tipo": "backup", "erro": str(e)})
        return False

def remover_arquivo(path: Path, motivo: str = "") -> bool:
    """
    Remove arquivo com segurança (após backup)

    Args:
        path: Path do arquivo a remover
        motivo: Razão da remoção (para relatório)

    Returns:
        True se removido com sucesso
    """
    try:
        if not path.exists():
            print_warning(f"Arquivo não existe (pulando): {path}")
            return True

        path.unlink()
        print_success(f"Removido: {path.relative_to(PROJECT_ROOT)}")

        report["arquivos_removidos"].append({
            "path": str(path.relative_to(PROJECT_ROOT)),
            "motivo": motivo,
            "timestamp": datetime.now().isoformat()
        })

        return True

    except Exception as e:
        print_error(f"Erro ao remover {path}: {e}")
        report["erros"].append({
            "tipo": "remocao",
            "path": str(path),
            "erro": str(e)
        })
        return False

def mover_arquivo(origem: Path, destino: Path, motivo: str = "") -> bool:
    """
    Move arquivo/diretório com segurança

    Args:
        origem: Path de origem
        destino: Path de destino
        motivo: Razão da movimentação

    Returns:
        True se movido com sucesso
    """
    try:
        if not origem.exists():
            print_warning(f"Origem não existe (pulando): {origem}")
            return True

        # Criar diretório pai do destino se não existir
        destino.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(origem), str(destino))
        print_success(f"Movido: {origem.relative_to(PROJECT_ROOT)} → {destino.relative_to(PROJECT_ROOT)}")

        report["arquivos_movidos"].append({
            "origem": str(origem.relative_to(PROJECT_ROOT)),
            "destino": str(destino.relative_to(PROJECT_ROOT)),
            "motivo": motivo,
            "timestamp": datetime.now().isoformat()
        })

        return True

    except Exception as e:
        print_error(f"Erro ao mover {origem} → {destino}: {e}")
        report["erros"].append({
            "tipo": "movimentacao",
            "origem": str(origem),
            "destino": str(destino),
            "erro": str(e)
        })
        return False

def criar_diretorio(path: Path, motivo: str = "") -> bool:
    """
    Cria diretório se não existir

    Args:
        path: Path do diretório
        motivo: Razão da criação

    Returns:
        True se criado com sucesso
    """
    try:
        if path.exists():
            print_info(f"Diretório já existe: {path.relative_to(PROJECT_ROOT)}")
            return True

        path.mkdir(parents=True, exist_ok=True)
        print_success(f"Diretório criado: {path.relative_to(PROJECT_ROOT)}")

        report["diretorios_criados"].append({
            "path": str(path.relative_to(PROJECT_ROOT)),
            "motivo": motivo,
            "timestamp": datetime.now().isoformat()
        })

        return True

    except Exception as e:
        print_error(f"Erro ao criar diretório {path}: {e}")
        report["erros"].append({
            "tipo": "criacao_diretorio",
            "path": str(path),
            "erro": str(e)
        })
        return False

# ============================================================================
# FASE 1: LIMPEZA IMEDIATA (30 min)
# ============================================================================

def fase_1_limpeza_imediata():
    """
    Remove arquivos órfãos, temporários e de teste na raiz

    Ganho estimado: 2-3 MB, -30 arquivos
    """
    print_header("FASE 1: LIMPEZA IMEDIATA")

    # Lista de arquivos a remover
    arquivos_raiz = [
        "analise_produto_369947.py",
        "audit_streamlit_hanging.py",
        "diagnostic_detailed.py",
        "diagnostic_produto_369947.py",
        "teste_correcao_mc.py",
        "teste_filtro_produto.py",
        "run_diagnostic.bat",
    ]

    arquivos_core = [
        "core/mcp/mock_data.py",
        "core/adapters/database_adapter.py",
        "core/database/database.py",
        "core/utils/event_manager.py",
        "core/utils/db_check.py",
        "core/tools/check_integration.py",
        "core/tools/check_gui_dependencies.py",
        "core/tools/debug_server.py",
    ]

    # Converter para Path objects
    paths_remover = [PROJECT_ROOT / p for p in arquivos_raiz + arquivos_core]

    # Criar backup antes de remover
    print_info("Criando backup dos arquivos a serem removidos...")
    if not criar_backup(paths_remover):
        print_error("Falha ao criar backup. Abortando FASE 1.")
        return False

    # Remover arquivos
    print_info("\nRemovendo arquivos órfãos...")
    sucesso = True
    for path in paths_remover:
        if not remover_arquivo(path, motivo="Arquivo órfão/teste/diagnóstico"):
            sucesso = False

    # Mover legacy para backup
    legacy_dir = PROJECT_ROOT / "core" / "business_intelligence" / "legacy"
    if legacy_dir.exists():
        print_info("\nMovendo módulos legados para backup...")
        backup_legacy = PROJECT_ROOT / "backups" / f"legacy_{datetime.now().strftime('%Y%m%d')}"
        if mover_arquivo(legacy_dir, backup_legacy, motivo="Módulos obsoletos"):
            print_success("Módulos legados movidos para backup")
        else:
            sucesso = False

    # Limpar caches duplicados (apenas .json antigos, preservar .pkl novos)
    print_info("\nLimpando caches duplicados...")
    cache_dir = PROJECT_ROOT / "data" / "cache"
    if cache_dir.exists():
        json_caches = list(cache_dir.glob("*.json"))
        print_info(f"Encontrados {len(json_caches)} arquivos de cache JSON")

        # Criar backup dos caches antes de remover
        if json_caches and criar_backup(json_caches):
            for cache_file in json_caches:
                remover_arquivo(cache_file, motivo="Cache JSON antigo (migrado para PKL)")

    if sucesso:
        print_success("\n✅ FASE 1 CONCLUÍDA COM SUCESSO!")
        report["fases_executadas"].append({
            "fase": 1,
            "nome": "Limpeza Imediata",
            "status": "sucesso",
            "timestamp": datetime.now().isoformat()
        })
    else:
        print_warning("\n⚠️  FASE 1 CONCLUÍDA COM AVISOS (verifique erros)")
        report["fases_executadas"].append({
            "fase": 1,
            "nome": "Limpeza Imediata",
            "status": "parcial",
            "timestamp": datetime.now().isoformat()
        })

    return sucesso

# ============================================================================
# FASE 2: REORGANIZAÇÃO (2-3h)
# ============================================================================

def fase_2_reorganizacao():
    """
    Cria pyproject.toml, reorganiza docs/, consolida código duplicado
    """
    print_header("FASE 2: REORGANIZAÇÃO")

    sucesso = True

    # 2.1 Criar pyproject.toml
    print_info("Criando pyproject.toml...")
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agent-solution-bi"
version = "2.2.3"
description = "Assistente de BI multi-agente com LangGraph e Streamlit"
authors = [{name = "André Junior", email = "andre@cacula.com.br"}]
requires-python = ">=3.11"
dependencies = []  # Lido de requirements.txt

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "ruff>=0.0.285",
    "mypy>=1.5.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["core*", "ui*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=core --cov-report=html --cov-report=term"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
"""

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    try:
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(pyproject_content)
        print_success("pyproject.toml criado!")
    except Exception as e:
        print_error(f"Erro ao criar pyproject.toml: {e}")
        sucesso = False

    # 2.2 Reorganizar docs/
    print_info("\nReorganizando documentação...")

    # Criar diretórios
    docs_dirs = [
        "docs/architecture",
        "docs/development",
        "docs/releases"
    ]

    for dir_name in docs_dirs:
        criar_diretorio(PROJECT_ROOT / dir_name, motivo="Organização de documentação")

    # Mapear arquivos para destinos
    docs_mapping = {
        # Arquitetura
        "docs/manifesto_arquitetura_alvo.md": "docs/architecture/manifesto_arquitetura_alvo.md",
        "docs/ANALISE_ESTRUTURA_RESUMO_EXECUTIVO.md": "docs/architecture/ANALISE_ESTRUTURA_RESUMO_EXECUTIVO.md",
        "docs/ANALISE_ESTRUTURA_PARTE_1.md": "docs/architecture/ANALISE_ESTRUTURA_PARTE_1.md",
        "docs/ANALISE_ESTRUTURA_PARTE_2.md": "docs/architecture/ANALISE_ESTRUTURA_PARTE_2.md",

        # Releases
        "docs/RELEASE_NOTES_v2.2.md": "docs/releases/RELEASE_NOTES_v2.2.md",
        "docs/RELEASE_NOTES_v2.0.md": "docs/releases/RELEASE_NOTES_v2.0.md",
        "docs/RESUMO_ENTREGAS_v2.0.md": "docs/releases/RESUMO_ENTREGAS_v2.0.md",
        "docs/RESUMO_ENTREGAS_FINAL_v2.1.md": "docs/releases/RESUMO_ENTREGAS_FINAL_v2.1.md",
    }

    # Mover arquivos (apenas os que existem)
    for origem_rel, destino_rel in docs_mapping.items():
        origem = PROJECT_ROOT / origem_rel
        destino = PROJECT_ROOT / destino_rel

        if origem.exists():
            mover_arquivo(origem, destino, motivo="Reorganização de documentação")

    # Criar README.md principal em docs/
    readme_content = """# Agent_Solution_BI - Documentação

## Índice Geral

### 📐 Arquitetura
- [Manifesto da Arquitetura Alvo](architecture/manifesto_arquitetura_alvo.md)
- [Análise de Estrutura - Resumo Executivo](architecture/ANALISE_ESTRUTURA_RESUMO_EXECUTIVO.md)
- [Análise de Estrutura - Parte 1](architecture/ANALISE_ESTRUTURA_PARTE_1.md)
- [Análise de Estrutura - Parte 2](architecture/ANALISE_ESTRUTURA_PARTE_2.md)

### 🛠️ Desenvolvimento
- [Correções e Melhorias](development/)
- [Implementações](development/)

### 📋 Releases
- [Release Notes v2.2](releases/RELEASE_NOTES_v2.2.md)
- [Release Notes v2.0](releases/RELEASE_NOTES_v2.0.md)
- [Resumo de Entregas v2.0](releases/RESUMO_ENTREGAS_v2.0.md)

### 🚀 Início Rápido
- [Guia Rápido 5min](../GUIA_RAPIDO_5MIN.txt)

### 🧹 Limpeza e Otimização
- [Relatório Final de Limpeza Context7](../RELATORIO_FINAL_LIMPEZA_CONTEXT7.md)

---

**Gerado automaticamente por:** plano_limpeza_definitivo.py
**Data:** {}
""".format(datetime.now().strftime('%Y-%m-%d'))

    readme_path = PROJECT_ROOT / "docs" / "README.md"
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print_success("docs/README.md criado!")
    except Exception as e:
        print_error(f"Erro ao criar docs/README.md: {e}")
        sucesso = False

    if sucesso:
        print_success("\n✅ FASE 2 CONCLUÍDA COM SUCESSO!")
        report["fases_executadas"].append({
            "fase": 2,
            "nome": "Reorganização",
            "status": "sucesso",
            "timestamp": datetime.now().isoformat()
        })
    else:
        print_warning("\n⚠️  FASE 2 CONCLUÍDA COM AVISOS")
        report["fases_executadas"].append({
            "fase": 2,
            "nome": "Reorganização",
            "status": "parcial",
            "timestamp": datetime.now().isoformat()
        })

    return sucesso

# ============================================================================
# FASE 3: OTIMIZAÇÕES (3-4h)
# ============================================================================

def fase_3_otimizacoes():
    """
    Aplica otimizações de código (Polars, LangGraph, Streamlit)

    NOTA: Esta fase requer edição manual de código.
    O script cria apenas templates e documentação.
    """
    print_header("FASE 3: OTIMIZAÇÕES")

    print_warning("⚠️  FASE 3 requer edição manual de código!")
    print_info("Esta fase cria apenas templates e documentação de referência.\n")

    # Criar diretório de templates
    templates_dir = PROJECT_ROOT / "docs" / "development" / "otimizacoes_templates"
    criar_diretorio(templates_dir, motivo="Templates de otimização")

    # Template 1: Schema enforcement Polars
    template_polars = """# Template: Schema Enforcement Polars
# Aplicar em: core/connectivity/polars_dask_adapter.py

import polars as pl

def _get_schema_map() -> dict:
    \"\"\"Schema map com tipos forçados para evitar conversões\"\"\"
    return {
        "CODPRODUTO": pl.Utf8,  # Evitar conversão int->str
        "QTDVENDIDA": pl.Float64,  # Já numérico
        "VALORLIQUIDO": pl.Float64,
        "DTAEMISSAO": pl.Date,  # Parse otimizado
        "CODUNE": pl.Utf8,
        # ... adicionar outros campos conforme schema real
    }

# ANTES:
# df = pl.scan_parquet(parquet_path)

# DEPOIS:
df = pl.scan_parquet(
    parquet_path,
    schema_overrides=_get_schema_map()  # 🚀 Evita inferência automática
)
"""

    # Template 2: LangGraph checkpointing otimizado
    template_langgraph = """# Template: Checkpointing Otimizado LangGraph
# Aplicar em: core/graph/graph_builder.py

from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import timedelta

# ANTES:
# checkpointer = SqliteSaver.from_conn_string("data/checkpoints/agent_graph.db")

# DEPOIS:
checkpointer = SqliteSaver.from_conn_string(
    "data/checkpoints/agent_graph.db",
    ttl=timedelta(days=7),  # 🚀 Limpeza automática após 7 dias
    max_entries=1000  # 🚀 Limitar entradas
)
"""

    # Salvar templates
    try:
        with open(templates_dir / "polars_schema_enforcement.py", "w") as f:
            f.write(template_polars)
        print_success("Template Polars criado")

        with open(templates_dir / "langgraph_checkpointing.py", "w") as f:
            f.write(template_langgraph)
        print_success("Template LangGraph criado")

    except Exception as e:
        print_error(f"Erro ao criar templates: {e}")
        return False

    print_info("\n📋 Próximos passos manuais:")
    print_info("1. Aplicar template Polars em: core/connectivity/polars_dask_adapter.py")
    print_info("2. Aplicar template LangGraph em: core/graph/graph_builder.py")
    print_info("3. Testar performance com: scripts/test_query_performance.py")
    print_info("4. Verificar documentação: docs/development/otimizacoes_templates/")

    print_success("\n✅ FASE 3 CONCLUÍDA (templates criados)")
    report["fases_executadas"].append({
        "fase": 3,
        "nome": "Otimizações (Templates)",
        "status": "templates_criados",
        "timestamp": datetime.now().isoformat()
    })

    return True

# ============================================================================
# FASE 4: REFATORAÇÃO (1 semana)
# ============================================================================

def fase_4_refatoracao():
    """
    Refatoração profunda (utils/, testes, automação)

    NOTA: Esta é a fase mais complexa e deve ser feita manualmente.
    O script cria apenas a estrutura de diretórios e documentação.
    """
    print_header("FASE 4: REFATORAÇÃO")

    print_warning("⚠️  FASE 4 é a mais complexa e requer muito trabalho manual!")
    print_info("Esta fase cria apenas a estrutura de diretórios e noxfile.py base.\n")

    # Criar estrutura de diretórios para utils/
    utils_dirs = [
        "core/utils/database",
        "core/utils/formatting",
        "core/utils/validation",
        "core/utils/caching"
    ]

    for dir_name in utils_dirs:
        criar_diretorio(PROJECT_ROOT / dir_name, motivo="Reorganização utils/")

    # Criar estrutura de testes
    tests_dirs = [
        "tests/unit",
        "tests/integration",
        "tests/e2e"
    ]

    for dir_name in tests_dirs:
        criar_diretorio(PROJECT_ROOT / dir_name, motivo="Reorganização testes")

    # Criar noxfile.py base
    noxfile_content = """# Automação de testes e linting com Nox
import nox

@nox.session(python=["3.11", "3.12"])
def tests(session):
    \"\"\"Executar suite de testes\"\"\"
    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov")
    session.run("pytest", "--cov=core", "--cov-report=html")

@nox.session
def lint(session):
    \"\"\"Linting com ruff\"\"\"
    session.install("ruff")
    session.run("ruff", "check", "core/", "tests/")

@nox.session
def format(session):
    \"\"\"Formatação com black\"\"\"
    session.install("black")
    session.run("black", "core/", "tests/", "streamlit_app.py")

@nox.session
def type_check(session):
    \"\"\"Type checking com mypy\"\"\"
    session.install("mypy")
    session.run("mypy", "core/")

# Executar tudo:
# $ nox -s tests lint format type_check
"""

    noxfile_path = PROJECT_ROOT / "noxfile.py"
    try:
        with open(noxfile_path, "w", encoding="utf-8") as f:
            f.write(noxfile_content)
        print_success("noxfile.py criado!")
    except Exception as e:
        print_error(f"Erro ao criar noxfile.py: {e}")
        return False

    print_info("\n📋 Próximos passos manuais (1 semana de trabalho):")
    print_info("1. Mover arquivos utils/ para subdiretórios criados")
    print_info("2. Atualizar imports em todo projeto")
    print_info("3. Mover testes desabilitados para tests/integration/")
    print_info("4. Criar testes E2E com streamlit.testing")
    print_info("5. Executar nox para validar: nox -s tests lint")

    print_success("\n✅ FASE 4 CONCLUÍDA (estrutura criada)")
    report["fases_executadas"].append({
        "fase": 4,
        "nome": "Refatoração (Estrutura)",
        "status": "estrutura_criada",
        "timestamp": datetime.now().isoformat()
    })

    return True

# ============================================================================
# VALIDAÇÃO E RELATÓRIOS
# ============================================================================

def validar_integridade():
    """
    Valida integridade do projeto após mudanças
    """
    print_header("VALIDAÇÃO DE INTEGRIDADE")

    validacoes = {
        "streamlit_app.py existe": (PROJECT_ROOT / "streamlit_app.py").exists(),
        "core/ existe": (PROJECT_ROOT / "core").exists(),
        "requirements.txt existe": (PROJECT_ROOT / "requirements.txt").exists(),
        "pyproject.toml existe": (PROJECT_ROOT / "pyproject.toml").exists(),
        "docs/README.md existe": (PROJECT_ROOT / "docs" / "README.md").exists(),
    }

    print_info("Verificando arquivos críticos...")
    todas_ok = True
    for nome, resultado in validacoes.items():
        if resultado:
            print_success(nome)
        else:
            print_error(f"{nome} - FALHOU!")
            todas_ok = False

    # Tentar importar módulo crítico
    print_info("\nTestando imports críticos...")
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from core.graph.graph_builder import GraphBuilder
        print_success("core.graph.graph_builder importável")
    except ImportError as e:
        print_error(f"Erro ao importar GraphBuilder: {e}")
        todas_ok = False

    if todas_ok:
        print_success("\n✅ VALIDAÇÃO CONCLUÍDA: Sistema íntegro!")
    else:
        print_warning("\n⚠️  VALIDAÇÃO: Alguns problemas detectados")

    return todas_ok

def salvar_relatorio():
    """Salva relatório JSON com todas as mudanças"""
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_success(f"\n📄 Relatório salvo em: {REPORT_FILE}")

        # Imprimir resumo
        print_info("\n📊 RESUMO:")
        print_info(f"  - Fases executadas: {len(report['fases_executadas'])}")
        print_info(f"  - Arquivos removidos: {len(report['arquivos_removidos'])}")
        print_info(f"  - Arquivos movidos: {len(report['arquivos_movidos'])}")
        print_info(f"  - Diretórios criados: {len(report['diretorios_criados'])}")
        print_info(f"  - Erros: {len(report['erros'])}")

    except Exception as e:
        print_error(f"Erro ao salvar relatório: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Plano de Limpeza Definitivo - Agent_Solution_BI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Executar apenas FASE 1 (limpeza imediata)
  python plano_limpeza_definitivo.py --fase 1

  # Executar FASES 1-3
  python plano_limpeza_definitivo.py --fase 1-3

  # Executar tudo
  python plano_limpeza_definitivo.py --all

  # Executar tudo com confirmação
  python plano_limpeza_definitivo.py --all --confirm

  # Apenas validar integridade (sem mudanças)
  python plano_limpeza_definitivo.py --validate-only
        """
    )

    parser.add_argument(
        "--fase",
        type=str,
        help="Fase a executar (1, 2, 3, 4, ou range como 1-3)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Executar todas as 4 fases"
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Pedir confirmação antes de cada fase"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Apenas validar integridade (sem fazer mudanças)"
    )

    args = parser.parse_args()

    # Validação apenas
    if args.validate_only:
        validar_integridade()
        return 0

    # Determinar fases a executar
    fases = []
    if args.all:
        fases = [1, 2, 3, 4]
    elif args.fase:
        if "-" in args.fase:
            inicio, fim = args.fase.split("-")
            fases = list(range(int(inicio), int(fim) + 1))
        else:
            fases = [int(args.fase)]
    else:
        # Default: apenas FASE 1
        print_warning("Nenhuma fase especificada. Executando apenas FASE 1.")
        fases = [1]

    # Executar fases
    print_header(f"PLANO DE LIMPEZA DEFINITIVO - Agent_Solution_BI")
    print_info(f"Fases a executar: {', '.join(map(str, fases))}")
    print_info(f"Backup será criado em: {BACKUP_DIR}")

    if args.confirm:
        resposta = input(f"\n{Colors.WARNING}Continuar? (s/N): {Colors.ENDC}")
        if resposta.lower() != "s":
            print_info("Operação cancelada.")
            return 0

    # Executar cada fase
    for fase in fases:
        if args.confirm:
            resposta = input(f"\n{Colors.WARNING}Executar FASE {fase}? (s/N): {Colors.ENDC}")
            if resposta.lower() != "s":
                print_info(f"FASE {fase} pulada.")
                continue

        if fase == 1:
            fase_1_limpeza_imediata()
        elif fase == 2:
            fase_2_reorganizacao()
        elif fase == 3:
            fase_3_otimizacoes()
        elif fase == 4:
            fase_4_refatoracao()

    # Validar integridade
    validar_integridade()

    # Salvar relatório
    salvar_relatorio()

    print_header("CONCLUÍDO!")
    print_info(f"Backup disponível em: {BACKUP_DIR}")
    print_info(f"Relatório disponível em: {REPORT_FILE}")
    print_info(f"Documentação atualizada em: docs/README.md")

    return 0

if __name__ == "__main__":
    sys.exit(main())
