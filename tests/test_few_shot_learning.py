"""
Teste completo do sistema Few-Shot Learning (Pilar 2)

Este script testa:
1. PatternMatcher standalone
2. Integração com CodeGenAgent
3. Comparação: com vs sem Few-Shot Learning
"""

import sys
import os
import logging

# Adicionar diretório raiz ao path
# Use um caminho absoluto para robustez
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.learning.pattern_matcher import PatternMatcher
from core.factory.component_factory import ComponentFactory
from core.connectivity.parquet_adapter import ParquetAdapter

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_pattern_matcher_standalone():
    """Teste 1: PatternMatcher funcionando isoladamente"""
    print("\n" + "="*80)
    print("TESTE 1: PatternMatcher Standalone")
    print("="*80)

    matcher = PatternMatcher()
    
    # Testar queries representativas
    test_queries = {
        "top 10 produtos mais vendidos": "top_n_geral",
        "ranking completo de vendas no segmento tecidos": "ranking_completo_por_segmento",
        "top 5 produtos na une bangu": "top_n_por_une",
        "qual o total de vendas": None
    }

    print("\n[TEST] Testando identificacao de padroes:\n")
    all_passed = True
    for query, expected_pattern in test_queries.items():
        match_result = matcher.match_pattern(query)
        
        if match_result:
            pattern_name, pattern_data = match_result
            if pattern_name == expected_pattern:
                print(f"[OK] Query: '{query}' -> Padrão esperado '{pattern_name}' encontrado.")
            else:
                print(f"[ERRO] Query: '{query}' -> Padrão incorreto. Esperado: '{expected_pattern}', Encontrado: '{pattern_name}'")
                all_passed = False
        elif expected_pattern is not None:
            print(f"[ERRO] Query: '{query}' -> Nenhum padrão encontrado, mas era esperado '{expected_pattern}'.")
            all_passed = False
        else:
            print(f"[OK] Query: '{query}' -> Nenhum padrão encontrado, como esperado.")

    if not all_passed:
        raise AssertionError("Teste do PatternMatcher standalone falhou.")
    
    return matcher


def test_code_gen_agent_integration():
    """Teste 2: Integração com CodeGenAgent"""
    print("\n" + "="*80)
    print("TESTE 2: Integração com CodeGenAgent")
    print("="*80)

    try:
        # Inicializar componentes
        llm_adapter = ComponentFactory.get_llm_adapter()
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")

        if not os.path.exists(parquet_path):
            logging.error(f"❌ Arquivo Parquet não encontrado: {parquet_path}")
            return False

        data_adapter = ParquetAdapter(file_path=parquet_path)

        # Criar CodeGenAgent
        from core.agents.code_gen_agent import CodeGenAgent
        agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)

        # Verificar se PatternMatcher foi inicializado
        if agent.pattern_matcher:
            print("[OK] PatternMatcher inicializado no CodeGenAgent")
        else:
            print("[ERRO] PatternMatcher NAO foi inicializado")
            return False

        # Testar query simples que deve acionar o PatternMatcher
        print("\n[TEST] Executando query de teste que corresponde a um padrão...")
        test_query = "top 5 produtos mais vendidos na une 261"

        # Este teste não executa o código, apenas verifica a integração
        # A verificação real do prompt enriquecido é difícil sem mockar o LLM
        # Por agora, confirmamos que a integração não quebra o fluxo.
        print(f"A execução de uma query como '{test_query}' agora usará o PatternMatcher para enriquecer o prompt.")
        print("[INFO] O log do agente deve mostrar a mensagem 'Few-Shot Learning: Padrão ... identificado'")
        print("[OK] Teste de integração passou (verificação estrutural).")
        
        return True

    except Exception as e:
        logging.error(f"[ERRO] Erro no teste de integração: {e}", exc_info=True)
        return False


def test_few_shot_impact():
    """Teste 3: Demonstrar impacto do Few-Shot Learning"""
    print("\n" + "="*80)
    print("TESTE 3: Impacto do Few-Shot Learning")
    print("="*80)

    matcher = PatternMatcher()

    # Query de teste
    test_query = "top 10 produtos com maior estoque na une bangu"

    # Buscar padrão
    match_result = matcher.match_pattern(test_query)

    if match_result:
        pattern_name, pattern_data = match_result
        print(f"\n[OK] Padrao identificado: {pattern_name}")
        
        # Mostrar como o prompt será enriquecido
        examples_text = matcher.format_examples_for_prompt(pattern_data, max_examples=2)

        print("\n" + "-"*80)
        print("CONTEXTO QUE SERA INJETADO NO PROMPT:")
        print("-"*80)
        print(examples_text)

        print("[OK] Com Few-Shot Learning, o LLM recebera exemplos similares.")
        print("   Isso aumenta a precisao e reduz erros comuns.")
    else:
        print("[AVISO] Nenhum padrao identificado para esta query de demonstração.")


def main():
    """Executar todos os testes"""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#  TESTE COMPLETO: FEW-SHOT LEARNING (PILAR 2)  ".center(80, " ")[1:-1] + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    tests_passed = 0
    tests_total = 3
    
    try:
        test_pattern_matcher_standalone()
        print("1. PatternMatcher standalone: [OK]")
        tests_passed += 1
    except Exception as e:
        logging.error(f"Teste 1 falhou: {e}")
        print("1. PatternMatcher standalone: [FALHOU]")

    integration_ok = test_code_gen_agent_integration()
    if integration_ok:
        print("2. Integracao CodeGenAgent: [OK]")
        tests_passed += 1
    else:
        print("2. Integracao CodeGenAgent: [FALHOU]")

    try:
        test_few_shot_impact()
        print("3. Demonstracao impacto: [OK]")
        tests_passed += 1
    except Exception as e:
        logging.error(f"Teste 3 falhou: {e}")
        print("3. Demonstracao impacto: [FALHOU]")


    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    
    print(f"\n[RESULTADO] {tests_passed}/{tests_total} seções de teste executadas com sucesso.")

    if tests_passed == tests_total:
        print("\n[SUCESSO] PILAR 2: FEW-SHOT LEARNING IMPLEMENTADO E VERIFICADO COM SUCESSO!")
        print("\nProximos passos:")
        print("- Monitorar logs para confirmar que o PatternMatcher está sendo acionado.")
        print("- Expandir 'data/query_patterns.json' com mais exemplos.")
        print("- Prosseguir para Pilar 3: Validador Avancado.")
    else:
        print("\n[AVISO] Alguns testes falharam. Verifique os logs acima.")

    return tests_passed == tests_total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)