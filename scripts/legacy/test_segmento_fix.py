"""
Teste da correcao do regex para queries de segmento
Data: 12/10/2025
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Forcar reload do modulo para pegar mudancas
import importlib
import core.business_intelligence.direct_query_engine
importlib.reload(core.business_intelligence.direct_query_engine)

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.hybrid_adapter import HybridDataAdapter

print("="*80)
print("TESTE: Correcao Regex - Ranking por Segmento")
print("="*80)

# Inicializar
adapter = HybridDataAdapter()
engine = DirectQueryEngine(adapter)

# Queries de teste (todas devem retornar top_produtos_por_segmento, nao ranking_segmentos)
test_queries = [
    # Casos que devem funcionar corretamente
    ("ranking de vendas no segmento tecidos", "top_produtos_por_segmento"),
    ("ranking no segmento papelaria", "top_produtos_por_segmento"),
    ("ranking segmento aviamentos", "top_produtos_por_segmento"),
    ("ranking do segmento tintas", "top_produtos_por_segmento"),
    ("ranking de vendas do segmento eletricos", "top_produtos_por_segmento"),

    # Caso que deve retornar ranking DE segmentos
    ("ranking de segmentos", "ranking_segmentos"),
    ("ranking dos segmentos", "ranking_segmentos"),

    # Outros casos
    ("top 10 produtos do segmento tecidos", "top_produtos_por_segmento"),
]

print("\nTestando classificacao de intents...")
print("-"*80)

passed = 0
failed = 0

for query, expected_type in test_queries:
    intent_type, params = engine.classify_intent_direct(query)

    status = "[OK]" if intent_type == expected_type else "[FALHOU]"
    if intent_type == expected_type:
        passed += 1
    else:
        failed += 1

    print(f"\n{status} Query: '{query}'")
    print(f"     Esperado: {expected_type}")
    print(f"     Recebido: {intent_type}")
    if params:
        print(f"     Params: {params}")

print("\n" + "="*80)
print(f"RESULTADO: {passed} passaram, {failed} falharam")
print("="*80)

if failed == 0:
    print("[SUCESSO] Todos os testes passaram!")
else:
    print(f"[ATENCAO] {failed} teste(s) falharam. Revisar regex.")
