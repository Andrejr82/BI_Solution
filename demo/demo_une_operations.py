"""
Demo Script - Operações UNE
Demonstra o uso das 3 ferramentas UNE implementadas

Execute: python demo/demo_une_operations.py
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.une_tools import (
    calcular_abastecimento_une,
    calcular_mc_produto,
    calcular_preco_final_une
)


def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title):
    """Imprime seção formatada"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def demo_1_abastecimento_basico():
    """
    DEMO 1: Cálculo de Abastecimento Básico
    Consulta produtos que precisam reposição em uma UNE específica
    """
    print_header("DEMO 1: Cálculo de Abastecimento Básico")

    print("Consulta: Quais produtos precisam abastecimento na UNE 2586?")
    print("\nCódigo:")
    print("""
result = calcular_abastecimento_une.invoke({
    'une_id': 2586
})
""")

    result = calcular_abastecimento_une.invoke({
        'une_id': 2586
    })

    print("\nResultado:")
    print(f"  Total de produtos: {result.get('total_produtos', 0)}")
    print(f"  Regra aplicada: {result.get('regra_aplicada', 'N/A')}")
    print(f"  UNE: {result.get('une_id', 'N/A')}")
    print(f"  Segmento: {result.get('segmento', 'N/A')}")

    if result.get('total_produtos', 0) > 0:
        print(f"\n  Top 5 produtos que mais precisam abastecimento:")
        for i, produto in enumerate(result['produtos'][:5], 1):
            print(f"    {i}. Código: {produto['codigo']} | "
                  f"Nome: {produto['nome_produto'][:30]}... | "
                  f"Qtd: {produto['qtd_a_abastecer']:.0f} | "
                  f"Estoque: {produto['percentual_estoque']:.1f}%")


def demo_2_abastecimento_com_filtro():
    """
    DEMO 2: Abastecimento com Filtro de Segmento
    Filtra produtos de um segmento específico que precisam reposição
    """
    print_header("DEMO 2: Abastecimento com Filtro de Segmento")

    print("Consulta: Mostre produtos TECIDOS para reposição na UNE 2586")
    print("\nCódigo:")
    print("""
result = calcular_abastecimento_une.invoke({
    'une_id': 2586,
    'segmento': 'TECIDOS'
})
""")

    result = calcular_abastecimento_une.invoke({
        'une_id': 2586,
        'segmento': 'TECIDOS'
    })

    print("\nResultado:")
    print(f"  Total de produtos TECIDOS: {result.get('total_produtos', 0)}")
    print(f"  UNE: {result.get('une_id', 'N/A')}")
    print(f"  Segmento filtrado: {result.get('segmento', 'N/A')}")

    if result.get('total_produtos', 0) > 0:
        print(f"\n  Top 3 produtos TECIDOS:")
        for i, produto in enumerate(result['produtos'][:3], 1):
            print(f"    {i}. {produto['nome_produto'][:40]}")
            print(f"       Estoque atual: {produto['estoque_atual']:.0f} | "
                  f"Linha verde: {produto['linha_verde']:.0f} | "
                  f"A abastecer: {produto['qtd_a_abastecer']:.0f}")


def demo_3_mc_produto():
    """
    DEMO 3: Consulta de MC (Média Comum) com Recomendações
    Verifica MC de um produto e recebe recomendação inteligente
    """
    print_header("DEMO 3: Consulta de MC com Recomendações Inteligentes")

    print("Consulta: Qual a MC do produto 704559 na UNE 2586?")
    print("\nCódigo:")
    print("""
result = calcular_mc_produto.invoke({
    'produto_id': 704559,
    'une_id': 2586
})
""")

    result = calcular_mc_produto.invoke({
        'produto_id': 704559,
        'une_id': 2586
    })

    if 'error' not in result:
        print("\nResultado:")
        print(f"  Produto: {result.get('nome', 'N/A')}")
        print(f"  Código: {result.get('produto_id', 'N/A')}")
        print(f"  Segmento: {result.get('segmento', 'N/A')}")
        print(f"  UNE: {result.get('une_id', 'N/A')}")
        print(f"\n  MC Calculada: {result.get('mc_calculada', 0):.2f}")
        print(f"  Estoque Atual: {result.get('estoque_atual', 0):.2f}")
        print(f"  Linha Verde: {result.get('linha_verde', 0):.2f}")
        print(f"  Percentual da LV: {result.get('percentual_linha_verde', 0):.2f}%")
        print(f"\n  [RECOMENDAÇÃO]: {result.get('recomendacao', 'N/A')}")
    else:
        print(f"\nErro: {result['error']}")


def demo_4_preco_atacado():
    """
    DEMO 4: Cálculo de Preço Atacado
    Calcula preço para venda acima de R$ 750 (atacado)
    """
    print_header("DEMO 4: Cálculo de Preço Atacado")

    print("Consulta: Calcule o preço de R$ 800 ranking 0 a vista")
    print("\nCódigo:")
    print("""
result = calcular_preco_final_une.invoke({
    'valor_compra': 800.0,
    'ranking': 0,
    'forma_pagamento': 'vista'
})
""")

    result = calcular_preco_final_une.invoke({
        'valor_compra': 800.0,
        'ranking': 0,
        'forma_pagamento': 'vista'
    })

    if 'error' not in result:
        print("\nResultado:")
        print(f"  Valor Original: R$ {result['valor_original']:.2f}")
        print(f"  Tipo de Preço: {result['tipo']}")
        print(f"  Ranking: {result['ranking']} ({result['desconto_ranking']})")
        print(f"  Forma de Pagamento: {result['forma_pagamento']} ({result['desconto_pagamento']})")
        print(f"\n  PREÇO FINAL: R$ {result['preco_final']:.2f}")
        print(f"  ECONOMIA: R$ {result['economia']:.2f} ({result['percentual_economia']:.2f}%)")
        print(f"\n  Detalhamento:")
        for parte in result['detalhamento'].split(' | '):
            print(f"    - {parte}")
    else:
        print(f"\nErro: {result['error']}")


def demo_5_preco_varejo():
    """
    DEMO 5: Cálculo de Preço Varejo
    Calcula preço para venda abaixo de R$ 750 (varejo)
    """
    print_header("DEMO 5: Cálculo de Preço Varejo")

    print("Consulta: Qual o preço final de R$ 600 ranking 2 pagando em 30 dias?")
    print("\nCódigo:")
    print("""
result = calcular_preco_final_une.invoke({
    'valor_compra': 600.0,
    'ranking': 2,
    'forma_pagamento': '30d'
})
""")

    result = calcular_preco_final_une.invoke({
        'valor_compra': 600.0,
        'ranking': 2,
        'forma_pagamento': '30d'
    })

    if 'error' not in result:
        print("\nResultado:")
        print(f"  Valor Original: R$ {result['valor_original']:.2f}")
        print(f"  Tipo de Preço: {result['tipo']}")
        print(f"  Ranking: {result['ranking']} ({result['desconto_ranking']})")
        print(f"  Forma de Pagamento: {result['forma_pagamento']} ({result['desconto_pagamento']})")
        print(f"\n  PREÇO FINAL: R$ {result['preco_final']:.2f}")
        print(f"  ECONOMIA: R$ {result['economia']:.2f} ({result['percentual_economia']:.2f}%)")
    else:
        print(f"\nErro: {result['error']}")


def demo_6_comparacao_formas_pagamento():
    """
    DEMO 6: Comparação de Formas de Pagamento
    Compara o mesmo valor com diferentes formas de pagamento
    """
    print_header("DEMO 6: Comparação de Formas de Pagamento")

    print("Consulta: Compare R$ 1000 ranking 3 em todas as formas de pagamento")
    print("\nCódigo:")
    print("""
formas = ['vista', '30d', '90d', '120d']
for forma in formas:
    result = calcular_preco_final_une.invoke({
        'valor_compra': 1000.0,
        'ranking': 3,  # Sem desconto de ranking
        'forma_pagamento': forma
    })
""")

    print("\nResultado:")
    print("\n  Tabela Comparativa:")
    print(f"  {'Forma Pagamento':<20} {'Desconto':<12} {'Preço Final':<15} {'Economia':<15}")
    print(f"  {'-'*20} {'-'*12} {'-'*15} {'-'*15}")

    formas = ['vista', '30d', '90d', '120d']
    for forma in formas:
        result = calcular_preco_final_une.invoke({
            'valor_compra': 1000.0,
            'ranking': 3,  # Sem desconto de ranking para comparar apenas forma de pagamento
            'forma_pagamento': forma
        })

        if 'error' not in result:
            print(f"  {forma:<20} {result['desconto_pagamento']:<12} "
                  f"R$ {result['preco_final']:<12.2f} R$ {result['economia']:<12.2f}")

    print("\n  Observação: Ranking 3 não tem desconto de ranking,")
    print("              então a diferença é apenas da forma de pagamento.")


def demo_7_workflow_completo():
    """
    DEMO 7: Workflow Completo
    Demonstra um fluxo típico de uso das 3 ferramentas
    """
    print_header("DEMO 7: Workflow Completo - Do Abastecimento ao Preço")

    print("Cenário: Gerente quer reabastecer TECIDOS na UNE 2586 e calcular preço da compra")

    # Passo 1: Verificar o que precisa abastecer
    print_section("PASSO 1: Verificar Produtos para Abastecimento")
    abastecimento = calcular_abastecimento_une.invoke({
        'une_id': 2586,
        'segmento': 'TECIDOS'
    })

    print(f"  Total de produtos TECIDOS para abastecer: {abastecimento['total_produtos']}")

    if abastecimento['total_produtos'] > 0:
        primeiro_produto = abastecimento['produtos'][0]
        print(f"\n  Produto mais urgente:")
        print(f"    Código: {primeiro_produto['codigo']}")
        print(f"    Nome: {primeiro_produto['nome_produto']}")
        print(f"    Quantidade a abastecer: {primeiro_produto['qtd_a_abastecer']:.0f}")

        # Passo 2: Verificar MC do produto
        print_section("PASSO 2: Consultar MC do Produto Mais Urgente")
        mc_result = calcular_mc_produto.invoke({
            'produto_id': primeiro_produto['codigo'],
            'une_id': 2586
        })

        if 'error' not in mc_result:
            print(f"  MC Calculada: {mc_result['mc_calculada']:.2f}")
            print(f"  Estoque Atual: {mc_result['estoque_atual']:.0f}")
            print(f"  Linha Verde: {mc_result['linha_verde']:.0f}")
            print(f"  Recomendação: {mc_result['recomendacao']}")

        # Passo 3: Calcular preço da compra
        print_section("PASSO 3: Calcular Preço da Compra de Reposição")
        valor_compra = primeiro_produto['qtd_a_abastecer'] * 10  # Exemplo: R$10/unidade

        print(f"  Supondo R$ 10,00 por unidade:")
        print(f"  Valor da compra: {primeiro_produto['qtd_a_abastecer']:.0f} × R$ 10 = R$ {valor_compra:.2f}")

        preco_result = calcular_preco_final_une.invoke({
            'valor_compra': valor_compra,
            'ranking': 0,  # TECIDOS = ranking 0
            'forma_pagamento': 'vista'
        })

        if 'error' not in preco_result:
            print(f"\n  Tipo de preço: {preco_result['tipo']}")
            print(f"  Preço final: R$ {preco_result['preco_final']:.2f}")
            print(f"  Economia: R$ {preco_result['economia']:.2f}")

        print_section("RESUMO DA OPERAÇÃO")
        print(f"  1. Identificados {abastecimento['total_produtos']} produtos TECIDOS para abastecer")
        print(f"  2. Produto mais urgente: {primeiro_produto['nome_produto'][:40]}")
        print(f"  3. MC do produto: {mc_result.get('mc_calculada', 0):.2f}")
        print(f"  4. Valor da compra: R$ {valor_compra:.2f}")
        print(f"  5. Preço final com descontos: R$ {preco_result.get('preco_final', 0):.2f}")
        print(f"  6. Economia total: R$ {preco_result.get('economia', 0):.2f}")


def main():
    """Executa todas as demos"""
    print("\n")
    print("+" + "-" * 78 + "+")
    print("|" + " " * 20 + "DEMO - OPERAÇÕES UNE" + " " * 38 + "|")
    print("|" + " " * 15 + "Agent_Solution_BI - MVP v1.0.0" + " " * 33 + "|")
    print("+" + "-" * 78 + "+")

    try:
        # Executar todas as demos
        demo_1_abastecimento_basico()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_2_abastecimento_com_filtro()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_3_mc_produto()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_4_preco_atacado()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_5_preco_varejo()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_6_comparacao_formas_pagamento()
        # input("\nPressione ENTER para continuar para a próxima demo...")

        demo_7_workflow_completo()

        # Mensagem final
        print_header("FIM DAS DEMOS")
        print("Todas as 7 demos foram executadas com sucesso!")
        print("\nPróximos passos:")
        print("  1. Teste as ferramentas na interface Streamlit: streamlit run streamlit_app.py")
        print("  2. Execute os testes automatizados: pytest tests/test_une_operations.py -v")
        print("  3. Leia a documentação completa: docs/IMPLEMENTACAO_UNE_MVP.md")
        print("\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\nErro durante execução da demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
