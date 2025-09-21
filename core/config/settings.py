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

# Função para carregar configurações de forma segura
def load_settings():
    """Carrega configurações de forma segura, tentando diferentes fontes"""
    import os
    import logging

    # Primeiro, tentar carregar apenas do ambiente (.env)
    try:
        settings = Settings()
        logging.info("✅ Settings carregadas do ambiente")
        return settings
    except Exception as e:
        logging.warning(f"Erro ao carregar do ambiente: {e}")

    # Se falhou, tentar carregar do Streamlit secrets
    try:
        import streamlit as st

        # Obter valores dos secrets ou variáveis de ambiente
        db_server = st.secrets.get("DB_SERVER", os.getenv("DB_SERVER", ""))
        db_name = st.secrets.get("DB_NAME", os.getenv("DB_NAME", ""))
        db_user = st.secrets.get("DB_USER", os.getenv("DB_USER", ""))
        db_password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
        openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

        settings = Settings(
            DB_SERVER=db_server,
            DB_NAME=db_name,
            DB_USER=db_user,
            DB_PASSWORD=db_password,
            DB_DRIVER=st.secrets.get("DB_DRIVER", os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")),
            DB_TRUST_SERVER_CERTIFICATE=st.secrets.get("DB_TRUST_SERVER_CERTIFICATE", os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")) == "yes",
            OPENAI_API_KEY=openai_key,
            LLM_MODEL_NAME=st.secrets.get("LLM_MODEL_NAME", os.getenv("LLM_MODEL_NAME", "gpt-4o"))
        )
        logging.info("✅ Settings carregadas do Streamlit secrets")
        return settings

    except Exception as e:
        logging.error(f"❌ Erro ao carregar do Streamlit: {e}")

        # Última tentativa: configurações mínimas
        try:
            settings = Settings(
                DB_SERVER="localhost",
                DB_NAME="temp",
                DB_USER="temp",
                DB_PASSWORD="temp",
                OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
                LLM_MODEL_NAME="gpt-4o"
            )
            logging.warning("⚠️ Usando configurações temporárias")
            return settings
        except Exception as final_e:
            logging.error(f"❌ Erro fatal: {final_e}")
            raise final_e

# Instância global das configurações (lazy loading)
settings = None

def get_settings():
    """Obtém as configurações usando lazy loading"""
    global settings
    if settings is None:
        settings = load_settings()
    return settings
