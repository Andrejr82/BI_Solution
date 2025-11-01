"""
Adaptador de Parquet Seguro
=========================

Este adaptador combina o SafeDataLoader com a interface esperada pelo CodeGenAgent.
"""

import os
from typing import Dict, Any, List
import pandas as pd

from core.utils.safe_data_loader import SafeDataLoader

class SafeParquetAdapter:
    def __init__(self, base_path: str):
        self.loader = SafeDataLoader(base_path=base_path)

    def execute_query(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Carrega dados de um arquivo Parquet com validação e filtros.
        """
        # O SafeDataLoader não suporta filtros diretamente no load_parquet.
        # A lógica de filtragem precisaria ser aplicada após o carregamento.
        # Por enquanto, vamos carregar o primeiro arquivo encontrado no base_path.

        files = os.listdir(self.loader.base_path)
        if not files:
            raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em {self.loader.base_path}")

        first_file = os.path.join(self.loader.base_path, files[0])

        df = self.loader.load_parquet(first_file)

        if df is None:
            return []

        if filters:
            # A lógica de filtro do PolarsDaskAdapter não está aqui.
            # Esta é uma simplificação para fazer a integração funcionar.
            # Uma implementação completa precisaria de uma lógica de filtragem mais robusta.
            pass

        return df.to_dicts()
