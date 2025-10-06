
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.connectivity.parquet_adapter import ParquetAdapter

# Crie uma instância do ParquetAdapter
parquet_path = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'
adapter = ParquetAdapter(file_path=str(parquet_path))

# Carregue o DataFrame e imprima o schema
adapter.connect()
print(adapter.get_schema())
