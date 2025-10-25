"""
Script para analisar todas as tabelas Parquet do projeto.
Objetivo: Classificar tabelas por engine recomendada (Polars vs Dask).

Autor: Claude Code
Data: 2025-10-20
"""

import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

# Adicionar path do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def get_file_size_mb(file_path: str) -> float:
    """Retorna tamanho do arquivo em MB."""
    return os.path.getsize(file_path) / (1024 ** 2)

def count_parquet_rows(file_path: str) -> int:
    """Conta linhas do arquivo Parquet usando Polars (rápido)."""
    try:
        import polars as pl
        return pl.scan_parquet(file_path).select(pl.len()).collect().item()
    except ImportError:
        # Fallback para PyArrow se Polars não instalado
        import pyarrow.parquet as pq
        return pq.read_table(file_path).num_rows
    except Exception as e:
        print(f"⚠️  Erro ao contar linhas de {file_path}: {e}")
        return -1

def count_parquet_columns(file_path: str) -> int:
    """Conta colunas do arquivo Parquet."""
    try:
        import polars as pl
        return len(pl.scan_parquet(file_path).collect_schema())
    except ImportError:
        import pyarrow.parquet as pq
        return len(pq.read_schema(file_path))
    except Exception as e:
        print(f"⚠️  Erro ao contar colunas de {file_path}: {e}")
        return -1

def analyze_all_tables(parquet_dir: str, threshold_mb: int = 500):
    """
    Analisa todas as tabelas Parquet em um diretório.

    Args:
        parquet_dir: Diretório contendo arquivos .parquet
        threshold_mb: Threshold em MB para escolher Polars vs Dask

    Returns:
        dict: Relatório completo da análise
    """
    print("=" * 70)
    print("ANALISE DE TABELAS PARQUET - HYBRID ADAPTER")
    print("=" * 70)
    print(f"Diretorio: {parquet_dir}")
    print(f"Threshold Polars/Dask: {threshold_mb} MB")
    print()

    # Encontrar todos os arquivos .parquet
    pattern = os.path.join(parquet_dir, "*.parquet")
    parquet_files = glob.glob(pattern)

    if not parquet_files:
        print(f"ERRO: Nenhum arquivo .parquet encontrado em {parquet_dir}")
        return None

    print(f"OK: Encontrados {len(parquet_files)} arquivo(s) Parquet\n")

    # Analisar cada arquivo
    tables = []
    total_size_mb = 0
    total_rows = 0
    polars_count = 0
    dask_count = 0

    for file_path in sorted(parquet_files):
        filename = os.path.basename(file_path)
        print(f"Analisando: {filename}...")

        size_mb = get_file_size_mb(file_path)
        rows = count_parquet_rows(file_path)
        columns = count_parquet_columns(file_path)

        # Decidir engine recomendada
        engine = "polars" if size_mb < threshold_mb else "dask"

        if engine == "polars":
            polars_count += 1
        else:
            dask_count += 1

        total_size_mb += size_mb
        total_rows += rows if rows > 0 else 0

        table_info = {
            "name": filename,
            "path": file_path,
            "size_mb": round(size_mb, 2),
            "rows": rows,
            "columns": columns,
            "engine_recommended": engine,
            "reason": f"Tamanho {size_mb:.1f}MB {'<' if engine == 'polars' else '>='} {threshold_mb}MB"
        }

        tables.append(table_info)

        # Print linha por linha
        engine_icon = "[P]" if engine == "polars" else "[D]"
        print(f"   {engine_icon} {engine.upper():6} | {size_mb:7.1f} MB | {rows:,} linhas | {columns} colunas")

    # Gerar relatório final
    report = {
        "timestamp": datetime.now().isoformat(),
        "parquet_dir": parquet_dir,
        "threshold_mb": threshold_mb,
        "summary": {
            "total_tables": len(tables),
            "total_size_mb": round(total_size_mb, 2),
            "total_size_gb": round(total_size_mb / 1024, 2),
            "total_rows": total_rows,
            "polars_recommended": polars_count,
            "dask_recommended": dask_count,
            "polars_percentage": round(100 * polars_count / len(tables), 1) if tables else 0
        },
        "tables": tables
    }

    # Print sumário
    print()
    print("=" * 70)
    print("SUMARIO DA ANALISE")
    print("=" * 70)
    print(f"Total de tabelas:         {report['summary']['total_tables']}")
    print(f"Tamanho total:            {report['summary']['total_size_gb']:.2f} GB ({report['summary']['total_size_mb']:.0f} MB)")
    print(f"Total de linhas:          {report['summary']['total_rows']:,}")
    print()
    print(f"[P] Polars recomendado:   {report['summary']['polars_recommended']} tabelas ({report['summary']['polars_percentage']}%)")
    print(f"[D] Dask recomendado:     {report['summary']['dask_recommended']} tabelas ({100 - report['summary']['polars_percentage']:.1f}%)")
    print()

    # Calcular ganho estimado
    polars_speedup = 8.1  # Do benchmark
    avg_speedup = (polars_count * polars_speedup + dask_count * 1.0) / len(tables) if tables else 1.0
    print(f">> Ganho estimado medio:  {avg_speedup:.1f}x mais rapido")
    print()

    # Recomendação
    if report['summary']['polars_percentage'] >= 80:
        recommendation = "OK: EXCELENTE para arquitetura hibrida! Maioria das queries sera rapida com Polars."
    elif report['summary']['polars_percentage'] >= 50:
        recommendation = "OK: BOM para arquitetura hibrida. Ganho significativo com Polars."
    else:
        recommendation = "AVISO: Muitas tabelas grandes. Considere aumentar threshold ou usar apenas Dask."

    print(f"Recomendacao: {recommendation}")
    print("=" * 70)

    return report

def save_report(report: dict, output_file: str):
    """Salva relatório em arquivo JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRelatorio salvo em: {output_file}")

def main():
    """Função principal."""
    # Configurações
    parquet_dir = os.path.join(PROJECT_ROOT, "data", "parquet")
    threshold_mb = int(os.getenv("POLARS_THRESHOLD_MB", "500"))
    output_file = os.path.join(PROJECT_ROOT, "reports", "table_analysis_report.json")

    # Criar diretório de reports se não existir
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Executar análise
    report = analyze_all_tables(parquet_dir, threshold_mb)

    if report:
        # Salvar relatório
        save_report(report, output_file)

        # Verificar se Polars está instalado
        print("\nVerificando instalacao do Polars...")
        try:
            import polars as pl
            print(f"OK: Polars {pl.__version__} instalado!")
        except ImportError:
            print("AVISO: Polars NAO instalado. Execute: pip install polars==1.34.0")
            print("       (Script usou PyArrow como fallback)")

        print("\nOK: Analise concluida com sucesso!")
        return 0
    else:
        print("\nERRO: Analise falhou!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
