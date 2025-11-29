# backend/app/core/data_scope_service.py
import polars as pl
import logging
import time # Adicionado para métricas
from typing import List, Optional

from app.infrastructure.database.models.user import User
from app.core.parquet_cache import cache

logger = logging.getLogger(__name__)

class DataScopeService:
    """
    Serviço para filtrar DataFrames baseados nas permissões de segmento do usuário.
    Garante que cada usuário veja apenas os dados aos quais tem acesso.
    """

    def __init__(self):
        self.admmat_df: pl.DataFrame = cache.get_dataframe("admmat.parquet")
        logger.info(f"DataScopeService inicializado com {self.admmat_df.height} registros totais.")

    def get_filtered_dataframe(self, user: User, max_rows: Optional[int] = None) -> pl.DataFrame:
        """
        Retorna o DataFrame admmat.parquet filtrado pelos allowed_segments do usuário.
        Se o usuário tiver '["*"]' ou for admin, retorna o DataFrame completo.
        
        Args:
            user: Usuário autenticado
            max_rows: Limite máximo de linhas a retornar (None = sem limite)
        """
        start_time = time.perf_counter()

        if not user or user.role == "admin" or "*" in user.segments_list:
            # logger.debug(f"Usuário {user.username} (Admin ou '*') acessando dados completos.")
            result_df = self.admmat_df
        else:
            allowed_segments = user.segments_list
            if not allowed_segments:
                logger.warning(f"Usuário {user.username} sem segmentos permitidos. Retornando DataFrame vazio.")
                return self.admmat_df.clear() # Retorna um DF vazio com o mesmo schema
            
            # logger.debug(f"Filtrando dados para usuário {user.username} com segmentos: {allowed_segments}")
            
            # Filtrar o DataFrame (Operação Vetorizada Polars - Ultra Rápida)
            # Assumindo que a coluna de segmento no Parquet é 'NOMESEGMENTO'
            result_df = self.admmat_df.filter(pl.col("NOMESEGMENTO").is_in(allowed_segments))
        
        # Aplicar limite de linhas se especificado
        if max_rows is not None and max_rows > 0:
            result_df = result_df.head(max_rows)
            logger.info(f"🔒 Limite de {max_rows} linhas aplicado para {user.username}")
        
        elapsed = time.perf_counter() - start_time
        
        # Log de Performance
        if elapsed > 0.05: # Alerta se demorar mais de 50ms
            logger.warning(f"⚠️ Filtro lento para {user.username}: {elapsed:.4f}s")
        else:
            logger.info(f"⚡ Filtro aplicado para {user.username}: {result_df.height} linhas em {elapsed:.4f}s")

        return result_df

# Inicializar o serviço como um singleton
data_scope_service = DataScopeService()
