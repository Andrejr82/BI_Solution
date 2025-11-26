"""
Sync SQL Server to Parquet
Reads data from SQL Server (admmatao) and overwrites the Parquet file.
This ensures the BI Agent always queries the latest data from the source of truth,
but via the performant Parquet interface.
"""
import pandas as pd
import pyodbc
import sys
import time
import os
from pathlib import Path

# Configurações
PARQUET_FILE = Path(r"C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet")
SERVER = r"FAMILIA\SQLJR,1433"
DATABASE = "Projeto_Caculinha" # Alterado para o banco correto
USERNAME = "AgenteVirtual"
PASSWORD = "Cacula@2020"
DRIVER = "ODBC Driver 17 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"TrustServerCertificate=yes;"
)

def sync_data():
    print("\n" + "="*70)
    print("  🔄 SINCRONIZAR SQL SERVER -> PARQUET (Chunked)")
    print("="*70 + "\n")

    start_time = time.time()

    try:
        print("🔌 Conectando ao SQL Server...")
        conn = pyodbc.connect(CONNECTION_STRING)
        
        print("📦 Lendo tabela '[Projeto_Caculinha].[dbo].[admmatao]' em chunks...")
        query = "SELECT * FROM [Projeto_Caculinha].[dbo].[admmatao]"
        
        # Ler em chunks para evitar timeout/memória excessiva
        chunk_size = 100000
        chunks = []
        total_rows = 0
        
        for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
            chunks.append(chunk)
            total_rows += len(chunk)
            print(f"  ...Lido chunk de {len(chunk)} linhas. Total parcial: {total_rows}")
        
        conn.close()
        print(f"✅ Leitura concluída. Total de linhas: {total_rows}")

        print("🔨 Concatenando DataFrames...")
        df = pd.concat(chunks, ignore_index=True)
        
        # Garantir diretório
        PARQUET_FILE.parent.mkdir(parents=True, exist_ok=True)

        print(f"💾 Salvando arquivo Parquet: {PARQUET_FILE}")
        df.to_parquet(PARQUET_FILE, index=False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Sincronização concluída com sucesso em {duration:.2f} segundos!")
        print(f"📂 Arquivo atualizado: {PARQUET_FILE}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a sincronização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_data()
