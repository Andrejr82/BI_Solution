"""
Script de Reorganização do Projeto
Autor: Claude Code
Data: 2025-10-18

Move arquivos da raiz para pastas apropriadas.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path(__file__).parent

# ================================================================================
# ESTRUTURA DE DIRETÓRIOS
# ================================================================================

DIRECTORY_STRUCTURE = {
    "docs/reports": "Relatórios e análises",
    "docs/guides": "Guias e tutoriais",
    "docs/planning": "Planejamento e roadmaps",
    "docs/releases": "Releases e entregas",
    "docs/indexes": "Índices e listagens",
    "docs/temp": "Documentos temporários",
    "scripts/utils": "Scripts utilitários",
    "scripts/data_processing": "Scripts de processamento de dados",
    "scripts/cleanup": "Scripts de limpeza",
}

# ================================================================================
# MAPEAMENTO DE ARQUIVOS
# ================================================================================

FILE_MAPPING = {
    # ========== RELATÓRIOS (docs/reports/) ==========
    "docs/reports": [
        "AUDIT_REPORT.md",
        "AUDIT_REPORT_20251017.md",
        "RELATORIO_EXECUTIVO_COMPLETO.md",
        "RELATORIO_FINAL_LIMPEZA.md",
        "DIFF_VALIDADORES_UNE_TOOLS.md",
    ],

    # ========== GUIAS (docs/guides/) ==========
    "docs/guides": [
        "COMECE_AQUI.txt",
        "README_FEW_SHOT.md",
        "README_LIMPEZA_PROJETO.md",
        "LIMPEZA_README.md",
        "GIT_CLEANUP_INSTRUCTIONS.md",
        "GEMINI.md",
    ],

    # ========== PLANEJAMENTO (docs/planning/) ==========
    "docs/planning": [
        "PLANO_FINALIZACAO.md",
        "RESUMO_FINALIZACAO.md",
        "IMPLEMENTACAO_COMPLETA_UNE_TOOLS.md",
        "INTEGRACAO_FEW_SHOT.md",
        "INTEGRACAO_VALIDADORES_RESUMO.md",
        "RECOMENDACOES_POS_INTEGRACAO.md",
    ],

    # ========== RELEASES E ENTREGAS (docs/releases/) ==========
    "docs/releases": [
        "ENTREGA_PILAR_2.md",
        "PILAR_2_IMPLEMENTADO.md",
        "RELEASE_NOTES_PILAR_2.md",
        "SUMARIO_ENTREGA_PILAR_2.md",
        "TODO_PILAR_2.md",
    ],

    # ========== ÍNDICES (docs/indexes/) ==========
    "docs/indexes": [
        "INDICE_LIMPEZA.md",
        "INDICE_PILAR_2.md",
        "LISTA_COMPLETA_ARQUIVOS.md",
    ],

    # ========== SCRIPTS DE LIMPEZA (scripts/cleanup/) ==========
    "scripts/cleanup": [
        "CLEAN_TEMP_FILES.py",
        "cleanup_project.py",
        "preview_cleanup.py",
        "EXECUTAR_LIMPEZA.bat",
    ],

    # ========== SCRIPTS DE PROCESSAMENTO (scripts/data_processing/) ==========
    "scripts/data_processing": [
        "process_admmat_extended.py",
        "process_admmat_extended_v2.py",
        "test_une_tools.py",
        "TEST_VALIDADORES.py",
        "test_validadores_funcionando.py",
    ],

    # ========== SCRIPTS UTILITÁRIOS (scripts/utils/) ==========
    "scripts/utils": [
        "run_fase1_tests.py",
        "run_streamlit.py",
        "start_app.py",
        "verify_cleanup.py",
        "run_streamlit.bat",
        "start_app.bat",
        "start_app.sh",
    ],

    # ========== DOCUMENTOS TEMPORÁRIOS (docs/temp/) ==========
    "docs/temp": [
        ".cleanup_report.md",
        "RESUMO_PILAR_2.txt",
        "SUMARIO_LIMPEZA.md",
    ],
}

# ================================================================================
# ARQUIVOS A MANTER NA RAIZ
# ================================================================================

KEEP_IN_ROOT = [
    "main.py",              # Backend FastAPI
    "streamlit_app.py",     # Frontend Streamlit
    "README.md",            # README principal
    "requirements.txt",     # Dependências
    ".gitignore",
    ".env",
    ".env.example",
    "pyproject.toml",
    "setup.py",
]


def create_directory_structure():
    """Cria a estrutura de diretórios."""
    print("\n" + "="*80)
    print("CRIANDO ESTRUTURA DE DIRETORIOS")
    print("="*80 + "\n")

    for dir_path, description in DIRECTORY_STRUCTURE.items():
        full_path = ROOT_DIR / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  [CRIADO] {dir_path} - {description}")
        else:
            print(f"  [EXISTE] {dir_path}")


def move_files(dry_run: bool = True):
    """
    Move arquivos para as pastas apropriadas.

    Args:
        dry_run: Se True, apenas simula sem mover
    """
    print("\n" + "="*80)
    print("MOVENDO ARQUIVOS")
    print("="*80 + "\n")

    if dry_run:
        print("MODO DRY-RUN: Apenas simulando, nao vai mover nada\n")

    files_moved = 0
    files_not_found = 0

    for dest_dir, files in FILE_MAPPING.items():
        print(f"\n--- {dest_dir} ---")

        for filename in files:
            source = ROOT_DIR / filename
            dest = ROOT_DIR / dest_dir / filename

            if not source.exists():
                print(f"  [NAO EXISTE] {filename}")
                files_not_found += 1
                continue

            if dest.exists():
                print(f"  [JA EXISTE] {dest_dir}/{filename}")
                continue

            if dry_run:
                print(f"  [MOVER] {filename} -> {dest_dir}/")
            else:
                try:
                    shutil.move(str(source), str(dest))
                    print(f"  [OK] Movido: {filename} -> {dest_dir}/")
                    files_moved += 1
                except Exception as e:
                    print(f"  [ERRO] {filename}: {e}")

    return files_moved, files_not_found


def create_readme_in_dirs():
    """Cria README.md em cada diretório explicando seu conteúdo."""
    print("\n" + "="*80)
    print("CRIANDO READMEs NOS DIRETORIOS")
    print("="*80 + "\n")

    readme_contents = {
        "docs/reports": """# Relatórios e Análises

Este diretório contém relatórios técnicos, auditorias e análises do projeto.

## Conteúdo
- Relatórios de auditoria
- Análises de implementação
- Relatórios executivos
- Comparações e diffs
""",

        "docs/guides": """# Guias e Tutoriais

Este diretório contém guias de uso, tutoriais e documentação de referência.

## Conteúdo
- Guias de início rápido
- Tutoriais de funcionalidades
- Instruções de configuração
- Documentação técnica
""",

        "docs/planning": """# Planejamento e Roadmaps

Este diretório contém planos de implementação, roadmaps e documentos de planejamento.

## Conteúdo
- Planos de implementação
- Roadmaps de features
- Resumos de finalizações
- Recomendações técnicas
""",

        "docs/releases": """# Releases e Entregas

Este diretório contém notas de release, entregas e documentação de versões.

## Conteúdo
- Release notes
- Documentos de entrega
- Sumários de implementações
- TODOs de versões
""",

        "docs/indexes": """# Índices e Listagens

Este diretório contém índices, listagens e organizações de arquivos.

## Conteúdo
- Índices de documentação
- Listagens de arquivos
- Organizações de conteúdo
""",

        "scripts/cleanup": """# Scripts de Limpeza

Este diretório contém scripts para limpeza e organização do projeto.

## Conteúdo
- Scripts de limpeza de arquivos temporários
- Scripts de organização
- Previews de limpeza
- Batches de execução
""",

        "scripts/data_processing": """# Scripts de Processamento de Dados

Este diretório contém scripts para processamento e transformação de dados.

## Conteúdo
- Scripts de processamento de parquet
- Scripts de teste
- Scripts de validação
- Transformações de dados
""",
    }

    for dir_path, content in readme_contents.items():
        readme_path = ROOT_DIR / dir_path / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [CRIADO] {dir_path}/README.md")
        else:
            print(f"  [EXISTE] {dir_path}/README.md")


def list_remaining_files():
    """Lista arquivos que ainda estão na raiz após a reorganização."""
    print("\n" + "="*80)
    print("ARQUIVOS RESTANTES NA RAIZ")
    print("="*80 + "\n")

    root_files = []
    for item in ROOT_DIR.iterdir():
        if item.is_file() and item.suffix in ['.py', '.md', '.txt', '.bat', '.sh']:
            root_files.append(item.name)

    root_files.sort()

    print("Arquivos que devem permanecer na raiz:")
    for f in root_files:
        if f in KEEP_IN_ROOT:
            print(f"  [OK] {f}")

    print("\nArquivos que ainda precisam ser organizados:")
    for f in root_files:
        if f not in KEEP_IN_ROOT and f != "REORGANIZE_PROJECT.py":
            print(f"  [REVISAR] {f}")


def main(dry_run: bool = True):
    """
    Executa a reorganização completa.

    Args:
        dry_run: Se True, apenas simula
    """
    print("\n" + "="*80)
    print("REORGANIZACAO DO PROJETO")
    print("="*80)

    if dry_run:
        print("\nMODO DRY-RUN: Apenas simulando")
        print("Execute com --execute para aplicar mudancas\n")

    # 1. Criar estrutura
    create_directory_structure()

    # 2. Mover arquivos
    moved, not_found = move_files(dry_run)

    # 3. Criar READMEs
    if not dry_run:
        create_readme_in_dirs()

    # 4. Listar restantes
    if not dry_run:
        list_remaining_files()

    # Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)

    if dry_run:
        print(f"  Arquivos que seriam movidos: {moved}")
        print(f"  Arquivos nao encontrados: {not_found}")
        print("\n  Para executar de verdade:")
        print("      python REORGANIZE_PROJECT.py --execute")
    else:
        print(f"  Arquivos movidos: {moved}")
        print(f"  Arquivos nao encontrados: {not_found}")
        print("\n  Proximos passos:")
        print("      1. Verifique a estrutura: ls -R docs/ scripts/")
        print("      2. Execute: git status")
        print("      3. Execute: git add -A")
        print("      4. Execute: git commit -m 'chore: Reorganizar estrutura do projeto'")

    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    execute = "--execute" in sys.argv or "-e" in sys.argv
    main(dry_run=not execute)
