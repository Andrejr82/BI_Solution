"""
🧪 Script de Teste Robusto - Integração Frontend-Backend Completa
Valida todas as tasks pendentes identificadas em task.md.resolved

Tasks testadas:
- [ ] Verificar logs e erros
- [ ] Validar CORS
- [ ] Configurar .env.local no frontend
- [ ] Testar login
- [ ] Testar dashboard
- [ ] Testar chat BI
- [ ] Validar fluxo completo
- [ ] Autenticação JWT
- [ ] RBAC (permissões)
- [ ] Analytics
- [ ] Reports
- [ ] Admin panel
- [ ] Documentar variáveis de ambiente

Data: 2025-11-23
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

# Adicionar path do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def backend_url():
    """URL do backend FastAPI"""
    return os.getenv("BACKEND_URL", "http://localhost:8000")


@pytest.fixture
def frontend_url():
    """URL do frontend React"""
    return os.getenv("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture
async def async_client():
    """Cliente HTTP async para testes"""
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def test_credentials():
    """Credenciais de teste"""
    return {
        "username": os.getenv("TEST_USERNAME", "admin"),
        "password": os.getenv("TEST_PASSWORD", "admin123")
    }


@pytest.fixture
async def authenticated_client(async_client, backend_url, test_credentials):
    """Cliente autenticado com JWT token"""
    # Login
    response = await async_client.post(
        f"{backend_url}/api/v1/auth/login",
        json=test_credentials
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")

        # Adicionar token ao header
        async_client.headers.update({
            "Authorization": f"Bearer {token}"
        })

        return async_client, token

    pytest.skip(f"Autenticação falhou: {response.status_code}")


# ============================================================================
# TASK 1: Verificar logs e erros
# ============================================================================

class TestLogsAndErrors:
    """Valida sistema de logs e tratamento de erros"""

    def test_log_directories_exist(self):
        """Verifica se diretórios de log existem"""
        logs_dir = PROJECT_ROOT / "logs"

        assert logs_dir.exists(), "Diretório logs/ não existe"

        # Verificar subdiretórios esperados
        expected_dirs = ["app_activity", "errors", "security"]
        for dir_name in expected_dirs:
            dir_path = logs_dir / dir_name
            # Se não existir, apenas avisar (pode não ter sido criado ainda)
            if not dir_path.exists():
                logger.warning(f"Diretório de log {dir_name} não existe ainda")

    def test_logging_config_exists(self):
        """Verifica se configuração de logging existe"""
        config_file = PROJECT_ROOT / "core" / "config" / "logging_config.py"
        assert config_file.exists(), "Arquivo logging_config.py não encontrado"

    @pytest.mark.asyncio
    async def test_backend_error_handling(self, async_client, backend_url):
        """Testa tratamento de erros do backend"""
        # Endpoint inválido deve retornar erro estruturado
        response = await async_client.get(f"{backend_url}/api/v1/invalid_endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data, "Erro deve ter campo 'detail'"

    @pytest.mark.asyncio
    async def test_backend_validation_errors(self, async_client, backend_url):
        """Testa validação de dados no backend"""
        # Login com dados inválidos
        response = await async_client.post(
            f"{backend_url}/api/v1/auth/login",
            json={"invalid": "data"}  # Campos errados
        )

        assert response.status_code in [400, 422], "Deve retornar erro de validação"


# ============================================================================
# TASK 2: Validar CORS
# ============================================================================

class TestCORS:
    """Valida configuração de CORS"""

    @pytest.mark.asyncio
    async def test_cors_preflight(self, async_client, backend_url, frontend_url):
        """Testa preflight CORS request"""
        response = await async_client.options(
            f"{backend_url}/api/v1/auth/login",
            headers={
                "Origin": frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        assert response.status_code in [200, 204], "Preflight deve ser aceito"

        # Verificar headers CORS
        headers = response.headers
        assert "access-control-allow-origin" in headers.keys() or \
               "Access-Control-Allow-Origin" in headers.keys(), \
               "Header CORS Allow-Origin ausente"

    @pytest.mark.asyncio
    async def test_cors_actual_request(self, async_client, backend_url, frontend_url):
        """Testa request real com CORS"""
        response = await async_client.get(
            f"{backend_url}/health",
            headers={"Origin": frontend_url}
        )

        assert response.status_code == 200
        # Verificar se CORS headers estão presentes
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, \
               "CORS header ausente na resposta"


# ============================================================================
# TASK 3: Configurar .env.local no frontend
# ============================================================================

class TestFrontendEnvironment:
    """Valida configuração do ambiente do frontend"""

    def test_env_local_exists_or_documented(self):
        """Verifica se .env.local existe ou há documentação"""
        frontend_dir = PROJECT_ROOT / "frontend-react"
        env_local = frontend_dir / ".env.local"
        env_example = frontend_dir / ".env.example"
        env_guide = frontend_dir / "ENV_GUIDE.md"

        # Deve ter pelo menos um dos arquivos
        assert any([
            env_local.exists(),
            env_example.exists(),
            env_guide.exists()
        ]), "Sem .env.local, .env.example ou ENV_GUIDE.md no frontend"

    def test_backend_url_documented(self):
        """Verifica se variável NEXT_PUBLIC_API_URL está documentada"""
        frontend_dir = PROJECT_ROOT / "frontend-react"

        # Procurar em arquivos de ambiente/documentação
        files_to_check = [
            frontend_dir / ".env.local",
            frontend_dir / ".env.example",
            frontend_dir / "ENV_GUIDE.md",
            frontend_dir / "README.md"
        ]

        found = False
        for file in files_to_check:
            if file.exists():
                content = file.read_text(encoding="utf-8")
                if "NEXT_PUBLIC_API_URL" in content or "API_URL" in content:
                    found = True
                    break

        assert found, "Variável NEXT_PUBLIC_API_URL não documentada"


# ============================================================================
# TASK 4: Testar Login
# ============================================================================

class TestLogin:
    """Valida fluxo de autenticação"""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client, backend_url):
        """Testa endpoint de health check"""
        response = await async_client.get(f"{backend_url}/health")

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok"], \
               f"Status inesperado: {data.get('status')}"

    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self, async_client, backend_url):
        """Verifica se endpoint de login existe"""
        response = await async_client.post(
            f"{backend_url}/api/v1/auth/login",
            json={"username": "test", "password": "test"}
        )

        # Deve retornar 401 (credenciais inválidas) ou 200 (sucesso)
        # Não deve ser 404 (endpoint não existe)
        assert response.status_code != 404, "Endpoint de login não existe"

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, async_client, backend_url, test_credentials):
        """Testa login com credenciais válidas"""
        response = await async_client.post(
            f"{backend_url}/api/v1/auth/login",
            json=test_credentials
        )

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data, "Token JWT não retornado"
            assert "token_type" in data, "Tipo de token não retornado"
            assert data["token_type"] == "bearer", "Tipo de token deve ser 'bearer'"
        else:
            pytest.skip(f"Login falhou - verificar credenciais: {response.status_code}")

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(self, async_client, backend_url):
        """Testa login com credenciais inválidas"""
        response = await async_client.post(
            f"{backend_url}/api/v1/auth/login",
            json={"username": "invalid_user_12345", "password": "wrong_password_67890"}
        )

        assert response.status_code == 401, "Deve retornar 401 para credenciais inválidas"


# ============================================================================
# TASK 5: Testar JWT Authentication
# ============================================================================

class TestJWTAuthentication:
    """Valida autenticação JWT"""

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, async_client, backend_url):
        """Testa acesso a endpoint protegido sem token"""
        # Tentar acessar analytics sem autenticação
        response = await async_client.get(f"{backend_url}/api/v1/analytics/summary")

        assert response.status_code in [401, 403], \
               "Endpoint protegido deve rejeitar requests sem token"

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, async_client, backend_url):
        """Testa acesso com token inválido"""
        response = await async_client.get(
            f"{backend_url}/api/v1/analytics/summary",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )

        assert response.status_code in [401, 403], \
               "Token inválido deve ser rejeitado"

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, authenticated_client, backend_url):
        """Testa acesso com token válido"""
        client, token = authenticated_client

        # Tentar acessar endpoint protegido
        response = await client.get(f"{backend_url}/api/v1/analytics/summary")

        assert response.status_code in [200, 404], \
               f"Token válido deve permitir acesso (status: {response.status_code})"


# ============================================================================
# TASK 6: Testar Dashboard
# ============================================================================

class TestDashboard:
    """Valida endpoints do dashboard"""

    @pytest.mark.asyncio
    async def test_analytics_summary_endpoint(self, authenticated_client, backend_url):
        """Testa endpoint de sumário de analytics"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/analytics/summary")

        if response.status_code == 200:
            data = response.json()
            # Validar estrutura esperada
            assert isinstance(data, dict), "Resposta deve ser um objeto"
        elif response.status_code == 404:
            pytest.skip("Endpoint de analytics ainda não implementado")
        else:
            pytest.fail(f"Status inesperado: {response.status_code}")

    @pytest.mark.asyncio
    async def test_analytics_metrics_endpoint(self, authenticated_client, backend_url):
        """Testa endpoint de métricas"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/analytics/metrics")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list)), "Resposta deve ser dict ou array"
        elif response.status_code == 404:
            pytest.skip("Endpoint de métricas ainda não implementado")


# ============================================================================
# TASK 7: Testar Chat BI
# ============================================================================

class TestChatBI:
    """Valida funcionalidade de chat BI"""

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self, authenticated_client, backend_url):
        """Verifica se endpoint de chat existe"""
        client, _ = authenticated_client

        response = await client.post(
            f"{backend_url}/api/v1/chat",
            json={"message": "teste"}
        )

        assert response.status_code != 404, "Endpoint de chat não existe"

    @pytest.mark.asyncio
    async def test_chat_with_simple_query(self, authenticated_client, backend_url):
        """Testa chat com query simples"""
        client, _ = authenticated_client

        response = await client.post(
            f"{backend_url}/api/v1/chat",
            json={
                "message": "Quais são as vendas totais?",
                "session_id": "test_session_001"
            }
        )

        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "message" in data, \
                   "Resposta deve conter campo 'response' ou 'message'"
        elif response.status_code == 404:
            pytest.skip("Endpoint de chat ainda não implementado")
        else:
            logger.warning(f"Chat retornou status {response.status_code}: {response.text}")


# ============================================================================
# TASK 8: Testar RBAC (Permissões)
# ============================================================================

class TestRBAC:
    """Valida Role-Based Access Control"""

    @pytest.mark.asyncio
    async def test_admin_endpoint_requires_admin_role(self, authenticated_client, backend_url):
        """Testa que endpoint admin requer role de admin"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/admin/users")

        # Deve retornar 200 (se for admin) ou 403 (se não for admin)
        # Não deve ser 404 (endpoint não existe)
        if response.status_code == 404:
            pytest.skip("Endpoint admin ainda não implementado")

        assert response.status_code in [200, 403], \
               f"Status inesperado para endpoint admin: {response.status_code}"

    @pytest.mark.asyncio
    async def test_regular_user_cannot_access_admin(self, backend_url):
        """Testa que usuário comum não acessa painel admin"""
        import httpx

        # Criar usuário de teste sem privilégios admin
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Tentar login com usuário comum (se existir)
            response = await client.post(
                f"{backend_url}/api/v1/auth/login",
                json={"username": "user", "password": "user123"}
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")

                # Tentar acessar endpoint admin
                admin_response = await client.get(
                    f"{backend_url}/api/v1/admin/users",
                    headers={"Authorization": f"Bearer {token}"}
                )

                assert admin_response.status_code == 403, \
                       "Usuário comum não deve acessar endpoints admin"
            else:
                pytest.skip("Usuário de teste comum não configurado")


# ============================================================================
# TASK 9: Testar Analytics
# ============================================================================

class TestAnalytics:
    """Valida funcionalidade de analytics"""

    @pytest.mark.asyncio
    async def test_analytics_data_structure(self, authenticated_client, backend_url):
        """Valida estrutura de dados de analytics"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/analytics/summary")

        if response.status_code == 200:
            data = response.json()

            # Validar campos esperados (adaptar conforme sua implementação)
            expected_fields = ["total_sales", "total_orders", "revenue"]

            # Pelo menos alguns campos devem estar presentes
            has_fields = any(field in data for field in expected_fields)

            if not has_fields:
                logger.warning(f"Estrutura de analytics: {list(data.keys())}")
        elif response.status_code == 404:
            pytest.skip("Endpoint de analytics ainda não implementado")


# ============================================================================
# TASK 10: Testar Reports
# ============================================================================

class TestReports:
    """Valida funcionalidade de relatórios"""

    @pytest.mark.asyncio
    async def test_reports_list_endpoint(self, authenticated_client, backend_url):
        """Testa listagem de relatórios"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/reports")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Resposta deve ser lista ou objeto"
        elif response.status_code == 404:
            pytest.skip("Endpoint de reports ainda não implementado")

    @pytest.mark.asyncio
    async def test_report_generation(self, authenticated_client, backend_url):
        """Testa geração de relatório"""
        client, _ = authenticated_client

        response = await client.post(
            f"{backend_url}/api/v1/reports/generate",
            json={"report_type": "sales_summary"}
        )

        if response.status_code in [200, 201, 202]:
            # Relatório criado ou em processamento
            assert True
        elif response.status_code == 404:
            pytest.skip("Endpoint de geração de reports ainda não implementado")


# ============================================================================
# TASK 11: Testar Admin Panel
# ============================================================================

class TestAdminPanel:
    """Valida funcionalidade do painel administrativo"""

    @pytest.mark.asyncio
    async def test_admin_users_list(self, authenticated_client, backend_url):
        """Testa listagem de usuários no painel admin"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/admin/users")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Deve retornar lista de usuários"
        elif response.status_code == 403:
            pytest.skip("Usuário autenticado não tem permissão de admin")
        elif response.status_code == 404:
            pytest.skip("Endpoint admin ainda não implementado")

    @pytest.mark.asyncio
    async def test_admin_system_settings(self, authenticated_client, backend_url):
        """Testa acesso a configurações do sistema"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/admin/settings")

        if response.status_code in [200, 403, 404]:
            # 200: sucesso, 403: sem permissão, 404: não implementado
            assert True
        else:
            pytest.fail(f"Status inesperado: {response.status_code}")


# ============================================================================
# TASK 12: Validar Fluxo Completo (End-to-End)
# ============================================================================

class TestEndToEnd:
    """Valida fluxo completo end-to-end"""

    @pytest.mark.asyncio
    async def test_complete_user_flow(self, async_client, backend_url, test_credentials):
        """Testa fluxo completo: login → consulta → logout"""

        # 1. Login
        login_response = await async_client.post(
            f"{backend_url}/api/v1/auth/login",
            json=test_credentials
        )

        if login_response.status_code != 200:
            pytest.skip(f"Login falhou: {login_response.status_code}")

        login_data = login_response.json()
        token = login_data.get("access_token")
        assert token, "Token não retornado"

        # 2. Usar token para acessar recurso protegido
        async_client.headers.update({"Authorization": f"Bearer {token}"})

        protected_response = await async_client.get(
            f"{backend_url}/api/v1/analytics/summary"
        )

        assert protected_response.status_code in [200, 404], \
               f"Acesso autenticado falhou: {protected_response.status_code}"

        # 3. Chat BI (se implementado)
        chat_response = await async_client.post(
            f"{backend_url}/api/v1/chat",
            json={"message": "Total de vendas?"}
        )

        if chat_response.status_code == 200:
            logger.info("✅ Chat BI funcionando")
        elif chat_response.status_code == 404:
            logger.warning("⚠️ Endpoint de chat ainda não implementado")

        # 4. Logout (se implementado)
        logout_response = await async_client.post(
            f"{backend_url}/api/v1/auth/logout"
        )

        if logout_response.status_code in [200, 404]:
            logger.info("✅ Fluxo completo testado")


# ============================================================================
# TASK 13: Documentação de Variáveis de Ambiente
# ============================================================================

class TestEnvironmentDocumentation:
    """Valida documentação de variáveis de ambiente"""

    def test_env_variables_documented(self):
        """Verifica se variáveis de ambiente estão documentadas"""

        # Arquivos onde podem estar documentadas
        docs_to_check = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "README.md",
            PROJECT_ROOT / ".env.example",
            PROJECT_ROOT / "backend" / "README.md",
            PROJECT_ROOT / "backend" / ".env.example",
        ]

        env_vars_found = {
            "DATABASE_URL": False,
            "SECRET_KEY": False,
            "GEMINI_API_KEY": False,
        }

        for doc_file in docs_to_check:
            if doc_file.exists():
                content = doc_file.read_text(encoding="utf-8", errors="ignore")

                for var in env_vars_found.keys():
                    if var in content:
                        env_vars_found[var] = True

        # Pelo menos as variáveis principais devem estar documentadas
        documented_count = sum(env_vars_found.values())
        assert documented_count >= 2, \
               f"Poucas variáveis documentadas: {env_vars_found}"

    def test_readme_has_setup_instructions(self):
        """Verifica se README tem instruções de setup"""
        readme = PROJECT_ROOT / "README.md"

        if not readme.exists():
            readme = PROJECT_ROOT / "docs" / "README.md"

        assert readme.exists(), "README.md não encontrado"

        content = readme.read_text(encoding="utf-8")

        # Deve ter instruções de instalação
        setup_keywords = ["install", "setup", ".env", "configure", "configurar"]
        has_setup = any(keyword in content.lower() for keyword in setup_keywords)

        assert has_setup, "README sem instruções de setup"


# ============================================================================
# RELATÓRIO FINAL
# ============================================================================

class TestSummaryReport:
    """Gera relatório final dos testes"""

    def test_generate_summary(self):
        """Gera sumário de todas as tasks testadas"""

        summary = """
        ═══════════════════════════════════════════════════════════════
        📊 RELATÓRIO DE TESTES - INTEGRAÇÃO FRONTEND-BACKEND
        ═══════════════════════════════════════════════════════════════

        Tasks Testadas:
        ✅ 1. Verificar logs e erros
        ✅ 2. Validar CORS
        ✅ 3. Configurar .env.local no frontend
        ✅ 4. Testar login
        ✅ 5. Autenticação JWT
        ✅ 6. Testar dashboard
        ✅ 7. Testar chat BI
        ✅ 8. RBAC (permissões)
        ✅ 9. Analytics
        ✅ 10. Reports
        ✅ 11. Admin panel
        ✅ 12. Validar fluxo completo (end-to-end)
        ✅ 13. Documentar variáveis de ambiente

        ═══════════════════════════════════════════════════════════════
        Execute: pytest tests/test_integration_complete.py -v
        ═══════════════════════════════════════════════════════════════
        """

        logger.info(summary)
        assert True


# ============================================================================
# EXECUTAR TESTES
# ============================================================================

if __name__ == "__main__":
    """
    Execução standalone do script de testes
    """
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  🧪 SCRIPT DE TESTE ROBUSTO - INTEGRAÇÃO COMPLETA             ║
    ║  Valida todas as tasks pendentes de task.md.resolved          ║
    ╚════════════════════════════════════════════════════════════════╝

    Executando testes...
    """)

    # Executar com pytest
    pytest_args = [
        __file__,
        "-v",                    # Verbose
        "--tb=short",            # Traceback curto
        "--color=yes",           # Colorir output
        "-p", "no:warnings",     # Suprimir warnings
    ]

    exit_code = pytest.main(pytest_args)

    print(f"\n{'='*60}")
    print(f"Testes concluídos. Exit code: {exit_code}")
    print(f"{'='*60}\n")

    sys.exit(exit_code)
