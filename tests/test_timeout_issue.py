"""
Teste para investigar timeout de 30s em query de ranking
"""
import time
from datetime import datetime

# Simular função de timeout do Streamlit
def calcular_timeout_dinamico(query: str) -> int:
    """Calcula timeout baseado na complexidade da query"""
    query_lower = query.lower()

    # Queries gráficas/evolutivas precisam de mais tempo
    if any(kw in query_lower for kw in ['gráfico', 'chart', 'evolução', 'tendência', 'sazonalidade', 'histórico']):
        return 60  # 60s para gráficos
    # Análises complexas (ranking, top, agregações)
    elif any(kw in query_lower for kw in ['ranking', 'top', 'maior', 'menor', 'análise', 'compare', 'comparar']):
        return 45  # 45s para análises
    # Queries simples (filtro direto)
    else:
        return 30  # 30s para queries simples

print("=" * 60)
print("TESTE: Detecção de Timeout Dinâmico")
print("=" * 60)

# Query do usuário
query = "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?"

print(f"\nQuery: {query}")
print(f"Query lowercase: {query.lower()}")

timeout = calcular_timeout_dinamico(query)
print(f"\n⏱️ Timeout calculado: {timeout}s")

# Verificar quais palavras-chave estão presentes
keywords_graficos = ['gráfico', 'chart', 'evolução', 'tendência', 'sazonalidade', 'histórico']
keywords_analises = ['ranking', 'top', 'maior', 'menor', 'análise', 'compare', 'comparar']

print("\n🔍 Análise de palavras-chave:")
print(f"Palavras-chave de gráficos encontradas: {[kw for kw in keywords_graficos if kw in query.lower()]}")
print(f"Palavras-chave de análises encontradas: {[kw for kw in keywords_analises if kw in query.lower()]}")

# Problema identificado
print("\n" + "=" * 60)
print("❌ PROBLEMA IDENTIFICADO:")
print("=" * 60)
print("A query contém '5 produtos mais vendidos' que é claramente um ranking,")
print("mas a palavra 'mais vendidos' NÃO corresponde exatamente a 'maior'.")
print("A função está procurando por 'maior' mas a query usa 'mais vendidos'.")
print(f"\nResultado: Timeout de apenas {timeout}s ao invés de 45s!")

print("\n" + "=" * 60)
print("✅ SOLUÇÃO:")
print("=" * 60)
print("Adicionar mais palavras-chave à lista de análises complexas:")
print("  - 'mais vendido', 'mais vendidos'")
print("  - 'menos vendido', 'menos vendidos'")
print("  - 'produtos', 'vendas', 'quantidade'")

# Testar solução
def calcular_timeout_dinamico_CORRIGIDO(query: str) -> int:
    """Calcula timeout baseado na complexidade da query - VERSÃO CORRIGIDA"""
    query_lower = query.lower()

    # Queries gráficas/evolutivas precisam de mais tempo
    if any(kw in query_lower for kw in ['gráfico', 'chart', 'evolução', 'tendência', 'sazonalidade', 'histórico']):
        return 60  # 60s para gráficos
    # Análises complexas (ranking, top, agregações)
    elif any(kw in query_lower for kw in [
        'ranking', 'top', 'maior', 'menor', 'análise', 'compare', 'comparar',
        'mais vendido', 'menos vendido', 'vendidos', 'produtos',  # NOVOS
        'liste', 'listar', 'mostre', 'mostrar'  # NOVOS
    ]):
        return 45  # 45s para análises
    # Queries simples (filtro direto)
    else:
        return 30  # 30s para queries simples

print(f"\n⏱️ Timeout CORRIGIDO: {calcular_timeout_dinamico_CORRIGIDO(query)}s")

# Testar outras queries similares
print("\n" + "=" * 60)
print("🧪 TESTES ADICIONAIS:")
print("=" * 60)

queries_teste = [
    "Top 10 produtos mais vendidos",
    "Produtos com maior estoque",
    "Ranking de vendas por UNE",
    "Mostre os 5 melhores produtos",
    "Liste os produtos sem movimento",
    "Qual o preço do produto 12345",  # Query simples
]

for q in queries_teste:
    timeout_antes = calcular_timeout_dinamico(q)
    timeout_depois = calcular_timeout_dinamico_CORRIGIDO(q)
    mudou = "✅" if timeout_antes != timeout_depois else "⚪"
    print(f"{mudou} '{q[:40]}...' → {timeout_antes}s → {timeout_depois}s")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
