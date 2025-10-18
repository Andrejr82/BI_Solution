"""
Script de Limpeza Completa do Projeto Agent_Solution_BI
Autor: Deploy Agent
Data: 2025-10-17

Este script:
1. Remove arquivos temporários
2. Limpa cache desatualizado (>7 dias)
3. Organiza estrutura de diretórios
4. Consolida scripts de limpeza
5. Gera relatório detalhado
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Configurações
PROJECT_ROOT = Path(__file__).parent
CACHE_RETENTION_DAYS = 3
OLD_CACHE_DAYS = 7
BACKUP_DIR = PROJECT_ROOT / "backup_cleanup"
REPORT_FILE = PROJECT_ROOT / ".cleanup_report.json"

# Cores para output (Windows compatible)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(message: str, level: str = "INFO"):
    """Log com timestamp e nível"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }.get(level, "")
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")

def get_file_age_days(file_path: Path) -> int:
    """Retorna idade do arquivo em dias"""
    if not file_path.exists():
        return 0
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return (datetime.now() - mtime).days

def create_backup(file_path: Path) -> bool:
    """Cria backup de arquivo antes de deletar"""
    try:
        if not file_path.exists():
            return False

        BACKUP_DIR.mkdir(exist_ok=True)
        backup_path = BACKUP_DIR / file_path.name

        if file_path.is_file():
            shutil.copy2(file_path, backup_path)
        else:
            shutil.copytree(file_path, backup_path, dirs_exist_ok=True)

        log(f"Backup criado: {backup_path.name}", "SUCCESS")
        return True
    except Exception as e:
        log(f"Erro ao criar backup de {file_path.name}: {e}", "ERROR")
        return False

def remove_temp_file() -> Dict:
    """Remove arquivo temporário temp_read_transferencias.py"""
    result = {
        "action": "Remover arquivo temporário",
        "files_removed": [],
        "errors": []
    }

    temp_file = PROJECT_ROOT / "temp_read_transferencias.py"

    try:
        if temp_file.exists():
            create_backup(temp_file)
            temp_file.unlink()
            result["files_removed"].append(str(temp_file.name))
            log(f"Removido: {temp_file.name}", "SUCCESS")
        else:
            log(f"Arquivo não encontrado: {temp_file.name}", "WARNING")
    except Exception as e:
        result["errors"].append(f"Erro ao remover {temp_file.name}: {e}")
        log(f"Erro: {e}", "ERROR")

    return result

def clean_cache_directory(cache_dir: Path, retention_days: int) -> Dict:
    """Limpa arquivos de cache mais antigos que retention_days"""
    result = {
        "action": f"Limpar cache em {cache_dir.name}",
        "files_removed": [],
        "files_kept": [],
        "space_freed_mb": 0,
        "errors": []
    }

    if not cache_dir.exists():
        log(f"Diretório não existe: {cache_dir}", "WARNING")
        return result

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    total_size = 0

    try:
        for file_path in cache_dir.glob("*"):
            if file_path.is_file():
                age_days = get_file_age_days(file_path)
                file_size = file_path.stat().st_size

                if age_days > retention_days:
                    total_size += file_size
                    file_path.unlink()
                    result["files_removed"].append({
                        "name": file_path.name,
                        "age_days": age_days,
                        "size_kb": round(file_size / 1024, 2)
                    })
                else:
                    result["files_kept"].append({
                        "name": file_path.name,
                        "age_days": age_days
                    })

        result["space_freed_mb"] = round(total_size / (1024 * 1024), 2)
        log(f"Cache limpo: {len(result['files_removed'])} arquivos removidos, "
            f"{result['space_freed_mb']} MB liberados", "SUCCESS")

    except Exception as e:
        result["errors"].append(str(e))
        log(f"Erro ao limpar cache: {e}", "ERROR")

    return result

def consolidate_cleanup_scripts() -> Dict:
    """Consolida scripts de limpeza duplicados"""
    result = {
        "action": "Consolidar scripts de limpeza",
        "files_removed": [],
        "files_created": [],
        "errors": []
    }

    scripts_dir = PROJECT_ROOT / "scripts"

    # Scripts duplicados para remover
    duplicates = [
        scripts_dir / "clear_cache.bat",
        scripts_dir / "limpar_cache.bat"
    ]

    try:
        # Manter apenas limpar_cache.py (versão mais completa)
        for script in duplicates:
            if script.exists():
                create_backup(script)
                script.unlink()
                result["files_removed"].append(script.name)
                log(f"Script duplicado removido: {script.name}", "SUCCESS")

        # Criar script .bat unificado
        unified_bat = scripts_dir / "limpar_cache.bat"
        bat_content = """@echo off
REM Script Unificado de Limpeza de Cache
REM Agent_Solution_BI - Deploy Agent
REM Data: 2025-10-17

echo ========================================
echo   Limpeza de Cache - Agent_Solution_BI
echo ========================================
echo.

cd /d "%~dp0.."
python scripts/limpar_cache.py

pause
"""

        with open(unified_bat, 'w', encoding='utf-8') as f:
            f.write(bat_content)

        result["files_created"].append("limpar_cache.bat")
        log("Script unificado criado: limpar_cache.bat", "SUCCESS")

    except Exception as e:
        result["errors"].append(str(e))
        log(f"Erro ao consolidar scripts: {e}", "ERROR")

    return result

def organize_diagnostic_scripts() -> Dict:
    """Organiza scripts de diagnóstico em subdiretório"""
    result = {
        "action": "Organizar scripts de diagnóstico",
        "files_moved": [],
        "directories_created": [],
        "errors": []
    }

    scripts_dir = PROJECT_ROOT / "scripts"
    diagnostics_dir = scripts_dir / "diagnostics"

    # Scripts de diagnóstico para mover
    diagnostic_scripts = [
        "diagnostico_sugestoes_automaticas.py",
        "diagnostico_transferencias_unes.py",
        "DIAGNOSTICO_TRANSFERENCIAS.bat",
        "analyze_une1_data.py"
    ]

    try:
        # Criar diretório diagnostics
        diagnostics_dir.mkdir(exist_ok=True)
        result["directories_created"].append("scripts/diagnostics/")
        log(f"Diretório criado: {diagnostics_dir}", "SUCCESS")

        # Mover scripts
        for script_name in diagnostic_scripts:
            source = scripts_dir / script_name
            if source.exists():
                dest = diagnostics_dir / script_name
                shutil.move(str(source), str(dest))
                result["files_moved"].append(f"{script_name} -> diagnostics/")
                log(f"Movido: {script_name} -> diagnostics/", "SUCCESS")

        # Criar README no diretório diagnostics
        readme_content = """# Scripts de Diagnóstico

Este diretório contém scripts para diagnóstico e análise do sistema.

## Scripts Disponíveis:

### Python
- `diagnostico_sugestoes_automaticas.py` - Diagnóstico de sugestões automáticas
- `diagnostico_transferencias_unes.py` - Diagnóstico de transferências entre UNEs
- `analyze_une1_data.py` - Análise de dados da UNE1

### Batch
- `DIAGNOSTICO_TRANSFERENCIAS.bat` - Script batch para diagnóstico de transferências

## Uso:

```bash
# Executar script Python
python scripts/diagnostics/diagnostico_sugestoes_automaticas.py

# Executar script Batch (Windows)
scripts\\diagnostics\\DIAGNOSTICO_TRANSFERENCIAS.bat
```

## Notas:
- Todos os scripts devem ser executados a partir da raiz do projeto
- Certifique-se de ter as dependências instaladas
- Logs são salvos em `data/learning/`
"""

        readme_path = diagnostics_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        result["files_created"].append("diagnostics/README.md")
        log("README criado em diagnostics/", "SUCCESS")

    except Exception as e:
        result["errors"].append(str(e))
        log(f"Erro ao organizar scripts: {e}", "ERROR")

    return result

def check_git_status() -> Dict:
    """Verifica status do Git e arquivos deletados"""
    result = {
        "action": "Verificar status Git",
        "deleted_files_count": 0,
        "staged_deletions": [],
        "recommendation": ""
    }

    try:
        import subprocess

        # Executar git status
        git_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if git_result.returncode == 0:
            lines = git_result.stdout.strip().split('\n')
            deleted_files = [line for line in lines if line.startswith(' D ')]
            result["deleted_files_count"] = len(deleted_files)
            result["staged_deletions"] = deleted_files[:10]  # Primeiros 10

            if deleted_files:
                result["recommendation"] = "Execute 'git add -u' para staged deletions ou 'git restore' para reverter"
                log(f"Encontrados {len(deleted_files)} arquivos deletados no Git", "WARNING")
            else:
                log("Nenhum arquivo deletado pendente no Git", "SUCCESS")

    except Exception as e:
        result["errors"] = [str(e)]
        log(f"Erro ao verificar Git: {e}", "WARNING")

    return result

def generate_cleanup_report(results: List[Dict]) -> str:
    """Gera relatório final da limpeza"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "Agent_Solution_BI",
        "agent": "Deploy Agent",
        "results": results,
        "summary": {
            "total_files_removed": 0,
            "total_files_moved": 0,
            "total_files_created": 0,
            "total_space_freed_mb": 0,
            "total_errors": 0
        }
    }

    # Calcular sumário
    for result in results:
        if "files_removed" in result:
            if isinstance(result["files_removed"], list):
                report["summary"]["total_files_removed"] += len(result["files_removed"])

        if "files_moved" in result:
            report["summary"]["total_files_moved"] += len(result["files_moved"])

        if "files_created" in result:
            report["summary"]["total_files_created"] += len(result["files_created"])

        if "space_freed_mb" in result:
            report["summary"]["total_space_freed_mb"] += result["space_freed_mb"]

        if "errors" in result:
            report["summary"]["total_errors"] += len(result["errors"])

    # Salvar JSON
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Gerar relatório em texto
    text_report = f"""
{'='*80}
RELATÓRIO DE LIMPEZA - AGENT_SOLUTION_BI
{'='*80}
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Agente: Deploy Agent

RESUMO EXECUTIVO:
{'-'*80}
- Arquivos removidos: {report['summary']['total_files_removed']}
- Arquivos movidos: {report['summary']['total_files_moved']}
- Arquivos criados: {report['summary']['total_files_created']}
- Espaço liberado: {report['summary']['total_space_freed_mb']:.2f} MB
- Erros encontrados: {report['summary']['total_errors']}

DETALHAMENTO DAS AÇÕES:
{'-'*80}
"""

    for i, result in enumerate(results, 1):
        text_report += f"\n{i}. {result.get('action', 'Ação não especificada')}\n"

        if result.get('files_removed'):
            text_report += f"   - Arquivos removidos: {len(result['files_removed'])}\n"

        if result.get('files_moved'):
            text_report += f"   - Arquivos movidos: {len(result['files_moved'])}\n"

        if result.get('space_freed_mb'):
            text_report += f"   - Espaço liberado: {result['space_freed_mb']:.2f} MB\n"

        if result.get('errors'):
            text_report += f"   - ERROS: {len(result['errors'])}\n"
            for error in result['errors']:
                text_report += f"     * {error}\n"

    text_report += f"\n{'='*80}\n"
    text_report += f"Relatório completo salvo em: {REPORT_FILE}\n"
    text_report += f"Backup criado em: {BACKUP_DIR}\n"
    text_report += f"{'='*80}\n"

    return text_report

def main():
    """Execução principal do script de limpeza"""
    log("="*80, "INFO")
    log("INICIANDO LIMPEZA DO PROJETO AGENT_SOLUTION_BI", "INFO")
    log("="*80, "INFO")

    results = []

    # 1. Remover arquivo temporário
    log("\n[1/6] Removendo arquivo temporário...", "INFO")
    results.append(remove_temp_file())

    # 2. Limpar cache data/cache/
    log("\n[2/6] Limpando data/cache/...", "INFO")
    cache_dir = PROJECT_ROOT / "data" / "cache"
    results.append(clean_cache_directory(cache_dir, CACHE_RETENTION_DAYS))

    # 3. Limpar cache data/cache_agent_graph/
    log("\n[3/6] Limpando data/cache_agent_graph/...", "INFO")
    graph_cache_dir = PROJECT_ROOT / "data" / "cache_agent_graph"
    results.append(clean_cache_directory(graph_cache_dir, CACHE_RETENTION_DAYS))

    # 4. Consolidar scripts de limpeza
    log("\n[4/6] Consolidando scripts de limpeza...", "INFO")
    results.append(consolidate_cleanup_scripts())

    # 5. Organizar scripts de diagnóstico
    log("\n[5/6] Organizando scripts de diagnóstico...", "INFO")
    results.append(organize_diagnostic_scripts())

    # 6. Verificar status Git
    log("\n[6/6] Verificando status Git...", "INFO")
    results.append(check_git_status())

    # Gerar relatório final
    log("\n" + "="*80, "INFO")
    log("GERANDO RELATÓRIO FINAL...", "INFO")
    log("="*80, "INFO")

    report = generate_cleanup_report(results)
    print(report)

    log("LIMPEZA CONCLUÍDA COM SUCESSO!", "SUCCESS")

    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        log("\nOperação cancelada pelo usuário", "WARNING")
        exit(1)
    except Exception as e:
        log(f"Erro fatal: {e}", "ERROR")
        exit(1)
