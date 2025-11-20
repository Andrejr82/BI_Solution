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

def update_admin_segmento():
    """
    Atualiza o campo 'segmento' para o usuário 'admin' na tabela 'usuarios'.
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
                if current_segmento is None:
                    new_segmento = "ARMARINHO E CONFECÇÃO" # Valor padrão para admin
                    conn.execute(
                        text("UPDATE usuarios SET segmento = :segmento WHERE id = :user_id"),
                        {"segmento": new_segmento, "user_id": user_id}
                    )
                    conn.commit()
                    logger.info(f"✅ Segmento do usuário 'admin' atualizado para '{new_segmento}'.")
                else:
                    logger.info(f"Segmento do usuário 'admin' já está definido como '{current_segmento}'. Nenhuma alteração necessária.")
            else:
                logger.warning("Usuário 'admin' não encontrado na tabela 'usuarios'.")

    except Exception as e:
        logger.error(f"Erro ao atualizar o segmento do admin: {e}", exc_info=True)

if __name__ == "__main__":
    update_admin_segmento()
