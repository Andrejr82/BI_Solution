"""
Configurações seguras para Streamlit Cloud
Versão que NUNCA executa código na importação
"""

from typing import Optional
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib
import os
import logging

logger = logging.getLogger(__name__)

class SafeSettings(BaseSettings):
    """
    Configurações seguras que evitam ValidationError no Streamlit Cloud
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Variáveis de ambiente individuais para a base de dados
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE: bool = True

    # Chave da API para o LLM
    OPENAI_API_KEY: SecretStr

    # Modelo LLM
    LLM_MODEL_NAME: str = "gpt-4o"

    @computed_field
    @property
    def SQL_SERVER_CONNECTION_STRING(self) -> str:
        """
        Gera a string de conexão para SQLAlchemy (mssql+pyodbc).
        """
        driver_formatted = self.DB_DRIVER.replace(' ', '+')
        password_quoted = urllib.parse.quote_plus(self.DB_PASSWORD.get_secret_value())

        conn_str = (
            f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@"
            f"{self.DB_SERVER}/{self.DB_NAME}?"
            f"driver={driver_formatted}"
        )
        if self.DB_TRUST_SERVER_CERTIFICATE:
            conn_str += "&TrustServerCertificate=yes"

        return conn_str

    @computed_field
    @property
    def PYODBC_CONNECTION_STRING(self) -> str:
        """
        Gera a string de conexão ODBC para uso direto com pyodbc.
        """
        conn_str = (
            f"DRIVER={self.DB_DRIVER};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD.get_secret_value()}"
        )
        if self.DB_TRUST_SERVER_CERTIFICATE:
            conn_str += ";TrustServerCertificate=yes"

        return conn_str

# NENHUMA instância é criada na importação!
# Apenas funções que retornam instâncias quando chamadas

def create_settings_from_env() -> Optional[SafeSettings]:
    """Cria settings a partir de variáveis de ambiente"""
    try:
        return SafeSettings()
    except Exception as e:
        logger.warning(f"Erro ao criar settings do ambiente: {e}")
        return None

def create_settings_from_streamlit() -> Optional[SafeSettings]:
    """Cria settings a partir do Streamlit secrets"""
    try:
        import streamlit as st

        return SafeSettings(
            DB_SERVER=st.secrets.get("DB_SERVER", ""),
            DB_NAME=st.secrets.get("DB_NAME", ""),
            DB_USER=st.secrets.get("DB_USER", ""),
            DB_PASSWORD=st.secrets.get("DB_PASSWORD", ""),
            DB_DRIVER=st.secrets.get("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            DB_TRUST_SERVER_CERTIFICATE=st.secrets.get("DB_TRUST_SERVER_CERTIFICATE", "yes") == "yes",
            OPENAI_API_KEY=st.secrets.get("OPENAI_API_KEY", ""),
            LLM_MODEL_NAME=st.secrets.get("LLM_MODEL_NAME", "gpt-4o")
        )
    except Exception as e:
        logger.warning(f"Erro ao criar settings do Streamlit: {e}")
        return None

def create_fallback_settings() -> SafeSettings:
    """Cria settings de fallback mínimas"""
    return SafeSettings(
        DB_SERVER="localhost",
        DB_NAME="temp",
        DB_USER="temp",
        DB_PASSWORD="temp",
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        LLM_MODEL_NAME="gpt-4o"
    )

# Variável global para cache (None na inicialização)
_cached_settings: Optional[SafeSettings] = None

def get_safe_settings() -> SafeSettings:
    """
    Obtém as configurações de forma segura usando lazy loading
    """
    global _cached_settings

    if _cached_settings is not None:
        return _cached_settings

    # Tentar carregar de diferentes fontes
    logger.info("🔧 Carregando configurações...")

    # 1. Tentar ambiente (.env)
    settings = create_settings_from_env()
    if settings:
        logger.info("✅ Settings carregadas do ambiente")
        _cached_settings = settings
        return settings

    # 2. Tentar Streamlit secrets
    settings = create_settings_from_streamlit()
    if settings:
        logger.info("✅ Settings carregadas do Streamlit")
        _cached_settings = settings
        return settings

    # 3. Fallback
    logger.warning("⚠️ Usando settings de fallback")
    settings = create_fallback_settings()
    _cached_settings = settings
    return settings