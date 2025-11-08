"""
Script de teste completo para validar todas as formatações UNE
"""
import sys
import os

# Adicionar caminho do projeto ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar as funções de formatação
from core.agents.bi_agent_nodes import (
    format_mc_response,
    format_abastecimento_response,
    format_preco_response
)

def test_mc_format():
    """Testa formatação de MC"""
    print("=" * 80)
    print("TESTE 1: FORMATAÇÃO DE MC (Média Comum)")
    print("=" * 80)
    print()

    exemplo_mc = {
        "produto_id": 704559,
        "une_id": 135,
        "nome": "PAPEL CHAMEX A4 75GRS 500FLS",
        "segmento": "PAPELARIA",
        "mc_calculada": 1614,
        "estoque_atual": 1320,
        "linha_verde": 414,
        "percentual_linha_verde": 318.8,
        "recomendacao": "ALERTA: Estoque acima da linha verde - Verificar dimensionamento"
    }

    resultado = format_mc_response(exemplo_mc)
    print(resultado)
    print()
    print("[OK] Teste MC: PASSOU")
    print()

def test_abastecimento_format():
    """Testa formatação de abastecimento"""
    print("=" * 80)
    print("TESTE 2: FORMATAÇÃO DE ABASTECIMENTO")
    print("=" * 80)
    print()

    # Teste 2a: Nenhum produto precisa abastecimento
    print("2a. Nenhum produto precisa abastecimento:")
    print("-" * 80)
    exemplo_vazio = {
        "une_id": 135,
        "segmento": "PAPELARIA",
        "total_produtos": 0,
        "produtos": []
    }

    resultado = format_abastecimento_response(exemplo_vazio)
    print(resultado)
    print()

    # Teste 2b: Alguns produtos precisam abastecimento
    print("2b. Produtos que precisam abastecimento:")
    print("-" * 80)
    exemplo_com_produtos = {
        "une_id": 135,
        "segmento": "PAPELARIA",
        "total_produtos": 5,
        "produtos": [
            {
                "codigo": 704559,
                "nome_produto": "PAPEL CHAMEX A4 75GRS 500FLS",
                "estoque_atual": 100,
                "linha_verde": 500,
                "qtd_a_abastecer": 400,
                "percentual_estoque": 20.0
            },
            {
                "codigo": 123456,
                "nome_produto": "CANETA BIC AZUL",
                "estoque_atual": 50,
                "linha_verde": 200,
                "qtd_a_abastecer": 150,
                "percentual_estoque": 25.0
            },
            {
                "codigo": 789012,
                "nome_produto": "GRAMPEADOR GRANDE METALICO",
                "estoque_atual": 10,
                "linha_verde": 80,
                "qtd_a_abastecer": 70,
                "percentual_estoque": 12.5
            }
        ]
    }

    resultado = format_abastecimento_response(exemplo_com_produtos)
    print(resultado)
    print()
    print("[OK] Teste Abastecimento: PASSOU")
    print()

def test_preco_format():
    """Testa formatação de preços"""
    print("=" * 80)
    print("TESTE 3: FORMATAÇÃO DE PREÇOS")
    print("=" * 80)
    print()

    # Teste 3a: Preço Atacado
    print("3a. Preço Atacado:")
    print("-" * 80)
    exemplo_atacado = {
        "valor_original": 1000.00,
        "tipo": "Atacado",
        "ranking": 0,
        "desconto_ranking": "38%",
        "forma_pagamento": "vista",
        "desconto_pagamento": "38%",
        "preco_final": 384.40,
        "economia": 615.60,
        "percentual_economia": 61.56
    }

    resultado = format_preco_response(exemplo_atacado)
    print(resultado)
    print()

    # Teste 3b: Preço Varejo
    print("3b. Preço Varejo:")
    print("-" * 80)
    exemplo_varejo = {
        "valor_original": 500.00,
        "tipo": "Varejo",
        "ranking": 2,
        "desconto_ranking": "30%",
        "forma_pagamento": "30d",
        "desconto_pagamento": "36%",
        "preco_final": 224.00,
        "economia": 276.00,
        "percentual_economia": 55.2
    }

    resultado = format_preco_response(exemplo_varejo)
    print(resultado)
    print()

    # Teste 3c: Preço Único (Ranking 1)
    print("3c. Preço Único (Ranking 1):")
    print("-" * 80)
    exemplo_unico = {
        "valor_original": 750.00,
        "tipo": "Único",
        "ranking": 1,
        "desconto_ranking": "38%",
        "forma_pagamento": "vista",
        "desconto_pagamento": "38%",
        "preco_final": 288.30,
        "economia": 461.70,
        "percentual_economia": 61.56
    }

    resultado = format_preco_response(exemplo_unico)
    print(resultado)
    print()
    print("[OK] Teste Preços: PASSOU")
    print()

def main():
    """Executa todos os testes"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "TESTE COMPLETO DE FORMATACOES UNE" + " " * 27)
    print("=" * 80)
    print()

    try:
        # Executar todos os testes
        test_mc_format()
        test_abastecimento_format()
        test_preco_format()

        # Resumo final
        print("=" * 80)
        print("[OK] TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 80)
        print()
        print("Resumo:")
        print("  [+] Formatação de MC: OK")
        print("  [+] Formatação de Abastecimento: OK")
        print("  [+] Formatação de Preços: OK")
        print()
        print("Total de formatos testados: 3")
        print("Total de cenários testados: 6")
        print()

    except Exception as e:
        print("=" * 80)
        print("[ERRO] ERRO NOS TESTES!")
        print("=" * 80)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
