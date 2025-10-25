"""
Teste de Validação das Correções de Erros de Memória
=====================================================

Este script testa as correções implementadas para resolver os erros:
1. NameError: name 'parquet_path' is not defined
2. MemoryError durante carregamento de dados
3. UnboundLocalError: cannot access local variable 'time'

Data: 2025-10-24
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_memory_error_queries():
    """Testa queries que falharam com MemoryError"""

    print("=" * 80)
    print("TESTE DE CORREÇÃO DE ERROS DE MEMÓRIA")
    print("=" * 80)

    from core.agents.code_gen_agent import CodeGenAgent
    from core.config.config import Config

    config = Config()
    agent = CodeGenAgent(config=config)

    # Queries que falharam anteriormente
    test_queries = [
        "gere um gráfico de vendas promocionais",
        "Dashboard executivo: KPIs principais por segmento",
        "KPIs principais por segmento une mad",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Testando: '{query}'")
        print("-" * 80)

        try:
            response = agent.generate_and_execute_code(query)

            if response and "erro" not in response.lower():
                print(f"[SUCESSO] Query executada com sucesso")
                results.append({
                    'query': query,
                    'status': 'SUCESSO',
                    'error': None
                })
            else:
                print(f"[AVISO] Query executada mas com possivel erro na resposta")
                results.append({
                    'query': query,
                    'status': 'AVISO',
                    'error': response[:200] if response else 'Resposta vazia'
                })

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"[ERRO] [{error_type}]: {error_msg}")
            results.append({
                'query': query,
                'status': 'ERRO',
                'error': f"{error_type}: {error_msg}"
            })

    # Relatório Final
    print("\n" + "=" * 80)
    print("RELATÓRIO FINAL DE TESTES")
    print("=" * 80)

    success_count = sum(1 for r in results if r['status'] == 'SUCESSO')
    warning_count = sum(1 for r in results if r['status'] == 'AVISO')
    error_count = sum(1 for r in results if r['status'] == 'ERRO')

    print(f"\n[SUCESSO] Sucessos: {success_count}/{len(test_queries)}")
    print(f"[AVISO] Avisos: {warning_count}/{len(test_queries)}")
    print(f"[ERRO] Erros: {error_count}/{len(test_queries)}")

    if error_count > 0:
        print("\nERROS ENCONTRADOS:")
        for r in results:
            if r['status'] == 'ERRO':
                print(f"\n  Query: {r['query']}")
                print(f"  Erro: {r['error']}")

    # Verificar tipos de erro específicos que foram corrigidos
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO DE CORREÇÕES ESPECÍFICAS")
    print("=" * 80)

    has_parquet_path_error = any(
        r['status'] == 'ERRO' and 'parquet_path' in r['error']
        for r in results
    )
    has_time_error = any(
        r['status'] == 'ERRO' and 'UnboundLocalError' in r['error'] and 'time' in r['error']
        for r in results
    )

    print(f"\n[OK] Erro 'parquet_path not defined': {'AINDA PRESENTE [ERRO]' if has_parquet_path_error else 'CORRIGIDO [OK]'}")
    print(f"[OK] Erro 'UnboundLocalError time': {'AINDA PRESENTE [ERRO]' if has_time_error else 'CORRIGIDO [OK]'}")
    print(f"[OK] Fallback otimizado funcionando: {'SIM [OK]' if error_count < len(test_queries) else 'NAO [ERRO]'}")

    return results


def test_parquet_path_fix():
    """Testa especificamente a correção do bug parquet_path"""

    print("\n" + "=" * 80)
    print("TESTE ESPECÍFICO: CORREÇÃO DO BUG parquet_path")
    print("=" * 80)

    import inspect
    from core.agents.code_gen_agent import CodeGenAgent

    # Obter código fonte da função
    source = inspect.getsource(CodeGenAgent._execute_generated_code)

    # Verificar se a correção está presente
    has_parquet_path_init = "parquet_path = None" in source
    has_parquet_path_assignment = "parquet_path = file_path" in source or "parquet_path = parquet_pattern" in source

    print(f"\n[OK] Inicializacao de parquet_path: {'PRESENTE [OK]' if has_parquet_path_init else 'AUSENTE [ERRO]'}")
    print(f"[OK] Atribuicao de parquet_path: {'PRESENTE [OK]' if has_parquet_path_assignment else 'AUSENTE [ERRO]'}")

    if has_parquet_path_init and has_parquet_path_assignment:
        print("\n[SUCESSO] CORRECAO IMPLEMENTADA CORRETAMENTE")
        return True
    else:
        print("\n[ERRO] CORRECAO INCOMPLETA OU AUSENTE")
        return False


def test_time_module_fix():
    """Testa especificamente a correção do UnboundLocalError com 'time'"""

    print("\n" + "=" * 80)
    print("TESTE ESPECÍFICO: CORREÇÃO DO UnboundLocalError 'time'")
    print("=" * 80)

    import inspect
    from core.agents.code_gen_agent import CodeGenAgent

    # Obter código fonte da função
    source = inspect.getsource(CodeGenAgent._execute_generated_code)

    # Verificar se 'time' está no local_scope
    has_time_in_scope = "local_scope['time']" in source

    print(f"\n[OK] Modulo 'time' adicionado ao local_scope: {'SIM [OK]' if has_time_in_scope else 'NAO [ERRO]'}")

    if has_time_in_scope:
        print("\n[SUCESSO] CORRECAO IMPLEMENTADA CORRETAMENTE")
        return True
    else:
        print("\n[ERRO] CORRECAO AUSENTE")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("INICIANDO TESTES DE VALIDAÇÃO DAS CORREÇÕES")
    print("Data: 2025-10-24")
    print("=" * 80)

    # Teste 1: Verificar correções de código
    parquet_ok = test_parquet_path_fix()
    time_ok = test_time_module_fix()

    # Teste 2: Executar queries reais
    results = test_memory_error_queries()

    # Relatório final
    print("\n" + "=" * 80)
    print("RESUMO GERAL")
    print("=" * 80)

    all_fixes_ok = parquet_ok and time_ok
    success_rate = sum(1 for r in results if r['status'] == 'SUCESSO') / len(results) * 100

    print(f"\n[OK] Correcoes de codigo: {'COMPLETAS [OK]' if all_fixes_ok else 'INCOMPLETAS [ERRO]'}")
    print(f"[OK] Taxa de sucesso nas queries: {success_rate:.1f}%")

    if all_fixes_ok and success_rate >= 60:
        print("\n[SUCESSO] CORRECOES VALIDADAS COM SUCESSO!")
    elif success_rate >= 40:
        print("\n[AVISO] CORRECOES PARCIALMENTE VALIDADAS - Melhorias ainda necessarias")
    else:
        print("\n[ERRO] CORRECOES NAO VALIDADAS - Problemas criticos persistem")
