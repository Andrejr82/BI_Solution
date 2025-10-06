"""
Testes de segurança para os módulos de proteção
"""
import pytest
import time
from core.security.rate_limiter import RateLimiter
from core.security.input_validator import (
    sanitize_username,
    validate_sql_injection,
    validate_email,
    sanitize_path,
    validate_password_strength,
    sanitize_html
)


class TestRateLimiter:
    """Testes para o rate limiter"""

    def test_rate_limiter_allows_under_limit(self):
        """Deve permitir chamadas abaixo do limite"""
        limiter = RateLimiter(max_calls=3, period=60)
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True

    def test_rate_limiter_blocks_over_limit(self):
        """Deve bloquear chamadas acima do limite"""
        limiter = RateLimiter(max_calls=3, period=60)
        limiter.is_allowed("user2")
        limiter.is_allowed("user2")
        limiter.is_allowed("user2")
        assert limiter.is_allowed("user2") == False

    def test_rate_limiter_resets_after_period(self):
        """Deve resetar após o período"""
        limiter = RateLimiter(max_calls=2, period=1)  # 1 segundo
        limiter.is_allowed("user3")
        limiter.is_allowed("user3")
        assert limiter.is_allowed("user3") == False
        time.sleep(1.1)  # Esperar período expirar
        assert limiter.is_allowed("user3") == True

    def test_rate_limiter_different_users(self):
        """Deve isolar limites por usuário"""
        limiter = RateLimiter(max_calls=2, period=60)
        limiter.is_allowed("user4")
        limiter.is_allowed("user4")
        assert limiter.is_allowed("user4") == False
        assert limiter.is_allowed("user5") == True  # Outro usuário ainda pode

    def test_rate_limiter_reset(self):
        """Deve resetar contador manualmente"""
        limiter = RateLimiter(max_calls=1, period=60)
        limiter.is_allowed("user6")
        assert limiter.is_allowed("user6") == False
        limiter.reset("user6")
        assert limiter.is_allowed("user6") == True

    def test_rate_limiter_remaining_calls(self):
        """Deve retornar número de chamadas restantes"""
        limiter = RateLimiter(max_calls=5, period=60)
        limiter.is_allowed("user7")
        limiter.is_allowed("user7")
        assert limiter.get_remaining_calls("user7") == 3


class TestInputValidator:
    """Testes para validadores de entrada"""

    def test_sanitize_username_removes_dangerous_chars(self):
        """Deve remover caracteres perigosos"""
        # Hífens são permitidos em usernames, mas aspas e espaços são removidos
        assert sanitize_username("admin'; DROP TABLE--") == "adminDROPTABLE--"
        assert sanitize_username("user@domain.com") == "userdomain.com"
        assert sanitize_username("valid_user-123") == "valid_user-123"

    def test_sanitize_username_limits_length(self):
        """Deve limitar tamanho do username"""
        long_name = "a" * 100
        result = sanitize_username(long_name)
        assert len(result) == 50

    def test_validate_sql_injection_detects_attacks(self):
        """Deve detectar tentativas de SQL injection"""
        with pytest.raises(ValueError):
            validate_sql_injection("admin'; DROP TABLE usuarios--")

        with pytest.raises(ValueError):
            validate_sql_injection("1=1 OR 1=1")

        with pytest.raises(ValueError):
            validate_sql_injection("DROP TABLE usuarios")

        with pytest.raises(ValueError):
            validate_sql_injection("DELETE FROM usuarios")

    def test_validate_sql_injection_allows_safe_text(self):
        """Deve permitir texto seguro"""
        safe_text = "Calcular total de vendas por categoria"
        assert validate_sql_injection(safe_text) == safe_text

    def test_validate_email_valid(self):
        """Deve validar emails corretos"""
        assert validate_email("user@example.com") == True
        assert validate_email("test.user@domain.co.uk") == True

    def test_validate_email_invalid(self):
        """Deve rejeitar emails inválidos"""
        assert validate_email("invalid") == False
        assert validate_email("@example.com") == False
        assert validate_email("user@") == False

    def test_sanitize_path_blocks_traversal(self):
        """Deve bloquear directory traversal"""
        with pytest.raises(ValueError):
            sanitize_path("../../etc/passwd")

        with pytest.raises(ValueError):
            sanitize_path("C:\\Windows\\System32")

    def test_sanitize_path_allows_safe_paths(self):
        """Deve permitir paths seguros"""
        safe_path = "data/parquet/file.parquet"
        assert sanitize_path(safe_path) == safe_path

    def test_validate_password_strength_weak(self):
        """Deve rejeitar senhas fracas"""
        is_valid, msg = validate_password_strength("abc")
        assert is_valid == False
        assert "8 caracteres" in msg

        is_valid, msg = validate_password_strength("password")
        assert is_valid == False

    def test_validate_password_strength_strong(self):
        """Deve aceitar senhas fortes"""
        is_valid, msg = validate_password_strength("Senha@Forte123")
        assert is_valid == True
        assert msg is None

    def test_sanitize_html_removes_scripts(self):
        """Deve remover tags script"""
        malicious = "<script>alert('XSS')</script>Texto"
        result = sanitize_html(malicious)
        assert "<script>" not in result
        assert "alert" not in result

    def test_sanitize_html_removes_event_handlers(self):
        """Deve remover event handlers"""
        malicious = '<img src="x" onerror="alert(1)">'
        result = sanitize_html(malicious)
        assert "onerror" not in result

    def test_sanitize_html_removes_javascript_urls(self):
        """Deve remover javascript: URLs"""
        malicious = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_html(malicious)
        assert "javascript:" not in result


class TestSecurityIntegration:
    """Testes de integração de segurança"""

    def test_login_protection_scenario(self):
        """Simula proteção de login completa"""
        limiter = RateLimiter(max_calls=3, period=300)

        # Username com caracteres perigosos - aspas são removidas
        raw_username = "admin'; DROP"
        clean_username = sanitize_username(raw_username)
        assert "'" not in clean_username
        assert ";" not in clean_username
        assert " " not in clean_username  # Espaços também são removidos

        # Tentativas de login
        assert limiter.is_allowed(clean_username) == True
        assert limiter.is_allowed(clean_username) == True
        assert limiter.is_allowed(clean_username) == True
        assert limiter.is_allowed(clean_username) == False  # Bloqueado

    def test_user_creation_validation(self):
        """Valida criação de usuário completa"""
        # Username
        username = sanitize_username("new_user@123")
        assert username == "new_user123"

        # Senha fraca deve falhar
        is_valid, msg = validate_password_strength("weak")
        assert is_valid == False

        # Senha forte deve passar
        is_valid, msg = validate_password_strength("Strong@Pass123")
        assert is_valid == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
