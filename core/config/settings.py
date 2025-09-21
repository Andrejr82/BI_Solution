from typing import Optional
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib

class Settings(BaseSettings):
    """
    Centraliza as configurações da aplicação, carregando variáveis de um ficheiro .env.
    Esta versão foi refatorada para ser mais robusta, construindo a connection string
    diretamente a partir das variáveis de ambiente.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis extras no .env
    )

    # Variáveis de ambiente individuais para a base de dados
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server" # Valor padrão comum
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

# Instância única das configurações para ser usada em toda a aplicação
try:
    settings = Settings()
except Exception as e:
    # Em caso de erro no Streamlit Cloud, tentar com secrets
    import logging
    import os

    logging.warning(f"Erro ao carregar settings padrão: {e}")
    logging.info("Tentando carregar do Streamlit secrets...")

    try:
        import streamlit as st

        # Criar settings usando os secrets do Streamlit
        settings = Settings(
            DB_SERVER=st.secrets.get("DB_SERVER", os.getenv("DB_SERVER", "")),
            DB_NAME=st.secrets.get("DB_NAME", os.getenv("DB_NAME", "")),
            DB_USER=st.secrets.get("DB_USER", os.getenv("DB_USER", "")),
            DB_PASSWORD=st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
            DB_DRIVER=st.secrets.get("DB_DRIVER", os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")),
            DB_TRUST_SERVER_CERTIFICATE=st.secrets.get("DB_TRUST_SERVER_CERTIFICATE", os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")) == "yes",
            OPENAI_API_KEY=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")),
            LLM_MODEL_NAME=st.secrets.get("LLM_MODEL_NAME", os.getenv("LLM_MODEL_NAME", "gpt-4o"))
        )
        logging.info("✅ Settings carregadas do Streamlit secrets")

    except Exception as inner_e:
        logging.error(f"❌ Erro fatal ao carregar settings: {inner_e}")
        raise inner_e
