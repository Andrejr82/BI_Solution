"""
Authentication Service
Handles authentication with hybrid SQL Server + Parquet fallback
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

import polars as pl
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.settings import get_settings
from app.infrastructure.database.models import User

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service with intelligent fallback.

    Priority:
    1. SQL Server (if USE_SQL_SERVER=true and available)
    2. Parquet (fallback or when SQL Server disabled)
    """

    def __init__(self):
        self.use_sql_server = settings.USE_SQL_SERVER

        # Try Docker path first, then development path
        docker_path = Path("/app/data/parquet/users.parquet")
        dev_path = Path(__file__).parent.parent.parent.parent / "data" / "parquet" / "users.parquet"

        if docker_path.exists():
            self.parquet_path = docker_path
        else:
            self.parquet_path = dev_path

    async def authenticate_user(
        self,
        username: str,
        password: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[dict]:
        """
        Authenticate user with hybrid approach.

        Args:
            username: User's username
            password: User's plain text password
            db: Optional database session (used when SQL Server is enabled)

        Returns:
            User dict if authenticated, None otherwise
        """
        user_data = None

        # OTIMIZAÇÃO: Parquet PRIMEIRO (10x mais rápido, sem timeout)
        try:
            user_data = await self._auth_from_parquet(username, password)
            if user_data:
                logger.info(f"User '{username}' authenticated via Parquet (FAST)")
                return user_data
        except Exception as e:
            logger.error(f"Parquet auth failed for '{username}': {e}")

        # Fallback SQL Server (apenas se Parquet falhar E SQL estiver habilitado)
        if self.use_sql_server and db is not None:
            try:
                user_data = await self._auth_from_sql(username, password, db)
                if user_data:
                    logger.info(f"User '{username}' authenticated via SQL Server")
                    return user_data
            except Exception as e:
                logger.warning(f"SQL Server auth failed for '{username}': {e}")

        return None

    async def _auth_from_sql(
        self,
        username: str,
        password: str,
        db: AsyncSession
    ) -> Optional[dict]:
        """Authenticate from SQL Server"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Verify password
        if not self._verify_password(password, user.hashed_password):
            return None

        # Check if active
        if not user.is_active:
            return None

        # Update last_login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email or "",
            "role": user.role,
            "is_active": user.is_active,
        }

    async def _auth_from_parquet(
        self,
        username: str,
        password: str
    ) -> Optional[dict]:
        """Authenticate from Parquet file"""
        logger.info(f"Password received length: {len(password)}")
        
        if not self.parquet_path.exists():
            logger.error(f"Parquet file not found: {self.parquet_path}")
            return None

        try:
            # Read users from Parquet
            df = pl.read_parquet(self.parquet_path)
            logger.info(f"Parquet loaded. Users found: {len(df)}")

            # Filter by username
            user_data = df.filter(pl.col("username") == username)

            if len(user_data) == 0:
                logger.warning(f"User '{username}' not found in Parquet")
                return None

            # Get user row
            user_row = user_data.row(0, named=True)
            logger.info(f"User found: {username}. Verifying password...")

            # Verify password
            hashed_password = user_row["hashed_password"]
            is_valid = self._verify_password(password, hashed_password)
            
            if not is_valid:
                logger.warning(f"Invalid password for user '{username}'")
                return None
            
            logger.info(f"Password verified for '{username}'")

            # Check if active
            if not user_row.get("is_active", True):
                logger.warning(f"User '{username}' is inactive")
                return None

            return {
                "id": str(user_row["id"]),
                "username": user_row["username"],
                "email": user_row.get("email", ""),
                "role": user_row["role"],
                "is_active": user_row.get("is_active", True),
            }
        except Exception as e:
            logger.error(f"Error reading/processing Parquet: {e}")
            return None

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False


# Global instance
auth_service = AuthService()
