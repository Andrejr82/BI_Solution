# ⚡ Quick Reference - Testes de Integração

## 🚀 Comandos Rápidos

### Executar Testes

```bash
# Modo mais simples
cd tests && run_integration_tests.bat

# Todos os testes
pytest tests/test_integration_complete.py -v

# Teste específico
pytest tests/test_integration_complete.py::TestLogin -v

# Com coverage
pytest tests/test_integration_complete.py --cov=backend --cov=core
```

### Iniciar Serviços

```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend-react && npm run dev

# Streamlit (alternativo)
streamlit run streamlit_app.py
```

## 📊 Status dos Testes por Task

| Task | Classe de Teste | Status | Comando |
|------|----------------|--------|---------|
| Logs/Erros | `TestLogsAndErrors` | ✅ | `pytest tests/test_integration_complete.py::TestLogsAndErrors -v` |
| CORS | `TestCORS` | ✅ | `pytest tests/test_integration_complete.py::TestCORS -v` |
| .env.local | `TestFrontendEnvironment` | ✅ | `pytest tests/test_integration_complete.py::TestFrontendEnvironment -v` |
| Login | `TestLogin` | ✅ | `pytest tests/test_integration_complete.py::TestLogin -v` |
| JWT | `TestJWTAuthentication` | ✅ | `pytest tests/test_integration_complete.py::TestJWTAuthentication -v` |
| Dashboard | `TestDashboard` | ✅ | `pytest tests/test_integration_complete.py::TestDashboard -v` |
| Chat BI | `TestChatBI` | ✅ | `pytest tests/test_integration_complete.py::TestChatBI -v` |
| RBAC | `TestRBAC` | ✅ | `pytest tests/test_integration_complete.py::TestRBAC -v` |
| Analytics | `TestAnalytics` | ✅ | `pytest tests/test_integration_complete.py::TestAnalytics -v` |
| Reports | `TestReports` | ✅ | `pytest tests/test_integration_complete.py::TestReports -v` |
| Admin | `TestAdminPanel` | ✅ | `pytest tests/test_integration_complete.py::TestAdminPanel -v` |
| End-to-End | `TestEndToEnd` | ✅ | `pytest tests/test_integration_complete.py::TestEndToEnd -v` |
| Docs | `TestEnvironmentDocumentation` | ✅ | `pytest tests/test_integration_complete.py::TestEnvironmentDocumentation -v` |

## 🔧 Configuração Rápida

### 1. Configurar Ambiente de Teste

```bash
# Copiar template
cp tests/.env.test.example tests/.env.test

# Editar credenciais
notepad tests/.env.test
```

### 2. Instalar Dependências

```bash
pip install pytest pytest-asyncio httpx python-dotenv
```

### 3. Verificar Serviços

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

## 🎯 Filtros Úteis

### Por Marker

```bash
# Apenas testes de integração
pytest tests/test_integration_complete.py -m integration

# Apenas testes unitários
pytest tests/test_integration_complete.py -m unit

# Apenas testes que requerem backend
pytest tests/test_integration_complete.py -m requires_backend
```

### Por Palavra-chave

```bash
# Todos os testes de login
pytest tests/test_integration_complete.py -k login

# Todos os testes de JWT
pytest tests/test_integration_complete.py -k jwt

# Todos os testes exceto admin
pytest tests/test_integration_complete.py -k "not admin"
```

### Por Status

```bash
# Parar no primeiro erro
pytest tests/test_integration_complete.py -x

# Mostrar apenas falhas
pytest tests/test_integration_complete.py --tb=short

# Mostrar apenas skips
pytest tests/test_integration_complete.py -rs
```

## 📋 Checklist Pré-Execução

- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:3000
- [ ] Arquivo `.env.test` configurado
- [ ] Credenciais de teste válidas
- [ ] Banco de dados acessível
- [ ] Ambiente virtual ativado

## 🐛 Troubleshooting Rápido

### Connection Refused

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Se não estiver, iniciar:
cd backend && python main.py
```

### 401 Unauthorized

```bash
# Verificar credenciais em .env.test
cat tests/.env.test | grep TEST_USERNAME

# Testar login manualmente
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### ModuleNotFoundError

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar pytest
python -m pytest --version
```

### Testes Lentos

```bash
# Executar em paralelo (requer pytest-xdist)
pip install pytest-xdist
pytest tests/test_integration_complete.py -n 4
```

## 📊 Interpretação de Resultados

### Símbolos

- `.` = Teste passou (PASSED)
- `F` = Teste falhou (FAILED)
- `s` = Teste pulado (SKIPPED)
- `E` = Erro na execução (ERROR)
- `x` = Falha esperada (XFAIL)

### Exit Codes

- `0` = Todos os testes passaram
- `1` = Alguns testes falharam
- `2` = Execução interrompida pelo usuário
- `3` = Erro interno do pytest
- `4` = Erro de uso do pytest
- `5` = Nenhum teste foi coletado

## 🔍 Debug Rápido

### Teste Específico com Máximo de Detalhes

```bash
pytest tests/test_integration_complete.py::TestLogin::test_login_with_valid_credentials \
  -vv \
  --tb=long \
  --log-cli-level=DEBUG \
  --capture=no
```

### Ver Output Completo

```bash
pytest tests/test_integration_complete.py -v -s
```

### Mostrar Variáveis Locais em Falhas

```bash
pytest tests/test_integration_complete.py -l
```

## 📈 Relatórios

### HTML

```bash
pip install pytest-html
pytest tests/test_integration_complete.py --html=report.html --self-contained-html
start report.html
```

### Coverage HTML

```bash
pytest tests/test_integration_complete.py --cov=backend --cov-report=html
start htmlcov/index.html
```

### JSON

```bash
pip install pytest-json-report
pytest tests/test_integration_complete.py --json-report --json-report-file=results.json
```

## 💡 Dicas

### 1. Watch Mode (Auto-rerun)

```bash
pip install pytest-watch
ptw tests/test_integration_complete.py
```

### 2. Retry em Falhas

```bash
pip install pytest-rerunfailures
pytest tests/test_integration_complete.py --reruns 3
```

### 3. Benchmark

```bash
pip install pytest-benchmark
pytest tests/test_integration_complete.py --benchmark-only
```

### 4. Timeout Global

```bash
pip install pytest-timeout
pytest tests/test_integration_complete.py --timeout=300
```

## 🎯 Casos de Uso Comuns

### Antes de Commitar

```bash
pytest tests/test_integration_complete.py -x --tb=short
```

### Antes de Deploy

```bash
pytest tests/test_integration_complete.py -v --tb=short --maxfail=5
```

### CI/CD

```bash
pytest tests/test_integration_complete.py -v --junitxml=test-results.xml --cov=backend --cov-report=xml
```

### Desenvolvimento

```bash
ptw tests/test_integration_complete.py -v --tb=short
```

## 📞 Links Úteis

- [Documentação Completa](README_TESTES.md)
- [Exemplos de Uso](EXEMPLOS_USO.md)
- [Resumo Executivo](../docs/RESUMO_TESTES_INTEGRACAO.md)
- [Pytest Docs](https://docs.pytest.org/)

---

**Última atualização:** 2025-11-23
