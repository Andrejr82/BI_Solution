"""
Teste do Sistema Inteligente de Chat BI com Gemini
"""

import sys
import os
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Importar sistema inteligente
from app.core.intelligent_chatbi import IntelligentChatBI

def test_chatbi():
    """Testa o sistema inteligente de Chat BI"""
    
    print("=" * 60)
    print("TESTE DO SISTEMA INTELIGENTE DE CHAT BI")
    print("=" * 60)
    
    # Verificar GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERRO: GEMINI_API_KEY não configurada no .env")
        return False
    
    print(f"✅ GEMINI_API_KEY configurada: {api_key[:20]}...")
    
    # Caminho do Parquet
    parquet_path = backend_path.parent / "data" / "parquet" / "admmat.parquet"
    
    if not parquet_path.exists():
        print(f"❌ ERRO: Arquivo Parquet não encontrado: {parquet_path}")
        return False
    
    print(f"✅ Arquivo Parquet encontrado: {parquet_path}")
    
    # Inicializar sistema
    print("\n🔧 Inicializando IntelligentChatBI...")
    try:
        chatbi = IntelligentChatBI(parquet_path)
        print("✅ Sistema inicializado com sucesso!")
    except Exception as e:
        print(f"❌ ERRO ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Testes de perguntas
    test_queries = [
        "olá",
        "quantas vendas tivemos do produto 59294 na une 261 nos ultimos 3 meses",
        "qual o preço do produto 59294",
        "total de vendas",
    ]
    
    print("\n" + "=" * 60)
    print("TESTANDO PERGUNTAS")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Teste {i}: '{query}'")
        print("-" * 60)
        
        try:
            result = chatbi.process_query(query)
            
            if result["success"]:
                print("✅ Sucesso!")
                print(f"Resposta: {result['text'][:200]}...")
            else:
                print("⚠️ Fallback usado")
                print(f"Resposta: {result['text'][:200]}...")
                
        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_chatbi()
    sys.exit(0 if success else 1)
