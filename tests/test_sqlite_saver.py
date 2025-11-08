"""
Teste de validação do SqliteSaver após correção
"""
import sys
import os

sys.path.insert(0, os.getcwd())

def test_sqlite_saver():
    """Testa se o SqliteSaver está funcionando corretamente"""
    print("="*60)
    print("TESTE SQLITE SAVER - VALIDACAO")
    print("="*60)

    try:
        # 1. Importar GraphBuilder
        print("\n1. Importando GraphBuilder...")
        from core.graph.graph_builder import GraphBuilder, SQLITE_AVAILABLE, SqliteSaver
        print("   OK: GraphBuilder importado")
        print(f"   SQLITE_AVAILABLE: {SQLITE_AVAILABLE}")
        print(f"   SqliteSaver: {SqliteSaver}")

        # 2. Verificar se SqliteSaver está disponível
        if not SQLITE_AVAILABLE:
            print("\n   AVISO: SqliteSaver não está disponível")
            print("   Sistema usará InMemorySaver como fallback")
            return False

        # 3. Testar criação de SqliteSaver
        print("\n2. Testando criação de SqliteSaver...")
        checkpoint_dir = os.path.join(os.getcwd(), "data", "checkpoints")
        checkpoint_db = os.path.join(checkpoint_dir, "test_checkpoint.db")

        # Criar checkpointer
        checkpointer = SqliteSaver.from_conn_string(checkpoint_db)
        print(f"   OK: SqliteSaver criado com sucesso")
        print(f"   DB: {checkpoint_db}")

        # 4. Limpar arquivo de teste
        if os.path.exists(checkpoint_db):
            os.remove(checkpoint_db)
            print("   OK: Arquivo de teste removido")

        print("\n" + "="*60)
        print("RESULTADO: SQLITE SAVER FUNCIONANDO CORRETAMENTE")
        print("="*60)
        print("\nO sistema pode usar checkpointing persistente!")

        return True

    except Exception as e:
        print(f"\nERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("RESULTADO: USANDO FALLBACK (InMemorySaver)")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_sqlite_saver()
    sys.exit(0 if success else 1)
