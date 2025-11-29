"""
Teste Avançado do RobustChatBI v2
Verifica busca por NOME de produto e UNE
"""

import sys
from pathlib import Path
import polars as pl

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.robust_chatbi import RobustChatBI

def test_robust_chatbi_v2():
    print("=" * 60)
    print("TESTE AVANCADO ROBUST CHAT BI (BUSCA POR NOME)")
    print("=" * 60)
    
    parquet_path = backend_path.parent / "data" / "parquet" / "admmat.parquet"
    
    # 1. Descobrir um nome de produto valido para testar
    print("\n1. Buscando dados de exemplo no Parquet...")
    try:
        lf = pl.scan_parquet(parquet_path)
        # Pegar um produto que tenha vendas
        sample = lf.filter(pl.col("MES_01") > 0).select(["PRODUTO", "NOME", "UNE"]).head(1).collect()
        
        if len(sample) == 0:
            print("Nao encontrei dados para teste.")
            return False
            
        row = sample.row(0, named=True)
        prod_id = str(row["PRODUTO"])
        prod_name = row["NOME"]
        une_id = str(row["UNE"])
        
        print(f"Dados encontrados para teste:")
        print(f"   ID: {prod_id}")
        print(f"   Nome: {prod_name}")
        print(f"   UNE: {une_id}")
        
    except Exception as e:
        print(f"Erro ao ler Parquet: {e}")
        return False

    # 2. Inicializar ChatBI
    print("\n2. Inicializando ChatBI...")
    chatbi = RobustChatBI(parquet_path)
    
    # 3. Testes
    tests = [
        {
            "desc": "Busca por ID (Regressao)",
            "query": f"vendas do produto {prod_id} na une {une_id}",
            "expect_success": True
        },
        {
            "desc": "Busca por NOME EXATO",
            "query": f"vendas de {prod_name} na une {une_id}",
            "expect_success": True
        },
        {
            "desc": "Busca por PARTE DO NOME",
            "query": f"vendas de {prod_name[:10]} na une {une_id}", # Primeiros 10 chars
            "expect_success": True
        }
    ]
    
    success_count = 0
    for i, test in enumerate(tests, 1):
        print(f"\nTeste {i}: {test['desc']}")
        print(f"   Query: '{test['query']}'")
        
        try:
            result = chatbi.process_query(test['query'])
            
            if result["success"] == test["expect_success"]:
                print("   PASSOU")
                if result["success"]:
                    # Remover emojis da resposta tambem para evitar erro
                    text_clean = result['text'].encode('ascii', 'ignore').decode('ascii')
                    print(f"   Resposta: {text_clean[:100]}...")
                success_count += 1
            else:
                print(f"   FALHOU (Esperado: {test['expect_success']}, Obtido: {result['success']})")
                text_clean = result['text'].encode('ascii', 'ignore').decode('ascii')
                print(f"   Resposta: {text_clean}")
                
        except Exception as e:
            print(f"   ERRO DE EXECUCAO: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"RESULTADO: {success_count}/{len(tests)} testes passaram")
    print("=" * 60)
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = test_robust_chatbi_v2()
    sys.exit(0 if success else 1)
