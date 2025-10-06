"""Teste rápido: UNE 2720"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

adapter = HybridDataAdapter()
engine = DirectQueryEngine(adapter)

print("\nTestando: 'Top 10 produtos UNE 2720'")
result = engine.process_query("Top 10 produtos UNE 2720")

if result.get('type') != 'error':
    print(f"[OK] {result.get('title')}")
    print(f"Summary: {result.get('summary', 'N/A')[:100]}")
else:
    print(f"[ERRO] {result.get('error')}")
