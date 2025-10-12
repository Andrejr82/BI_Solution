"""
Teste de mapeamento inteligente - Usuário pode usar variações!
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("TESTE: MAPEAMENTO INTELIGENTE DE TERMOS")
print("=" * 70)

# Simular diferentes queries do usuário
test_queries = [
    "qual o ranking de vendas no segmento tecido?",      # singular
    "qual o ranking de vendas no segmento tecidos?",     # plural
    "ranking de tecido",                                  # abreviado
    "produtos de limpeza mais vendidos",                  # termo coloquial
    "top 10 do armarinho",                                # termo informal
]

print("\nQUERIES DE TESTE (variações que o usuário pode usar):")
for i, query in enumerate(test_queries, 1):
    print(f"  {i}. '{query}'")

print("\n" + "=" * 70)
print("RESULTADO ESPERADO:")
print("=" * 70)

print("""
O LLM deve INTERPRETAR e MAPEAR automaticamente:

1. "tecido" (singular) → 'TECIDOS' (plural no banco)
2. "tecidos" (plural) → 'TECIDOS' (exato)
3. "tecido" → 'TECIDOS' (interpretação inteligente)
4. "produtos de limpeza" → 'MATERIAL DE LIMPEZA' (mapeamento semântico)
5. "armarinho" → 'ARMARINHO E CONFECÇÃO' (expansão automática)

Usuário NÃO precisa saber valores exatos do banco!
""")

print("=" * 70)
print("AGORA REINICIE O STREAMLIT E TESTE!")
print("=" * 70)
