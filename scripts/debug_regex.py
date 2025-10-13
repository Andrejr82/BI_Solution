"""
Debug do regex para segmentos
"""
import re

# Regex atual
pattern = r'ranking\s*(de\s*vendas)?\s*(no|do|de|em|segmento)\s*segmento\s+(\w+)'

# Queries de teste
queries = [
    "ranking de vendas no segmento tecidos",
    "ranking no segmento papelaria",
    "ranking segmento aviamentos",
    "ranking do segmento tintas",
]

print("Testando regex pattern:")
print(f"Pattern: {pattern}\n")

for query in queries:
    query_lower = query.lower()
    match = re.search(pattern, query_lower)

    print(f"Query: '{query}'")
    if match:
        print(f"  [MATCH] Grupos: {match.groups()}")
        print(f"  Segmento capturado: {match.group(3)}")
    else:
        print(f"  [NO MATCH]")
    print()
