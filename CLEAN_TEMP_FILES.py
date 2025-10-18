"""
Script de Limpeza de Arquivos Temporários
Autor: Claude Code
Data: 2025-10-18

Remove arquivos temporários de correções antigas e documentação duplicada.
"""

import os
from pathlib import Path
from typing import List

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent

# ================================================================================
# ARQUIVOS A REMOVER (correções antigas e duplicados)
# ================================================================================

FILES_TO_REMOVE = [
    # Scripts de correção de bugs antigos
    "00_LEIA_PRIMEIRO.txt",
    "analyze_bug.py",
    "analyze_case_corrections.py",
    "auto_fix_complete.py",
    "bug_analyzer.py",
    "CHECK_CURRENT_STATE.py",
    "check_files.py",
    "CORRIGIR_AGORA.bat",
    "corrigir_agora.sh",
    "data_agent_schema_validation.py",
    "EXECUTAR_CORRECAO_COMPLETA.py",
    "execute_corrections.py",
    "EXECUTE_FIX.bat",
    "find_bug.py",
    "FIX_NOW.py",
    "fix_schema_validation.py",
    "FIX_TRANSFERENCIAS.py",
    "fix_transferencias_bug.py",
    "inspect_bug.py",
    "locate_and_fix.py",
    "QUICK_FIX.bat",
    "quick_fix.py",
    "read_and_fix.py",
    "read_file.py",
    "read_une_tools.py",
    "run_fix.bat",
    "RUN_FULL_CORRECTION.bat",
    "run_read.bat",
    "run_schema_validation.py",
    "show_diff.py",
    "simple_diagnostic.py",
    "test_transferencias_fix.py",
    "VALIDATE_CORRECTIONS.py",
    "verify_fix_ready.py",
    "grep_estoque.sh",

    # Documentação duplicada/antiga de correções
    "ARVORE_DE_ARQUIVOS.txt",
    "BUG_FIX_INDEX.md",
    "BUG_FIX_SUMMARY.md",
    "CORRECAO_TRANSFERENCIAS.md",
    "ENTREGA_FINAL.md",
    "ENTREGA_FINAL_CODE_AGENT.md",
    "EXECUTIVE_SUMMARY_CASE_CORRECTIONS.md",
    "FIX_BUG_README.md",
    "FIX_CASE_SENSITIVITY.py",
    "GUIA_RAPIDO.txt",
    "GUIA_VISUAL_RAPIDO.txt",
    "INDEX_CASE_CORRECTIONS.md",
    "INDICE_CORRECAO.md",
    "LEIA_ME_CORRECAO_TRANSFERENCIAS.md",
    "LISTA_ARQUIVOS_CRIADOS.txt",
    "MANIFESTO_CORRECAO.txt",
    "QUICK_START_GUIDE.md",
    "READ_UNE_TOOLS.txt",
    "README_CASE_CORRECTIONS.md",
    "README_CORRECAO_BUG.md",
    "README_VALIDATION.md",
    "RESUMO_EXECUTIVO_CODE_AGENT.md",
    "RESUMO_EXECUTIVO_CORRECAO.md",
    "START_HERE.md",
    "START_HERE.txt",
    "SUMARIO_1_PAGINA.txt",
    "VALIDATION_IMPLEMENTATION.md",
    "VISAO_GERAL.txt",
    "analysis_case_corrections.md",

    # Backups antigos
    "BACKUP_direct_query_engine_20251018.py",

    # Arquivos duplicados no core
    "core/agents/code_gen_agent_new.py",

    # Testes temporários
    "tests/test_column_validation.py",
]

# ================================================================================
# DIRETÓRIOS A REMOVER
# ================================================================================

DIRS_TO_REMOVE = [
    "examples",  # Se vazio ou apenas com exemplos temporários
]

# ================================================================================
# ARQUIVOS A MANTER (garantir que não sejam removidos)
# ================================================================================

FILES_TO_KEEP = [
    "PLANO_FINALIZACAO.md",  # Plano recém-criado
    "AUDIT_REPORT.md",  # Relatório de auditoria pode ser útil
    "docs/DIAGNOSTICO_RAPIDO_ERROS_QUERIES.md",  # Diagnóstico útil
    "docs/RELATORIO_ANALISE_PILAR_2.md",  # Relatório do Pilar 2
]


def remove_file(file_path: Path) -> bool:
    """
    Remove um arquivo se ele existir.

    Returns:
        True se removeu, False se não existia
    """
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"  [OK] Removido: {file_path.relative_to(ROOT_DIR)}")
            return True
        except Exception as e:
            print(f"  [ERRO] Ao remover {file_path.name}: {e}")
            return False
    else:
        print(f"  [NAO EXISTE] {file_path.relative_to(ROOT_DIR)}")
        return False


def remove_directory(dir_path: Path) -> bool:
    """
    Remove um diretório se ele existir e estiver vazio ou com conteúdo temporário.

    Returns:
        True se removeu, False caso contrário
    """
    if not dir_path.exists():
        print(f"  [NAO EXISTE] Diretorio: {dir_path.relative_to(ROOT_DIR)}")
        return False

    try:
        # Remover todos os arquivos dentro primeiro
        for item in dir_path.rglob("*"):
            if item.is_file():
                item.unlink()

        # Remover diretórios vazios
        for item in sorted(dir_path.rglob("*"), reverse=True):
            if item.is_dir():
                try:
                    item.rmdir()
                except OSError:
                    pass  # Não vazio, pular

        # Remover o diretório principal
        dir_path.rmdir()
        print(f"  [OK] Diretorio removido: {dir_path.relative_to(ROOT_DIR)}")
        return True
    except Exception as e:
        print(f"  [ERRO] Ao remover diretorio {dir_path.name}: {e}")
        return False


def clean_temp_files(dry_run: bool = True):
    """
    Limpa arquivos temporários do projeto.

    Args:
        dry_run: Se True, apenas lista o que seria removido sem remover
    """
    print("="*80)
    print("LIMPEZA DE ARQUIVOS TEMPORARIOS")
    print("="*80)
    print()

    if dry_run:
        print("MODO DRY-RUN: Apenas listando, nao vai remover nada")
        print("Execute com dry_run=False para remover de verdade")
        print()

    # Contar arquivos
    files_found = 0
    files_removed = 0
    dirs_removed = 0

    # ========== REMOVER ARQUIVOS ==========
    print("Arquivos a remover:")
    print("-"*80)

    for file_rel in FILES_TO_REMOVE:
        file_path = ROOT_DIR / file_rel

        # Verificar se não está na lista de manter
        should_keep = any(keep in str(file_rel) for keep in FILES_TO_KEEP)
        if should_keep:
            print(f"  [MANTER] {file_rel} (na lista de protecao)")
            continue

        files_found += 1

        if not dry_run:
            if remove_file(file_path):
                files_removed += 1
        else:
            if file_path.exists():
                print(f"  [REMOVER] {file_rel}")
                files_removed += 1
            else:
                print(f"  [NAO EXISTE] {file_rel}")

    print()

    # ========== REMOVER DIRETÓRIOS ==========
    print("Diretorios a remover:")
    print("-"*80)

    for dir_rel in DIRS_TO_REMOVE:
        dir_path = ROOT_DIR / dir_rel

        if not dry_run:
            if remove_directory(dir_path):
                dirs_removed += 1
        else:
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*")))
                print(f"  [REMOVER] {dir_rel} ({file_count} itens)")
                dirs_removed += 1
            else:
                print(f"  [NAO EXISTE] {dir_rel}")

    print()

    # ========== RESUMO ==========
    print("="*80)
    print("RESUMO DA LIMPEZA")
    print("="*80)

    if dry_run:
        print(f"  Arquivos encontrados: {files_found}")
        print(f"  Arquivos que seriam removidos: {files_removed}")
        print(f"  Diretorios que seriam removidos: {dirs_removed}")
        print()
        print("  Para executar a limpeza de verdade, execute:")
        print("      python CLEAN_TEMP_FILES.py --execute")
    else:
        print(f"  Arquivos processados: {files_found}")
        print(f"  Arquivos removidos: {files_removed}")
        print(f"  Diretorios removidos: {dirs_removed}")
        print()
        print("  Limpeza concluida com sucesso!")
        print()
        print("  Proximos passos:")
        print("      1. Verifique se tudo esta OK")
        print("      2. Execute: git status")
        print("      3. Execute: git add -A")
        print("      4. Execute: git commit -m 'chore: Limpar arquivos temporarios'")

    print("="*80)


if __name__ == "__main__":
    import sys

    # Verificar argumentos
    execute = "--execute" in sys.argv or "-e" in sys.argv

    # Executar limpeza
    clean_temp_files(dry_run=not execute)
