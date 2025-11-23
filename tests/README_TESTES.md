# 🧪 Guia de Testes de Integração - Agent Solution BI

## 📋 Visão Geral

Este diretório contém testes robustos que validam **todas as tasks pendentes** identificadas em `task.md.resolved`:

### ✅ Tasks Validadas

| # | Task | Status | Testes |
|---|------|--------|--------|
| 1 | Verificar logs e erros | ✅ | `TestLogsAndErrors` |
| 2 | Validar CORS | ✅ | `TestCORS` |
| 3 | Configurar .env.local | ✅ | `TestFrontendEnvironment` |
| 4 | Testar login | ✅ | `TestLogin` |
| 5 | Autenticação JWT | ✅ | `TestJWTAuthentication` |
| 6 | Testar dashboard | ✅ | `TestDashboard` |
| 7 | Testar chat BI | ✅ | `TestChatBI` |
| 8 | RBAC (permissões) | ✅ | `TestRBAC` |
| 9 | Analytics | ✅ | `TestAnalytics` |
| 10 | Reports | ✅ | `TestReports` |
| 11 | Admin panel | ✅ | `TestAdminPanel` |
| 12 | Fluxo end-to-end | ✅ | `TestEndToEnd` |
| 13 | Documentação | ✅ | `TestEnvironmentDocumentation` |

## 🚀 Executando os Testes

### Opção 1: Script Automatizado (Recomendado)

```bash
# Windows
cd tests
run_integration_tests.bat
```

O script automaticamente:
- ✅ Ativa o ambiente virtual
- ✅ Instala dependências necessárias
- ✅ Verifica se backend/frontend estão rodando
- ✅ Executa todos os testes
- ✅ Gera relatório detalhado

### Opção 2: Pytest Manual

```bash
# Todos os testes
pytest tests/test_integration_complete.py -v

# Testes específicos
pytest tests/test_integration_complete.py::TestLogin -v

# Com coverage
pytest tests/test_integration_complete.py --cov=backend --cov-report=html

# Modo verbose com logs
pytest tests/test_integration_complete.py -v --log-cli-level=INFO
```

### Opção 3: Execução Standalone

```bash
python tests/test_integration_complete.py
```

## 📦 Pré-Requisitos

### 1. Serviços Rodando

**Backend FastAPI:**
```bash
cd backend
python main.py
# → http://localhost:8000
```

**Frontend React:**
```bash
cd frontend-react
npm run dev
# → http://localhost:3000
```

### 2. Dependências Python

```bash
pip install pytest pytest-asyncio httpx python-dotenv
```

### 3. Configuração de Ambiente

Copie o arquivo de exemplo:
```bash
cp tests/.env.test.example tests/.env.test
```

Edite `.env.test` com suas credenciais:
```env
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
TEST_USERNAME=admin
TEST_PASSWORD=admin123
```

## 📊 Estrutura dos Testes

### Classes de Teste

```
test_integration_complete.py
├── TestLogsAndErrors          # Validação de logs e erros
├── TestCORS                   # Configuração CORS
├── TestFrontendEnvironment    # Variáveis de ambiente frontend
├── TestLogin                  # Autenticação e login
├── TestJWTAuthentication      # Tokens JWT
├── TestDashboard              # Endpoints de dashboard
├── TestChatBI                 # Funcionalidade de chat
├── TestRBAC                   # Controle de acesso
├── TestAnalytics              # Analytics e métricas
├── TestReports                # Geração de relatórios
├── TestAdminPanel             # Painel administrativo
├── TestEndToEnd               # Fluxo completo
├── TestEnvironmentDocumentation # Validação de docs
└── TestSummaryReport          # Relatório final
```

### Fixtures Disponíveis

```python
@pytest.fixture
async def async_client():
    """Cliente HTTP assíncrono"""

@pytest.fixture
def test_credentials():
    """Credenciais de teste"""

@pytest.fixture
async def authenticated_client():
    """Cliente autenticado com JWT"""

@pytest.fixture
def backend_url():
    """URL do backend"""

@pytest.fixture
def frontend_url():
    """URL do frontend"""
```

## 🎯 Casos de Uso

### Executar apenas testes rápidos

```bash
pytest tests/test_integration_complete.py -m "not e2e" -v
```

### Executar apenas testes que requerem backend

```bash
pytest tests/test_integration_complete.py -m requires_backend -v
```

### Executar com timeout

```bash
pytest tests/test_integration_complete.py --timeout=300 -v
```

### Modo debug (parar no primeiro erro)

```bash
pytest tests/test_integration_complete.py -x -v
```

### Executar teste específico

```bash
pytest tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials -v
```

## 📈 Interpretando Resultados

### ✅ Sucesso (PASSED)

```
tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials PASSED
```
✅ Funcionalidade implementada e funcionando corretamente

### ⏭️ Pulado (SKIPPED)

```
tests/test_integration_complete.py::TestChatBI::test_chat_endpoint_exists SKIPPED
```
⏭️ Funcionalidade ainda não implementada (esperado)

### ❌ Falha (FAILED)

```
tests/test_integration_complete.py::TestCORS::test_cors_preflight FAILED
```
❌ Problema encontrado - precisa correção

### ⚠️ Erro (ERROR)

```
tests/test_integration_complete.py::TestDashboard::test_analytics_summary ERROR
```
⚠️ Erro de infraestrutura (backend não rodando, timeout, etc.)

## 🔍 Troubleshooting

### Problema: "Connection refused"

**Causa:** Backend/Frontend não está rodando

**Solução:**
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend-react
npm run dev

# Terminal 3: Testes
pytest tests/test_integration_complete.py -v
```

### Problema: "401 Unauthorized"

**Causa:** Credenciais de teste inválidas

**Solução:**
1. Verifique `tests/.env.test`
2. Confirme que usuário existe no banco
3. Ou ajuste `TEST_USERNAME` e `TEST_PASSWORD`

### Problema: Muitos testes pulados

**Causa:** Endpoints ainda não implementados

**Solução:** Isso é esperado! Os testes validam o que **deve** ser implementado.

### Problema: "ModuleNotFoundError"

**Causa:** Dependências não instaladas

**Solução:**
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

## 📝 Adicionando Novos Testes

### Template de Teste

```python
class TestMinhaFuncionalidade:
    """Valida minha nova funcionalidade"""

    @pytest.mark.asyncio
    async def test_meu_endpoint(self, authenticated_client, backend_url):
        """Testa meu novo endpoint"""
        client, _ = authenticated_client

        response = await client.get(f"{backend_url}/api/v1/meu-endpoint")

        assert response.status_code == 200
        data = response.json()
        assert "campo_esperado" in data
```

### Boas Práticas

1. **Nome descritivo:** `test_what_it_does_when_condition`
2. **Docstring clara:** Explique o que está sendo testado
3. **Asserts específicos:** Verifique valores exatos, não apenas tipos
4. **Mensagens úteis:** Use `assert x, "Mensagem clara do erro"`
5. **Cleanup:** Use fixtures para limpar dados de teste

## 📊 Cobertura de Código

### Gerar relatório de cobertura

```bash
pytest tests/test_integration_complete.py \
  --cov=backend \
  --cov=core \
  --cov-report=html \
  --cov-report=term
```

### Visualizar relatório

```bash
# Abre no navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac/Linux
```

## 🎓 Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Async Client](https://www.python-httpx.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 📞 Suporte

Se encontrar problemas:

1. ✅ Verifique logs: `logs/errors/`
2. ✅ Execute com `-v` para mais detalhes
3. ✅ Verifique se serviços estão rodando
4. ✅ Confirme variáveis de ambiente em `.env.test`

## 📅 Histórico

- **2025-11-23:** Criação inicial do script de testes robusto
- Valida todas as 13 tasks pendentes de `task.md.resolved`
- Cobertura: Logs, CORS, Auth JWT, Dashboard, Chat BI, RBAC, Analytics, Reports, Admin, E2E

---

**Status:** ✅ Pronto para uso

**Última atualização:** 2025-11-23
