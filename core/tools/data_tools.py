"""
Módulo de ferramentas de dados para o Agent_BI.
Estas ferramentas são componentes simples e reutilizáveis que os agentes podem executar.
"""
import logging
from typing import List, Dict, Any

from langchain_core.tools import tool

from core.connectivity.parquet_adapter import ParquetAdapter # Corrected Import

logger = logging.getLogger(__name__)

@tool
def fetch_data_from_query(query_filters: Dict[str, Any], parquet_adapter: ParquetAdapter) -> List[Dict[str, Any]]:
    """
    Ferramenta que recebe um dicionário de filtros, os executa usando o ParquetAdapter injetado,
    e retorna os dados brutos como uma lista de dicionários.
    query_filters exemplo: {"column_name": "value", "another_column": ">10"}
    """
    logger.info(f"Executando consulta com filtros: {query_filters}")
    try:
        results = parquet_adapter.execute_query(query_filters)
        logger.info(f"Consulta executada com sucesso. {len(results)} linhas retornadas.")
        return results
    except Exception as e:
        logger.error(f"Erro ao executar a consulta na ferramenta: {e}", exc_info=True)
<<<<<<< HEAD
        return [{"error": "Falha ao executar a consulta no arquivo Parquet.", "details": str(e)}]
=======
        return [{"error": "Falha ao executar a consulta no arquivo Parquet.", "details": str(e)}]
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
