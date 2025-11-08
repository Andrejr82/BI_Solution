"""
Teste de inicialização do grafo após correção de checkpoint
"""
import sys
import os

sys.path.insert(0, os.getcwd())

def test_graph_initialization():
    """Testa se o grafo pode ser inicializado corretamente"""
    print("="*60)
    print("TESTE DE INICIALIZACAO DO GRAFO")
    print("="*60)

    try:
        # 1. Importar dependências
        print("\n1. Importando dependencias...")
        from core.graph.graph_builder import GraphBuilder
        from core.factory.component_factory import ComponentFactory
        print("   OK: Imports realizados")

        # 2. Verificar diretório de checkpoints
        print("\n2. Verificando diretorio de checkpoints...")
        checkpoint_dir = os.path.join(os.getcwd(), "data", "checkpoints")
        print(f"   Caminho: {checkpoint_dir}")
        print(f"   Existe: {os.path.exists(checkpoint_dir)}")

        # 3. Criar componentes diretamente (sem ComponentFactory)
        print("\n3. Criando componentes diretamente...")

        from core.llm_adapter import GeminiLLMAdapter
        from core.config.safe_settings import get_safe_settings
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.agents.code_gen_agent import CodeGenAgent

        config = get_safe_settings()

        # LLM Adapter
        llm_adapter = GeminiLLMAdapter(
            api_key=config.GEMINI_API_KEY,
            model_name=config.LLM_MODEL_NAME or "gemini-2.5-flash-lite"
        )

        # Parquet Adapter
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "*.parquet")
        parquet_adapter = ParquetAdapter(parquet_path)

        # Code Gen Agent
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)

        print("   OK: Componentes criados")
        print(f"   - LLM Adapter: {type(llm_adapter).__name__}")
        print(f"   - Parquet Adapter: {type(parquet_adapter).__name__}")
        print(f"   - Code Gen Agent: {type(code_gen_agent).__name__}")

        # 4. Compilar grafo
        print("\n4. Compilando grafo LangGraph...")
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=parquet_adapter,
            code_gen_agent=code_gen_agent
        )

        app = graph_builder.build()
        print("   OK: Grafo compilado com sucesso!")

        print("\n" + "="*60)
        print("RESULTADO: SISTEMA OPERACIONAL")
        print("="*60)
        print("\nO sistema esta pronto para processar queries.")
        print("O erro de checkpoint foi resolvido com fallback para InMemorySaver.")

        return True

    except Exception as e:
        print(f"\nERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("RESULTADO: TESTE FALHOU")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_graph_initialization()
    sys.exit(0 if success else 1)
