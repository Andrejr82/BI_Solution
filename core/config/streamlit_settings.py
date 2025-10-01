"""
Configurações específicas para Streamlit Cloud
Versão simplificada que evita erros de validação
"""

import os
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class StreamlitSettings:
    """
    Configurações simplificadas para Streamlit Cloud
    Evita problemas de validação do Pydantic
    """

    def __init__(self):
        # Detectar se estamos no Streamlit Cloud
        self.is_streamlit_cloud = self._detect_streamlit_cloud()

        # Configurações essenciais
        self.GEMINI_API_KEY = self._get_gemini_key()
        self.DEEPSEEK_API_KEY = self._get_deepseek_key()
        self.LLM_MODEL_NAME = self._get_llm_model()

        # Configurações de banco (opcionais)
        if not self.is_streamlit_cloud:
            self.DB_SERVER = os.getenv("DB_SERVER")
            self.DB_NAME = os.getenv("DB_NAME")
            self.DB_USER = os.getenv("DB_USER")
            self.DB_PASSWORD = os.getenv("DB_PASSWORD")
            self.DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
            self.DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
        else:
            # No Streamlit Cloud, não usar banco por padrão
            self.DB_SERVER = None
            self.DB_NAME = None
            self.DB_USER = None
            self.DB_PASSWORD = None
            self.DB_DRIVER = "ODBC Driver 17 for SQL Server"
            self.DB_TRUST_SERVER_CERTIFICATE = "yes"

    def _detect_streamlit_cloud(self) -> bool:
        """Detecta se estamos rodando no Streamlit Cloud"""
        indicators = [
            os.getenv("STREAMLIT_SHARING") == "true",
            os.getenv("STREAMLIT_CLOUD") == "true",
            "/mount/src/" in os.getcwd(),
            "streamlit.app" in os.getenv("HOSTNAME", ""),
        ]
        return any(indicators)

    def _get_gemini_key(self) -> str:
        """Obtém a chave do Gemini de forma segura"""
        # Tentar obter do Streamlit secrets primeiro
        try:
            if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

        # Fallback para variável de ambiente
        return os.getenv("GEMINI_API_KEY", "")

    def _get_deepseek_key(self) -> str:
        """Obtém a chave do DeepSeek de forma segura"""
        # Tentar obter do Streamlit secrets primeiro
        try:
            if hasattr(st, 'secrets') and "DEEPSEEK_API_KEY" in st.secrets:
                return st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            pass

        # Fallback para variável de ambiente
        return os.getenv("DEEPSEEK_API_KEY", "")

    def _get_llm_model(self) -> str:
        """Obtém o modelo LLM configurado"""
        # Tentar obter do Streamlit secrets primeiro
        try:
            if hasattr(st, 'secrets') and "LLM_MODEL_NAME" in st.secrets:
                return st.secrets["LLM_MODEL_NAME"]
        except Exception:
            pass

        # Fallback para variável de ambiente
        return os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash-latest")

    def get_sql_connection_string(self) -> Optional[str]:
        """
        Gera string de conexão SQL Server se configurações estiverem disponíveis
        """
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return None

        import urllib.parse

        try:
            driver_formatted = self.DB_DRIVER.replace(' ', '+')
            password_quoted = urllib.parse.quote_plus(str(self.DB_PASSWORD))

            conn_str = (
                f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@"
                f"{self.DB_SERVER}/{self.DB_NAME}?"
                f"driver={driver_formatted}"
            )

            if self.DB_TRUST_SERVER_CERTIFICATE == "yes":
                conn_str += "&TrustServerCertificate=yes"

            return conn_str

        except Exception as e:
            logger.error(f"Erro ao gerar string de conexão: {e}")
            return None

    def get_pyodbc_connection_string(self) -> Optional[str]:
        """
        Gera string de conexão PYODBC se configurações estiverem disponíveis
        """
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return None

        try:
            conn_str = (
                f"DRIVER={self.DB_DRIVER};"
                f"SERVER={self.DB_SERVER};"
                f"DATABASE={self.DB_NAME};"
                f"UID={self.DB_USER};"
                f"PWD={self.DB_PASSWORD}"
            )

            if self.DB_TRUST_SERVER_CERTIFICATE == "yes":
                conn_str += ";TrustServerCertificate=yes"

            return conn_str

        except Exception as e:
            logger.error(f"Erro ao gerar string de conexão PYODBC: {e}")
            return None

    def is_database_available(self) -> bool:
        """Verifica se configurações de banco estão disponíveis"""
        return all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD])

    def log_config_status(self):
        """Log do status das configurações"""
        logger.info(f"Streamlit Cloud: {self.is_streamlit_cloud}")
        logger.info(f"Gemini API configurada: {'Sim' if self.GEMINI_API_KEY else 'Não'}")
        logger.info(f"DeepSeek API configurada: {'Sim' if self.DEEPSEEK_API_KEY else 'Não'}")
        logger.info(f"Modelo LLM: {self.LLM_MODEL_NAME}")
        logger.info(f"Banco de dados disponível: {'Sim' if self.is_database_available() else 'Não'}")

# Instância global das configurações (lazy loading)
streamlit_settings = None

def get_streamlit_settings():
    """Obtém as configurações do Streamlit de forma lazy"""
    global streamlit_settings
    if streamlit_settings is None:
        streamlit_settings = StreamlitSettings()
    return streamlit_settings