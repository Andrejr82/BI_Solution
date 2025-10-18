"""
Script de Teste - Few-Shot Learning

Testa a funcionalidade completa do FewShotManager:
1. Carregamento de queries históricas
2. Busca de exemplos relevantes
3. Formatação de prompt para LLM
4. Estatísticas do sistema

Autor: Code Agent
Data: 2025-10-18
"""

import sys
from pathlib import Path

# Adicionar root ao path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from core.learning.few_shot_manager import FewShotManager, get_few_shot_examples
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_load_queries():
    """Teste 1: Carregar queries bem-sucedidas"""
    print("\n" + "="*80)
    print("TESTE 1: CARREGAR QUERIES BEM-SUCEDIDAS")
    print("="*80)

    manager = FewShotManager()
    queries = manager.load_successful_queries(days=30)

    print(f"\n✓ Queries encontradas nos últimos 30 dias: {len(queries)}")

    if queries:
        # Mostrar amostra
        print("\n--- Amostra de 3 queries ---")
        for i, q in enumerate(queries[:3], 1):
            print(f"\n{i}. Query: {q.get('query', 'N/A')[:80]}...")
            print(f"   Intent: {q.get('intent', 'N/A')}")
            print(f"   Rows: {q.get('rows', 0)}")
            print(f"   Timestamp: {q.get('timestamp', 'N/A')}")

    return len(queries) > 0


def test_find_relevant_examples():
    """Teste 2: Buscar exemplos relevantes"""
    print("\n" + "="*80)
    print("TESTE 2: BUSCAR EXEMPLOS RELEVANTES")
    print("="*80)

    manager = FewShotManager()

    # Queries de teste
    test_queries = [
        ("ranking de vendas de tecidos", "python_analysis"),
        ("transferências entre lojas", "une_transferencias"),
        ("estoque de produtos", "une_estoque"),
        ("melhor cliente do mês", "python_analysis"),
    ]

    for test_query, intent in test_queries:
        print(f"\n--- Query: '{test_query}' ---")
        print(f"Intent: {intent}")

        examples = manager.find_relevant_examples(test_query, intent)

        print(f"✓ Exemplos encontrados: {len(examples)}")

        if examples:
            print("\nTop 3 mais relevantes:")
            for i, ex in enumerate(examples[:3], 1):
                score = ex.get('similarity_score', 0)
                query_text = ex.get('query', 'N/A')[:60]
                print(f"  {i}. [{score:.2f}] {query_text}...")

    return True


def test_format_prompt():
    """Teste 3: Formatar exemplos para prompt"""
    print("\n" + "="*80)
    print("TESTE 3: FORMATAR EXEMPLOS PARA PROMPT")
    print("="*80)

    manager = FewShotManager(max_examples=2)

    test_query = "ranking de vendas por produto"
    examples = manager.find_relevant_examples(test_query, "python_analysis")

    formatted = manager.format_examples_for_prompt(examples)

    print(f"\n✓ Prompt formatado ({len(formatted)} caracteres)")
    print("\n--- Preview do Prompt ---")
    print(formatted[:800] + "\n..." if len(formatted) > 800 else formatted)

    return len(formatted) > 0


def test_statistics():
    """Teste 4: Estatísticas do histórico"""
    print("\n" + "="*80)
    print("TESTE 4: ESTATÍSTICAS DO HISTÓRICO")
    print("="*80)

    manager = FewShotManager()
    stats = manager.get_statistics()

    print(f"\n✓ Total de queries: {stats['total_queries']}")
    print(f"✓ Média de linhas retornadas: {stats['avg_rows']:.1f}")

    if stats['intents']:
        print("\n✓ Distribuição por Intent:")
        for intent, count in sorted(stats['intents'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_queries']) * 100
            print(f"  - {intent}: {count} ({percentage:.1f}%)")

    if stats['oldest_query']:
        print(f"\n✓ Query mais antiga: {stats['oldest_query']}")
    if stats['newest_query']:
        print(f"✓ Query mais recente: {stats['newest_query']}")

    return stats['total_queries'] > 0


def test_convenience_function():
    """Teste 5: Função de conveniência"""
    print("\n" + "="*80)
    print("TESTE 5: FUNÇÃO DE CONVENIÊNCIA")
    print("="*80)

    test_query = "produtos mais vendidos"
    formatted = get_few_shot_examples(test_query, intent="python_analysis", max_examples=3)

    print(f"\n✓ Função get_few_shot_examples() executada")
    print(f"✓ Retornou {len(formatted)} caracteres")

    if formatted:
        print("\n--- Preview ---")
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)

    return True


def test_integration_scenario():
    """Teste 6: Cenário de integração completo"""
    print("\n" + "="*80)
    print("TESTE 6: CENÁRIO DE INTEGRAÇÃO COMPLETO")
    print("="*80)

    # Simular fluxo real do agent
    user_query = "listar top 10 produtos com maior estoque"
    intent = "python_analysis"

    print(f"\nCenário: Usuário pergunta '{user_query}'")
    print(f"Intent detectado: {intent}")

    # 1. Buscar exemplos
    manager = FewShotManager(max_examples=3)
    examples = manager.find_relevant_examples(user_query, intent)

    print(f"\n✓ Passo 1: {len(examples)} exemplos relevantes encontrados")

    # 2. Formatar para prompt
    few_shot_context = manager.format_examples_for_prompt(examples)

    print(f"✓ Passo 2: Contexto formatado ({len(few_shot_context)} chars)")

    # 3. Simular montagem do prompt final
    system_prompt = """Você é um assistente de análise de dados.
Gere código Python para responder a pergunta do usuário."""

    enhanced_prompt = f"""{system_prompt}

{few_shot_context}

IMPORTANTE: Use os exemplos acima como referência mas adapte para a pergunta atual.
"""

    print(f"✓ Passo 3: Prompt final montado ({len(enhanced_prompt)} chars)")
    print("\n--- Preview do Prompt Final ---")
    print(enhanced_prompt[:600] + "\n...")

    return len(examples) > 0


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("INICIANDO BATERIA DE TESTES - FEW-SHOT LEARNING")
    print("="*80)

    results = []

    try:
        results.append(("Load Queries", test_load_queries()))
    except Exception as e:
        logger.error(f"Erro no teste Load Queries: {e}")
        results.append(("Load Queries", False))

    try:
        results.append(("Find Examples", test_find_relevant_examples()))
    except Exception as e:
        logger.error(f"Erro no teste Find Examples: {e}")
        results.append(("Find Examples", False))

    try:
        results.append(("Format Prompt", test_format_prompt()))
    except Exception as e:
        logger.error(f"Erro no teste Format Prompt: {e}")
        results.append(("Format Prompt", False))

    try:
        results.append(("Statistics", test_statistics()))
    except Exception as e:
        logger.error(f"Erro no teste Statistics: {e}")
        results.append(("Statistics", False))

    try:
        results.append(("Convenience Function", test_convenience_function()))
    except Exception as e:
        logger.error(f"Erro no teste Convenience Function: {e}")
        results.append(("Convenience Function", False))

    try:
        results.append(("Integration Scenario", test_integration_scenario()))
    except Exception as e:
        logger.error(f"Erro no teste Integration Scenario: {e}")
        results.append(("Integration Scenario", False))

    # Resumo
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*80)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    print("="*80)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
