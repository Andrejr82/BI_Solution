"""
Settings Configuration
Pydantic Settings with environment variables
"""

from functools import lru_cache
from typing import Literal
import os

from pydantic import Field, field_validator, model_validator, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Application settings"""

    # Calculate absolute path to .env file
    # backend/app/config/settings.py -> backend/.env
    _base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _env_path = os.path.join(_base_dir, ".env")

    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Agent BI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000"
    )

    # @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    # @classmethod
    # def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
    #     if isinstance(v, str):
    #         return [i.strip() for i in v.split(",")]
    #     return v

    # Database - SQL Server
    # Usando aioodbc para suporte assíncrono com SQLAlchemy
    DATABASE_URL: str = Field(
        default="mssql+aioodbc://AgenteVirtual:Cacula@2020@FAMILIA\\SQLJR,1433/Projeto_Caculinha?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Connection string para aioodbc (SQLServerAdapter)
    # Deve corresponder aos mesmos parâmetros do DATABASE_URL
    PYODBC_CONNECTION_STRING: str = Field(
        default="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Projeto_Caculinha;UID=AgenteVirtual;PWD=Cacula@2020;TrustServerCertificate=yes"
    )
    
    # Hybrid Architecture Flags
    USE_SQL_SERVER: bool = False  # Disabled by default to prevent timeouts
    FALLBACK_TO_PARQUET: bool = True
    SQL_SERVER_TIMEOUT: int = 2  # Reduced timeout

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-min-32-chars-long"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_AUTH_PER_MINUTE: int = 5

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    # Sentry
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # Prometheus
    METRICS_ENABLED: bool = True

    # AI / LLM
    GEMINI_API_KEY: str | None = None
    LLM_MODEL_NAME: str = "models/gemini-2.5-flash"
    INTENT_CLASSIFICATION_MODEL: str = "models/gemini-2.5-flash"
    CODE_GENERATION_MODEL: str = "models/gemini-2.5-flash"

    @model_validator(mode="after")
    def compute_pyodbc_string(self) -> "Settings":
        # OTIMIZAÇÃO: Se DATABASE_URL vazio, desabilitar SQL Server (evita timeout de 10s no login!)
        if not self.DATABASE_URL or self.DATABASE_URL.strip() == "":
            self.USE_SQL_SERVER = False
            self.FALLBACK_TO_PARQUET = True
            return self

        # Força a verificação da variável de ambiente para USE_SQL_SERVER
        if os.environ.get("USE_SQL_SERVER", "false").lower() == "true":
            self.USE_SQL_SERVER = True
        # Se a URL for SQLite, e a variável de ambiente não for true, desabilitar o uso do SQL Server
        elif self.DATABASE_URL and self.DATABASE_URL.startswith("sqlite"):
            self.USE_SQL_SERVER = False
            self.FALLBACK_TO_PARQUET = True
            return self

        # Se PYODBC_CONNECTION_STRING for o default, tentar derivar de DATABASE_URL
        default_pyodbc = self.model_fields["PYODBC_CONNECTION_STRING"].default
        if self.PYODBC_CONNECTION_STRING == default_pyodbc and self.DATABASE_URL:
            try:
                url = make_url(str(self.DATABASE_URL))
                # Construir string ODBC
                # DRIVER={driver};SERVER=host;DATABASE=db;UID=user;PWD=pass
                driver = url.query.get("driver", "ODBC Driver 17 for SQL Server")
                trust_cert = url.query.get("TrustServerCertificate", "yes")
                
                # Tratar host e port
                server = url.host
                if url.port:
                    server = f"{server},{url.port}"
                
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={url.database};"
                    f"TrustServerCertificate={trust_cert};"
                )
                
                if url.username:
                    conn_str += f"UID={url.username};PWD={url.password};"
                else:
                    conn_str += "Trusted_Connection=yes;"
                    
                self.PYODBC_CONNECTION_STRING = conn_str
            except Exception:
                # Se falhar, manter o default ou o que foi passado
                pass
        return self


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
