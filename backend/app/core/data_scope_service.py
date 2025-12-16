# backend/app/core/data_scope_service.py
import polars as pl
import logging
import time
from typing import List, Optional, Union
from pathlib import Path

from app.infrastructure.database.models.user import User
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DataScopeService:
    """
    Serviço para filtrar DataFrames baseados nas permissões de segmento do usuário.
    Garante que cada usuário veja apenas os dados aos quais tem acesso.
    
    PERFORMANCE UPDATE: Uses LazyFrame (scan_parquet) to avoid loading full dataset into memory.
    """

    def __init__(self):
        # Determine path once
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = Path(__file__).parent.parent.parent / "data" / "parquet" / "admmat.parquet"
        
        if docker_path.exists():
            self.parquet_path = str(docker_path)
        else:
            self.parquet_path = str(dev_path)
            
        logger.info(f"DataScopeService: Initialized with Lazy Path: {self.parquet_path}")

    def _get_base_lazyframe(self) -> pl.LazyFrame:
        """
        Returns a base LazyFrame with global filters applied.
        WORKAROUND: Uses read_parquet().lazy() instead of scan_parquet() 
        to avoid 'assertion left == right failed' panic in streaming engine.
        """
        # lf = pl.scan_parquet(self.parquet_path)
        # Using eager read + lazy conversion to bypass streaming reader bug
        try:
            lf = pl.read_parquet(self.parquet_path).lazy()
        except Exception as e:
            logger.error(f"Failed to read parquet file eagerly: {e}")
            # Fallback to scan if read fails (though scan is likely to fail too if it's the same bug)
            lf = pl.scan_parquet(self.parquet_path)
        
        # GLOBAL FILTER: Apply allowed UNEs whitelist if configured
        if settings.ALLOWED_UNES:
            # We assume 'UNE' column exists, but check schema safely if needed
            # In Lazy mode, we just apply the filter. If col doesn't exist, it will fail at collection time.
            lf = lf.filter(pl.col("UNE").is_in(settings.ALLOWED_UNES))
            
        return lf

    def get_filtered_dataframe(self, user: User, max_rows: Optional[int] = None) -> Union[pl.DataFrame, pl.LazyFrame]:
        """
        Retorna o DataFrame admmat.parquet filtrado pelos allowed_segments do usuário.
        
        Args:
            user: Usuário autenticado
            max_rows: Limite máximo de linhas a retornar (None = sem limite)
            
        Returns:
            pl.DataFrame: The collected filtered data.
        """
        start_time = time.perf_counter()
        
        try:
            lf = self._get_base_lazyframe()
            
            # 1. Apply User Permission Filters
            if not user or user.role == "admin" or "*" in user.segments_list:
                # Admin or Full Access: No segment filter
                pass
            else:
                allowed_segments = user.segments_list
                if not allowed_segments:
                    logger.warning(f"Usuário {user.username} sem segmentos permitidos.")
                    return pl.DataFrame() # Return empty DF
                
                # Check schema for column name (optimization: cached schema could be better)
                schema = lf.collect_schema()
                segment_col = "NOMESEGMENTO" if "NOMESEGMENTO" in schema.names() else "SEGMENTO"
                
                if segment_col in schema.names():
                    lf = lf.filter(pl.col(segment_col).is_in(allowed_segments))
                else:
                    logger.warning(f"Coluna de segmento não encontrada no schema. Retornando vazio.")
                    return pl.DataFrame()

            # 2. Apply Row Limits (Optimization: Limit at source)
            if max_rows is not None and max_rows > 0:
                lf = lf.head(max_rows)
                
            # 3. Collect Data
            # Removed streaming=True due to panic issues
            result_df = lf.collect()
            
            elapsed = time.perf_counter() - start_time
            logger.info(f"⚡ Filtro LAZY (via Eager) para {user.username}: {result_df.height} linhas em {elapsed:.4f}s")
            
            return result_df

        except Exception as e:
            logger.error(f"Erro ao filtrar dados (Lazy): {e}")
            return pl.DataFrame() # Fail safe

    def get_filtered_lazyframe(self, user: User) -> pl.LazyFrame:
        """
        Retorna um LazyFrame com os filtros de segurança aplicados, mas SEM coletar os dados.
        Permite que os endpoints façam agregações otimizadas antes de trazer dados para a memória.
        """
        try:
            lf = self._get_base_lazyframe()
            
            if not user or user.role == "admin" or "*" in user.segments_list:
                return lf
            
            allowed_segments = user.segments_list
            if not allowed_segments:
                return self._get_empty_lazyframe(lf)
            
            schema = lf.collect_schema()
            segment_col = "NOMESEGMENTO" if "NOMESEGMENTO" in schema.names() else "SEGMENTO"
            
            if segment_col in schema.names():
                return lf.filter(pl.col(segment_col).is_in(allowed_segments))
            
            return self._get_empty_lazyframe(lf)
            
        except Exception as e:
            logger.error(f"Erro ao obter LazyFrame: {e}")
            # Retornar um LazyFrame vazio seguro usando um scan dummy ou similar
            # Hack: Scan no mesmo arquivo com filtro impossível
            return self._get_base_lazyframe().filter(pl.lit(False))

    def _get_empty_lazyframe(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Helper para retornar LazyFrame vazio preservando schema"""
        return lf.filter(pl.lit(False))

    def get_user_segments(self, user: User) -> List[str]:
        """
        Retorna a lista de segmentos únicos disponíveis para o usuário.
        Se admin, faz um scan rápido para pegar valores únicos.
        """
        if not user:
            return []
            
        if user.role != "admin" and "*" not in user.segments_list:
            return user.segments_list
            
        # For admins, we need to fetch unique segments from DB
        try:
            lf = self._get_base_lazyframe()
            schema = lf.collect_schema()
            segment_col = "NOMESEGMENTO" if "NOMESEGMENTO" in schema.names() else "SEGMENTO"
            
            if segment_col in schema.names():
                # Efficient unique value extraction
                unique_segments = lf.select(segment_col).unique().collect().get_column(segment_col).to_list()
                return [str(s) for s in unique_segments if s]
                
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar segmentos únicos: {e}")
            return []

# Inicializar o serviço como um singleton
data_scope_service = DataScopeService()