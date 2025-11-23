"""
Data Adapter Dependency
Provides the HybridDataAdapter instance to API endpoints.
"""

from typing import Annotated
from fastapi import Depends, Request

from app.infrastructure.data.hybrid_adapter import HybridDataAdapter

def get_data_adapter(request: Request) -> HybridDataAdapter:
    """
    Dependency to get the HybridDataAdapter instance from app state.
    The adapter is initialized in main.py lifespan.
    """
    if not hasattr(request.app.state, "data_adapter"):
        # Fallback if not initialized (e.g. during tests)
        # But ideally should be initialized in lifespan
        request.app.state.data_adapter = HybridDataAdapter()
        
    return request.app.state.data_adapter

# Type alias for easier usage in endpoints
DataAdapter = Annotated[HybridDataAdapter, Depends(get_data_adapter)]
