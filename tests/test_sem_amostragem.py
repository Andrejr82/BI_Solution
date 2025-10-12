"""
Teste do Sistema SEM Amostragem - Validação da Simplificação
"""

import os
import sys
from datetime import datetime

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TESTE SISTEMA SEM AMOSTRAGEM - SIMPLIFICADO")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)

from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

# Inicializar componentes
print("\n[1/3] Inicializando HybridDataAdapter...")
data_adapter = HybridDataAdapter()

print("\n[2/3] Inicializando DirectQueryEngine...")
direct_engine = DirectQueryEngine(data_adapter)

# Testes
print("\n" + "=" * 80)
print("TESTES DE QUERIES")
print("=" * 80)

queries_teste = [
    ("Query Genérica", "top 10 produtos"),
    ("Query com Filtro", "produtos com estoque baixo"),
    ("Query de Segmento", "produtos do segmento tecidos"),
]

resultados = []

for nome, query in queries_teste:
    print(f"\n🔍 Testando: {nome}")
    print(f"   Query: '{query}'")

    start = datetime.now()
    result = direct_engine.process_query(query)
    elapsed = (datetime.now() - start).total_seconds()

    # Verificar dados retornados
    if hasattr(direct_engine, '_cached_data') and direct_engine._cached_data:
        cache_data = list(direct_engine._cached_data.values())[0]
        dataset_size = len(cache_data)
    else:
        dataset_size = "N/A"

    status = "✅ OK" if result and result.get('type') != 'error' else "❌ ERRO"

    print(f"   Status: {status}")
    print(f"   Tempo: {elapsed:.2f}s")
    print(f"   Dataset: {dataset_size:,} registros" if isinstance(dataset_size, int) else f"   Dataset: {dataset_size}")
    print(f"   Type: {result.get('type', 'N/A')}")

    resultados.append({
        "nome": nome,
        "query": query,
        "status": status,
        "tempo": elapsed,
        "dataset_size": dataset_size,
        "type": result.get('type', 'N/A')
    })

# Validação crítica: Dataset completo usado
print("\n" + "=" * 80)
print("VALIDAÇÃO CRÍTICA")
print("=" * 80)

dataset_completo = False
if hasattr(direct_engine, '_cached_data') and direct_engine._cached_data:
    cache_data = list(direct_engine._cached_data.values())[0]
    dataset_size = len(cache_data)

    print(f"\n📊 Dataset em cache: {dataset_size:,} registros")

    # Validar que é dataset completo (> 1 milhão)
    if dataset_size > 1000000:
        print("✅ CONFIRMADO: Sistema usa dataset COMPLETO (sem amostragem)")
        dataset_completo = True
    elif dataset_size <= 20000:
        print("❌ ERRO: Sistema ainda usa amostragem!")
        dataset_completo = False
    else:
        print(f"⚠️  AVISO: Dataset com {dataset_size:,} registros (verificar)")

print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)

total = len(resultados)
sucessos = sum(1 for r in resultados if "✅" in r['status'])

print(f"\n📊 Testes executados: {total}")
print(f"   ✅ Sucessos: {sucessos}/{total}")
print(f"   ❌ Falhas: {total - sucessos}/{total}")

if dataset_completo and sucessos == total:
    print("\n🎉 SISTEMA SIMPLIFICADO E FUNCIONANDO PERFEITAMENTE!")
    print("   ✅ Sem amostragem")
    print("   ✅ Dataset completo sempre usado")
    print("   ✅ Código mais simples")
    print("   ✅ Zero bugs de amostragem")
elif dataset_completo:
    print("\n⚠️  Sistema usa dataset completo mas tem algumas falhas")
else:
    print("\n❌ Sistema ainda usa amostragem - Verificar código")

print("\n" + "=" * 80)
