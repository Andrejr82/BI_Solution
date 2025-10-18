"""
Script de Verificação Pós-Limpeza
Agent_Solution_BI - Deploy Agent
Data: 2025-10-17

Verifica se a limpeza foi executada corretamente e gera relatório de status.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*80}")
    print(f"{Colors.CYAN}  {title}{Colors.END}")
    print(f"{'='*80}\n")

def print_status(item: str, status: bool, details: str = ""):
    """Imprime status com cores"""
    icon = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"  {icon} {item}")
    if details:
        print(f"    {Colors.BLUE}→{Colors.END} {details}")

def check_temp_files() -> Dict:
    """Verifica se arquivos temporários foram removidos"""
    result = {
        "name": "Arquivos Temporários",
        "status": True,
        "issues": [],
        "details": []
    }

    # Verificar temp_read_transferencias.py
    temp_file = PROJECT_ROOT / "temp_read_transferencias.py"
    if temp_file.exists():
        result["status"] = False
        result["issues"].append(f"Arquivo temporário ainda existe: {temp_file.name}")
    else:
        result["details"].append("temp_read_transferencias.py removido")

    # Verificar padrão temp_*.py
    temp_files = list(PROJECT_ROOT.glob("temp_*.py"))
    if temp_files:
        result["status"] = False
        result["issues"].extend([f"Encontrado: {f.name}" for f in temp_files])
    else:
        result["details"].append("Nenhum arquivo temp_*.py encontrado")

    return result

def check_cache_cleaned() -> Dict:
    """Verifica se cache foi limpo corretamente"""
    result = {
        "name": "Limpeza de Cache",
        "status": True,
        "issues": [],
        "details": []
    }

    # Verificar data/cache/
    cache_dir = PROJECT_ROOT / "data" / "cache"
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        result["details"].append(f"Arquivos em data/cache/: {len(cache_files)}")

        # Verificar se há arquivos antigos
        from datetime import timedelta
        old_files = 0
        for f in cache_files:
            age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
            if age_days > 3:
                old_files += 1

        if old_files > 0:
            result["status"] = False
            result["issues"].append(f"{old_files} arquivos com mais de 3 dias encontrados")
        else:
            result["details"].append("Todos os arquivos são recentes (<3 dias)")
    else:
        result["issues"].append("Diretório data/cache/ não existe")

    # Verificar data/cache_agent_graph/
    graph_cache = PROJECT_ROOT / "data" / "cache_agent_graph"
    if graph_cache.exists():
        graph_files = list(graph_cache.glob("*.pkl"))
        result["details"].append(f"Arquivos em data/cache_agent_graph/: {len(graph_files)}")
    else:
        result["issues"].append("Diretório data/cache_agent_graph/ não existe")

    return result

def check_scripts_consolidated() -> Dict:
    """Verifica se scripts foram consolidados"""
    result = {
        "name": "Consolidação de Scripts",
        "status": True,
        "issues": [],
        "details": []
    }

    scripts_dir = PROJECT_ROOT / "scripts"

    # Verificar se duplicados foram removidos
    duplicates = [
        scripts_dir / "clear_cache.bat",
        PROJECT_ROOT / "clear_cache.bat"
    ]

    for dup in duplicates:
        if dup.exists():
            result["status"] = False
            result["issues"].append(f"Script duplicado ainda existe: {dup.name}")

    # Verificar se versões consolidadas existem
    required = [
        scripts_dir / "limpar_cache.py",
        scripts_dir / "limpar_cache.bat"
    ]

    for req in required:
        if req.exists():
            result["details"].append(f"Script consolidado OK: {req.name}")
        else:
            result["status"] = False
            result["issues"].append(f"Script consolidado não encontrado: {req.name}")

    return result

def check_diagnostics_organized() -> Dict:
    """Verifica se scripts de diagnóstico foram organizados"""
    result = {
        "name": "Organização de Diagnósticos",
        "status": True,
        "issues": [],
        "details": []
    }

    scripts_dir = PROJECT_ROOT / "scripts"
    diagnostics_dir = scripts_dir / "diagnostics"

    # Verificar se diretório foi criado
    if diagnostics_dir.exists():
        result["details"].append("Diretório scripts/diagnostics/ criado")

        # Verificar scripts movidos
        expected_scripts = [
            "diagnostico_sugestoes_automaticas.py",
            "diagnostico_transferencias_unes.py",
            "DIAGNOSTICO_TRANSFERENCIAS.bat",
            "analyze_une1_data.py",
            "README.md"
        ]

        for script in expected_scripts:
            if (diagnostics_dir / script).exists():
                result["details"].append(f"Script OK: {script}")
            else:
                result["status"] = False
                result["issues"].append(f"Script não encontrado: {script}")

        # Verificar se ainda existem na raiz de scripts/
        for script in expected_scripts[:-1]:  # Excluir README
            if (scripts_dir / script).exists():
                result["status"] = False
                result["issues"].append(f"Script não foi movido: {script}")
    else:
        result["status"] = False
        result["issues"].append("Diretório scripts/diagnostics/ não foi criado")

    return result

def check_backup_created() -> Dict:
    """Verifica se backup foi criado"""
    result = {
        "name": "Backup de Arquivos",
        "status": True,
        "issues": [],
        "details": []
    }

    backup_dir = PROJECT_ROOT / "backup_cleanup"

    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*"))
        result["details"].append(f"Diretório de backup criado com {len(backup_files)} arquivos")

        if len(backup_files) == 0:
            result["issues"].append("Backup criado mas vazio (pode ser normal se não havia o que deletar)")
    else:
        result["issues"].append("Diretório de backup não foi criado (pode ser normal se limpeza não foi executada)")

    return result

def check_documentation_created() -> Dict:
    """Verifica se documentação foi criada"""
    result = {
        "name": "Documentação de Limpeza",
        "status": True,
        "issues": [],
        "details": []
    }

    docs = [
        "cleanup_project.py",
        "EXECUTAR_LIMPEZA.bat",
        "preview_cleanup.py",
        "verify_cleanup.py",
        "LIMPEZA_README.md",
        "GIT_CLEANUP_INSTRUCTIONS.md",
        "SUMARIO_LIMPEZA.md"
    ]

    for doc in docs:
        doc_path = PROJECT_ROOT / doc
        if doc_path.exists():
            result["details"].append(f"Arquivo criado: {doc}")
        else:
            result["status"] = False
            result["issues"].append(f"Arquivo não encontrado: {doc}")

    return result

def check_git_status() -> Dict:
    """Verifica status do Git"""
    result = {
        "name": "Status Git",
        "status": True,
        "issues": [],
        "details": []
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
            lines = git_result.stdout.strip().split('\n') if git_result.stdout.strip() else []

            deleted_files = [l for l in lines if l.startswith(' D ')]
            modified_files = [l for l in lines if l.startswith(' M ')]
            new_files = [l for l in lines if l.startswith('??')]

            result["details"].append(f"Arquivos deletados (staged): {len([l for l in lines if l.startswith('D ')])}")
            result["details"].append(f"Arquivos deletados (unstaged): {len(deleted_files)}")
            result["details"].append(f"Arquivos modificados: {len(modified_files)}")
            result["details"].append(f"Arquivos novos: {len(new_files)}")

            if deleted_files:
                result["issues"].append(f"{len(deleted_files)} arquivos deletados não staged")
            if new_files:
                result["issues"].append(f"{len(new_files)} arquivos novos não tracked")

    except Exception as e:
        result["issues"].append(f"Erro ao verificar Git: {e}")

    return result

def generate_verification_report(checks: List[Dict]) -> str:
    """Gera relatório de verificação"""
    passed = sum(1 for c in checks if c["status"])
    total = len(checks)

    report = f"""
{'='*80}
RELATÓRIO DE VERIFICAÇÃO PÓS-LIMPEZA
{'='*80}
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projeto: Agent_Solution_BI
Deploy Agent

RESUMO:
{'-'*80}
Status Geral: {passed}/{total} verificações passaram
Taxa de Sucesso: {(passed/total*100):.1f}%

DETALHES:
{'-'*80}
"""

    for check in checks:
        status_icon = "✓ PASSOU" if check["status"] else "✗ FALHOU"
        report += f"\n{check['name']}: {status_icon}\n"

        if check["details"]:
            report += "  Detalhes:\n"
            for detail in check["details"]:
                report += f"    • {detail}\n"

        if check["issues"]:
            report += "  Issues:\n"
            for issue in check["issues"]:
                report += f"    ! {issue}\n"

    report += f"\n{'='*80}\n"

    if passed == total:
        report += "✓ VERIFICAÇÃO COMPLETA: Todas as verificações passaram!\n"
        report += "\nPróximos passos:\n"
        report += "  1. Revisar mudanças: git status\n"
        report += "  2. Commit: git commit -m 'chore: Limpeza automatizada'\n"
        report += "  3. Push: git push origin main\n"
    else:
        report += "! ATENÇÃO: Algumas verificações falharam.\n"
        report += "\nRecomendações:\n"
        report += "  1. Revisar issues acima\n"
        report += "  2. Executar limpeza novamente se necessário\n"
        report += "  3. Verificar logs em .cleanup_report.json\n"

    report += f"{'='*80}\n"

    return report

def main():
    """Função principal"""
    print_header("VERIFICAÇÃO PÓS-LIMPEZA - AGENT_SOLUTION_BI")

    checks = []

    # Executar verificações
    print(f"{Colors.CYAN}Executando verificações...{Colors.END}\n")

    print(f"{Colors.BLUE}[1/7]{Colors.END} Verificando arquivos temporários...")
    result = check_temp_files()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[2/7]{Colors.END} Verificando limpeza de cache...")
    result = check_cache_cleaned()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[3/7]{Colors.END} Verificando consolidação de scripts...")
    result = check_scripts_consolidated()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[4/7]{Colors.END} Verificando organização de diagnósticos...")
    result = check_diagnostics_organized()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[5/7]{Colors.END} Verificando backup...")
    result = check_backup_created()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[6/7]{Colors.END} Verificando documentação...")
    result = check_documentation_created()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    print(f"{Colors.BLUE}[7/7]{Colors.END} Verificando status Git...")
    result = check_git_status()
    checks.append(result)
    print_status(result["name"], result["status"],
                 f"{len(result['details'])} checks OK, {len(result['issues'])} issues")

    # Gerar relatório
    report = generate_verification_report(checks)
    print(report)

    # Salvar relatório JSON
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "project": "Agent_Solution_BI",
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c["status"]),
            "failed": sum(1 for c in checks if not c["status"]),
            "success_rate": round(sum(1 for c in checks if c["status"]) / len(checks) * 100, 1)
        }
    }

    report_file = PROJECT_ROOT / ".verification_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Relatório JSON salvo em: {report_file}\n")

    return 0 if all(c["status"] for c in checks) else 1

if __name__ == "__main__":
    exit(main())
