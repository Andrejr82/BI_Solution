import logging
import os
import sys

<<<<<<< HEAD
from core.config.safe_settings import get_safe_settings
=======
from core.config import OPENAI_API_KEY, SQLALCHEMY_DATABASE_URI
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399

"""
Script para depurar o servidor e identificar erros.
"""

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

# Adiciona o diretório raiz ao PATH para importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    logging.info("Verificando importações...")

    # Tenta importar as dependências
    logging.info("LangChain OpenAI importado com sucesso")

    logging.info("SQLDatabase importado com sucesso")

    # Verifica a configuração
    logging.info("Verificando configuração...")

<<<<<<< HEAD
    settings = get_safe_settings()

    if not settings.GEMINI_API_KEY and not settings.DEEPSEEK_API_KEY:
        logging.error("Nenhuma chave de API LLM configurada (Gemini ou DeepSeek)")
    else:
        if settings.GEMINI_API_KEY:
            logging.info("GEMINI_API_KEY configurada")
        if settings.DEEPSEEK_API_KEY:
            logging.info("DEEPSEEK_API_KEY configurada")

    if not settings.SQL_SERVER_CONNECTION_STRING:
        logging.warning("SQL_SERVER_CONNECTION_STRING não está configurada - modo sem banco")
    else:
        logging.info("SQL_SERVER_CONNECTION_STRING configurada")
=======
    if not OPENAI_API_KEY:
        logging.error("OPENAI_API_KEY não está configurada")
    else:
        logging.info("OPENAI_API_KEY configurada")

    if not SQLALCHEMY_DATABASE_URI:
        logging.error("SQLALCHEMY_DATABASE_URI não está configurada")
    else:
        logging.info("SQLALCHEMY_DATABASE_URI configurada")
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399

    # Verifica as ferramentas SQL
    logging.info("Verificando ferramentas SQL...")
    logging.info("Ferramentas SQL importadas com sucesso")

    logging.info("Verificação de configuração e ferramentas SQL concluída com sucesso")

except Exception as e:
    logging.error(f"Erro durante a verificação: {e}", exc_info=True)
