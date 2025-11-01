"""
Script de Análise de Métricas Diárias
Analisa logs existentes para calcular métricas de performance
Data: 30/10/2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any

# Adicionar raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def load_jsonl(filepath: Path) -> List[Dict]:
    """Carrega arquivo JSONL"""
    if not filepath.exists():
        return []

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data


def load_json(filepath: Path) -> Dict:
    """Carrega arquivo JSON"""
    if not filepath.exists():
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_date(date_str: str) -> Dict[str, Any]:
    """
    Analisa métricas de uma data específica

    Args:
        date_str: Data no formato YYYYMMDD (ex: "20251030")

    Returns:
        Dicionário com métricas calculadas
    """
    data_dir = ROOT_DIR / "data"

    # Arquivos da data
    error_log = data_dir / "learning" / f"error_log_{date_str}.jsonl"
    query_history = data_dir / "query_history" / f"history_{date_str}.json"
    error_counts = data_dir / "learning" / f"error_counts_{date_str}.json"
    successful_queries = data_dir / "learning" / f"successful_queries_{date_str}.jsonl"

    # Carregar dados
    errors = load_jsonl(error_log)
    queries = load_json(query_history)
    counts = load_json(error_counts)
    successes = load_jsonl(successful_queries)

    # Calcular métricas
    total_queries = len(queries.get("queries", []))
    total_errors = len(errors)
    total_successes = len(successes)

    # Taxa de erro
    error_rate = (total_errors / total_queries * 100) if total_queries > 0 else 0
    success_rate = 100 - error_rate

    # Tipos de erro
    error_types = Counter(e.get("error_type", "Unknown") for e in errors)

    # Tempo médio (se disponível)
    execution_times = [
        q.get("execution_time", 0)
        for q in queries.get("queries", [])
        if q.get("execution_time")
    ]
    avg_time = sum(execution_times) / len(execution_times) if execution_times else 0

    # Queries mais comuns
    query_texts = [q.get("query", "") for q in queries.get("queries", [])]
    common_queries = Counter(query_texts).most_common(5)

    return {
        "date": date_str,
        "total_queries": total_queries,
        "total_errors": total_errors,
        "total_successes": total_successes,
        "error_rate": error_rate,
        "success_rate": success_rate,
        "avg_execution_time": avg_time,
        "error_types": dict(error_types.most_common(5)),
        "common_queries": common_queries,
        "raw_data": {
            "errors_file": str(error_log),
            "queries_file": str(query_history),
            "counts_file": str(error_counts),
        }
    }


def compare_dates(date1: str, date2: str) -> Dict[str, Any]:
    """Compara métricas entre duas datas"""
    metrics1 = analyze_date(date1)
    metrics2 = analyze_date(date2)

    # Calcular variações
    error_rate_change = metrics2["error_rate"] - metrics1["error_rate"]
    success_rate_change = metrics2["success_rate"] - metrics1["success_rate"]
    time_change = metrics2["avg_execution_time"] - metrics1["avg_execution_time"]

    return {
        "date_before": date1,
        "date_after": date2,
        "improvements": {
            "error_rate": {
                "before": metrics1["error_rate"],
                "after": metrics2["error_rate"],
                "change": error_rate_change,
                "change_pct": (error_rate_change / metrics1["error_rate"] * 100) if metrics1["error_rate"] > 0 else 0
            },
            "success_rate": {
                "before": metrics1["success_rate"],
                "after": metrics2["success_rate"],
                "change": success_rate_change,
                "change_pct": (success_rate_change / metrics1["success_rate"] * 100) if metrics1["success_rate"] > 0 else 0
            },
            "avg_time": {
                "before": metrics1["avg_execution_time"],
                "after": metrics2["avg_execution_time"],
                "change": time_change,
                "change_pct": (time_change / metrics1["avg_execution_time"] * 100) if metrics1["avg_execution_time"] > 0 else 0
            }
        },
        "metrics_before": metrics1,
        "metrics_after": metrics2
    }


def print_report(metrics: Dict[str, Any]):
    """Imprime relatório formatado"""
    print("="*80)
    print(f"ANALISE DE METRICAS - {metrics['date']}")
    print("="*80)
    print()

    print("RESUMO GERAL")
    print("-"*80)
    print(f"  Total de Queries: {metrics['total_queries']}")
    print(f"  Sucessos: {metrics['total_successes']} ({metrics['success_rate']:.1f}%)")
    print(f"  Erros: {metrics['total_errors']} ({metrics['error_rate']:.1f}%)")
    print(f"  Tempo Medio: {metrics['avg_execution_time']:.2f}s")
    print()

    if metrics['error_types']:
        print("ERROS MAIS COMUNS")
        print("-"*80)
        for error_type, count in metrics['error_types'].items():
            pct = (count / metrics['total_errors'] * 100) if metrics['total_errors'] > 0 else 0
            print(f"  {error_type}: {count} ({pct:.1f}%)")
        print()

    if metrics['common_queries']:
        print("QUERIES MAIS COMUNS")
        print("-"*80)
        for query, count in metrics['common_queries']:
            if query:  # Ignorar vazias
                print(f"  [{count}x] {query[:60]}...")
        print()

    print("ARQUIVOS ANALISADOS")
    print("-"*80)
    for key, filepath in metrics['raw_data'].items():
        exists = "[OK]" if Path(filepath).exists() else "[MISSING]"
        print(f"  {exists} {filepath}")
    print()
    print("="*80)


def print_comparison(comparison: Dict[str, Any]):
    """Imprime relatório de comparação"""
    print("="*80)
    print(f"COMPARACAO: {comparison['date_before']} vs {comparison['date_after']}")
    print("="*80)
    print()

    improvements = comparison['improvements']

    print("MELHORIAS")
    print("-"*80)

    # Taxa de erro
    err = improvements['error_rate']
    arrow = "↓" if err['change'] < 0 else "↑"
    status = "[OK]" if err['change'] < 0 else "[WARN]"
    print(f"  {status} Taxa de Erro: {err['before']:.1f}% → {err['after']:.1f}% ({arrow}{abs(err['change']):.1f}pp)")

    # Taxa de sucesso
    suc = improvements['success_rate']
    arrow = "↑" if suc['change'] > 0 else "↓"
    status = "[OK]" if suc['change'] > 0 else "[WARN]"
    print(f"  {status} Taxa de Sucesso: {suc['before']:.1f}% → {suc['after']:.1f}% ({arrow}{abs(suc['change']):.1f}pp)")

    # Tempo médio
    time = improvements['avg_time']
    if time['before'] > 0:
        arrow = "↓" if time['change'] < 0 else "↑"
        status = "[OK]" if time['change'] < 0 else "[WARN]"
        print(f"  {status} Tempo Medio: {time['before']:.2f}s → {time['after']:.2f}s ({arrow}{abs(time['change']):.2f}s)")

    print()
    print("="*80)


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Analisa métricas diárias do sistema")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"),
                       help="Data para análise (YYYYMMDD)")
    parser.add_argument("--compare", help="Data para comparar (YYYYMMDD)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")

    args = parser.parse_args()

    try:
        if args.compare:
            # Modo comparação
            comparison = compare_dates(args.compare, args.date)

            if args.json:
                print(json.dumps(comparison, indent=2, ensure_ascii=False))
            else:
                print_comparison(comparison)
        else:
            # Modo análise simples
            metrics = analyze_date(args.date)

            if args.json:
                print(json.dumps(metrics, indent=2, ensure_ascii=False))
            else:
                print_report(metrics)

        return 0

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
