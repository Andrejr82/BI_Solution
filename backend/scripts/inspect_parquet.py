"""Inspect Parquet Schema"""
import pandas as pd
import pyarrow.parquet as pq

file_path = r"C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet"

try:
    with open("parquet_schema.txt", "w", encoding="utf-8") as f:
        # Read schema
        parquet_file = pq.ParquetFile(file_path)
        f.write(f"Schema for {file_path}:\n")
        f.write(str(parquet_file.schema) + "\n\n")
        
        # Read first few rows to check data types and content
        df = pd.read_parquet(file_path).head(5)
        f.write("First 5 rows:\n")
        f.write(str(df) + "\n\n")
        
        f.write("Columns and Types:\n")
        f.write(str(df.dtypes) + "\n")
        
    print("Schema saved to parquet_schema.txt")
    
except Exception as e:
    print(f"Error reading parquet: {e}")
