"""
Script de Teste - Detecção de Queries Amplas FASE 1.2
======================================================
Data: 2025-10-29

Testa o sistema de detecção de queries amplas implementado na FASE 1.2.
"""

import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agents.code_gen_agent import CodeGenAgent


def test_broad_query_detection():
    """
    Testa detecção de queries amplas com casos reais de falha.
    """
    # Mock do agente apenas para teste de detecção
    agent = CodeGenAgent(
        llm_adapter=None,  # Não precisa de LLM para teste de detecção
        data_adapter=None
    )

    # Queries de teste (baseadas em falhas históricas reais)
    test_queries = [
        # ===== QUERIES AMPLAS (devem ser detectadas) =====
        ("Mostre todos os produtos", True),
        ("Liste todas as vendas", True),
        ("Quero ver tudo de estoque", True),
        ("Análise geral de produtos", True),
        ("Todos os dados disponíveis", True),
        ("Ranking de todas as UNEs", True),
        ("Comparar todos os segmentos", True),
        ("Mostre tudo sobre vendas", True),
        ("Dados completos de estoque", True),
        ("Quero ver todas as informações", True),

        # ===== QUERIES ESPECÍFICAS (NÃO devem ser detectadas) =====
        ("Top 10 produtos mais vendidos da UNE NIG", False),
        ("Produtos do segmento ARMARINHO com estoque < 10", False),
        ("Vendas da UNE BEL nos últimos 30 dias", False),
        ("5 fornecedores com maior volume", False),
        ("Estoque da UNE SAO para produtos críticos", False),
        ("Top 20 clientes com maior faturamento", False),
        ("Produtos em falta da UNE RIO", False),
        ("Ranking top 15 UNEs por vendas", False),
        ("Produtos da categoria FERRAMENTAS com preço > 100", False),
        ("Análise de vendas da UNE NIG", False),
    ]

    print("\n" + "="*80)
    print("TESTE DE DETECÇÃO DE QUERIES AMPLAS - FASE 1.2")
    print("="*80 + "\n")

    correct = 0
    total = len(test_queries)
    false_positives = []
    false_negatives = []

    for question, expected_broad in test_queries:
        is_broad, reason = agent.detect_broad_query(question)

        is_correct = is_broad == expected_broad
        status = "✅ CORRETO" if is_correct else "❌ ERRO"
        correct += 1 if is_correct else 0

        print(f"{status} | Detectado={is_broad} (Esperado={expected_broad})")
        print(f"   Query: {question}")
        print(f"   Razão: {reason}")
        print()

        # Rastrear erros
        if not is_correct:
            if is_broad and not expected_broad:
                false_positives.append((question, reason))
            elif not is_broad and expected_broad:
                false_negatives.append((question, reason))

    accuracy = (correct / total) * 100

    print("="*80)
    print(f"RESULTADO: {correct}/{total} corretos ({accuracy:.1f}% de acurácia)")
    print("="*80 + "\n")

    # Relatório detalhado de erros
    if false_positives:
        print("⚠️  FALSOS POSITIVOS (detectou como ampla, mas era específica):")
        for query, reason in false_positives:
            print(f"   - {query}")
            print(f"     Razão: {reason}\n")

    if false_negatives:
        print("⚠️  FALSOS NEGATIVOS (NÃO detectou como ampla, mas era):")
        for query, reason in false_negatives:
            print(f"   - {query}")
            print(f"     Razão: {reason}\n")

    # Critério de sucesso
    success = accuracy >= 90  # 90% de acurácia mínima
    print("\n" + "="*80)
    if success:
        print("✅ TESTE PASSOU! Acurácia >= 90%")
    else:
        print("❌ TESTE FALHOU! Acurácia < 90%")
    print("="*80 + "\n")

    return success

def test_educational_message():
    """
    Testa geração de mensagem educativa.
    """
    agent = CodeGenAgent(
        llm_adapter=None,
        data_adapter=None
    )

    print("\n" + "="*80)
    print("TESTE DE MENSAGEM EDUCATIVA")
    print("="*80 + "\n")

    test_queries = [
        "Mostre todos os produtos",
        "Liste todas as vendas",
        "Ranking de todas as UNEs"
    ]

    for question in test_queries:
        is_broad, reason = agent.detect_broad_query(question)
        if is_broad:
            message = agent.get_educational_message(question, reason)
            print(f"Query: {question}")
            print(f"Mensagem gerada:")
            print("-" * 80)
            print(message)
            print("-" * 80 + "\n")

def test_with_historical_failures():
    """
    Testa com queries históricas que falharam por timeout.
    """
    agent = CodeGenAgent(
        llm_adapter=None,
        data_adapter=None
    )

    print("\n" + "="*80)
    print("TESTE COM QUERIES HISTÓRICAS QUE CAUSARAM TIMEOUT")
    print("="*80 + "\n")

    # Queries reais que causaram timeout (baseado em histórico)
    historical_failures = [
        "Mostre todos os produtos de todas as UNEs",
        "Análise completa de vendas",
        "Dados gerais de estoque",
        "Todas as informações disponíveis",
        "Ranking geral de produtos"
    ]

    detected_count = 0
    for question in historical_failures:
        is_broad, reason = agent.detect_broad_query(question)

        status = "✅ DETECTADO" if is_broad else "❌ NÃO DETECTADO"
        detected_count += 1 if is_broad else 0

        print(f"{status} | {question}")
        print(f"   Razão: {reason}\n")

    detection_rate = (detected_count / len(historical_failures)) * 100
    print("="*80)
    print(f"Taxa de detecção: {detected_count}/{len(historical_failures)} ({detection_rate:.1f}%)")
    print("="*80 + "\n")

    return detection_rate >= 80  # 80% de detecção mínima


if __name__ == "__main__":
    print("\n🚀 INICIANDO BATERIA DE TESTES - FASE 1.2\n")

    results = []

    # Teste 1: Detecção básica
    print("📋 TESTE 1: Detecção Básica")
    results.append(("Detecção Básica", test_broad_query_detection()))

    # Teste 2: Mensagem educativa
    print("\n📋 TESTE 2: Mensagem Educativa")
    test_educational_message()
    results.append(("Mensagem Educativa", True))  # Teste visual

    # Teste 3: Queries históricas
    print("\n📋 TESTE 3: Queries Históricas")
    results.append(("Queries Históricas", test_with_historical_failures()))

    # Relatório final
    print("\n" + "="*80)
    print("RELATÓRIO FINAL DOS TESTES")
    print("="*80 + "\n")

    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*80)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("FASE 1.2 IMPLEMENTADA COM SUCESSO!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Revisar implementação da FASE 1.2")
    print("="*80 + "\n")
