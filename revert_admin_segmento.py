import sys
import os
from pathlib import Path
import logging

# Adicionar diretório raiz ao path para importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.utils.db_connection import get_db_connection
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def revert_admin_segmento():
    """
    Define o campo 'segmento' para NULL para o usuário 'admin' na tabela 'usuarios'.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Não foi possível obter conexão com o banco de dados. Verifique a configuração.")
            return

        with conn:
            # Verificar se o usuário 'admin' existe
            result = conn.execute(
                text("SELECT id, segmento FROM usuarios WHERE username = :username"),
                {"username": "admin"}
            ).fetchone()

            if result:
                user_id, current_segmento = result
                if current_segmento is not None:
                    conn.execute(
                        text("UPDATE usuarios SET segmento = NULL WHERE id = :user_id"),
                        {"user_id": user_id}
                    )
                    conn.commit()
                    logger.info(f"✅ Segmento do usuário 'admin' revertido para NULL.")
                else:
                    logger.info(f"Segmento do usuário 'admin' já é NULL. Nenhuma alteração necessária.")
            else:
                logger.warning("Usuário 'admin' não encontrado na tabela 'usuarios'.")

    except Exception as e:
        logger.error(f"Erro ao reverter o segmento do admin: {e}", exc_info=True)

if __name__ == "__main__":
    revert_admin_segmento()
