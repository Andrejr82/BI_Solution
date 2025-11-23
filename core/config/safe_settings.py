"""
Configurações ULTRA SIMPLES para Streamlit Cloud
ZERO Pydantic, ZERO ValidationError
"""

import os
import logging

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente do .env no início
load_dotenv()

class SafeSettings:
    """
    Configuração simples SEM Pydantic - NUNCA falha
    """

    def __init__(self):
        self.GEMINI_API_KEY = self._get_gemini_key()
        self.DEEPSEEK_API_KEY = self._get_deepseek_key()
        self.LLM_MODEL_NAME = self._get_llm_model()

        # Modelos específicos para cada LLM
        self.GEMINI_MODEL_NAME = self._get_gemini_model()
        self.DEEPSEEK_MODEL_NAME = self._get_deepseek_model()

        # Configurações de banco (opcionais) - Streamlit Cloud ou .env
        self.DB_SERVER = self._get_secret_or_env("DB_SERVER", "")
        self.DB_NAME = self._get_secret_or_env("DB_NAME", "")
        self.DB_USER = self._get_secret_or_env("DB_USER", "")
        self.DB_PASSWORD = self._get_secret_or_env("DB_PASSWORD", "")
        self.DB_DRIVER = self._get_secret_or_env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        self.DB_TRUST_SERVER_CERTIFICATE = self._get_secret_or_env("DB_TRUST_SERVER_CERTIFICATE", "yes")

        # Configurações de limpeza de cache
        self.CACHE_AUTO_CLEAN = self._get_bool_setting("CACHE_AUTO_CLEAN", True)
        self.CACHE_MAX_AGE_DAYS = self._get_int_setting("CACHE_MAX_AGE_DAYS", 7)
        self.CACHE_FORCE_CLEAN = self._get_bool_setting("CACHE_FORCE_CLEAN", False)

        # Configurações da estratégia de modelos híbridos
        self.INTENT_CLASSIFICATION_MODEL = self._get_secret_or_env("INTENT_CLASSIFICATION_MODEL", "models/gemini-2.5-flash")
        self.CODE_GENERATION_MODEL = self._get_secret_or_env("CODE_GENERATION_MODEL", "models/gemini-2.5-pro")
        self.INTENT_CLASSIFICATION_TEMPERATURE = self._get_float_setting("INTENT_CLASSIFICATION_TEMPERATURE", 0.0)
        self.CODE_GENERATION_TEMPERATURE = self._get_float_setting("CODE_GENERATION_TEMPERATURE", 0.2)

    def _get_gemini_key(self):
        """Obtém chave Gemini de forma segura"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except:
            pass
        key = os.getenv("GEMINI_API_KEY", "")
        # Remover aspas se existirem
        if key:
            key = key.strip('"').strip("'")
        return key

    def _get_deepseek_key(self):
        """Obtém chave DeepSeek de forma segura"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "DEEPSEEK_API_KEY" in st.secrets:
                return st.secrets["DEEPSEEK_API_KEY"]
        except:
            pass
        key = os.getenv("DEEPSEEK_API_KEY", "")
        # Remover aspas se existirem
        if key:
            key = key.strip('"').strip("'")
        return key

    def _get_llm_model(self):
        """Obtém modelo LLM (genérico, mantido para compatibilidade)"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "LLM_MODEL_NAME" in st.secrets:
                return st.secrets["LLM_MODEL_NAME"]
        except:
            pass

        return os.getenv("LLM_MODEL_NAME", "models/gemini-2.5-flash")

    def _get_gemini_model(self):
        """Obtém modelo Gemini específico"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "GEMINI_MODEL_NAME" in st.secrets:
                return st.secrets["GEMINI_MODEL_NAME"]
        except:
            pass

        model = os.getenv("GEMINI_MODEL_NAME", "models/gemini-2.5-flash")
        # Remover aspas se existirem
        if model:
            model = model.strip('"').strip("'")
        return model

    def _get_deepseek_model(self):
        """Obtém modelo DeepSeek específico"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and "DEEPSEEK_MODEL_NAME" in st.secrets:
                return st.secrets["DEEPSEEK_MODEL_NAME"]
        except:
            pass

        model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
        # Remover aspas se existirem
        if model:
            model = model.strip('"').strip("'")
        return model

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

    def _get_bool_setting(self, key, default=False):
        """Obtém configuração booleana de secrets ou env"""
        value = self._get_secret_or_env(key, str(default))
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return default

    def _get_int_setting(self, key, default=0):
        """Obtém configuração inteira de secrets ou env"""
        value = self._get_secret_or_env(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def _get_float_setting(self, key, default=0.0):
        """Obtém configuração float de secrets ou env"""
        value = self._get_secret_or_env(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

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
        logger.info("[INFO] Carregando configurações simples...")
        _cached_settings = SafeSettings()
        logger.info("[OK] Configurações carregadas com sucesso")
        return _cached_settings
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        # Retornar configuração mínima mesmo se houver erro
        _cached_settings = SafeSettings()
        return _cached_settings

def reset_safe_settings_cache():
    """
    Força a limpeza do cache de configurações.
    Útil em desenvolvimento quando o .env é alterado.
    """
    global _cached_settings
    _cached_settings = None
    logger.info("[INFO] Cache de configurações foi limpo.")