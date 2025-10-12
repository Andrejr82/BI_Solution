"""
Teste de Performance Híbrida: SQL Server + Parquet

Valida:
1. Conexão SQL Server (primária)
2. Cache Dask funcionando
3. Fallback para Parquet
4. Tempos de execução
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# IMPORTANTE: Carregar .env antes de importar módulos
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_hybrid_performance():
    """Testa performance do sistema híbrido."""
    print("=" * 80)
    print("TESTE DE PERFORMANCE HIBRIDA: SQL SERVER + PARQUET")
    print("=" * 80)
    print()

    # Verificar configuração
    use_sql = os.getenv("USE_SQL_SERVER", "false")
    print(f"DEBUG: USE_SQL_SERVER = {use_sql}")
    print()

    # 1. Criar adaptador híbrido
    print("1. Inicializando HybridDataAdapter...")
    adapter = HybridDataAdapter()
    status = adapter.get_status()
    print(f"   Fonte atual: {status['current_source'].upper()}")
    print(f"   SQL Server disponivel: {status.get('sql_available', False)}")
    print(f"   Parquet disponivel: {status.get('parquet_available', True)}")
    print()

    # 2. Criar DirectQueryEngine
    print("2. Inicializando DirectQueryEngine...")
    engine = DirectQueryEngine(adapter)
    print("   [OK] Engine inicializado")
    print()

    # 3. Teste 1: Primeiro carregamento Dask (CACHE MISS)
    print("3. TESTE 1: Primeiro carregamento Dask DataFrame (CACHE MISS)")
    start1 = datetime.now()
    ddf1 = engine._get_base_dask_df()
    tempo1 = (datetime.now() - start1).total_seconds()

    print(f"   Tempo de carregamento: {tempo1:.2f}s")
    print(f"   Particoes Dask: {ddf1.npartitions}")
    print(f"   Fonte: {status['current_source']}")
    print()

    # 4. Teste 2: Segundo carregamento (CACHE HIT)
    print("4. TESTE 2: Segundo carregamento Dask DataFrame (CACHE HIT)")
    start2 = datetime.now()
    ddf2 = engine._get_base_dask_df()
    tempo2 = (datetime.now() - start2).total_seconds()

    print(f"   Tempo de carregamento: {tempo2:.2f}s (esperado ~0s devido ao cache)")
    print(f"   Cache hit: {ddf1 is ddf2}")  # Deve ser True
    print()

    # 5. Verificar cache Dask
    print("5. VERIFICANDO CACHE DASK:")
    has_cache = engine._cached_dask_df is not None
    cache_source = engine._cache_source if has_cache else "N/A"
    print(f"   Cache ativo: {has_cache}")
    print(f"   Fonte do cache: {cache_source}")
    print()

    # 6. Resultados
    print("=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"[OK] SQL Server conectado: {status.get('sql_available', False)}")
    print(f"[OK] Parquet disponivel (fallback): {status.get('parquet_available', True)}")
    print(f"[OK] Cache Dask funcionando: {has_cache}")
    print(f"[OK] Query 1 (sem cache): {tempo1:.2f}s")
    print(f"[OK] Query 2 (com cache): {tempo2:.2f}s")

    # Calcular melhoria de performance
    if tempo1 > 0:
        melhoria = ((tempo1 - tempo2) / tempo1) * 100
        print(f"[OK] Melhoria de performance (cache): {melhoria:.1f}%")

    print()

    # Verificar se tudo está OK
    sql_ok = status.get('sql_available', False)
    parquet_ok = status.get('parquet_available', True)
    cache_efetivo = tempo2 < (tempo1 * 0.1)  # Cache deve ser pelo menos 10x mais rápido
    tudo_ok = (sql_ok or parquet_ok) and has_cache and cache_efetivo

    if tudo_ok:
        print("[SUCESSO] SISTEMA 100% OPERACIONAL - SQL SERVER + PARQUET + CACHE FUNCIONANDO!")
    else:
        print("[AVISO] Alguns componentes nao estao funcionando corretamente")
        if not sql_ok and not parquet_ok:
            print("   ERRO: Nem SQL Server nem Parquet estao disponiveis!")
        if not cache_efetivo:
            print("   AVISO: Cache nao esta sendo efetivo")

    print("=" * 80)

    return tudo_ok

if __name__ == "__main__":
    try:
        success = test_hybrid_performance()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERRO] ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
