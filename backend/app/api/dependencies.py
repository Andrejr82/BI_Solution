"""
API Dependencies
FastAPI dependency injection utilities
"""

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
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Validate token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


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
