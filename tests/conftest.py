"""
Configuração global do pytest para testes de integração

Este arquivo é carregado automaticamente pelo pytest e configura:
- Fixtures globais
- Markers personalizados
- Configurações de ambiente
- Hooks de pytest
"""

import pytest
import os
import sys
from pathlib import Path
import logging

# Adicionar projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    """Configuração executada antes de todos os testes"""

    # Registrar markers customizados
    config.addinivalue_line(
        "markers", "integration: marca testes de integração (lentos)"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários (rápidos)"
    )
    config.addinivalue_line(
        "markers", "e2e: marca testes end-to-end (muito lentos)"
    )
    config.addinivalue_line(
        "markers", "requires_backend: requer backend rodando"
    )
    config.addinivalue_line(
        "markers", "requires_frontend: requer frontend rodando"
    )


@pytest.fixture(scope="session")
def backend_running():
    """Verifica se backend está rodando"""
    import httpx

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

    try:
        response = httpx.get(f"{backend_url}/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def frontend_running():
    """Verifica se frontend está rodando"""
    import httpx

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    try:
        response = httpx.get(frontend_url, timeout=5.0)
        return response.status_code in [200, 404]  # 404 também indica que está rodando
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """Valida ambiente antes de executar testes"""

    # Verificar arquivo .env
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        logging.warning("⚠️ Arquivo .env não encontrado - alguns testes podem falhar")

    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Log de configuração
    logging.info("=" * 60)
    logging.info("🧪 AMBIENTE DE TESTES CONFIGURADO")
    logging.info(f"Backend URL: {os.getenv('BACKEND_URL', 'http://localhost:8000')}")
    logging.info(f"Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    logging.info("=" * 60)


@pytest.fixture
def clean_test_data():
    """Limpa dados de teste após cada teste"""
    yield
    # Cleanup após o teste
    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook para capturar resultado de cada teste"""

    outcome = yield
    rep = outcome.get_result()

    # Salvar resultado no item para acesso posterior
    setattr(item, f"rep_{rep.when}", rep)


def pytest_runtest_logreport(report):
    """Hook para logging customizado dos testes"""

    if report.when == "call":
        # Log de resultado de cada teste
        status = "✅" if report.passed else "❌"
        logging.info(f"{status} {report.nodeid}")
