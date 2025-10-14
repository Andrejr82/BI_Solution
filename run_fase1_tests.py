import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from core.tools.une_tools import (
    calcular_abastecimento_une,
    calcular_mc_produto,
    calcular_preco_final_une,
)

def run_tests():
    """Executa testes manuais para as ferramentas UNE."""

    print("--- Iniciando testes manuais da Fase 1 ---")

    # Teste 1: calcular_abastecimento_une
    print("\n--- Testando calcular_abastecimento_une ---")
    try:
        result = calcular_abastecimento_une.invoke({"une_id": 2586, "segmento": "TECIDOS"})
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            print("Sucesso! Amostra de resultado:")
            print(f"  Total de produtos: {result.get('total_produtos', 0)}")
            if result.get('total_produtos', 0) > 0:
                print(f"  Primeiro produto: {result['produtos'][0]['nome_produto']}")
    except Exception as e:
        print(f"Falha no teste: {e}")

    # Teste 2: calcular_mc_produto
    print("\n--- Testando calcular_mc_produto ---")
    try:
        result = calcular_mc_produto.invoke({"produto_id": 704559, "une_id": 2586})
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            print("Sucesso! Amostra de resultado:")
            print(f"  Produto: {result.get('nome', 'N/A')}")
            print(f"  MC Calculada: {result.get('mc_calculada', 0):.2f}")
            print(f"  Recomendação: {result.get('recomendacao', 'N/A')}")
    except Exception as e:
        print(f"Falha no teste: {e}")

    # Teste 3: calcular_preco_final_une
    print("\n--- Testando calcular_preco_final_une ---")
    try:
        result = calcular_preco_final_une.invoke({
            "valor_compra": 800.0,
            "ranking": 0,
            "forma_pagamento": "vista",
        })
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            print("Sucesso! Amostra de resultado:")
            print(f"  Valor Original: R$ {result['valor_original']:.2f}")
            print(f"  Preço Final: R$ {result['preco_final']:.2f}")
            print(f"  Economia: R$ {result['economia']:.2f}")
    except Exception as e:
        print(f"Falha no teste: {e}")

    print("\n--- Testes manuais da Fase 1 concluídos ---")

if __name__ == "__main__":
    run_tests()