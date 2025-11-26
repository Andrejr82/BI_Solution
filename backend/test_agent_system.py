"""
Script de teste para verificar integração do sistema de agentes
"""
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_agent_system():
    """Testa o sistema de agentes"""
    print("=" * 60)
    print("TESTE DO SISTEMA DE AGENTES BI")
    print("=" * 60)
    
    # Teste 1: Verificar GEMINI_API_KEY
    print("\n1. Verificando GEMINI_API_KEY...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   ✅ GEMINI_API_KEY configurada ({api_key[:10]}...)")
    else:
        print("   ❌ GEMINI_API_KEY não encontrada")
        return False
    
    # Teste 2: Importar QueryProcessor
    print("\n2. Importando QueryProcessor...")
    try:
        from app.core.query_processor import QueryProcessor
        print("   ✅ QueryProcessor importado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao importar: {e}")
        return False
    
    # Teste 3: Inicializar QueryProcessor
    print("\n3. Inicializando QueryProcessor...")
    try:
        qp = QueryProcessor()
        print("   ✅ QueryProcessor inicializado")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar: {e}")
        return False
    
    # Teste 4: Processar query simples
    print("\n4. Testando query simples...")
    try:
        result = qp.process_query("Olá, qual seu nome?")
        print(f"   ✅ Query processada")
        print(f"   Tipo de resultado: {result.get('type', 'N/A')}")
        print(f"   Resposta: {result.get('output', 'N/A')[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro ao processar query: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_agent_system()
    sys.exit(0 if success else 1)
