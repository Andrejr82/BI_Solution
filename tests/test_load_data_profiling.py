"""
Profiling Simplificado - Foco em load_data()

Objetivo: Medir tempo e memória de load_data() sem LLM
Data: 2025-10-21
"""

import sys
import os
import time
import tracemalloc
import psutil
from datetime import datetime

# Fix encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import dask.dataframe as dd

def profile_load_data():
    """Simula load_data() do CodeGenAgent com profiling."""

    print("\n" + "="*80)
    print("🔍 PROFILING: load_data() - Simulação Real")
    print("="*80 + "\n")

    parquet_path = os.path.join(os.getcwd(), "data", "parquet", "*.parquet")
    process = psutil.Process()

    # Memória inicial
    mem_before = process.memory_info()
    vm_before = psutil.virtual_memory()

    print(f"📊 ANTES de carregar:")
    print(f"   RAM processo: {mem_before.rss / (1024**2):.1f}MB")
    print(f"   RAM sistema disponível: {vm_before.available / (1024**3):.2f}GB")
    print(f"   RAM sistema total: {vm_before.total / (1024**3):.2f}GB")
    print()

    # Iniciar tracemalloc
    tracemalloc.start()

    # ============================================================
    # FASE 1: read_parquet (lazy)
    # ============================================================
    print("⏱️  FASE 1: dd.read_parquet() (lazy)...")
    start = time.time()

    ddf = dd.read_parquet(parquet_path, engine='pyarrow')

    elapsed_read = time.time() - start
    print(f"   ✅ Tempo: {elapsed_read:.3f}s")
    print(f"   Partições: {ddf.npartitions}")
    print(f"   Colunas: {len(ddf.columns)}")
    print()

    # ============================================================
    # FASE 2: Conversão de tipos (lazy)
    # ============================================================
    print("⏱️  FASE 2: Conversão de tipos (lazy)...")
    start = time.time()

    # Normalizar nomes (igual ao CodeGenAgent)
    column_mapping = {
        'une': 'UNE_ID',
        'nomesegmento': 'NOMESEGMENTO',
        'codigo': 'PRODUTO',
        'nome_produto': 'NOME',
        'une_nome': 'UNE',
        'nomegrupo': 'NOMEGRUPO',
        'ean': 'EAN',
        'preco_38_percent': 'LIQUIDO_38',
        'venda_30_d': 'VENDA_30DD',
        'estoque_atual': 'ESTOQUE_UNE',
        'embalagem': 'EMBALAGEM',
        'tipo': 'TIPO',
        'NOMECATEGORIA': 'NOMECATEGORIA',
        'NOMESUBGRUPO': 'NOMESUBGRUPO',
        'NOMEFABRICANTE': 'NOMEFABRICANTE'
    }

    rename_dict = {k: v for k, v in column_mapping.items() if k in ddf.columns}
    ddf = ddf.rename(columns=rename_dict)

    # Converter tipos
    if 'ESTOQUE_UNE' in ddf.columns:
        ddf['ESTOQUE_UNE'] = dd.to_numeric(ddf['ESTOQUE_UNE'], errors='coerce').fillna(0)

    for i in range(1, 13):
        col_name = f'mes_{i:02d}'
        if col_name in ddf.columns:
            ddf[col_name] = dd.to_numeric(ddf[col_name], errors='coerce').fillna(0)

    elapsed_types = time.time() - start
    print(f"   ✅ Tempo: {elapsed_types:.3f}s")
    print()

    # ============================================================
    # FASE 3: compute() - CRÍTICO!
    # ============================================================
    print("🚨 FASE 3: ddf.compute() - CARREGANDO TUDO NA MEMÓRIA...")
    print("   ⚠️  ATENÇÃO: Isso pode demorar 10-30s e usar muita RAM!")
    print()

    start_compute = time.time()

    try:
        print("   Executando compute()...")
        df_pandas = ddf.compute()

        elapsed_compute = time.time() - start_compute

        # Memória após compute
        mem_after = process.memory_info()
        vm_after = psutil.virtual_memory()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"   ✅ SUCESSO!")
        print(f"   Tempo: {elapsed_compute:.3f}s")
        print(f"   DataFrame shape: {df_pandas.shape}")
        print()

        print(f"📊 DEPOIS de carregar:")
        print(f"   RAM processo: {mem_after.rss / (1024**2):.1f}MB")
        print(f"   RAM processo Δ: {(mem_after.rss - mem_before.rss) / (1024**2):+.1f}MB")
        print(f"   RAM sistema disponível: {vm_after.available / (1024**3):.2f}GB")
        print(f"   RAM sistema usada Δ: {(vm_before.available - vm_after.available) / (1024**3):+.2f}GB")
        print(f"   Tracemalloc peak: {peak / (1024**2):.1f}MB")
        print()

        # ============================================================
        # RESUMO
        # ============================================================
        print("="*80)
        print("📋 RESUMO DE TEMPOS:")
        print("="*80)
        print(f"  1. read_parquet (lazy)    : {elapsed_read:.3f}s")
        print(f"  2. Conversão tipos (lazy) : {elapsed_types:.3f}s")
        print(f"  3. compute() (CRÍTICO)    : {elapsed_compute:.3f}s  ⚠️")
        print(f"  " + "-"*76)
        print(f"  TOTAL                     : {elapsed_read + elapsed_types + elapsed_compute:.3f}s")
        print()

        print("📊 RESUMO DE MEMÓRIA:")
        print("="*80)
        print(f"  RAM processo usada        : {(mem_after.rss - mem_before.rss) / (1024**2):+.1f}MB")
        print(f"  RAM sistema consumida     : {(vm_before.available - vm_after.available) / (1024**3):+.2f}GB")
        print(f"  Tracemalloc peak          : {peak / (1024**2):.1f}MB")
        print()

        # ============================================================
        # TESTE: Filtro UNE = 'MAD'
        # ============================================================
        print("="*80)
        print("🔬 TESTE: Aplicar filtro UNE == 'MAD' (DEPOIS de carregar)")
        print("="*80)
        print()

        start_filter = time.time()
        if 'UNE' in df_pandas.columns:
            df_mad = df_pandas[df_pandas['UNE'] == 'MAD']
            elapsed_filter = time.time() - start_filter

            print(f"✅ Filtro aplicado em {elapsed_filter:.3f}s")
            print(f"   Linhas ANTES: {len(df_pandas):,}")
            print(f"   Linhas DEPOIS: {len(df_mad):,}")
            print(f"   Redução: {(1 - len(df_mad)/len(df_pandas))*100:.1f}%")
            print()

            print("⚠️  PROBLEMA:")
            print(f"   - Carregamos {len(df_pandas):,} linhas na memória")
            print(f"   - Usamos apenas {len(df_mad):,} linhas ({len(df_mad)/len(df_pandas)*100:.1f}%)")
            print(f"   - Desperdício: {len(df_pandas) - len(df_mad):,} linhas ({(1 - len(df_mad)/len(df_pandas))*100:.1f}%)")
            print()

        # ============================================================
        # COMPARAÇÃO: Se filtrássemos ANTES
        # ============================================================
        print("="*80)
        print("💡 SOLUÇÃO: Filtrar ANTES de compute()")
        print("="*80)
        print()

        print("Se aplicássemos filtro ANTES:")
        print()

        # Simular filtro lazy
        start_lazy = time.time()
        ddf2 = dd.read_parquet(parquet_path, engine='pyarrow')
        ddf2 = ddf2.rename(columns=rename_dict)

        if 'UNE' in ddf2.columns:
            ddf2_filtered = ddf2[ddf2['UNE'] == 'MAD']  # Lazy filter
            df_mad_lazy = ddf2_filtered.compute()  # Compute apenas MAD
            elapsed_lazy = time.time() - start_lazy

            print(f"✅ Tempo total (lazy filter): {elapsed_lazy:.3f}s")
            print(f"   Linhas carregadas: {len(df_mad_lazy):,}")
            print()

            print(f"📈 GANHO:")
            print(f"   Tempo atual:      {elapsed_compute:.3f}s")
            print(f"   Tempo com filtro: {elapsed_lazy:.3f}s")
            print(f"   Economia:         {elapsed_compute - elapsed_lazy:.3f}s ({(1 - elapsed_lazy/elapsed_compute)*100:.1f}% mais rápido)")
            print()

        return {
            'success': True,
            'time_total': elapsed_read + elapsed_types + elapsed_compute,
            'time_compute': elapsed_compute,
            'memory_mb': (mem_after.rss - mem_before.rss) / (1024**2),
            'rows_total': len(df_pandas),
            'rows_filtered': len(df_mad) if 'UNE' in df_pandas.columns else 0
        }

    except MemoryError as e:
        elapsed_compute = time.time() - start_compute
        tracemalloc.stop()

        print(f"   ❌ FALHA: MemoryError")
        print(f"   Tempo até falha: {elapsed_compute:.3f}s")
        print(f"   Erro: {e}")
        print()

        return {
            'success': False,
            'error': str(e),
            'time_until_fail': elapsed_compute
        }

    except Exception as e:
        elapsed_compute = time.time() - start_compute
        tracemalloc.stop()

        print(f"   ❌ ERRO: {type(e).__name__}")
        print(f"   Tempo até erro: {elapsed_compute:.3f}s")
        print(f"   Mensagem: {e}")
        print()

        import traceback
        traceback.print_exc()

        return {
            'success': False,
            'error': str(e),
            'time_until_fail': elapsed_compute
        }


if __name__ == "__main__":
    try:
        result = profile_load_data()

        print("\n" + "="*80)
        print("🎯 CONCLUSÃO FINAL")
        print("="*80 + "\n")

        if result['success']:
            print("✅ load_data() executado com sucesso")
            print()
            print("🚨 BOTTLENECK IDENTIFICADO:")
            print(f"   compute() consome {result['time_compute'] / result['time_total'] * 100:.1f}% do tempo total")
            print()
            print("🔧 RECOMENDAÇÃO:")
            print("   Implementar Plano A: load_data(filters={...})")
            print("   Para aproveitar PolarsDaskAdapter com predicate pushdown")
            print()
        else:
            print("❌ load_data() FALHOU")
            print(f"   Erro: {result.get('error')}")
            print()
            print("🚨 CONFIRMADO:")
            print("   Sistema NÃO consegue carregar dataset completo")
            print("   SOLUÇÃO URGENTE: Implementar filtros obrigatórios")
            print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido.\n")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
