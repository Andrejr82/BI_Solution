
import pyarrow.parquet as pq
import pandas as pd

# Set pandas to display all columns
pd.set_option('display.max_columns', None)

# Path to the Parquet file
file_path = r"C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet"

# Read the Parquet file schema
try:
    parquet_file = pq.ParquetFile(file_path)
    print("Schema:")
    print(parquet_file.schema)

    # Read the first 5 rows to inspect the data
    df = pd.read_parquet(file_path)
    print("\nFirst 5 rows:")
    print(df.head())

except Exception as e:
    print(f"Error reading Parquet file: {e}")
