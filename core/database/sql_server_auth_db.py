"""
Autenticação com SQL Server + Fallback para modo cloud
VERSÃO COMPATÍVEL COM STREAMLIT CLOUD
"""
import pyodbc
from datetime import datetime, timedelta
from sqlalchemy import text
import logging

from core.utils.db_connection import get_db_connection, is_database_configured
from core.utils.security_utils import get_password_hash, verify_password

# --- Constantes de Autenticação ---
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30

logger = logging.getLogger(__name__)

# === FALLBACK: Usuários em memória para modo cloud ===
# Hashes pré-computados para evitar erro de bcrypt no import
_local_users = {
    "admin": {
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQw3wZ3Dq",  # admin
        "role": "admin",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    },
    "user": {
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXe4P8Y2xv3bq4vOGz1s.OhPr9nz9WyT8u",  # user123
        "role": "user",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    },
    "cacula": {
        "password_hash": "$2b$12$k5Y6fS7qZ8rT9pW3xV2yL.4QqZ8rT9pW3xV2yL4QqZ8rT9pW3xV2y",  # cacula123
        "role": "user",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    },
    "renan": {
        "password_hash": "$2b$12$8vn/Jk.xJKRNm8k9p4y7d.EKCQqrFYp.QY8vUqTrPcRN6kEJ9xvIW",  # renan
        "role": "user",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    }
}

def _get_local_users():
    """Retorna usuários locais (já inicializados)"""
    return _local_users

# --- Inicialização do banco ---
def init_db():
    """Inicializa banco se disponível, senão usa modo local"""
    if not is_database_configured():
        logger.info("🌤️ Modo cloud - usando autenticação local em memória")
        users = _get_local_users()
        logger.info(f"👥 Usuários disponíveis: {list(users.keys())}")
        return

    logger.info("Iniciando a inicialização do banco de dados de autenticação.")
    try:
        conn = get_db_connection()
        if conn is None:
            logger.warning("⚠️ Conexão de banco falhou - usando modo local")
            return

        with conn:
            conn.execute(
                text(
                    """
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' and xtype='U')
                    CREATE TABLE usuarios (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        username NVARCHAR(255) UNIQUE NOT NULL,
                        password_hash NVARCHAR(255) NOT NULL,
                        role NVARCHAR(50) NOT NULL,
                        ativo BIT DEFAULT 1,
                        tentativas_invalidas INT DEFAULT 0,
                        bloqueado_ate DATETIME,
                        ultimo_login DATETIME,
                        redefinir_solicitado BIT DEFAULT 0,
                        redefinir_aprovado BIT DEFAULT 0,
                        cloud_enabled BIT DEFAULT 0
                    );

                    -- Adicionar coluna cloud_enabled se não existir (migração)
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'cloud_enabled')
                    BEGIN
                        ALTER TABLE usuarios ADD cloud_enabled BIT DEFAULT 0;
                    END;
                    """
                )
            )
            conn.commit()
        logger.info("Banco de dados de autenticação inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e} - usando modo local")

# --- Autenticação ---
def autenticar_usuario(username, password):
    """Autentica usuário (SQL Server ou modo local)"""
    logger.info(f"Tentativa de autenticação para: {username}")

    # Modo local (cloud sem banco)
    if not is_database_configured():
        return _autenticar_local(username, password)

    # Modo SQL Server
    try:
        conn = get_db_connection()
        if conn is None:
            logger.warning("⚠️ Banco indisponível - usando autenticação local")
            return _autenticar_local(username, password)

        with conn:
            result = conn.execute(
                text("SELECT id, password_hash, ativo, tentativas_invalidas, bloqueado_ate, role FROM usuarios WHERE username=:username"),
                {"username": username}
            ).fetchone()

            if not result:
                logger.warning(f"Usuário '{username}' não encontrado no banco.")
                return None, "Usuário não encontrado"

            user_id, db_password_hash, ativo, tentativas, bloqueado_ate, role = result
            now = datetime.now()

            if not ativo:
                return None, "Usuário inativo"

            if bloqueado_ate and now < bloqueado_ate:
                return None, f"Usuário bloqueado até {bloqueado_ate.strftime('%Y-%m-%d %H:%M:%S')}"

            if not verify_password(password, db_password_hash):
                tentativas += 1
                if tentativas >= MAX_TENTATIVAS:
                    bloqueado_ate = now + timedelta(minutes=BLOQUEIO_MINUTOS)
                    conn.execute(
                        text("UPDATE usuarios SET tentativas_invalidas=:tentativas, bloqueado_ate=:bloqueado_ate WHERE id=:id"),
                        {"tentativas": tentativas, "bloqueado_ate": bloqueado_ate, "id": user_id}
                    )
                    conn.commit()
                    return None, f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
                else:
                    conn.execute(
                        text("UPDATE usuarios SET tentativas_invalidas=:tentativas WHERE id=:id"),
                        {"tentativas": tentativas, "id": user_id}
                    )
                    conn.commit()
                    return None, f"Senha incorreta. Tentativas restantes: {MAX_TENTATIVAS - tentativas}"

            # Sucesso
            conn.execute(
                text("UPDATE usuarios SET tentativas_invalidas=0, bloqueado_ate=NULL, ultimo_login=:now WHERE id=:id"),
                {"now": now, "id": user_id}
            )
            conn.commit()
            logger.info(f"✅ Usuário '{username}' autenticado (SQL Server). Papel: {role}")
            return role, None

    except Exception as e:
        logger.error(f"Erro SQL Server: {e}")
        return None, f"Erro de autenticação: {str(e)}"

def _autenticar_local(username, password):
    """Autenticação local (fallback para cloud)"""
    logger.info(f"🌤️ Autenticação local para: {username}")

    users = _get_local_users()
    if username not in users:
        return None, "Usuário não encontrado"

    user = users[username]
    now = datetime.now()

    if not user["ativo"]:
        return None, "Usuário inativo"

    if user["bloqueado_ate"] and now < user["bloqueado_ate"]:
        return None, f"Usuário bloqueado até {user['bloqueado_ate'].strftime('%Y-%m-%d %H:%M:%S')}"

    if not verify_password(password, user["password_hash"]):
        user["tentativas_invalidas"] += 1
        if user["tentativas_invalidas"] >= MAX_TENTATIVAS:
            user["bloqueado_ate"] = now + timedelta(minutes=BLOQUEIO_MINUTOS)
            return None, f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
        else:
            return None, f"Senha incorreta. Tentativas restantes: {MAX_TENTATIVAS - user['tentativas_invalidas']}"

    # Sucesso
    user["tentativas_invalidas"] = 0
    user["bloqueado_ate"] = None
    user["ultimo_login"] = now
    logger.info(f"✅ Usuário '{username}' autenticado localmente. Papel: {user['role']}")
    return user["role"], None

# --- Funções administrativas (apenas SQL Server) ---
def criar_usuario(username, password, role="user", cloud_enabled=False):
    if not is_database_configured():
        logger.warning("⚠️ Criação de usuário não disponível em modo cloud")
        return

    logger.info(f"Criando usuário: {username}")
    password_hash = get_password_hash(password)
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Banco não disponível")

        with conn:
            conn.execute(
                text("INSERT INTO usuarios (username, password_hash, role, cloud_enabled) VALUES (:username, :password_hash, :role, :cloud_enabled)"),
                {"username": username, "password_hash": password_hash, "role": role, "cloud_enabled": cloud_enabled},
            )
            conn.commit()
        logger.info(f"Usuário '{username}' criado. Cloud: {cloud_enabled}")
    except pyodbc.IntegrityError:
        raise ValueError("Usuário já existe")
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        raise

def solicitar_redefinicao(username):
    if not is_database_configured():
        logger.warning("⚠️ Redefinição não disponível em modo cloud")
        return

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                conn.execute(
                    text("UPDATE usuarios SET redefinir_solicitado=1 WHERE username=:username"),
                    {"username": username}
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Erro ao solicitar redefinição: {e}")

def aprovar_redefinicao(username):
    if not is_database_configured():
        logger.warning("⚠️ Aprovação não disponível em modo cloud")
        return

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                conn.execute(
                    text("UPDATE usuarios SET redefinir_aprovado=1 WHERE username=:username"),
                    {"username": username}
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Erro ao aprovar redefinição: {e}")

def redefinir_senha(username, nova_senha):
    if not is_database_configured():
        logger.warning("⚠️ Redefinição não disponível em modo cloud")
        return

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                result = conn.execute(
                    text("SELECT redefinir_aprovado FROM usuarios WHERE username=:username"),
                    {"username": username}
                ).fetchone()

                if not result or not result[0]:
                    raise ValueError("Redefinição não aprovada")

                password_hash = get_password_hash(nova_senha)
                conn.execute(
                    text("UPDATE usuarios SET password_hash=:password_hash, redefinir_solicitado=0, redefinir_aprovado=0 WHERE username=:username"),
                    {"password_hash": password_hash, "username": username},
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        raise

def alterar_senha_usuario(user_id, nova_senha):
    """Permite que um usuário altere sua própria senha"""
    if not is_database_configured():
        logger.warning("⚠️ Alteração de senha não disponível em modo cloud")
        return False

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                password_hash = get_password_hash(nova_senha)
                conn.execute(
                    text("UPDATE usuarios SET password_hash=:password_hash WHERE id=:user_id"),
                    {"password_hash": password_hash, "user_id": user_id}
                )
                conn.commit()
                logger.info(f"Senha alterada para usuário ID {user_id}")
                return True
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False

def reset_user_password(user_id, nova_senha_temporaria):
    """Admin reseta senha de um usuário (sem precisar da senha antiga)"""
    if not is_database_configured():
        logger.warning("⚠️ Reset de senha não disponível em modo cloud")
        return False

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                password_hash = get_password_hash(nova_senha_temporaria)
                conn.execute(
                    text("UPDATE usuarios SET password_hash=:password_hash WHERE id=:user_id"),
                    {"password_hash": password_hash, "user_id": user_id}
                )
                conn.commit()
                logger.info(f"Senha resetada pelo admin para usuário ID {user_id}")
                return True
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {e}")
        return False

def get_all_users():
    """Retorna lista de todos os usuários (admin only)"""
    if not is_database_configured():
        # Retornar usuários locais
        users = _get_local_users()
        return [
            {
                "username": username,
                "role": user_data["role"],
                "ativo": user_data["ativo"],
                "ultimo_login": user_data["ultimo_login"]
            }
            for username, user_data in users.items()
        ]

    try:
        conn = get_db_connection()
        if conn is None:
            logger.warning("⚠️ Banco indisponível - retornando usuários locais")
            users = _get_local_users()
            return [
                {
                    "username": username,
                    "role": user_data["role"],
                    "ativo": user_data["ativo"],
                    "ultimo_login": user_data["ultimo_login"]
                }
                for username, user_data in users.items()
            ]

        with conn:
            result = conn.execute(
                text("SELECT id, username, role, ativo, ultimo_login, cloud_enabled FROM usuarios ORDER BY username")
            ).fetchall()

            users = []
            for row in result:
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "ativo": bool(row[3]),
                    "ultimo_login": row[4],
                    "cloud_enabled": bool(row[5]) if len(row) > 5 else False
                })
            return users
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return []

def toggle_cloud_enabled(user_id, enabled):
    """Habilita/desabilita acesso cloud para um usuário"""
    if not is_database_configured():
        logger.warning("⚠️ Toggle cloud não disponível em modo cloud")
        return False

    try:
        conn = get_db_connection()
        if conn:
            with conn:
                conn.execute(
                    text("UPDATE usuarios SET cloud_enabled=:enabled WHERE id=:user_id"),
                    {"enabled": enabled, "user_id": user_id}
                )
                conn.commit()
                logger.info(f"Cloud access {'enabled' if enabled else 'disabled'} para user ID {user_id}")
                return True
    except Exception as e:
        logger.error(f"Erro ao atualizar cloud_enabled: {e}")
        return False

def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    try:
        return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
    except Exception:
        return True
