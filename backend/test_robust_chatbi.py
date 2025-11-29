"""
Teste do Sistema Robusto de Chat BI (REGEX)
"""

import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.robust_chatbi import RobustChatBI

def test_robust_chatbi():
    """Testa o sistema robusto de Chat BI"""
    
    print("=" * 60)
    print("TESTE DO SISTEMA ROBUSTO DE CHAT BI (REGEX)")
    print("=" * 60)
    
    # Caminho do Parquet
    parquet_path = backend_path.parent / "data" / "parquet" / "admmat.parquet"
    
    if not parquet_path.exists():
        print(f"ERRO: Arquivo Parquet nao encontrado: {parquet_path}")
        return False
    
    print(f"OK: Arquivo Parquet encontrado: {parquet_path}")
    
    # Inicializar sistema
    print("\nInicializando RobustChatBI...")
    try:
        chatbi = RobustChatBI(parquet_path)
        print("OK: Sistema inicializado com sucesso!")
    except Exception as e:
        print(f"ERRO ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Testes de perguntas
    test_queries = [
        ("ola", "Saudacao"),
        ("quantas vendas tivemos do produto 59294 na une 261 nos ultimos 3 meses", "Vendas com produto, UNE e periodo"),
        ("qual o preco do produto 59294 na une scr", "Preco com produto e UNE"),
        ("vendas do produto 59294", "Vendas apenas com produto"),
    ]
    
    print("\n" + "=" * 60)
    print("TESTANDO PERGUNTAS")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_queries)
    
    for i, (query, description) in enumerate(test_queries, 1):
        print(f"\nTeste {i}: {description}")
        print(f"Pergunta: '{query}'")
        print("-" * 60)
        
        try:
            result = chatbi.process_query(query)
            
            if result["success"]:
                print("SUCESSO!")
                print(f"Resposta: {result['text'][:150]}...")
                success_count += 1
            else:
                print("FALLBACK usado")
                print(f"Resposta: {result['text'][:150]}...")
                
        except Exception as e:
            print(f"ERRO: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {success_count}/{total_count} testes bem-sucedidos")
    print("=" * 60)
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_robust_chatbi()
    sys.exit(0 if success else 1)
