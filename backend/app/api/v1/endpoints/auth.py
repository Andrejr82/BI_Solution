"""Authentication Endpoints
Login, logout, refresh token, and current user
"""

from datetime import datetime, timezone
from typing import Annotated

import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.config.database import get_db
from app.config.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token,
)
from app.infrastructure.database.models import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Production authentication endpoint - optimized for speed.

    Uses hybrid authentication:
    1. Parquet (primary, fast)
    2. SQL Server (only if explicitly enabled and USE_SQL_SERVER=true)

    Fast and efficient with proper error handling.
    """
    from app.core.auth_service import auth_service
    from app.config.settings import settings

    # Autentica usando Parquet diretamente quando SQL Server desabilitado
    user_data = await auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password,
        db=db if settings.USE_SQL_SERVER else None,
    )

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_data.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Generate tokens
    token_data = {
        "sub": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"]
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/login_form", response_model=Token)
async def login_form(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login endpoint that accepts form data (used by HTML login page)."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user information."""
    return current_user

@router.post("/logout")
async def logout() -> dict[str, str]:
    """Placeholder logout endpoint (client can discard tokens)."""
    return {"detail": "Logged out"}


@router.post("/change-password")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    old_password: str = Form(...),
    new_password: str = Form(...)
):
    """Change user password (updates Parquet only)."""
    import polars as pl
    from app.config.security import get_password_hash
    from pathlib import Path

    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # Determine Parquet path (same logic as auth_service)
    docker_path = Path("/app/data/parquet/users.parquet")
    dev_path = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "parquet" / "users.parquet"
    parquet_path = docker_path if docker_path.exists() else dev_path

    if not parquet_path.exists():
        raise HTTPException(status_code=500, detail="User database not found")

    try:
        df = pl.read_parquet(parquet_path)
        new_hash = get_password_hash(new_password)
        
        # Update password for specific user
        df = df.with_columns(
            pl.when(pl.col("id") == current_user.id)
            .then(pl.lit(new_hash))
            .otherwise(pl.col("hashed_password"))
            .alias("hashed_password")
        )
        
        df.write_parquet(parquet_path)
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update password: {str(e)}")

