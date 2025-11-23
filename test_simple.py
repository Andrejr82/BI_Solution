"""Teste simplificado das otimizacoes"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("TESTE SIMPLIFICADO - QUICK WINS")
print("=" * 60)
print()

# TESTE 1: Fast-Path Detection
print("TESTE 1: Fast-Path Detection")
print("-" * 60)

from core.graph.graph_builder import detect_fast_path_query

queries = [
    ("mc do produto 369947 na une scr", "execute_une_tool"),
    ("estoque produto 123 une mad", "execute_une_tool"),
    ("liste produtos do segmento tecidos", "classify_intent"),
    ("ola bom dia", None),
]

passed = 0
for query, expected in queries:
    result = detect_fast_path_query(query)
    if result == expected:
        print(f"[PASS] '{query[:40]}' -> {result}")
        passed += 1
    else:
        print(f"[FAIL] '{query[:40]}' -> {result} (esperado: {expected})")

print(f"\nResultado: {passed}/{len(queries)} testes passaram")
print()

# TESTE 2: Cache de Catalog
print("TESTE 2: Cache de Catalog")
print("-" * 60)

import time
from core.agents.code_gen_agent import _load_catalog_cached

# Limpar cache
_load_catalog_cached.cache_clear()

# Primeira chamada
start = time.time()
cat1 = _load_catalog_cached()
t1 = time.time() - start

# Segunda chamada (deve ser do cache)
start = time.time()
cat2 = _load_catalog_cached()
t2 = time.time() - start

print(f"1a chamada (disco): {t1:.4f}s")
print(f"2a chamada (cache): {t2:.6f}s")

if cat1 and cat2:
    print("[PASS] Catalogo carregado")
else:
    print("[FAIL] Catalogo vazio")

if cat1 is cat2:
    print("[PASS] Cache funcionando (mesmo objeto)")
else:
    print("[FAIL] Cache nao esta funcionando")

if t1 > 0 and t2 > 0:
    speedup = t1 / t2
    print(f"Speedup: {speedup:.0f}x mais rapido")
print()

# TESTE 3: Import bi_agent_nodes
print("TESTE 3: Modulo bi_agent_nodes")
print("-" * 60)

try:
    from core.agents.bi_agent_nodes import classify_intent
    print("[PASS] Modulo importado com sucesso")
except Exception as e:
    print(f"[FAIL] Erro ao importar: {e}")

print()
print("=" * 60)
print("TESTES CONCLUIDOS")
print("=" * 60)
print()
print("Proximo passo: streamlit run streamlit_app.py")
