import sys
import os
import polars as pl
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

try:
    from app.core.data_scope_service import DataScopeService
    from app.config.settings import settings

    print("Settings ALLOWED_UNES:", settings.ALLOWED_UNES)

    print("Initializing DataScopeService...")
    service = DataScopeService()
    df = service.admmat_df
    
    print(f"DataFrame loaded. Shape: {df.shape}")
    
    if "UNE" in df.columns:
        print("UNE column type:", df.schema["UNE"])
        print("Sample UNEs:", df.select("UNE").head(5))
    else:
        print("ERROR: UNE column missing!")

    print("Testing get_business_kpis logic...")
    
    # 1. Total de Produtos
    total_produtos = df.select(pl.col("PRODUTO")).n_unique()
    print(f"Total Produtos: {total_produtos}")

    # 3. Produtos em Ruptura logic
    # (pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0) == 0) & ...
    
    df_ruptura = df.filter(
        (pl.col("ESTOQUE_CD").cast(pl.Float64, strict=False).fill_null(0) == 0) &
        (pl.col("ESTOQUE_UNE").cast(pl.Float64, strict=False).fill_null(0) < pl.col("ESTOQUE_LV").cast(pl.Float64, strict=False).fill_null(0)) &
        (pl.col("VENDA_30DD").cast(pl.Float64, strict=False).fill_null(0) > 0)
    )
    print(f"Produtos Ruptura: {len(df_ruptura)}")
    
    print("SUCCESS: Simulation complete without errors.")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
