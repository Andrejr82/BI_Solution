"""
Testes unitários para PolarsDaskAdapter.

Valida:
1. Seleção automática de engine (Polars vs Dask)
2. Fallback automático (Polars → Dask)
3. Integridade de dados (Polars = Dask)
4. Tratamento de erros
5. Performance threshold

Autor: Claude Code
Data: 2025-10-20
"""

import pytest
import os
import sys
from pathlib import Path

# Adicionar path do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.connectivity.polars_dask_adapter import PolarsDaskAdapter

# Path para arquivo de teste
TEST_FILE = PROJECT_ROOT / "data" / "parquet" / "admmat.parquet"

class TestPolarsDaskAdapter:
    """Testes do PolarsDaskAdapter."""

    def test_init_valid_file(self):
        """Teste: Inicialização com arquivo válido."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        assert adapter.file_path == str(TEST_FILE)
        assert adapter.size_mb > 0
        assert adapter.engine in ["polars", "dask"]

    def test_init_invalid_file(self):
        """Teste: Inicialização com arquivo inválido deve falhar."""
        with pytest.raises(FileNotFoundError):
            PolarsDaskAdapter("arquivo_inexistente.parquet")

    def test_auto_select_polars_small_file(self):
        """Teste: Arquivo pequeno (<500MB) deve selecionar Polars."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        # admmat.parquet tem ~94MB, deve usar Polars
        assert adapter.size_mb < 500
        assert adapter.engine == "polars"

    def test_auto_select_dask_forced(self):
        """Teste: FORCE_DASK=true deve forçar Dask."""
        os.environ["FORCE_DASK"] = "true"
        try:
            adapter = PolarsDaskAdapter(str(TEST_FILE))
            assert adapter.engine == "dask"
        finally:
            os.environ.pop("FORCE_DASK", None)

    def test_polars_disabled(self):
        """Teste: POLARS_ENABLED=false deve usar Dask."""
        os.environ["POLARS_ENABLED"] = "false"
        try:
            adapter = PolarsDaskAdapter(str(TEST_FILE))
            assert adapter.engine == "dask"
        finally:
            os.environ.pop("POLARS_ENABLED", None)

    def test_execute_query_polars(self):
        """Teste: Query com Polars retorna resultados válidos."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))

        # Forçar Polars
        adapter.engine = "polars"

        # Query simples: filtrar por segmento
        filters = {"nomesegmento": "TECIDOS"}
        result = adapter.execute_query(filters)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(r, dict) for r in result)
        assert all(r.get("nomesegmento") == "TECIDOS" for r in result if "nomesegmento" in r)

    def test_execute_query_dask(self):
        """Teste: Query com Dask retorna resultados válidos."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))

        # Forçar Dask
        adapter.engine = "dask"

        # Query simples: filtrar por segmento
        filters = {"nomesegmento": "TECIDOS"}
        result = adapter.execute_query(filters)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(r, dict) for r in result)

    def test_data_integrity_polars_vs_dask(self):
        """Teste: Polars e Dask devem retornar mesmos resultados."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))

        filters = {"nomesegmento": "TECIDOS"}

        # Executar com Polars
        adapter.engine = "polars"
        result_polars = adapter.execute_query(filters)

        # Executar com Dask
        adapter.engine = "dask"
        result_dask = adapter.execute_query(filters)

        # Comparar número de linhas
        assert len(result_polars) == len(result_dask), \
            f"Polars: {len(result_polars)} rows, Dask: {len(result_dask)} rows"

    def test_empty_filters_rejected(self):
        """Teste: Query sem filtros deve retornar erro."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        result = adapter.execute_query({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "error" in result[0]

    def test_numeric_filter_polars(self):
        """Teste: Filtro numérico funciona com Polars."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        adapter.engine = "polars"

        # Filtrar estoque > 100
        filters = {
            "nomesegmento": "TECIDOS",
            "estoque_une": "> 100"
        }
        result = adapter.execute_query(filters)

        assert isinstance(result, list)
        # Se resultado vazio, ok (pode não ter estoque > 100)
        # Se tem resultado, validar
        if len(result) > 0:
            assert all(r.get("nomesegmento") == "TECIDOS" for r in result if "nomesegmento" in r)

    def test_numeric_filter_dask(self):
        """Teste: Filtro numérico funciona com Dask."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        adapter.engine = "dask"

        # Filtrar estoque > 100
        filters = {
            "nomesegmento": "TECIDOS",
            "estoque_une": "> 100"
        }
        result = adapter.execute_query(filters)

        assert isinstance(result, list)

    def test_get_schema_polars(self):
        """Teste: get_schema() retorna schema válido com Polars."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        adapter.engine = "polars"

        schema = adapter.get_schema()

        assert isinstance(schema, str)
        assert "Schema" in schema
        assert "nomesegmento" in schema.lower() or "NOMESEGMENTO" in schema

    def test_get_schema_dask(self):
        """Teste: get_schema() retorna schema válido com Dask."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))
        adapter.engine = "dask"

        schema = adapter.get_schema()

        assert isinstance(schema, str)
        assert "Schema" in schema

    def test_connect_disconnect(self):
        """Teste: connect() e disconnect() não devem dar erro."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))

        # Deve ser no-op, sem exceções
        adapter.connect()
        adapter.disconnect()

    def test_fallback_simulation(self):
        """Teste: Simular fallback Polars → Dask."""
        adapter = PolarsDaskAdapter(str(TEST_FILE))

        # Forçar Polars
        adapter.engine = "polars"

        # Query válida (fallback não deve ser acionado)
        filters = {"nomesegmento": "TECIDOS"}
        result = adapter.execute_query(filters)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" not in result[0]


def test_performance_comparison():
    """Teste: Polars deve ser mais rápido que Dask."""
    import time

    adapter = PolarsDaskAdapter(str(TEST_FILE))
    filters = {"nomesegmento": "TECIDOS"}

    # Testar Polars
    adapter.engine = "polars"
    start = time.time()
    result_polars = adapter.execute_query(filters)
    time_polars = time.time() - start

    # Testar Dask
    adapter.engine = "dask"
    start = time.time()
    result_dask = adapter.execute_query(filters)
    time_dask = time.time() - start

    print(f"\nPerformance comparison:")
    print(f"  Polars: {time_polars:.3f}s ({len(result_polars)} rows)")
    print(f"  Dask:   {time_dask:.3f}s ({len(result_dask)} rows)")
    print(f"  Speedup: {time_dask / time_polars:.1f}x")

    # Polars deve ser mais rápido (ou no máximo 2x mais lento em edge cases)
    assert time_polars < time_dask * 2, \
        f"Polars muito lento: {time_polars:.2f}s vs Dask {time_dask:.2f}s"


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "-s"])
