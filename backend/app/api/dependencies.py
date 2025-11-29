"""
API Dependencies
FastAPI dependency injection utilities
"""

import json # Adicionado
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.security import decode_token
from app.infrastructure.database.models import User
from app.schemas.auth import TokenData
from sqlalchemy import select

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current user from JWT token - PARQUET ONLY (SIMPLIFIED)
    """
    import polars as pl
    from pathlib import Path
    from datetime import datetime, timezone
    import sys

    print("==> get_current_user CALLED <==", file=sys.stderr, flush=True)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode JWT
    try:
        token = credentials.credentials
        payload = decode_token(token)

        if payload.get("type") != "access":
            print("==> Invalid token type <==", file=sys.stderr, flush=True)
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            print("==> No user_id in token <==", file=sys.stderr, flush=True)
            raise credentials_exception

        print(f"==> Token decoded: user_id={user_id} <==", file=sys.stderr, flush=True)

    except JWTError as e:
        print(f"==> JWT Error: {e} <==", file=sys.stderr, flush=True)
        raise credentials_exception

    # Read from Parquet ONLY
    # Docker path vs Dev path
    docker_path = Path("/app/data/parquet/users.parquet")
    dev_path = Path(__file__).parent.parent.parent.parent / "data" / "parquet" / "users.parquet"
    parquet_path = docker_path if docker_path.exists() else dev_path
    print(f"==> Parquet path: {parquet_path} <==", file=sys.stderr, flush=True)

    if not parquet_path.exists():
        print(f"==> Parquet NOT FOUND <==", file=sys.stderr, flush=True)
        raise credentials_exception

    try:
        df = pl.read_parquet(parquet_path)
        print(f"==> Parquet loaded: {len(df)} rows <==", file=sys.stderr, flush=True)

        # Simple filter without cast
        user_data = df.filter(pl.col("id") == user_id)
        print(f"==> Filter result: {len(user_data)} rows <==", file=sys.stderr, flush=True)

        if len(user_data) == 0:
            print(f"==> User {user_id} NOT FOUND <==", file=sys.stderr, flush=True)
            raise credentials_exception

        user_row = user_data.row(0, named=True)
        print(f"==> User found: {user_row['username']} <==", file=sys.stderr, flush=True)

        user = User(
            id=user_row["id"],
            username=user_row["username"],
            email=user_row.get("email", ""),
            role=user_row["role"],
            is_active=user_row.get("is_active", True),
            hashed_password=user_row["hashed_password"],
            allowed_segments=user_row.get("allowed_segments", "[]"), # Adicionado
            created_at=user_row.get("created_at", datetime.now(timezone.utc)),
            updated_at=user_row.get("updated_at", datetime.now(timezone.utc)),
            last_login=user_row.get("last_login")
        )

        if not user.is_active:
            print("==> User INACTIVE <==", file=sys.stderr, flush=True)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        print(f"==> SUCCESS: {user.username} authenticated <==", file=sys.stderr, flush=True)
        return user

    except HTTPException:
        raise
    except Exception as e:
        print(f"==> ERROR: {e} <==", file=sys.stderr, flush=True)
        raise credentials_exception


async def get_current_user_old(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT token - PARQUET ONLY VERSION
    
    Simplified version that ONLY uses Parquet for maximum speed and reliability.
    """
    import sys
    import polars as pl
    from pathlib import Path
    from datetime import datetime, timezone
    
    print("==> get_current_user CALLED <==", file=sys.stderr, flush=True)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and validate JWT token
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        print(f"==> Token decoded successfully <==", file=sys.stderr, flush=True)

        if payload.get("type") != "access":
            print(f"==> Invalid token type: {payload.get('type')} <==", file=sys.stderr, flush=True)
            raise credentials_exception

        user_id: str | None = payload.get("sub")
        if user_id is None:
            print(f"==> No user_id in token <==", file=sys.stderr, flush=True)
            raise credentials_exception
            
        print(f"==> Looking for user_id: {user_id} <==", file=sys.stderr, flush=True)

    except JWTError as e:
        print(f"==> JWT Error: {e} <==", file=sys.stderr, flush=True)
        raise credentials_exception

    # Load user from Parquet
    docker_path = Path("/app/data/parquet/users.parquet")
    dev_path = Path(__file__).parent.parent.parent / "data" / "parquet" / "users.parquet"
    parquet_path = docker_path if docker_path.exists() else dev_path
    
    print(f"==> Parquet path: {parquet_path} <==", file=sys.stderr, flush=True)
    print(f"==> Exists: {parquet_path.exists()} <==", file=sys.stderr, flush=True)

    if not parquet_path.exists():
        print(f"==> ERROR: Parquet file not found! <==", file=sys.stderr, flush=True)
        raise credentials_exception

    try:
        df = pl.read_parquet(parquet_path)
        print(f"==> Parquet loaded: {len(df)} rows <==", file=sys.stderr, flush=True)
        
        # Filter for user (simple comparison without cast)
        user_data = df.filter(pl.col("id") == user_id)
        print(f"==> Filter result: {len(user_data)} rows <==", file=sys.stderr, flush=True)

        if len(user_data) == 0:
            print(f"==> User {user_id} NOT FOUND <==", file=sys.stderr, flush=True)
            raise credentials_exception

        user_row = user_data.row(0, named=True)
        print(f"==> User found: {user_row.get('username')} <==", file=sys.stderr, flush=True)

        user = User(
            id=user_row["id"],
            username=user_row["username"],
            email=user_row.get("email", ""),
            role=user_row["role"],
            is_active=user_row.get("is_active", True),
            hashed_password=user_row["hashed_password"],
            created_at=user_row.get("created_at", datetime.now(timezone.utc)),
            updated_at=user_row.get("updated_at", datetime.now(timezone.utc)),
            last_login=user_row.get("last_login")
        )

        if not user.is_active:
            print(f"==> User {user.username} is INACTIVE <==", file=sys.stderr, flush=True)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        print(f"==> User {user.username} AUTHENTICATED <==", file=sys.stderr, flush=True)
        return user

    except HTTPException:
        raise
    except Exception as e:
        print(f"==> ERROR: {e} <==", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_user_from_token(token: str) -> User:
    """
    Get current user from raw JWT token string
    Used for SSE endpoints where EventSource doesn't support custom headers
    """
    import polars as pl
    from pathlib import Path
    from datetime import datetime, timezone
    import sys
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode JWT
    try:
        payload = decode_token(token)
        
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Read from Parquet
    docker_path = Path("/app/data/parquet/users.parquet")
    dev_path = Path(__file__).parent.parent.parent.parent / "data" / "parquet" / "users.parquet"
    parquet_path = docker_path if docker_path.exists() else dev_path
    
    if not parquet_path.exists():
        raise credentials_exception
    
    try:
        df = pl.read_parquet(parquet_path)
        user_data = df.filter(pl.col("id") == user_id)
        
        if len(user_data) == 0:
            raise credentials_exception
        
        # CORREÇÃO: Definir user_row antes de usar
        user_row = user_data.row(0, named=True)
        
        user = User(
            id=user_row["id"],
            username=user_row["username"],
            email=user_row.get("email", ""),
            role=user_row["role"],
            is_active=user_row.get("is_active", True),
            hashed_password=user_row["hashed_password"],
            allowed_segments=user_row.get("allowed_segments", "[]"), # Adicionado
            created_at=user_row.get("created_at", datetime.now(timezone.utc)),
            updated_at=user_row.get("updated_at", datetime.now(timezone.utc)),
            last_login=user_row.get("last_login")
        )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception



def require_role(*allowed_roles: str):
    """
    Dependency to require specific roles
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency to require specific permission
    
    Usage:
        @router.get("/reports")
        async def get_reports(user: User = Depends(require_permission("VIEW_REPORTS"))):
            ...
    """
    # Permission mapping (same as frontend)
    ROLE_PERMISSIONS = {
        "admin": ["*"],  # All permissions
        "user": [
            "VIEW_ANALYTICS", "VIEW_REPORTS", "CREATE_REPORTS", 
            "EDIT_REPORTS", "USE_CHAT"
        ],
        "viewer": ["VIEW_ANALYTICS", "VIEW_REPORTS"],
    }
    
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
        
        if "*" not in user_permissions and permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {permission}"
            )
        return current_user
    
    return permission_checker
