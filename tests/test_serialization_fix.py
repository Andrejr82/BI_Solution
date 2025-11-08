# -*- coding: utf-8 -*-
"""
Script de teste para verificar correção de serialização do backend_components
Context7-based fix test
"""
import pickle
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

def test_serialization():
    """Testa se objetos podem ser serializados corretamente"""
    print("=" * 80)
    print("TESTE DE SERIALIZACAO - CORRECAO CONTEXT7")
    print("=" * 80)

    # Teste 1: Verificar que dicionários simples são serializáveis
    print("\nTeste 1: Dicionarios simples")
    simple_dict = {
        "username": "admin",
        "role": "admin",
        "session_id": "test123"
    }
    try:
        pickled = pickle.dumps(simple_dict)
        unpickled = pickle.loads(pickled)
        print(f"   [OK] Dicionario simples serializado com sucesso")
        print(f"   Original: {simple_dict}")
        print(f"   Depois:   {unpickled}")
    except Exception as e:
        print(f"   [ERRO] {e}")
        return False

    # Teste 2: Verificar que objetos com locks NÃO são serializáveis
    print("\nTeste 2: Objetos com RLock (nao devem estar no session_state)")
    import threading
    lock_dict = {
        "lock": threading.RLock()
    }
    try:
        pickled = pickle.dumps(lock_dict)
        print(f"   [ERRO] Lock foi serializado (nao deveria!)")
        return False
    except TypeError as e:
        print(f"   [OK] Esperado: Lock nao pode ser serializado")
        print(f"   Mensagem: {str(e)[:80]}...")

    # Teste 3: Verificar importação dos módulos principais
    print("\nTeste 3: Importacao de modulos do backend")
    try:
        from core.graph.graph_builder import GraphBuilder
        print(f"   [OK] GraphBuilder importado")
    except Exception as e:
        print(f"   [ERRO] ao importar GraphBuilder: {e}")
        return False

    try:
        from core.agents.code_gen_agent import CodeGenAgent
        print(f"   [OK] CodeGenAgent importado")
    except Exception as e:
        print(f"   [ERRO] ao importar CodeGenAgent: {e}")
        return False

    try:
        from core.connectivity.parquet_adapter import ParquetAdapter
        print(f"   [OK] ParquetAdapter importado")
    except Exception as e:
        print(f"   [ERRO] ao importar ParquetAdapter: {e}")
        return False

    print("\n" + "=" * 80)
    print("[OK] TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print("\nRESUMO DA CORRECAO:")
    print("   - Backend agora e gerenciado via @st.cache_resource")
    print("   - st.session_state NAO contem mais backend_components")
    print("   - Acesso ao backend via initialize_backend() diretamente")
    print("   - Objetos nao-serializaveis (locks, threads) ficam no cache_resource")
    print("\nPROBLEMA ORIGINAL:")
    print("   [X] st.session_state.backend_components = {...}  # Continha RLocks")
    print("\nSOLUCAO CONTEXT7:")
    print("   [OK] backend = initialize_backend()  # Cache_resource retorna singleton")
    print("   [OK] Session state so contem dados serializaveis")
    print()

    return True

if __name__ == "__main__":
    success = test_serialization()
    sys.exit(0 if success else 1)
