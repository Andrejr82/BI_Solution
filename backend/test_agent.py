import asyncio
import sys
import os

# Adicionar o diretório raiz ao path para importar app
sys.path.append(os.getcwd())

async def test():
    print("1. Testando imports básicos...")
    try:
        import polars as pl
        print(f"✅ Polars importado: {pl.__version__}")
    except Exception as e:
        print(f"❌ Erro ao importar Polars: {e}")

    try:
        import langchain
        print(f"✅ Langchain importado: {langchain.__version__}")
    except Exception as e:
        print(f"❌ Erro ao importar Langchain: {e}")

    print("\n2. Testando QueryProcessor...")
    try:
        from app.core.query_processor import QueryProcessor
        qp = QueryProcessor()
        print("✅ QueryProcessor inicializado")
        
        print("\n3. Testando processamento...")
        result = await asyncio.to_thread(qp.process_query, "qual é o preço do produto 25")
        print(f"✅ Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Erro no QueryProcessor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
