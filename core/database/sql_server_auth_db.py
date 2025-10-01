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
_local_users = {
    "admin": {
        "password_hash": get_password_hash("admin"),
        "role": "admin",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    },
    "user": {
        "password_hash": get_password_hash("user123"),
        "role": "user",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    },
    "cacula": {
        "password_hash": get_password_hash("cacula123"),
        "role": "user",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    }
}

# --- Inicialização do banco ---
def init_db():
    """Inicializa banco se disponível, senão usa modo local"""
    if not is_database_configured():
        logger.info("🌤️ Modo cloud - usando autenticação local em memória")
        logger.info(f"👥 Usuários disponíveis: {list(_local_users.keys())}")
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
                        redefinir_aprovado BIT DEFAULT 0
                    );
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
        logger.error(f"Erro SQL Server: {e} - fallback para modo local")
        return _autenticar_local(username, password)

def _autenticar_local(username, password):
    """Autenticação local (fallback para cloud)"""
    logger.info(f"🌤️ Autenticação local para: {username}")

    if username not in _local_users:
        return None, "Usuário não encontrado"

    user = _local_users[username]
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
def criar_usuario(username, password, role="user"):
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
                text("INSERT INTO usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)"),
                {"username": username, "password_hash": password_hash, "role": role},
            )
            conn.commit()
        logger.info(f"Usuário '{username}' criado.")
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

def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    try:
        return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
    except Exception:
        return True
