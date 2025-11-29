"""
Testes de Cenario Completos para RobustChatBI
Verifica todos os fluxos de interacao
"""

import sys
import json
from pathlib import Path
import polars as pl

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.robust_chatbi import RobustChatBI

def run_scenarios():
    print("=" * 60)
    print("TESTES DE CENARIO - ROBUST CHAT BI")
    print("=" * 60)
    
    parquet_path = backend_path.parent / "data" / "parquet" / "admmat.parquet"
    
    if not parquet_path.exists():
        print(f"ERRO: Arquivo parquet nao encontrado em {parquet_path}")
        return False

    # 1. Preparacao de Dados
    print("\n[1] Preparando dados de teste...")
    try:
        lf = pl.scan_parquet(parquet_path)
        
        # Encontrar um produto valido com vendas
        valid_prod = lf.filter(pl.col("MES_01") > 0).select(["PRODUTO", "NOME", "UNE"]).head(1).collect()
        if len(valid_prod) == 0:
            print("ERRO: Nao foi possivel encontrar dados validos no parquet.")
            return False
            
        row = valid_prod.row(0, named=True)
        prod_id = str(row["PRODUTO"])
        prod_name = row["NOME"]
        une_id = str(row["UNE"])
        
        # Encontrar uma UNE onde o produto NAO existe (para testar sugestao)
        # Pegar uma UNE que nao esta na lista de UNEs desse produto
        unes_com_produto = lf.filter(pl.col("PRODUTO") == int(prod_id)).select("UNE").unique().collect()["UNE"].to_list()
        todas_unes = lf.select("UNE").unique().head(20).collect()["UNE"].to_list()
        
        une_sem_produto = None
        for u in todas_unes:
            if u not in unes_com_produto:
                une_sem_produto = str(u)
                break
        
        if not une_sem_produto:
            une_sem_produto = "999999" # Fallback improvavel
            
        print(f"   Produto Teste: {prod_id} ({prod_name})")
        print(f"   UNE com Produto: {une_id}")
        print(f"   UNE sem Produto: {une_sem_produto}")
        
    except Exception as e:
        print(f"ERRO na preparacao de dados: {e}")
        return False

    # 2. Inicializacao
    print("\n[2] Inicializando ChatBI...")
    chatbi = RobustChatBI(parquet_path)
    
    # Funcao auxiliar para normalizar texto (remove acentos e lowercase)
    def normalize(text):
        import unicodedata
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

    # 3. Execucao dos Cenarios
    scenarios = [
        {
            "name": "Saudacao Simples",
            "query": "Ola, bom dia",
            "check": lambda r: "ola" in normalize(r["text"]) or "ajudar" in normalize(r["text"]),
            "desc": "Deve retornar mensagem de boas vindas"
        },
        {
            "name": "Produto Inexistente",
            "query": "vendas do produto 999999",
            "check": lambda r: "nao encontrei" in normalize(r["text"]) or "nao foi encontrado" in normalize(r["text"]),
            "desc": "Deve informar que produto nao existe"
        },
        {
            "name": "Busca por ID (Sucesso)",
            "query": f"quantas vendas do produto {prod_id} na une {une_id}",
            "check": lambda r: r["success"] is True and str(prod_id) in r["text"],
            "desc": "Deve retornar dados de vendas"
        },
        {
            "name": "Busca por Nome (Sucesso)",
            "query": f"vendas de {prod_name} na loja {une_id}",
            "check": lambda r: r["success"] is True,
            "desc": "Deve entender o nome do produto e retornar sucesso"
        },
        {
            "name": "Sugestao de UNE (Produto existe, UNE errada)",
            "query": f"vendas do produto {prod_id} na une {une_sem_produto}",
            "check": lambda r: r["success"] is False and "disponivel nas seguintes unes" in normalize(r["text"]),
            "desc": "Deve sugerir UNEs onde o produto esta disponivel"
        }
    ]
    
    failures = 0
    for i, sc in enumerate(scenarios, 1):
        print(f"\n[Teste {i}] {sc['name']}")
        print(f"   Query: {sc['query']}")
        
        try:
            result = chatbi.process_query(sc['query'])
            
            # Limpar texto para impressao segura
            safe_text = result["text"].encode('ascii', 'ignore').decode('ascii').replace('\n', ' ')
            
            if sc['check'](result):
                print(f"   PASSOU")
                print(f"   Resposta: {safe_text[:100]}...")
            else:
                print(f"   FALHOU")
                print(f"   Esperado: {sc['desc']}")
                print(f"   Obtido: {safe_text}")
                failures += 1
                
        except Exception as e:
            print(f"   ERRO DE EXECUCAO: {e}")
            failures += 1

    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {len(scenarios) - failures}/{len(scenarios)} testes passaram")
    print("=" * 60)
    
    return failures == 0

if __name__ == "__main__":
    success = run_scenarios()
    sys.exit(0 if success else 1)
