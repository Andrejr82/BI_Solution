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
logger = logging.getLogger(__name__) # General logger
security_logger = logging.getLogger("security") # Dedicated security logger


class AuthService:
    """
    Authentication service with intelligent fallback.

    Priority:
    1. SQL Server (if USE_SQL_SERVER=true and available)
    2. Parquet (fallback or when SQL Server disabled)
    """

    def __init__(self):
        self.use_sql_server = settings.USE_SQL_SERVER
        self.use_supabase = settings.USE_SUPABASE_AUTH

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

        Priority:
        1. Supabase (if USE_SUPABASE_AUTH=true)
        2. Parquet (fallback or when Supabase disabled)
        3. SQL Server (last resort)

        Args:
            username: User's username or email
            password: User's plain text password
            db: Optional database session (used when SQL Server is enabled)

        Returns:
            User dict if authenticated, None otherwise
        """
        user_data = None

        # Priority 1: Supabase Auth (if enabled)
        if self.use_supabase:
            try:
                user_data = await self._auth_from_supabase(username, password)
                if user_data:
                    security_logger.info(f"User '{username}' authenticated via Supabase")
                    return user_data
            except Exception as e:
                security_logger.warning(f"Supabase auth failed for '{username}': {e}")

        # Priority 2: Parquet (fallback or primary if Supabase disabled)
        try:
            user_data = await self._auth_from_parquet(username, password)
            if user_data:
                security_logger.info(f"User '{username}' authenticated via Parquet")
                return user_data
        except Exception as e:
            security_logger.error(f"Parquet auth failed for '{username}': {e}")

        # Priority 3: SQL Server (last resort)
        if self.use_sql_server and db is not None:
            try:
                user_data = await self._auth_from_sql(username, password, db)
                if user_data:
                    security_logger.info(f"User '{username}' authenticated via SQL Server")
                    return user_data
            except Exception as e:
                security_logger.warning(f"SQL Server auth failed for '{username}': {e}")

        security_logger.warning(f"Authentication failed for user '{username}' - Invalid credentials or inactive.")
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
            security_logger.warning(f"User '{username}' not found in SQL Server.")
            return None

        # Verify password
        if not self._verify_password(password, user.hashed_password):
            security_logger.warning(f"Invalid password attempt for user '{username}' in SQL Server.")
            return None

        # Check if active
        if not user.is_active:
            security_logger.warning(f"Inactive user '{username}' attempted to log in via SQL Server.")
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

    async def _auth_from_supabase(
        self,
        username: str,
        password: str
    ) -> Optional[dict]:
        """Authenticate from Supabase Auth"""
        try:
            from app.core.supabase_client import get_supabase_client
            from supabase import AuthApiError

            try:
                supabase = get_supabase_client()
            except ValueError as ve:
                security_logger.error(f"Supabase client not configured: {ve}")
                return None

            # Supabase usa email para login, então tentamos com username como email
            # Se username não for email, tentamos adicionar @agentbi.com
            email = username if "@" in username else f"{username}@agentbi.com"

            # Tentar autenticar com Supabase - Python usa estrutura diferente
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            except AuthApiError as auth_err:
                security_logger.warning(f"Supabase auth failed for '{email}': {auth_err}")
                return None

            # Na biblioteca Python, response tem session e user
            if not response or not response.session or not response.session.user:
                security_logger.warning(f"Supabase auth failed: no user/session returned for '{email}'")
                return None

            user = response.session.user

            # Buscar metadados adicionais (role) se existir tabela user_profiles
            role = "user"  # Default
            try:
                profile_response = supabase.table("user_profiles").select("*").eq("id", str(user.id)).execute()
                if profile_response.data and len(profile_response.data) > 0:
                    role = profile_response.data[0].get("role", "user")
            except Exception as e:
                logger.warning(f"Could not fetch user profile from Supabase: {e}")

            return {
                "id": str(user.id),
                "username": email.split("@")[0],  # Extrair username do email
                "email": user.email or email,
                "role": role,
                "is_active": True,
            }

        except Exception as e:
            security_logger.error(f"Supabase authentication error for '{username}': {e}")
            return None

    async def _auth_from_parquet(
        self,
        username: str,
        password: str
    ) -> Optional[dict]:
        """Authenticate from Parquet file"""
        # logger.info(f"Password received length: {len(password)}") # Removed sensitive logging
        
        if not self.parquet_path.exists():
            security_logger.error(f"Parquet file not found for authentication: {self.parquet_path}")
            return None

        try:
            # Read users from Parquet
            df = pl.read_parquet(self.parquet_path)
            # security_logger.info(f"Parquet loaded. Users found: {len(df)}") # Removed verbose logging

            # Filter by username
            user_data = df.filter(pl.col("username") == username)

            if len(user_data) == 0:
                security_logger.warning(f"User '{username}' not found in Parquet.")
                return None

            # Get user row
            user_row = user_data.row(0, named=True)
            security_logger.info(f"User '{username}' found in Parquet. Verifying password...")

            # Verify password
            hashed_password = user_row["hashed_password"]
            is_valid = self._verify_password(password, hashed_password)
            
            if not is_valid:
                security_logger.warning(f"Invalid password attempt for user '{username}' in Parquet.")
                return None
            
            security_logger.info(f"Password verified for '{username}' in Parquet.")

            # Check if active
            if not user_row.get("is_active", True):
                security_logger.warning(f"Inactive user '{username}' attempted to log in via Parquet.")
                return None

            return {
                "id": str(user_row["id"]),
                "username": user_row["username"],
                "email": user_row.get("email", ""),
                "role": user_row["role"],
                "is_active": user_row.get("is_active", True),
            }
        except Exception as e:
            security_logger.error(f"Error reading/processing Parquet for user '{username}': {e}")
            return None

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            security_logger.error(f"Password verification error for provided hash: {e}")
            return False


# Global instance
auth_service = AuthService()
