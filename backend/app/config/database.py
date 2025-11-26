"""
Database Configuration
SQLAlchemy async engine and session
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import get_settings

settings = get_settings()

# Create async engine with optimized pool settings
# Use NullPool when SQL Server is disabled to avoid connection attempts
from sqlalchemy.pool import NullPool

if settings.USE_SQL_SERVER:
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_timeout=settings.SQL_SERVER_TIMEOUT,
        connect_args={"timeout": settings.SQL_SERVER_TIMEOUT},
    )
else:
    # Use NullPool when SQL Server is disabled - no connection pooling, no connection attempts
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # Dummy in-memory DB when SQL disabled
        poolclass=NullPool,
        echo=False,
    )

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all models"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """Context manager for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
