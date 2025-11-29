"""
Análise Profunda da Estrutura de Dados e Tipos
Verifica compatibilidade com o Agente de BI
"""

import polars as pl
from pathlib import Path
import sys

def analyze_data_structure():
    print("=" * 60)
    print("ANÁLISE DE ESTRUTURA DE DADOS E TIPOS")
    print("=" * 60)
    
    # Caminho do Parquet
    parquet_path = Path("data/parquet/admmat.parquet")
    if not parquet_path.exists():
        # Tentar caminho relativo ao backend
        parquet_path = Path("../data/parquet/admmat.parquet")
    
    print(f"Arquivo: {parquet_path}")
    
    try:
        # Ler schema e amostra
        lf = pl.scan_parquet(parquet_path)
        schema = lf.collect_schema()
        
        print("\n1. SCHEMA E TIPOS DE DADOS:")
        print("-" * 60)
        for name, dtype in schema.items():
            print(f"{name:<15} | {str(dtype):<15}")
            
        # Verificar colunas críticas para o agente
        print("\n2. ANÁLISE DE COLUNAS CRÍTICAS:")
        print("-" * 60)
        
        # PRODUTO
        if "PRODUTO" in schema:
            dtype = schema["PRODUTO"]
            print(f"PRODUTO: {dtype}")
            if str(dtype) in ["Int64", "Int32"]:
                print("✅ Tipo correto (Inteiro). Agente deve converter input string para int.")
            elif str(dtype) == "Utf8":
                print("⚠️ Tipo String. Agente deve comparar como string.")
            else:
                print(f"❌ Tipo inesperado: {dtype}")
        else:
            print("❌ Coluna PRODUTO não encontrada!")

        # UNE
        if "UNE" in schema:
            dtype = schema["UNE"]
            print(f"UNE: {dtype}")
            if str(dtype) in ["Int64", "Int32"]:
                print("✅ Tipo Inteiro. UNEs são numéricas.")
            elif str(dtype) == "Utf8":
                print("ℹ️ Tipo String. UNEs podem conter letras.")
        else:
            print("❌ Coluna UNE não encontrada!")
            
        # MESES
        mes_cols = [c for c in schema.names() if c.startswith("MES_")]
        print(f"\nColunas de Mês encontradas: {len(mes_cols)}")
        if mes_cols:
            dtype = schema[mes_cols[0]]
            print(f"Tipo dos meses ({mes_cols[0]}): {dtype}")
            if str(dtype) in ["Float64", "Float32", "Int64"]:
                print("✅ Tipo numérico. Cálculos de soma/média funcionarão.")
            else:
                print("❌ Tipo não numérico! Cálculos falharão.")
        
        # Amostra de dados
        print("\n3. AMOSTRA DE DADOS (Top 5):")
        print("-" * 60)
        df_head = lf.head(5).collect()
        print(df_head)
        
        # Teste de consulta simulada
        print("\n4. SIMULAÇÃO DE CONSULTA DO AGENTE:")
        print("-" * 60)
        
        # Simular busca de produto 59294
        print("Buscando produto 59294...")
        
        # Tentar como int
        try:
            count_int = lf.filter(pl.col("PRODUTO") == 59294).select(pl.count()).collect().item()
            print(f"Busca como INT: {count_int} registros encontrados")
        except Exception as e:
            print(f"Busca como INT falhou: {e}")
            
        # Tentar como string
        try:
            count_str = lf.filter(pl.col("PRODUTO").cast(pl.Utf8) == "59294").select(pl.count()).collect().item()
            print(f"Busca como STRING: {count_str} registros encontrados")
        except Exception as e:
            print(f"Busca como STRING falhou: {e}")

    except Exception as e:
        print(f"❌ Erro fatal na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_data_structure()
