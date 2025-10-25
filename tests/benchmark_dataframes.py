"""
Benchmark: Polars vs Pandas vs Dask
=====================================

Testa performance das 3 bibliotecas com operações reais do projeto:
1. Leitura de Parquet
2. Filtros simples
3. Agregações (groupby + sum)
4. Joins
5. Conversões de tipo
6. Ordenação

Usa os dados reais do projeto para resultados precisos.

Autor: Agent Solution BI
Data: 2025-10-20
"""

import sys
import os
import time
import psutil
import gc
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports das bibliotecas a testar
import pandas as pd
import dask.dataframe as dd
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    print("⚠️ Polars não instalado. Instale com: pip install polars")

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor de uso de memória"""
    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = 0

    def start(self):
        gc.collect()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def get_usage(self):
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        return current_memory - self.start_memory


def get_parquet_path():
    """Encontra o arquivo Parquet do projeto"""
    parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
    parquet_files = [f for f in os.listdir(parquet_dir) if f.endswith('.parquet')]

    if not parquet_files:
        raise FileNotFoundError("Nenhum arquivo Parquet encontrado!")

    parquet_path = os.path.join(parquet_dir, parquet_files[0])
    file_size = os.path.getsize(parquet_path) / 1024 / 1024  # MB

    logger.info(f"📁 Arquivo: {parquet_files[0]}")
    logger.info(f"💾 Tamanho: {file_size:.2f} MB")

    return parquet_path


def benchmark_pandas(parquet_path):
    """Benchmark com Pandas"""
    logger.info("\n" + "="*80)
    logger.info("🐼 PANDAS - Benchmark")
    logger.info("="*80)

    results = {}
    mem_monitor = MemoryMonitor()

    # 1. LEITURA (chunked para evitar MemoryError)
    logger.info("\n📖 Teste 1: Leitura de Parquet (com filtro inicial)")
    logger.info("   ℹ️  Simulando query real do projeto: filtrar por segmento")
    mem_monitor.start()
    start = time.time()

    # Ler com filtro (simula uso real do projeto)
    df = pd.read_parquet(
        parquet_path,
        engine='pyarrow',
        filters=[('nomesegmento', 'in', ['TECIDOS', 'PAPELARIA', 'FESTAS'])]
    )

    read_time = time.time() - start
    read_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {read_time:.2f}s")
    logger.info(f"   💾 Memória: {read_memory:.2f} MB")
    logger.info(f"   📊 Registros: {len(df):,}")
    logger.info(f"   ℹ️  (Filtrados 3 segmentos principais)")

    results['read_time'] = read_time
    results['read_memory'] = read_memory
    results['total_rows'] = len(df)

    # 2. FILTRO SIMPLES
    logger.info("\n🔍 Teste 2: Filtro Simples (NOMESEGMENTO = 'TECIDOS')")
    mem_monitor.start()
    start = time.time()
    df_filtered = df[df['nomesegmento'] == 'TECIDOS']
    filter_time = time.time() - start
    filter_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {filter_time:.3f}s")
    logger.info(f"   💾 Memória: {filter_memory:.2f} MB")
    logger.info(f"   📊 Registros filtrados: {len(df_filtered):,}")

    results['filter_time'] = filter_time
    results['filter_memory'] = filter_memory
    results['filter_rows'] = len(df_filtered)

    # 3. AGREGAÇÃO (GroupBy + Sum)
    logger.info("\n📊 Teste 3: Agregação (GroupBy por segmento + Sum)")
    mem_monitor.start()
    start = time.time()
    df_agg = df.groupby('nomesegmento')['venda_30_d'].sum().reset_index()
    agg_time = time.time() - start
    agg_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {agg_time:.3f}s")
    logger.info(f"   💾 Memória: {agg_memory:.2f} MB")
    logger.info(f"   📊 Grupos: {len(df_agg):,}")

    results['agg_time'] = agg_time
    results['agg_memory'] = agg_memory

    # 4. CONVERSÃO DE TIPOS
    logger.info("\n🔄 Teste 4: Conversão de Tipos (estoque para numérico)")
    mem_monitor.start()
    start = time.time()
    df_copy = df.copy()
    df_copy['estoque_atual'] = pd.to_numeric(df_copy['estoque_atual'], errors='coerce').fillna(0)
    convert_time = time.time() - start
    convert_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {convert_time:.3f}s")
    logger.info(f"   💾 Memória: {convert_memory:.2f} MB")

    results['convert_time'] = convert_time
    results['convert_memory'] = convert_memory

    # 5. ORDENAÇÃO
    logger.info("\n🔀 Teste 5: Ordenação (por venda_30_d)")
    mem_monitor.start()
    start = time.time()
    df_sorted = df.sort_values('venda_30_d', ascending=False).head(1000)
    sort_time = time.time() - start
    sort_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {sort_time:.3f}s")
    logger.info(f"   💾 Memória: {sort_memory:.2f} MB")

    results['sort_time'] = sort_time
    results['sort_memory'] = sort_memory

    # TOTAL
    total_time = read_time + filter_time + agg_time + convert_time + sort_time
    results['total_time'] = total_time

    logger.info(f"\n⏱️  TEMPO TOTAL: {total_time:.2f}s")

    return results


def benchmark_dask(parquet_path):
    """Benchmark com Dask"""
    logger.info("\n" + "="*80)
    logger.info("🚀 DASK - Benchmark")
    logger.info("="*80)

    results = {}
    mem_monitor = MemoryMonitor()

    # 1. LEITURA (Lazy + Filtro)
    logger.info("\n📖 Teste 1: Leitura de Parquet (lazy + filtro)")
    logger.info("   ℹ️  Simulando query real do projeto: filtrar por segmento")
    mem_monitor.start()
    start = time.time()

    # Ler com filtro PyArrow (predicate pushdown)
    ddf = dd.read_parquet(
        parquet_path,
        engine='pyarrow',
        filters=[('nomesegmento', 'in', ['TECIDOS', 'PAPELARIA', 'FESTAS'])]
    )

    read_lazy_time = time.time() - start

    logger.info(f"   ⏱️  Tempo (lazy load): {read_lazy_time:.3f}s")
    logger.info(f"   📊 Partições: {ddf.npartitions}")

    # Compute para obter total de linhas
    start = time.time()
    total_rows = len(ddf)
    compute_time = time.time() - start
    read_lazy_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo (compute count): {compute_time:.3f}s")
    logger.info(f"   💾 Memória: {read_lazy_memory:.2f} MB")
    logger.info(f"   📊 Registros: {total_rows:,}")
    logger.info(f"   ℹ️  (Filtrados 3 segmentos principais)")

    results['read_time'] = read_lazy_time + compute_time
    results['read_memory'] = read_lazy_memory
    results['total_rows'] = total_rows

    # 2. FILTRO SIMPLES
    logger.info("\n🔍 Teste 2: Filtro Simples (NOMESEGMENTO = 'TECIDOS')")
    mem_monitor.start()
    start = time.time()
    ddf_filtered = ddf[ddf['nomesegmento'] == 'TECIDOS']
    df_filtered = ddf_filtered.compute()
    filter_time = time.time() - start
    filter_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {filter_time:.3f}s")
    logger.info(f"   💾 Memória: {filter_memory:.2f} MB")
    logger.info(f"   📊 Registros filtrados: {len(df_filtered):,}")

    results['filter_time'] = filter_time
    results['filter_memory'] = filter_memory
    results['filter_rows'] = len(df_filtered)

    # 3. AGREGAÇÃO (GroupBy + Sum)
    logger.info("\n📊 Teste 3: Agregação (GroupBy por segmento + Sum)")
    mem_monitor.start()
    start = time.time()
    ddf_agg = ddf.groupby('nomesegmento')['venda_30_d'].sum().reset_index()
    df_agg = ddf_agg.compute()
    agg_time = time.time() - start
    agg_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {agg_time:.3f}s")
    logger.info(f"   💾 Memória: {agg_memory:.2f} MB")
    logger.info(f"   📊 Grupos: {len(df_agg):,}")

    results['agg_time'] = agg_time
    results['agg_memory'] = agg_memory

    # 4. CONVERSÃO DE TIPOS
    logger.info("\n🔄 Teste 4: Conversão de Tipos (estoque para numérico)")
    mem_monitor.start()
    start = time.time()
    ddf_copy = ddf.copy()
    ddf_copy['estoque_atual'] = dd.to_numeric(ddf_copy['estoque_atual'], errors='coerce').fillna(0)
    df_converted = ddf_copy.compute()
    convert_time = time.time() - start
    convert_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {convert_time:.3f}s")
    logger.info(f"   💾 Memória: {convert_memory:.2f} MB")

    results['convert_time'] = convert_time
    results['convert_memory'] = convert_memory

    # 5. ORDENAÇÃO
    logger.info("\n🔀 Teste 5: Ordenação (por venda_30_d)")
    mem_monitor.start()
    start = time.time()
    ddf_sorted = ddf.nlargest(1000, 'venda_30_d')
    df_sorted = ddf_sorted.compute()
    sort_time = time.time() - start
    sort_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {sort_time:.3f}s")
    logger.info(f"   💾 Memória: {sort_memory:.2f} MB")

    results['sort_time'] = sort_time
    results['sort_memory'] = sort_memory

    # TOTAL
    total_time = results['read_time'] + filter_time + agg_time + convert_time + sort_time
    results['total_time'] = total_time

    logger.info(f"\n⏱️  TEMPO TOTAL: {total_time:.2f}s")

    return results


def benchmark_polars(parquet_path):
    """Benchmark com Polars"""
    if not POLARS_AVAILABLE:
        logger.warning("⚠️ Polars não disponível - pulando testes")
        return None

    logger.info("\n" + "="*80)
    logger.info("⚡ POLARS - Benchmark")
    logger.info("="*80)

    results = {}
    mem_monitor = MemoryMonitor()

    # 1. LEITURA (com filtro)
    logger.info("\n📖 Teste 1: Leitura de Parquet (com filtro)")
    logger.info("   ℹ️  Simulando query real do projeto: filtrar por segmento")
    mem_monitor.start()
    start = time.time()

    # Ler com filtro (Polars suporta predicate pushdown nativo)
    df = pl.scan_parquet(parquet_path).filter(
        pl.col('nomesegmento').is_in(['TECIDOS', 'PAPELARIA', 'FESTAS'])
    ).collect()

    read_time = time.time() - start
    read_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {read_time:.2f}s")
    logger.info(f"   💾 Memória: {read_memory:.2f} MB")
    logger.info(f"   📊 Registros: {len(df):,}")
    logger.info(f"   ℹ️  (Filtrados 3 segmentos principais)")

    results['read_time'] = read_time
    results['read_memory'] = read_memory
    results['total_rows'] = len(df)

    # 2. FILTRO SIMPLES
    logger.info("\n🔍 Teste 2: Filtro Simples (NOMESEGMENTO = 'TECIDOS')")
    mem_monitor.start()
    start = time.time()
    df_filtered = df.filter(pl.col('nomesegmento') == 'TECIDOS')
    filter_time = time.time() - start
    filter_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {filter_time:.3f}s")
    logger.info(f"   💾 Memória: {filter_memory:.2f} MB")
    logger.info(f"   📊 Registros filtrados: {len(df_filtered):,}")

    results['filter_time'] = filter_time
    results['filter_memory'] = filter_memory
    results['filter_rows'] = len(df_filtered)

    # 3. AGREGAÇÃO (GroupBy + Sum)
    logger.info("\n📊 Teste 3: Agregação (GroupBy por segmento + Sum)")
    mem_monitor.start()
    start = time.time()
    df_agg = df.groupby('nomesegmento').agg(pl.col('venda_30_d').sum())
    agg_time = time.time() - start
    agg_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {agg_time:.3f}s")
    logger.info(f"   💾 Memória: {agg_memory:.2f} MB")
    logger.info(f"   📊 Grupos: {len(df_agg):,}")

    results['agg_time'] = agg_time
    results['agg_memory'] = agg_memory

    # 4. CONVERSÃO DE TIPOS
    logger.info("\n🔄 Teste 4: Conversão de Tipos (estoque para numérico)")
    mem_monitor.start()
    start = time.time()
    df_copy = df.with_columns(pl.col('estoque_atual').cast(pl.Float64, strict=False).fill_null(0))
    convert_time = time.time() - start
    convert_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {convert_time:.3f}s")
    logger.info(f"   💾 Memória: {convert_memory:.2f} MB")

    results['convert_time'] = convert_time
    results['convert_memory'] = convert_memory

    # 5. ORDENAÇÃO
    logger.info("\n🔀 Teste 5: Ordenação (por venda_30_d)")
    mem_monitor.start()
    start = time.time()
    df_sorted = df.sort('venda_30_d', descending=True).head(1000)
    sort_time = time.time() - start
    sort_memory = mem_monitor.get_usage()

    logger.info(f"   ⏱️  Tempo: {sort_time:.3f}s")
    logger.info(f"   💾 Memória: {sort_memory:.2f} MB")

    results['sort_time'] = sort_time
    results['sort_memory'] = sort_memory

    # TOTAL
    total_time = read_time + filter_time + agg_time + convert_time + sort_time
    results['total_time'] = total_time

    logger.info(f"\n⏱️  TEMPO TOTAL: {total_time:.2f}s")

    return results


def print_comparison(pandas_results, dask_results, polars_results):
    """Imprime comparação dos resultados"""
    logger.info("\n" + "="*80)
    logger.info("📊 COMPARAÇÃO FINAL")
    logger.info("="*80)

    # Tabela de tempos
    logger.info("\n⏱️  TEMPOS DE EXECUÇÃO (segundos)")
    logger.info("-" * 80)
    logger.info(f"{'Operação':<25} {'Pandas':>12} {'Dask':>12} {'Polars':>12} {'Vencedor':>12}")
    logger.info("-" * 80)

    operations = [
        ('Leitura', 'read_time'),
        ('Filtro', 'filter_time'),
        ('Agregação', 'agg_time'),
        ('Conversão Tipos', 'convert_time'),
        ('Ordenação', 'sort_time'),
        ('TOTAL', 'total_time')
    ]

    winners = {'pandas': 0, 'dask': 0, 'polars': 0}

    for op_name, op_key in operations:
        pandas_val = pandas_results.get(op_key, float('inf'))
        dask_val = dask_results.get(op_key, float('inf'))
        polars_val = polars_results.get(op_key, float('inf')) if polars_results else float('inf')

        values = {'pandas': pandas_val, 'dask': dask_val, 'polars': polars_val}
        winner = min(values, key=values.get)

        if op_key != 'total_time':
            winners[winner] += 1

        logger.info(f"{op_name:<25} {pandas_val:>12.3f} {dask_val:>12.3f} {polars_val:>12.3f} {winner:>12}")

    # Tabela de memória
    logger.info("\n💾 USO DE MEMÓRIA (MB)")
    logger.info("-" * 80)
    logger.info(f"{'Operação':<25} {'Pandas':>12} {'Dask':>12} {'Polars':>12}")
    logger.info("-" * 80)

    mem_operations = [
        ('Leitura', 'read_memory'),
        ('Filtro', 'filter_memory'),
        ('Agregação', 'agg_memory'),
        ('Conversão Tipos', 'convert_memory'),
        ('Ordenação', 'sort_memory')
    ]

    for op_name, op_key in mem_operations:
        pandas_val = pandas_results.get(op_key, 0)
        dask_val = dask_results.get(op_key, 0)
        polars_val = polars_results.get(op_key, 0) if polars_results else 0

        logger.info(f"{op_name:<25} {pandas_val:>12.2f} {dask_val:>12.2f} {polars_val:>12.2f}")

    # Resumo
    logger.info("\n" + "="*80)
    logger.info("🏆 VENCEDORES POR CATEGORIA")
    logger.info("="*80)
    logger.info(f"🐼 Pandas: {winners['pandas']} vitórias")
    logger.info(f"🚀 Dask:   {winners['dask']} vitórias")
    logger.info(f"⚡ Polars: {winners['polars']} vitórias")

    overall_winner = max(winners, key=winners.get)
    logger.info(f"\n🏆 VENCEDOR GERAL: {overall_winner.upper()}")

    return overall_winner, winners


def main():
    """Executa todos os benchmarks"""
    logger.info("="*80)
    logger.info("🔬 BENCHMARK: Polars vs Pandas vs Dask")
    logger.info("="*80)
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

    # Encontrar arquivo Parquet
    try:
        parquet_path = get_parquet_path()
    except Exception as e:
        logger.error(f"❌ Erro ao localizar arquivo Parquet: {e}")
        return

    # Executar benchmarks
    pandas_results = benchmark_pandas(parquet_path)
    dask_results = benchmark_dask(parquet_path)
    polars_results = benchmark_polars(parquet_path) if POLARS_AVAILABLE else None

    # Comparar resultados
    winner, scores = print_comparison(pandas_results, dask_results, polars_results)

    # Salvar relatório
    report_path = os.path.join("tests", "benchmark_dataframes_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("BENCHMARK: Polars vs Pandas vs Dask\n")
        f.write("="*80 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write(f"Vencedor Geral: {winner.upper()}\n")
        f.write(f"Pandas: {scores['pandas']} vitórias\n")
        f.write(f"Dask: {scores['dask']} vitórias\n")
        f.write(f"Polars: {scores['polars']} vitórias\n\n")

        f.write("Detalhes:\n")
        f.write(f"Pandas Total: {pandas_results['total_time']:.2f}s\n")
        f.write(f"Dask Total: {dask_results['total_time']:.2f}s\n")
        if polars_results:
            f.write(f"Polars Total: {polars_results['total_time']:.2f}s\n")

    logger.info(f"\n📄 Relatório salvo em: {report_path}")


if __name__ == "__main__":
    main()
