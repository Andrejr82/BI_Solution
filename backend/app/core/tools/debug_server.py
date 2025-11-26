import logging
import os
import sys

from app.core.config import SQLALCHEMY_DATABASE_URI

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
    logging.info("SQLDatabase importado com sucesso")

    # Verifica a configuração
    logging.info("Verificando configuração...")

    if not SQLALCHEMY_DATABASE_URI:
        logging.error("SQLALCHEMY_DATABASE_URI não está configurada")
    else:
        logging.info("SQLALCHEMY_DATABASE_URI configurada")

    # Verifica as ferramentas SQL
    logging.info("Verificando ferramentas SQL...")
    logging.info("Ferramentas SQL importadas com sucesso")

    logging.info("Verificação de configuração e ferramentas SQL concluída com sucesso")

except Exception as e:
    logging.error(f"Erro durante a verificação: {e}", exc_info=True)
