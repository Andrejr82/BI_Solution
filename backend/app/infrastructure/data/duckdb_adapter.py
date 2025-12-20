import duckdb
import os
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

logger = logging.getLogger(__name__)

class DuckDBAdapter:
    """
    Adapter for querying Parquet files using DuckDB.
    Follows Singleton pattern to manage connection efficiently (though DuckDB is fast to connect).
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DuckDBAdapter, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.connection = duckdb.connect(database=':memory:')
        self._setup_macros()
        logger.info("DuckDBAdapter initialized (In-Memory)")

    def _setup_macros(self):
        """Setup reusable macros or settings"""
        # Example: set threads if needed
        # self.connection.execute("PRAGMA threads=4")
        pass

    def _get_parquet_path(self, extended: bool = False) -> str:
        """Resolve absolute path to parquet file"""
        # TODO: Get from settings
        base_dir = Path(os.getcwd())
        if extended:
             path = base_dir / "data" / "parquet" / "admmat_extended.parquet"
             if path.exists():
                 return str(path)
        
        path = base_dir / "data" / "parquet" / "admmat.parquet"
        if not path.exists():
             # Fallback for tests path structure
             path = base_dir / "backend" / "data" / "parquet" / "admmat.parquet"
        
        return str(path).replace("\\", "/") # DuckDB prefers forward slashes or escaped backslashes

    def query(self, sql: str, params: Optional[Union[List, Dict]] = None) -> pd.DataFrame:
        """
        Execute raw SQL query and return Pandas DataFrame.
        """
        try:
            # If params provided, use them safely (DuckDB supports binding)
            # However, for 'FROM' clauses with dynamic paths, we handled path in python.
            if params:
                 return self.connection.execute(sql, params).df()
            else:
                 return self.connection.execute(sql).df()
        except Exception as e:
            logger.error(f"DuckDB Query Error: {e} | SQL: {sql}")
            raise e

    def load_data(self, 
                  columns: Optional[List[str]] = None, 
                  filters: Optional[Dict[str, Any]] = None,
                  limit: Optional[int] = None,
                  order_by: Optional[str] = None) -> pd.DataFrame:
        """
        Optimized data loader that builds SQL dynamically.
        Replaces 'pd.read_parquet' with predicate pushdown.
        """
        parquet_file = self._get_parquet_path()
        
        # 1. Select clause
        cols_str = "*"
        if columns:
            # Sanitize column names just in case
            cols_str = ", ".join([f'"{c}"' for c in columns])
        
        query_parts = [f"SELECT {cols_str} FROM '{parquet_file}'"]
        
        # 2. Where clause (Predicate Pushdown)
        params = []
        if filters:
            conditions = []
            for col, val in filters.items():
                if isinstance(val, list):
                    # IN clause: col IN (?, ?, ?)
                    placeholders = ", ".join(["?" for _ in val])
                    conditions.append(f'"{col}" IN ({placeholders})')
                    params.extend(val)
                else:
                    # Equality
                    conditions.append(f'"{col}" = ?')
                    params.append(val)
            
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))
        
        # 3. Order By
        if order_by:
             query_parts.append(f"ORDER BY {order_by}")

        # 4. Limit
        if limit:
            query_parts.append(f"LIMIT {limit}")
            
        sql = " ".join(query_parts)
        # logger.debug(f"DuckDB Load SQL: {sql} | Params: {params}")
        
        return self.query(sql, params)

    def execute_aggregation(self, 
                          agg_col: str, 
                          agg_func: str, 
                          group_by: Optional[List[str]] = None,
                          filters: Optional[Dict[str, Any]] = None,
                          limit: int = 50) -> pd.DataFrame:
        """
        Perform fast aggregation directly in DuckDB.
        """
        parquet_file = self._get_parquet_path()
        
        # Validations
        valid_aggs = {'sum', 'avg', 'min', 'max', 'count', 'count_distinct'}
        if agg_func not in valid_aggs:
            raise ValueError(f"Invalid aggregation: {agg_func}")
            
        sql_agg = f"{agg_func}({agg_col})"
        if agg_func == 'count_distinct':
             sql_agg = f"count(DISTINCT {agg_col})"
        
        select_clause = f"{sql_agg} as valor"
        group_clause = ""
        
        if group_by:
            group_cols = ", ".join([f'"{c}"' for c in group_by])
            select_clause = f"{group_cols}, {select_clause}"
            group_clause = f"GROUP BY {group_cols}"
            
        query_parts = [f"SELECT {select_clause} FROM '{parquet_file}'"]
        
        # Filters
        params = []
        if filters:
            conditions = []
            for col, val in filters.items():
                if isinstance(val, list):
                    placeholders = ", ".join(["?" for _ in val])
                    conditions.append(f'"{col}" IN ({placeholders})')
                    params.extend(val)
                elif isinstance(val, str) and "%" in val: # LIKE support
                     conditions.append(f'"{col}" LIKE ?')
                     params.append(val)
                else:
                    conditions.append(f'"{col}" = ?')
                    params.append(val)
            
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))
                
        if group_clause:
            query_parts.append(group_clause)
            
        # Order by aggregated value desc
        query_parts.append("ORDER BY valor DESC")
        
        query_parts.append(f"LIMIT {limit}")
        
        sql = " ".join(query_parts)
        return self.query(sql, params)

# Global instance
duckdb_adapter = DuckDBAdapter()
