"""
Configurações ULTRA SIMPLES para Streamlit Cloud
ZERO Pydantic, ZERO ValidationError
"""

import os
import logging

logger = logging.getLogger(__name__)

class SafeSettings:
    """
    Configuração simples SEM Pydantic - NUNCA falha
    """

    def __init__(self):
        self.GEMINI_API_KEY = self._get_gemini_key()
        self.DEEPSEEK_API_KEY = self._get_deepseek_key()
        self.LLM_MODEL_NAME = self._get_llm_model()

        # Configurações de banco (opcionais) - Streamlit Cloud ou .env
        self.DB_SERVER = self._get_secret_or_env("DB_SERVER", "")
        self.DB_NAME = self._get_secret_or_env("DB_NAME", "")
        self.DB_USER = self._get_secret_or_env("DB_USER", "")
        self.DB_PASSWORD = self._get_secret_or_env("DB_PASSWORD", "")
        self.DB_DRIVER = self._get_secret_or_env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        self.DB_TRUST_SERVER_CERTIFICATE = self._get_secret_or_env("DB_TRUST_SERVER_CERTIFICATE", "yes")

    def _get_gemini_key(self):
        """Obtém chave Gemini de forma segura"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except:
            pass
        return os.getenv("GEMINI_API_KEY", "")

    def _get_deepseek_key(self):
        """Obtém chave DeepSeek de forma segura"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "DEEPSEEK_API_KEY" in st.secrets:
                return st.secrets["DEEPSEEK_API_KEY"]
        except:
            pass
        return os.getenv("DEEPSEEK_API_KEY", "")

    def _get_llm_model(self):
        """Obtém modelo LLM"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "LLM_MODEL_NAME" in st.secrets:
                return st.secrets["LLM_MODEL_NAME"]
        except:
            pass

        return os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite")

    def _get_secret_or_env(self, key, default=""):
        """Obtém valor de Streamlit secrets ou variável de ambiente"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                value = st.secrets[key]
                if value:  # Só retorna se não for vazio
                    return value
        except:
            pass

        return os.getenv(key, default)

    def get_sql_connection_string(self):
        """Gera string de conexão SQL se disponível"""
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return None

        try:
            import urllib.parse
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
            logger.error(f"Erro ao gerar connection string: {e}")
            return None

    def get_pyodbc_connection_string(self):
        """Gera string de conexão PYODBC"""
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
            logger.error(f"Erro ao gerar PYODBC string: {e}")
            return None

    def is_database_available(self):
        """Verifica se banco está configurado"""
        return bool(self.get_sql_connection_string())

    # Compatibilidade com código antigo
    @property
    def SQL_SERVER_CONNECTION_STRING(self):
        """Propriedade para compatibilidade"""
        return self.get_sql_connection_string()

    @property
    def PYODBC_CONNECTION_STRING(self):
        """Propriedade para compatibilidade"""
        return self.get_pyodbc_connection_string()

# NUNCA criar instância na importação!
_cached_settings = None

def get_safe_settings():
    """
    Obtém configurações simples - NUNCA falha
    """
    global _cached_settings

    if _cached_settings is not None:
        return _cached_settings

    try:
        logger.info("🔧 Carregando configurações simples...")
        _cached_settings = SafeSettings()
        logger.info("✅ Configurações carregadas com sucesso")
        return _cached_settings
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        # Retornar configuração mínima mesmo se houver erro
        _cached_settings = SafeSettings()
        return _cached_settings