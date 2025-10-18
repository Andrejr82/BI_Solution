"""
DEMONSTRAÇÃO - Few-Shot Learning em Ação

Este script demonstra exatamente como o Few-Shot Learning
vai melhorar a geração de código da LLM.

Autor: Code Agent
Data: 2025-10-18
"""

import sys
from pathlib import Path

# Adicionar root ao path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from core.learning.few_shot_manager import FewShotManager


def print_separator():
    print("\n" + "="*80 + "\n")


def demo_1_sem_few_shot():
    """Demonstra geração SEM few-shot"""
    print_separator()
    print("DEMONSTRAÇÃO 1: SEM FEW-SHOT LEARNING")
    print_separator()

    user_query = "ranking de vendas de tecidos"

    print("Pergunta do usuário:")
    print(f"  '{user_query}'")
    print()

    print("Prompt enviado para LLM (SEM exemplos):")
    print("─"*80)
    prompt_sem_few_shot = f"""
Você é um assistente de análise de dados.
Gere código Python para responder a pergunta do usuário.

Pergunta: {user_query}

Responda apenas com código Python executável.
"""
    print(prompt_sem_few_shot)
    print("─"*80)

    print()
    print("❌ PROBLEMA:")
    print("  - LLM não sabe qual padrão de código usar")
    print("  - Pode gerar código inconsistente")
    print("  - Pode usar bibliotecas erradas")
    print("  - Pode esquecer best practices")


def demo_2_com_few_shot():
    """Demonstra geração COM few-shot"""
    print_separator()
    print("DEMONSTRAÇÃO 2: COM FEW-SHOT LEARNING")
    print_separator()

    user_query = "ranking de vendas de tecidos"
    intent = "python_analysis"

    print("Pergunta do usuário:")
    print(f"  '{user_query}'")
    print(f"  Intent: {intent}")
    print()

    # Buscar exemplos
    manager = FewShotManager(max_examples=2)
    examples = manager.find_relevant_examples(user_query, intent)

    print(f"Exemplos encontrados: {len(examples)}")
    if examples:
        print("\nTop exemplos:")
        for i, ex in enumerate(examples[:2], 1):
            score = ex.get('similarity_score', 0)
            query = ex.get('query', 'N/A')[:60]
            print(f"  {i}. [{score:.0%}] {query}...")

    # Formatar para prompt
    few_shot_context = manager.format_examples_for_prompt(examples)

    print()
    print("Prompt enviado para LLM (COM exemplos):")
    print("─"*80)

    prompt_com_few_shot = f"""
Você é um assistente de análise de dados.
Gere código Python para responder a pergunta do usuário.

{few_shot_context}

IMPORTANTE: Use os exemplos acima como referência mas adapte para a pergunta atual.

Pergunta: {user_query}

Responda apenas com código Python executável.
"""

    # Mostrar apenas preview
    print(prompt_com_few_shot[:800])
    print("...")
    print(prompt_com_few_shot[-200:])
    print("─"*80)

    print()
    print("✅ VANTAGENS:")
    print("  - LLM vê exemplos reais que funcionaram")
    print("  - Mantém padrão consistente de código")
    print("  - Usa bibliotecas corretas")
    print("  - Aplica best practices automaticamente")
    print("  - Adapta exemplos para query atual")


def demo_3_comparacao():
    """Compara resultados esperados"""
    print_separator()
    print("DEMONSTRAÇÃO 3: COMPARAÇÃO DE RESULTADOS ESPERADOS")
    print_separator()

    print("Query: 'ranking de vendas de tecidos'\n")

    print("❌ SEM FEW-SHOT (código genérico):")
    print("─"*80)
    print("""
import pandas as pd

# Código genérico, pode ou não funcionar
df = pd.read_csv('vendas.csv')
ranking = df.groupby('tecido')['valor'].sum()
print(ranking.sort_values())
""")
    print("─"*80)
    print("Problemas:")
    print("  - Não sabe de onde vem os dados")
    print("  - Nome de coluna pode estar errado")
    print("  - Formato de saída inconsistente")

    print("\n\n✅ COM FEW-SHOT (baseado em exemplos):")
    print("─"*80)
    print("""
import pandas as pd

# Código baseado em exemplos que funcionaram
df = load_data('vendas')  # ✓ Função correta do sistema

# Filtrar apenas tecidos
tecidos = df[df['categoria'] == 'tecidos']

# Agrupar e somar
ranking = tecidos.groupby('produto_nome')['valor_total'].sum()

# Ordenar decrescente
ranking = ranking.sort_values(ascending=False)

# Formatar saída
print("\\n=== RANKING DE VENDAS - TECIDOS ===")
print(ranking.head(10))
print(f"\\nTotal: R$ {ranking.sum():,.2f}")
""")
    print("─"*80)
    print("Vantagens:")
    print("  ✓ Usa load_data() (padrão do sistema)")
    print("  ✓ Nomes de colunas corretos")
    print("  ✓ Filtro de categoria adequado")
    print("  ✓ Formatação de saída bonita")
    print("  ✓ Ordenação correta (decrescente)")


def demo_4_metricas():
    """Mostra métricas do sistema"""
    print_separator()
    print("DEMONSTRAÇÃO 4: MÉTRICAS DO SISTEMA")
    print_separator()

    manager = FewShotManager()
    stats = manager.get_statistics()

    print("Estatísticas do histórico de aprendizado:\n")

    print(f"Total de queries bem-sucedidas: {stats['total_queries']}")
    print(f"Média de linhas retornadas: {stats['avg_rows']:.1f}")

    if stats['intents']:
        print("\nDistribuição por Intent:")
        for intent, count in sorted(stats['intents'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_queries'] * 100) if stats['total_queries'] > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"  {intent:25} {count:3} ({percentage:5.1f}%) {bar}")

    if stats['oldest_query'] and stats['newest_query']:
        print(f"\nPeríodo:")
        print(f"  Mais antiga: {stats['oldest_query']}")
        print(f"  Mais recente: {stats['newest_query']}")

    print("\n💡 Quanto mais o sistema é usado, melhor ele fica!")
    print("   Cada query bem-sucedida vira exemplo para o futuro.")


def demo_5_casos_uso():
    """Mostra diferentes casos de uso"""
    print_separator()
    print("DEMONSTRAÇÃO 5: CASOS DE USO")
    print_separator()

    manager = FewShotManager(max_examples=3)

    casos = [
        ("ranking de vendas de tecidos", "python_analysis"),
        ("transferências entre lojas", "une_transferencias"),
        ("estoque atual de produtos", "une_estoque"),
        ("melhor cliente do mês", "python_analysis"),
    ]

    for i, (query, intent) in enumerate(casos, 1):
        print(f"\n{i}. Query: '{query}'")
        print(f"   Intent: {intent}")

        examples = manager.find_relevant_examples(query, intent)

        if examples:
            print(f"   ✓ Encontrados {len(examples)} exemplos relevantes")
            top = examples[0]
            score = top.get('similarity_score', 0)
            similar_query = top.get('query', 'N/A')[:50]
            print(f"   Mais similar ({score:.0%}): '{similar_query}...'")
        else:
            print(f"   ⚠ Nenhum exemplo encontrado (histórico vazio ou query muito diferente)")


def main():
    """Executa todas as demonstrações"""
    print("\n" + "="*80)
    print(" "*20 + "FEW-SHOT LEARNING - DEMONSTRAÇÃO")
    print("="*80)

    try:
        demo_1_sem_few_shot()
        input("\n[Enter para continuar...]")

        demo_2_com_few_shot()
        input("\n[Enter para continuar...]")

        demo_3_comparacao()
        input("\n[Enter para continuar...]")

        demo_4_metricas()
        input("\n[Enter para continuar...]")

        demo_5_casos_uso()

    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
        return

    print_separator()
    print("RESUMO DA DEMONSTRAÇÃO")
    print_separator()

    print("""
O Few-Shot Learning melhora a geração de código porque:

1. ✅ LLM vê exemplos REAIS que funcionaram
2. ✅ Mantém CONSISTÊNCIA entre respostas
3. ✅ Usa PADRÕES do seu sistema específico
4. ✅ Aprende com SUCESSO anterior
5. ✅ Melhora CONTINUAMENTE com uso

PRÓXIMO PASSO:

1. Execute os testes:
   python scripts/test_few_shot_learning.py

2. Integre no code_gen_agent.py:
   Veja: INTEGRACAO_FEW_SHOT.md

3. Teste com queries reais e veja a melhoria!
""")

    print("="*80)


if __name__ == "__main__":
    main()
