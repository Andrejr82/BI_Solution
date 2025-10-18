"""
Preview de Limpeza - Agent_Solution_BI
Mostra o que será removido SEM executar a limpeza

Deploy Agent - 2025-10-17
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent
CACHE_RETENTION_DAYS = 3

def format_size(bytes: int) -> str:
    """Formata tamanho em bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def get_file_age_days(file_path: Path) -> int:
    """Retorna idade do arquivo em dias"""
    if not file_path.exists():
        return 0
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return (datetime.now() - mtime).days

def preview_temp_files() -> Dict:
    """Preview de arquivos temporários"""
    result = {
        "category": "Arquivos Temporários",
        "files": [],
        "total_size": 0
    }

    temp_patterns = ["temp_*.py", "tmp_*.py", "scratch_*.py"]

    for pattern in temp_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.is_file():
                size = file_path.stat().st_size
                result["files"].append({
                    "name": file_path.name,
                    "size": size,
                    "age_days": get_file_age_days(file_path)
                })
                result["total_size"] += size

    # Adicionar temp_read_transferencias.py explicitamente
    temp_file = PROJECT_ROOT / "temp_read_transferencias.py"
    if temp_file.exists():
        size = temp_file.stat().st_size
        result["files"].append({
            "name": temp_file.name,
            "size": size,
            "age_days": get_file_age_days(temp_file)
        })
        result["total_size"] += size

    return result

def preview_cache(cache_dir: Path, retention_days: int) -> Dict:
    """Preview de limpeza de cache"""
    result = {
        "category": f"Cache - {cache_dir.name}",
        "files_to_remove": [],
        "files_to_keep": [],
        "total_size_to_free": 0,
        "total_size_kept": 0
    }

    if not cache_dir.exists():
        result["warning"] = f"Diretório não existe: {cache_dir}"
        return result

    for file_path in cache_dir.glob("*"):
        if file_path.is_file():
            age_days = get_file_age_days(file_path)
            size = file_path.stat().st_size

            file_info = {
                "name": file_path.name,
                "size": size,
                "age_days": age_days,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            }

            if age_days > retention_days:
                result["files_to_remove"].append(file_info)
                result["total_size_to_free"] += size
            else:
                result["files_to_keep"].append(file_info)
                result["total_size_kept"] += size

    return result

def preview_duplicate_scripts() -> Dict:
    """Preview de scripts duplicados"""
    result = {
        "category": "Scripts Duplicados",
        "files": [],
        "total_size": 0
    }

    scripts_dir = PROJECT_ROOT / "scripts"
    duplicates = [
        scripts_dir / "clear_cache.bat",
        scripts_dir / "limpar_cache.bat"
    ]

    for script in duplicates:
        if script.exists():
            size = script.stat().st_size
            result["files"].append({
                "name": script.name,
                "size": size,
                "reason": "Duplicado - será consolidado em versão única"
            })
            result["total_size"] += size

    return result

def preview_diagnostic_scripts() -> Dict:
    """Preview de scripts de diagnóstico a serem movidos"""
    result = {
        "category": "Scripts de Diagnóstico (a mover)",
        "files": [],
        "destination": "scripts/diagnostics/"
    }

    scripts_dir = PROJECT_ROOT / "scripts"
    diagnostic_scripts = [
        "diagnostico_sugestoes_automaticas.py",
        "diagnostico_transferencias_unes.py",
        "DIAGNOSTICO_TRANSFERENCIAS.bat",
        "analyze_une1_data.py"
    ]

    for script_name in diagnostic_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            result["files"].append({
                "name": script_name,
                "size": script_path.stat().st_size,
                "current": "scripts/",
                "new": "scripts/diagnostics/"
            })

    return result

def print_preview(data: Dict):
    """Imprime preview formatado"""
    print(f"\n{'='*80}")
    print(f"  {data['category']}")
    print(f"{'='*80}")

    if "warning" in data:
        print(f"\n  AVISO: {data['warning']}")
        return

    if "files" in data and data["files"]:
        print(f"\n  Total de arquivos: {len(data['files'])}")
        if data.get("total_size"):
            print(f"  Espaço total: {format_size(data['total_size'])}")

        print(f"\n  Arquivos:")
        for file_info in data["files"][:10]:  # Mostrar primeiros 10
            name = file_info["name"]
            size = format_size(file_info["size"])

            if "age_days" in file_info:
                age = file_info["age_days"]
                print(f"    - {name:<50} {size:>10} ({age} dias)")
            elif "reason" in file_info:
                reason = file_info["reason"]
                print(f"    - {name:<50} {size:>10}")
                print(f"      Razão: {reason}")
            elif "current" in file_info:
                print(f"    - {name:<50} {size:>10}")
                print(f"      {file_info['current']} -> {file_info['new']}")

        if len(data["files"]) > 10:
            print(f"    ... e mais {len(data['files']) - 10} arquivos")

    if "files_to_remove" in data:
        print(f"\n  Arquivos a REMOVER: {len(data['files_to_remove'])}")
        print(f"  Espaço a liberar: {format_size(data['total_size_to_free'])}")

        if data["files_to_remove"]:
            print(f"\n  Primeiros 5 arquivos mais antigos:")
            sorted_files = sorted(data["files_to_remove"], key=lambda x: x["age_days"], reverse=True)
            for file_info in sorted_files[:5]:
                name = file_info["name"][:40]
                size = format_size(file_info["size"])
                age = file_info["age_days"]
                modified = file_info["modified"]
                print(f"    - {name:<40} {size:>10} ({age} dias) - {modified}")

    if "files_to_keep" in data:
        print(f"\n  Arquivos a MANTER: {len(data['files_to_keep'])}")
        print(f"  Espaço mantido: {format_size(data['total_size_kept'])}")

    if "destination" in data:
        print(f"\n  Destino: {data['destination']}")

def main():
    """Função principal"""
    print("\n" + "="*80)
    print("  PREVIEW DE LIMPEZA - AGENT_SOLUTION_BI")
    print("  Mostra o que será removido SEM executar a limpeza")
    print("="*80)
    print(f"\n  Política de retenção: {CACHE_RETENTION_DAYS} dias")
    print(f"  Data atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Arquivos temporários
    temp_preview = preview_temp_files()
    print_preview(temp_preview)

    # 2. Cache data/cache/
    cache_dir = PROJECT_ROOT / "data" / "cache"
    cache_preview = preview_cache(cache_dir, CACHE_RETENTION_DAYS)
    print_preview(cache_preview)

    # 3. Cache data/cache_agent_graph/
    graph_cache_dir = PROJECT_ROOT / "data" / "cache_agent_graph"
    graph_preview = preview_cache(graph_cache_dir, CACHE_RETENTION_DAYS)
    print_preview(graph_preview)

    # 4. Scripts duplicados
    duplicates_preview = preview_duplicate_scripts()
    print_preview(duplicates_preview)

    # 5. Scripts de diagnóstico
    diagnostics_preview = preview_diagnostic_scripts()
    print_preview(diagnostics_preview)

    # Resumo total
    total_files_remove = (
        len(temp_preview["files"]) +
        len(cache_preview["files_to_remove"]) +
        len(graph_preview["files_to_remove"]) +
        len(duplicates_preview["files"])
    )

    total_files_move = len(diagnostics_preview["files"])

    total_space_free = (
        temp_preview["total_size"] +
        cache_preview["total_size_to_free"] +
        graph_preview["total_size_to_free"] +
        duplicates_preview["total_size"]
    )

    print(f"\n{'='*80}")
    print("  RESUMO GERAL")
    print(f"{'='*80}")
    print(f"\n  Total de arquivos a remover: {total_files_remove}")
    print(f"  Total de arquivos a mover: {total_files_move}")
    print(f"  Espaço total a liberar: {format_size(total_space_free)}")

    print(f"\n{'='*80}")
    print("  PRÓXIMOS PASSOS")
    print(f"{'='*80}")
    print("\n  Para executar a limpeza:")
    print("    Windows: EXECUTAR_LIMPEZA.bat")
    print("    Linux/Mac: python cleanup_project.py")
    print("\n  Para limpar apenas cache:")
    print("    python scripts/limpar_cache.py")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
