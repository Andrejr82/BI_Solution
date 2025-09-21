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

    # Variáveis de ambiente individuais para a base de dados (opcionais para Streamlit Cloud)
    DB_SERVER: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[SecretStr] = None
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server" # Valor padrão comum
    DB_TRUST_SERVER_CERTIFICATE: bool = True

    # Chave da API para o LLM
    OPENAI_API_KEY: SecretStr

    # Modelo LLM
    LLM_MODEL_NAME: str = "gpt-4o"
    
    @computed_field
    @property
    def SQL_SERVER_CONNECTION_STRING(self) -> Optional[str]:
        """
        Gera a string de conexão para SQLAlchemy (mssql+pyodbc).
        Retorna None se configurações de DB não estiverem disponíveis.
        """
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return None

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
    def PYODBC_CONNECTION_STRING(self) -> Optional[str]:
        """
        Gera a string de conexão ODBC para uso direto com pyodbc.
        Retorna None se configurações de DB não estiverem disponíveis.
        """
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return None

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
settings = Settings()
