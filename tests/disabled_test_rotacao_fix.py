"""Teste específico para rotação"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

adapter = ParquetAdapter('data/parquet/admmat.parquet')
engine = DirectQueryEngine(adapter)

result = engine.process_query('Produtos com maior rotação de estoque')
print(f'Query Type: {result.get("query_type")}')
print(f'Result Type: {result.get("type")}')
print(f'Title: {result.get("title", "N/A")}')
