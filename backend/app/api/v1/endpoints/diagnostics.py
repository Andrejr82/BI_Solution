from typing import Annotated, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends

from app.api.dependencies import require_role
from app.config.settings import settings
from app.infrastructure.database.models import User

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])

@router.get("/db-status")
async def get_db_status(
    current_user: Annotated[User, Depends(require_role("admin"))]
):
    """
    Status das conexões com banco de dados e arquivos.
    """
    # Verificar Parquet (Root Data vs Backend Data)
    # Backend usa logicamente: app/data/parquet OU ../../../../data/parquet
    
    # Vamos verificar ambos para reportar
    backend_parquet = Path("/app/data/parquet/admmat.parquet")
    local_parquet = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"
    
    parquet_status = "unknown"
    parquet_size = 0
    parquet_path_used = "none"
    
    if backend_parquet.exists():
        parquet_status = "ok"
        parquet_size = backend_parquet.stat().st_size
        parquet_path_used = str(backend_parquet)
    elif local_parquet.exists():
        parquet_status = "ok"
        parquet_size = local_parquet.stat().st_size
        parquet_path_used = str(local_parquet)
    else:
        parquet_status = "missing"

    return {
        "parquet": {
            "status": parquet_status,
            "size_mb": round(parquet_size / 1024 / 1024, 2) if parquet_size else 0,
            "path": parquet_path_used
        },
        "sql_server": {
            "status": "enabled" if settings.USE_SQL_SERVER else "disabled",
            "url": settings.DATABASE_URL if settings.USE_SQL_SERVER else None
        },
        "supabase": {
            "status": "enabled" if settings.USE_SUPABASE_AUTH else "disabled",
            "url": settings.SUPABASE_URL if settings.USE_SUPABASE_AUTH else None
        }
    }
