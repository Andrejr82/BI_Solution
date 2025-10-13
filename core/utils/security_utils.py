"""
Módulo para core/utils/security_utils.py. Fornece as funções: verify_password, get_password_hash.
"""

from passlib.context import CryptContext

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Bcrypt tem limite de 72 bytes - truncar se necessário
    # Encode para UTF-8 e limitar tamanho
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)
