# 🎯 Exemplos de Uso - Testes de Integração

## 📋 Cenários Comuns

### 1. Executar Testes Antes de um Deploy

```bash
# Terminal 1: Iniciar backend
cd backend
python main.py

# Terminal 2: Iniciar frontend
cd frontend-react
npm run dev

# Terminal 3: Executar testes
cd tests
run_integration_tests.bat

# Se todos passarem → OK para deploy!
```

### 2. Verificar se Nova Feature Quebrou Algo

```bash
# Executar apenas testes relacionados
pytest tests/test_integration_complete.py::TestChatBI -v

# Se falhar, debugar com mais detalhes
pytest tests/test_integration_complete.py::TestChatBI::test_chat_with_simple_query -vv --tb=long
```

### 3. Testar Apenas Endpoints Implementados

```bash
# Pular testes de funcionalidades não implementadas
pytest tests/test_integration_complete.py -v --co  # Mostra todos os testes
pytest tests/test_integration_complete.py -v -k "not admin"  # Pula testes de admin
```

### 4. Desenvolvimento Orientado a Testes (TDD)

```bash
# 1. Rodar testes (vão falhar)
pytest tests/test_integration_complete.py::TestReports -v

# 2. Implementar endpoint de reports

# 3. Rodar novamente (devem passar)
pytest tests/test_integration_complete.py::TestReports -v
```

### 5. CI/CD Pipeline

```yaml
# .github/workflows/tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Start backend
      run: |
        cd backend
        start /b python main.py
        timeout /t 10

    - name: Run tests
      run: pytest tests/test_integration_complete.py -v --junitxml=test-results.xml

    - name: Publish results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-results.xml
```

## 🔍 Debugging de Testes

### Teste Falhando: Login

```bash
# Executar com máximo de detalhes
pytest tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials -vv --tb=long --log-cli-level=DEBUG

# Verificar logs do backend
cat logs/errors/error_*.log | grep "login"

# Testar manualmente
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Teste Falhando: CORS

```bash
# Verificar configuração CORS no backend
grep -r "CORSMiddleware" backend/

# Testar preflight manualmente
curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Teste Falhando: JWT

```bash
# Gerar token manualmente
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

# Testar endpoint protegido
curl http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Análise de Cobertura

### Gerar Relatório HTML

```bash
pytest tests/test_integration_complete.py \
  --cov=backend \
  --cov=core \
  --cov-report=html \
  --cov-report=term-missing

# Abrir relatório
start htmlcov/index.html
```

### Verificar Cobertura por Arquivo

```bash
pytest tests/test_integration_complete.py \
  --cov=backend/app/api/v1/endpoints \
  --cov-report=term

# Output:
# Name                                    Stmts   Miss  Cover
# -----------------------------------------------------------
# backend/app/api/v1/endpoints/auth.py      45      3    93%
# backend/app/api/v1/endpoints/admin.py     32     20    38%
```

## 🎯 Casos de Uso Avançados

### 1. Testar Performance

```bash
# Instalar pytest-benchmark
pip install pytest-benchmark

# Executar com benchmark
pytest tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials --benchmark-only
```

### 2. Executar Testes em Paralelo

```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Executar em paralelo
pytest tests/test_integration_complete.py -n 4  # 4 workers
```

### 3. Monitorar Testes em Loop (Watch Mode)

```bash
# Instalar pytest-watch
pip install pytest-watch

# Executar em modo watch
ptw tests/test_integration_complete.py -v
```

### 4. Gerar Relatório JSON

```bash
pytest tests/test_integration_complete.py \
  --json-report \
  --json-report-file=test_results.json

# Analisar JSON
cat test_results.json | jq '.summary'
```

## 🔧 Customização dos Testes

### Adicionar Credenciais Personalizadas

```bash
# .env.test
TEST_USERNAME=meu_usuario
TEST_PASSWORD=minha_senha
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=admin123

# Executar
pytest tests/test_integration_complete.py -v
```

### Testar contra Ambiente de Staging

```bash
# .env.test
BACKEND_URL=https://staging-api.agentsolutionbi.com
FRONTEND_URL=https://staging.agentsolutionbi.com

# Executar
pytest tests/test_integration_complete.py -v
```

### Adicionar Timeout Customizado

```bash
# Para testes lentos
pytest tests/test_integration_complete.py \
  --timeout=600 \
  -m slow
```

## 📈 Relatórios Customizados

### Relatório HTML Bonito

```bash
# Instalar pytest-html
pip install pytest-html

# Gerar relatório
pytest tests/test_integration_complete.py \
  --html=report.html \
  --self-contained-html

# Abrir
start report.html
```

### Relatório para Gestores

```bash
# Gerar relatório simples
pytest tests/test_integration_complete.py -v > test_results.txt

# Processar resultados
python -c "
import re
with open('test_results.txt') as f:
    content = f.read()
    passed = len(re.findall('PASSED', content))
    failed = len(re.findall('FAILED', content))
    skipped = len(re.findall('SKIPPED', content))

print(f'''
📊 RELATÓRIO DE TESTES
━━━━━━━━━━━━━━━━━━━━━
✅ Passou: {passed}
❌ Falhou: {failed}
⏭️ Pulado: {skipped}
━━━━━━━━━━━━━━━━━━━━━
Total: {passed + failed + skipped}
Taxa de Sucesso: {passed/(passed+failed)*100:.1f}%
''')
"
```

## 🐛 Troubleshooting Avançado

### Problema: Testes Inconsistentes (Flaky Tests)

```bash
# Executar mesmo teste várias vezes
pytest tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials --count=10

# Se falhar algumas vezes → é flaky
# Adicionar retry:
pip install pytest-rerunfailures
pytest tests/test_integration_complete.py --reruns 3 --reruns-delay 1
```

### Problema: Timeout em Testes de Chat BI

```python
# Ajustar timeout no teste específico
@pytest.mark.asyncio
@pytest.mark.timeout(60)  # 60 segundos
async def test_chat_with_complex_query(self, authenticated_client, backend_url):
    # ...
```

### Problema: Banco de Dados Sujo Após Testes

```python
# Adicionar fixture de cleanup
@pytest.fixture(autouse=True)
def cleanup_database():
    yield
    # Limpar dados de teste
    # db.execute("DELETE FROM test_data WHERE created_by = 'test'")
```

## 📚 Exemplos de Output

### ✅ Todos os Testes Passando

```
tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials PASSED     [10%]
tests/test_integration_complete.py::TestJWTAuthentication::test_protected_endpoint_with_valid_token PASSED [20%]
tests/test_integration_complete.py::TestDashboard::test_analytics_summary_endpoint PASSED   [30%]
...

=============== 40 passed in 15.32s ===============
```

### ⚠️ Algumas Funcionalidades Ainda Não Implementadas

```
tests/test_integration_complete.py::TestReports::test_reports_list_endpoint SKIPPED       [60%]
tests/test_integration_complete.py::TestAdminPanel::test_admin_users_list SKIPPED         [70%]

=============== 35 passed, 5 skipped in 12.45s ===============
```

### ❌ Bug Encontrado

```
tests/test_integration_complete.py::TestCORS::test_cors_preflight FAILED                  [15%]

FAILED tests/test_integration_complete.py::TestCORS::test_cors_preflight
AssertionError: Header CORS Allow-Origin ausente

=============== 1 failed, 39 passed in 14.02s ===============
```

## 🎓 Melhores Práticas

### 1. Execute Testes Antes de Commitar

```bash
# Pre-commit hook (.git/hooks/pre-commit)
#!/bin/bash
pytest tests/test_integration_complete.py -x
if [ $? -ne 0 ]; then
    echo "❌ Testes falharam! Commit abortado."
    exit 1
fi
```

### 2. Documente Testes que Falham Esperadamente

```python
@pytest.mark.xfail(reason="Endpoint ainda não implementado")
async def test_future_feature(self):
    # ...
```

### 3. Use Markers para Organizar

```python
@pytest.mark.integration
@pytest.mark.requires_backend
async def test_backend_integration(self):
    # ...
```

### 4. Mantenha Testes Independentes

```python
# ❌ Ruim - depende de outro teste
def test_create_user():
    user = create_user("test")

def test_delete_user():
    delete_user("test")  # Depende do teste anterior!

# ✅ Bom - independente
@pytest.fixture
def test_user():
    user = create_user("test")
    yield user
    delete_user("test")

def test_delete_user(test_user):
    delete_user(test_user)
```

---

**Última atualização:** 2025-11-23

**Contribua:** Se encontrar novos casos de uso úteis, adicione a este documento!
