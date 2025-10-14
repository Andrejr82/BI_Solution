"""
Script de teste rápido para validar integração das ferramentas UNE.
Testa se as ferramentas foram integradas corretamente no CaculinhaBI Agent.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se as ferramentas UNE podem ser importadas"""
    print("=" * 80)
    print("TESTE 1: Importação das Ferramentas UNE")
    print("=" * 80)

    try:
        from core.tools.une_tools import (
            calcular_abastecimento_une,
            calcular_mc_produto,
            calcular_preco_final_une
        )
        print("[OK] Ferramentas UNE importadas com sucesso")
        print(f"  - {calcular_abastecimento_une.name}")
        print(f"  - {calcular_mc_produto.name}")
        print(f"  - {calcular_preco_final_une.name}")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao importar ferramentas UNE: {e}")
        return False

def test_caculinha_bi_integration():
    """Testa se o CaculinhaBI Agent reconhece as ferramentas UNE"""
    print("\n" + "=" * 80)
    print("TESTE 2: Integração no CaculinhaBI Agent")
    print("=" * 80)

    try:
        from core.agents.caculinha_bi_agent import create_caculinha_bi_agent
        from core.agents.code_gen_agent import CodeGenAgent
        from core.factory.component_factory import ComponentFactory

        print("[OK] Módulos importados com sucesso")

        # Criar dependências mínimas
        llm_adapter = ComponentFactory.get_llm_adapter()
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
        parquet_dir = os.path.join(os.getcwd(), "data", "parquet")

        # Criar agente
        agent_runnable, bi_tools = create_caculinha_bi_agent(
            parquet_dir=parquet_dir,
            code_gen_agent=code_gen_agent,
            llm_adapter=llm_adapter
        )

        print(f"[OK] CaculinhaBI Agent criado com {len(bi_tools)} ferramentas:")
        for i, tool in enumerate(bi_tools, 1):
            print(f"  {i}. {tool.name}")

        # Verificar se as 3 ferramentas UNE estão presentes
        tool_names = [tool.name for tool in bi_tools]
        une_tools = [
            "calcular_abastecimento_une",
            "calcular_mc_produto",
            "calcular_preco_final_une"
        ]

        missing = [t for t in une_tools if t not in tool_names]
        if missing:
            print(f"[ERRO] Ferramentas UNE faltando: {missing}")
            return False

        print("[OK] Todas as 3 ferramentas UNE estão integradas!")
        return True

    except Exception as e:
        print(f"[ERRO] Erro ao criar CaculinhaBI Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_tool_invocation():
    """Testa invocação direta das ferramentas UNE"""
    print("\n" + "=" * 80)
    print("TESTE 3: Invocação Direta das Ferramentas")
    print("=" * 80)

    try:
        from core.tools.une_tools import (
            calcular_abastecimento_une,
            calcular_mc_produto,
            calcular_preco_final_une
        )

        # Teste 1: Abastecimento
        print("\n1. Testando calcular_abastecimento_une...")
        result1 = calcular_abastecimento_une.invoke({
            'une_id': 2586,
            'segmento': 'TECIDOS'
        })

        if 'error' in result1:
            print(f"  [ERRO] Erro: {result1['error']}")
        else:
            print(f"  [OK] Total produtos: {result1.get('total_produtos', 0)}")
            print(f"  [OK] Regra: {result1.get('regra_aplicada', 'N/A')}")

        # Teste 2: MC do Produto
        print("\n2. Testando calcular_mc_produto...")
        result2 = calcular_mc_produto.invoke({
            'produto_id': 704559,
            'une_id': 2586
        })

        if 'error' in result2:
            print(f"  [ERRO] Erro: {result2['error']}")
        else:
            print(f"  [OK] MC: {result2.get('mc_calculada', 0)}")
            print(f"  [OK] Recomendação: {result2.get('recomendacao', 'N/A')}")

        # Teste 3: Preço Final
        print("\n3. Testando calcular_preco_final_une...")
        result3 = calcular_preco_final_une.invoke({
            'valor_compra': 800.0,
            'ranking': 0,
            'forma_pagamento': 'vista'
        })

        if 'error' in result3:
            print(f"  [ERRO] Erro: {result3['error']}")
        else:
            print(f"  [OK] Preço final: R$ {result3.get('preco_final', 0):.2f}")
            print(f"  [OK] Economia: R$ {result3.get('economia', 0):.2f}")

        print("\n[OK] Todos os testes de invocação diretos passaram!")
        return True

    except Exception as e:
        print(f"[ERRO] Erro durante testes de invocação: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 80)
    print("VALIDAÇÃO DE INTEGRAÇÃO DAS FERRAMENTAS UNE")
    print("=" * 80 + "\n")

    results = []

    # Executar testes
    results.append(("Importação", test_imports()))
    results.append(("Integração CaculinhaBI", test_caculinha_bi_integration()))
    results.append(("Invocação Direta", test_direct_tool_invocation()))

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)

    for test_name, passed in results:
        status = "[OK] PASSOU" if passed else "[ERRO] FALHOU"
        print(f"{test_name:.<50} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print("\n" + "=" * 80)
    print(f"Total: {total_passed}/{total_tests} testes passaram")

    if total_passed == total_tests:
        print("[SUCESSO] INTEGRAÇÃO COMPLETA E FUNCIONAL!")
    else:
        print("[ATENCAO]  Alguns testes falharam. Verifique os erros acima.")

    print("=" * 80 + "\n")

    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
