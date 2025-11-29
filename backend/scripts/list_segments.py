import polars as pl
import sys
import time
from pathlib import Path

def list_segments():
    parquet_path = Path("data/parquet/admmat.parquet")
    
    if not parquet_path.exists():
        print(f"❌ Arquivo não encontrado: {parquet_path}")
        return

    print(f"📂 Lendo arquivo: {parquet_path} ...")
    start = time.time()
    
    # Scan (Lazy) para ser instantâneo mesmo em arquivos gigantes
    df = pl.scan_parquet(parquet_path)
    
    # Obter valores únicos de NOMESEGMENTO
    segments = df.select(pl.col("NOMESEGMENTO").unique()).collect().to_series().to_list()
    
    # Ordenar e limpar vazios
    segments = sorted([s for s in segments if s])
    
    end = time.time()
    
    print("\n📋 SEGMENTOS DISPONÍVEIS NO PARQUET:")
    print("=" * 50)
    for seg in segments:
        print(f"  • {seg}")
    print("=" * 50)
    print(f"\n⏱️ Tempo de leitura: {(end - start):.4f} segundos")
    print(f"ℹ️ Use estes nomes EXATOS ao cadastrar usuários.")

if __name__ == "__main__":
    list_segments()
