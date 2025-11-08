"""
Teste de importação do módulo SqliteSaver e inicialização do GraphBuilder.
Este teste valida que todos os módulos necessários podem ser importados corretamente.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sqlite_import():
    """Testa a importação do SqliteSaver"""
    print("=" * 60)
    print("TESTE 1: Importação do SqliteSaver")
    print("=" * 60)

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        print("[OK] SqliteSaver importado com sucesso!")
        print(f"  Localizacao: {SqliteSaver.__module__}")
        return True
    except ImportError as e:
        print(f"[ERRO] Erro ao importar SqliteSaver: {e}")
        return False

def test_graph_builder_import():
    """Testa a importação do GraphBuilder"""
    print("\n" + "=" * 60)
    print("TESTE 2: Importação do GraphBuilder")
    print("=" * 60)

    try:
        from core.graph.graph_builder import GraphBuilder
        print("[OK] GraphBuilder importado com sucesso!")
        print(f"  Localizacao: {GraphBuilder.__module__}")
        return True
    except ImportError as e:
        print(f"[ERRO] Erro ao importar GraphBuilder: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checkpoint_creation():
    """Testa a criação de um checkpointer"""
    print("\n" + "=" * 60)
    print("TESTE 3: Criação de Checkpointer")
    print("=" * 60)

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        # Testar criação com memória
        with SqliteSaver.from_conn_string(":memory:") as checkpointer:
            print("[OK] Checkpointer em memoria criado com sucesso!")
            print(f"  Tipo: {type(checkpointer)}")

        # Testar criação com arquivo
        test_db = "test_checkpoint.db"
        with SqliteSaver.from_conn_string(test_db) as checkpointer:
            print(f"[OK] Checkpointer com arquivo criado com sucesso!")
            print(f"  Arquivo: {test_db}")

        # Limpar arquivo de teste
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"  Arquivo de teste removido")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao criar checkpointer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_builder_initialization():
    """Testa a inicialização completa do GraphBuilder"""
    print("\n" + "=" * 60)
    print("TESTE 4: Inicialização do GraphBuilder")
    print("=" * 60)

    try:
        from core.graph.graph_builder import GraphBuilder
        from core.llm_base import BaseLLMAdapter
        from core.connectivity.hybrid_adapter import HybridDataAdapter
        from core.agents.code_gen_agent import CodeGenAgent

        print("[OK] Todos os modulos necessarios importados!")
        print("  - GraphBuilder")
        print("  - BaseLLMAdapter")
        print("  - HybridDataAdapter")
        print("  - CodeGenAgent")

        print("\nNOTA: Para testar a construcao completa do grafo, seria necessario")
        print("      inicializar todos os adaptadores, o que requer configuracao")
        print("      completa do ambiente.")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao importar modulos necessarios: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO: LangGraph SqliteSaver")
    print("=" * 60)

    results = []

    # Executar testes
    results.append(("Importação SqliteSaver", test_sqlite_import()))
    results.append(("Importação GraphBuilder", test_graph_builder_import()))
    results.append(("Criação Checkpointer", test_checkpoint_creation()))
    results.append(("Inicialização GraphBuilder", test_graph_builder_initialization()))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for name, result in results:
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, result in results if result)
    total_tests = len(results)

    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {total_passed}/{total_tests} testes passaram")
    print("=" * 60)

    if total_passed == total_tests:
        print("\n[OK] TODOS OS TESTES PASSARAM!")
        print("  O modulo SqliteSaver esta corretamente instalado e funcionando.")
        return 0
    else:
        print(f"\n[ERRO] {total_tests - total_passed} TESTE(S) FALHARAM!")
        print("  Verifique os erros acima para mais detalhes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
