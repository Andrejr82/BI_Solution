import sys
import os
from pathlib import Path
import polars as pl
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_insights")

# Adicionar o diretório raiz ao path para importar módulos do backend
sys.path.append(str(Path.cwd() / "backend"))

def test_parquet_structure():
    """Verifica se as colunas necessárias existem no Parquet"""
    parquet_path = Path("backend/data/parquet/admmat.parquet")
    
    if not parquet_path.exists():
        logger.error(f"❌ Arquivo Parquet não encontrado: {parquet_path}")
        return False

    try:
        # Ler apenas o schema para ser rápido
        df = pl.scan_parquet(parquet_path)
        schema = df.collect_schema()
        columns = schema.names()
        
        logger.info(f"✅ Arquivo Parquet encontrado. Colunas disponíveis: {len(columns)}")
        
        # Colunas críticas para os Insights
        critical_cols = {
            "Segmento": ["NOMESEGMENTO", "SEGMENTO", "CATEGORIA"],
            "Vendas": ["VENDA_30DD", "QtdVenda", "VENDA"],
            "Receita": ["MES_01", "VrVenda", "RECEITA"],
            "Estoque": ["ESTOQUE_UNE", "QtdEstoque"],
            "Produto Nome": ["NOME", "NOMPRODUTO"],
            "Produto ID": ["PRODUTO", "CODPRODUTO"]
        }
        
        found_map = {}
        
        print("\n--- Verificação de Colunas ---")
        all_good = True
        for friendly_name, candidates in critical_cols.items():
            found = None
            for c in candidates:
                if c in columns:
                    found = c
                    break
            
            if found:
                print(f"✅ {friendly_name}: Encontrado como '{found}'")
                found_map[friendly_name] = found
            else:
                print(f"❌ {friendly_name}: NÃO ENCONTRADO (Procurado: {candidates})")
                all_good = False
        
        if not all_good:
            logger.error("❌ Faltam colunas críticas para gerar os insights.")
            return False
            
        return verify_data_logic(parquet_path, found_map)

    except Exception as e:
        logger.error(f"❌ Erro ao ler Parquet: {e}")
        return False

def verify_data_logic(parquet_path, col_map):
    """Testa a lógica exata de agregação usada no endpoint"""
    print("\n--- Testando Lógica de Agregação (Polars) ---")
    
    try:
        df = pl.read_parquet(parquet_path)
        
        # 1. Teste de Vendas por Segmento
        c_seg = col_map["Segmento"]
        c_sales = col_map["Vendas"]
        c_rev = col_map["Receita"]
        
        print(f"Simulando agregação por {c_seg}...")
        
        df_sales = df.group_by(c_seg).agg([
            pl.col(c_sales).sum().alias("total_vendas"),
            pl.col(c_rev).sum().alias("receita_total")
        ]).sort("receita_total", descending=True).head(5)
        
        print("Top 5 Segmentos:")
        print(df_sales)
        
        if df_sales.height == 0:
            logger.warning("⚠️ Agregação retornou 0 linhas.")
        else:
            logger.info("✅ Lógica de Vendas: SUCESSO")

        return True
        
    except Exception as e:
        logger.error(f"❌ Falha na lógica de processamento: {e}")
        return False

if __name__ == "__main__":
    success = test_parquet_structure()
    if success:
        print("\n✅ DIAGNÓSTICO CONCLUÍDO: O backend tem tudo para funcionar.")
        sys.exit(0)
    else:
        print("\n❌ DIAGNÓSTICO FALHOU: Corrija os nomes das colunas no código.")
        sys.exit(1)
