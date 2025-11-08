"""
Script de Limpeza do Projeto Agent_Solution_BI
Executa limpeza organizada em 4 fases
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

def criar_backup(fase: str):
    """Cria backup antes de cada fase"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BASE_DIR / "backups" / f"pre_limpeza_{fase}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Backup criado: {backup_dir}")
    return backup_dir

def mover_arquivo(origem: Path, destino: Path, backup_dir: Path = None):
    """Move arquivo com backup opcional"""
    if not origem.exists():
        print(f"[AVISO] Arquivo nao encontrado: {origem}")
        return False

    if backup_dir:
        backup_file = backup_dir / origem.name
        shutil.copy2(origem, backup_file)

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(origem), str(destino))
    print(f"[OK] Movido: {origem.name} -> {destino}")
    return True

def deletar_arquivo(arquivo: Path, backup_dir: Path = None):
    """Deleta arquivo com backup opcional"""
    if not arquivo.exists():
        print(f"[AVISO] Arquivo nao encontrado: {arquivo}")
        return False

    if backup_dir:
        backup_file = backup_dir / arquivo.name
        shutil.copy2(arquivo, backup_file)

    arquivo.unlink()
    print(f"[DELETE] Deletado: {arquivo.name}")
    return True

# ==================== FASE 1: LIMPAR TEMPORÁRIOS DA RAIZ ====================
def fase1_limpar_temporarios():
    """Move arquivos de diagnóstico e testes para locais apropriados"""
    print("\n" + "="*60)
    print("FASE 1: LIMPEZA DE ARQUIVOS TEMPORÁRIOS NA RAIZ")
    print("="*60)

    backup = criar_backup("fase1")

    # Criar diretórios de destino
    diagnostics_dir = BASE_DIR / "docs" / "diagnostics"
    manual_tests_dir = BASE_DIR / "tests" / "manual"
    audit_dir = BASE_DIR / "docs" / "audit"

    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    manual_tests_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    # Scripts de diagnóstico → docs/diagnostics/
    diagnosticos = [
        "analise_produto_369947.py",
        "diagnostic_detailed.py",
        "diagnostic_produto_369947.py",
        "audit_streamlit_hanging.py",
        "run_diagnostic.bat"
    ]

    for arq in diagnosticos:
        origem = BASE_DIR / arq
        destino = diagnostics_dir / arq
        mover_arquivo(origem, destino, backup)

    # Testes manuais → tests/manual/
    testes = [
        "teste_correcao_mc.py",
        "teste_filtro_produto.py"
    ]

    for arq in testes:
        origem = BASE_DIR / arq
        destino = manual_tests_dir / arq
        mover_arquivo(origem, destino, backup)

    # Relatórios de audit → docs/audit/
    audits = [
        "AUDIT_REPORT_FINAL.txt",
        "AUDIT_STREAMLIT_HANGING.md",
        "AUDIT_RESULTS_2025_10_21.json",
        "CODIGO_CORRECAO_PRONTO.md",
        "GUIA_RAPIDO_5MIN.txt",
        "RELATORIO_AUDIT_COMPLETO.md",
        "RESUMO_EXECUTIVO_AUDIT.txt",
        "SOLUCAO_IMEDIATA.md",
        "INDICE_AUDIT_STREAMLIT.md"
    ]

    for arq in audits:
        origem = BASE_DIR / arq
        destino = audit_dir / arq
        mover_arquivo(origem, destino, backup)

    print("\n[OK] FASE 1 CONCLUIDA!")

# ==================== FASE 2: REMOVER CÓDIGO DUPLICADO ====================
def fase2_remover_duplicados():
    """Remove versões duplicadas de código"""
    print("\n" + "="*60)
    print("FASE 2: REMOÇÃO DE CÓDIGO DUPLICADO")
    print("="*60)

    backup = criar_backup("fase2")

    # Criar diretório de arquivo
    archive_dir = BASE_DIR / "core" / "agents" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # code_gen_agent duplicados → archive
    duplicados_agents = [
        "code_gen_agent_fase_1_2.py",
        "code_gen_agent_integrated.py"
    ]

    for arq in duplicados_agents:
        origem = BASE_DIR / "core" / "agents" / arq
        destino = archive_dir / arq
        mover_arquivo(origem, destino, backup)

    # Legacy engines ja estao em legacy/, apenas confirmar
    legacy_dir = BASE_DIR / "core" / "business_intelligence" / "legacy"
    if legacy_dir.exists():
        print(f"[OK] Legacy engines ja em: {legacy_dir}")

    print("\n[OK] FASE 2 CONCLUIDA!")

# ==================== FASE 3: LIMPAR BACKUPS ANTIGOS ====================
def fase3_limpar_backups():
    """Remove backups antigos (>30 dias)"""
    print("\n" + "="*60)
    print("FASE 3: LIMPEZA DE BACKUPS ANTIGOS")
    print("="*60)

    backups_dir = BASE_DIR / "backups"
    if not backups_dir.exists():
        print("[AVISO] Diretorio backups/ nao encontrado")
        return

    hoje = datetime.now()
    limite = hoje - timedelta(days=30)

    removidos = 0
    for backup in backups_dir.iterdir():
        if backup.is_dir():
            # Extrair data do nome (assumindo formato com data)
            try:
                # Formato: algo_20251101
                data_str = backup.name.split("_")[-1]
                if len(data_str) == 8 and data_str.isdigit():
                    data_backup = datetime.strptime(data_str, "%Y%m%d")

                    if data_backup < limite:
                        print(f"[DELETE] Removendo backup antigo: {backup.name}")
                        shutil.rmtree(backup)
                        removidos += 1
            except:
                print(f"[AVISO] Nao foi possivel processar: {backup.name}")

    print(f"\n[OK] FASE 3 CONCLUIDA! ({removidos} backups removidos)")

# ==================== FASE 4: LIMPAR CACHE E GRÁFICOS ====================
def fase4_limpar_cache():
    """Limpa cache antigo e gráficos"""
    print("\n" + "="*60)
    print("FASE 4: LIMPEZA DE CACHE E GRÁFICOS ANTIGOS")
    print("="*60)

    hoje = datetime.now()

    # Cache > 7 dias
    cache_dir = BASE_DIR / "data" / "cache"
    if cache_dir.exists():
        limite_cache = hoje - timedelta(days=7)
        removidos = 0
        for cache_file in cache_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if mtime < limite_cache:
                cache_file.unlink()
                removidos += 1
        print(f"[OK] Cache limpo: {removidos} arquivos removidos")

    # Graficos > 30 dias -> archive
    charts_dir = BASE_DIR / "reports" / "charts"
    if charts_dir.exists():
        archive_charts = BASE_DIR / "reports" / "charts_archive"
        archive_charts.mkdir(parents=True, exist_ok=True)

        limite_graficos = hoje - timedelta(days=30)
        arquivados = 0

        for chart in charts_dir.glob("grafico_*.png"):
            mtime = datetime.fromtimestamp(chart.stat().st_mtime)
            if mtime < limite_graficos:
                destino = archive_charts / chart.name
                shutil.move(str(chart), str(destino))
                arquivados += 1

        for chart in charts_dir.glob("grafico_*.html"):
            mtime = datetime.fromtimestamp(chart.stat().st_mtime)
            if mtime < limite_graficos:
                destino = archive_charts / chart.name
                shutil.move(str(chart), str(destino))
                arquivados += 1

        print(f"[OK] Graficos arquivados: {arquivados} arquivos")

    # Cache agent graph
    cache_graph_dir = BASE_DIR / "data" / "cache_agent_graph"
    if cache_graph_dir.exists():
        removidos = 0
        for cache_file in cache_graph_dir.glob("*.pkl"):
            cache_file.unlink()
            removidos += 1
        print(f"[OK] Cache LangGraph limpo: {removidos} arquivos")

    print("\n[OK] FASE 4 CONCLUIDA!")

# ==================== EXECUTAR TODAS AS FASES ====================
def executar_todas():
    """Executa todas as fases de limpeza"""
    print("\n" + "="*70)
    print("INICIANDO LIMPEZA COMPLETA DO PROJETO")
    print("="*70)

    try:
        fase1_limpar_temporarios()
        fase2_remover_duplicados()
        fase3_limpar_backups()
        fase4_limpar_cache()

        print("\n" + "="*70)
        print("LIMPEZA COMPLETA FINALIZADA COM SUCESSO!")
        print("="*70)
        print("\nResumo:")
        print("  - Arquivos temporarios organizados")
        print("  - Codigo duplicado arquivado")
        print("  - Backups antigos removidos")
        print("  - Cache e graficos limpos")
        print("\nBackups criados em: backups/pre_limpeza_*")

    except Exception as e:
        print(f"\nERRO: {e}")
        print("Os backups foram criados e podem ser restaurados.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        fase = sys.argv[1]
        if fase == "1":
            fase1_limpar_temporarios()
        elif fase == "2":
            fase2_remover_duplicados()
        elif fase == "3":
            fase3_limpar_backups()
        elif fase == "4":
            fase4_limpar_cache()
        else:
            print("Uso: python limpar_projeto.py [1|2|3|4]")
    else:
        # Executar todas as fases
        executar_todas()
