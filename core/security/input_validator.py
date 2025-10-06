"""
Validadores de entrada para prevenir ataques de injeção
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def sanitize_username(username: str) -> str:
    """
    Remove caracteres perigosos de um username

    Args:
        username: Username fornecido pelo usuário

    Returns:
        Username sanitizado

    Example:
        >>> sanitize_username("admin'; DROP TABLE--")
        'adminDROPTABLE'
    """
    if not username:
        return ""

    # Permitir apenas caracteres alfanuméricos, ponto, underscore e hífen
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', username)

    if sanitized != username:
        logger.warning(f"Username sanitizado: '{username}' -> '{sanitized}'")

    return sanitized[:50]  # Limitar tamanho


def validate_sql_injection(text: str) -> str:
    """
    Valida texto para detectar possíveis SQL injections

    Args:
        text: Texto a ser validado

    Returns:
        Texto original se válido

    Raises:
        ValueError: Se padrão suspeito for detectado

    Example:
        >>> validate_sql_injection("admin'; DROP TABLE usuarios--")
        ValueError: Padrão suspeito detectado: --
    """
    if not text:
        return text

    # Padrões comuns de SQL injection
    dangerous_patterns = [
        '--',           # Comentário SQL
        ';',            # Separador de comandos
        '/*',           # Comentário multi-linha
        '*/',
        'xp_',          # Stored procedures SQL Server
        'sp_',
        'DROP',         # Comandos DDL
        'CREATE',
        'ALTER',
        'DELETE',
        'INSERT',
        'UPDATE',
        'EXEC',
        'EXECUTE',
        'UNION',        # UNION based injection
        'SELECT.*FROM', # SELECT com FROM
        '1=1',          # Condições sempre verdadeiras
        '1\'=\'1',
        'OR 1=1',
        'OR \'1\'=\'1',
    ]

    text_upper = text.upper()

    for pattern in dangerous_patterns:
        if pattern.upper() in text_upper:
            logger.error(f"🚨 TENTATIVA DE SQL INJECTION DETECTADA: '{text}' - Padrão: '{pattern}'")
            raise ValueError(f"Entrada inválida: padrão suspeito detectado")

    return text


def validate_email(email: str) -> bool:
    """
    Valida formato de email

    Args:
        email: Email a ser validado

    Returns:
        True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_path(path: str) -> str:
    """
    Sanitiza path para prevenir directory traversal

    Args:
        path: Path fornecido pelo usuário

    Returns:
        Path sanitizado

    Raises:
        ValueError: Se padrão suspeito for detectado
    """
    # Detectar tentativas de directory traversal
    dangerous_path_patterns = ['..', '~', '/etc', '/root', 'C:\\Windows']

    for pattern in dangerous_path_patterns:
        if pattern in path:
            logger.error(f"🚨 TENTATIVA DE DIRECTORY TRAVERSAL: '{path}'")
            raise ValueError("Path inválido")

    return path


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida força da senha

    Args:
        password: Senha a ser validada

    Returns:
        (is_valid, error_message)

    Example:
        >>> validate_password_strength("abc")
        (False, "Senha deve ter pelo menos 8 caracteres")
    """
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"

    if not re.search(r'[a-z]', password):
        return False, "Senha deve conter letra minúscula"

    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter letra maiúscula"

    if not re.search(r'\d', password):
        return False, "Senha deve conter número"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Senha deve conter caractere especial"

    return True, None


def sanitize_html(text: str) -> str:
    """
    Remove tags HTML potencialmente perigosas (XSS prevention)

    Args:
        text: Texto a ser sanitizado

    Returns:
        Texto sem tags HTML perigosas
    """
    # Remover tags script
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Remover atributos on* (onclick, onerror, etc)
    text = re.sub(r'\s*on\w+\s*=\s*["\'].*?["\']', '', text, flags=re.IGNORECASE)

    # Remover javascript: URLs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

    return text
