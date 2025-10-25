# 🔐 Plano de Segurança Completo - Agent Solution BI

**Data:** 2025-10-05
**Versão:** 1.0
**Status:** 🔴 VULNERABILIDADES CRÍTICAS ENCONTRADAS

---

## 🚨 VULNERABILIDADES CRÍTICAS IDENTIFICADAS

### 1. ⚠️ CRÍTICO - Credenciais Expostas no .env

**Arquivo:** `.env` (linha 1-42)

**Problemas:**
```env
# ❌ EXPOSTO NO REPOSITÓRIO
MSSQL_PASSWORD=Cacula@2020
GEMINI_API_KEY="AIzaSyDf92aZaYWrdh_kctKGIwUCyxDIqJfazig"
DEEPSEEK_API_KEY="sk-af1bc8f63e6b4789876ab7eda11901f5"
OPENAI_API_KEY="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"
```

**Risco:** 🔴 CRÍTICO
- API keys podem ser usadas indevidamente
- Acesso não autorizado ao banco de dados
- Custos financeiros (uso de APIs)

**Ação Imediata:**
1. ✅ Verificar se `.env` está no .gitignore
2. ❌ REVOCAR todas API keys imediatamente
3. ✅ Criar `.env.example` sem valores reais
4. ✅ Remover `.env` do histórico Git

---

### 2. ⚠️ CRÍTICO - Bypass de Autenticação Hardcoded

**Arquivo:** `core/auth.py:112-120`

```python
# ❌ BYPASS DE AUTENTICAÇÃO EM PRODUÇÃO
if username == 'admin' and password == 'bypass':
    st.session_state["authenticated"] = True
    st.session_state["role"] = "admin"
```

**Risco:** 🔴 CRÍTICO
- Qualquer pessoa pode fazer login como admin
- Bypass completo do sistema de autenticação

**Ação Imediata:**
- Remover ou proteger com flag de ambiente
- Nunca deixar em produção

---

### 3. ⚠️ ALTO - .gitignore com Problemas de Merge

**Arquivo:** `.gitignore:63-86`

```
<<<<<<< HEAD
=======
data/parquet/
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
```

**Risco:** 🟠 ALTO
- Conflitos não resolvidos
- Arquivos sensíveis podem não ser ignorados

**Ação Imediata:**
- Corrigir merge conflicts
- Validar todas entradas

---

### 4. ⚠️ MÉDIO - Secrets no Streamlit

**Arquivo:** `.streamlit/secrets.toml`

```toml
GEMINI_API_KEY = "AIzaSyDf92aZaYWrdh_kctKGIwUCyxDIqJfazig"
DEEPSEEK_API_KEY = "sk-af1bc8f63e6b4789876ab7eda11901f5"
```

**Risco:** 🟡 MÉDIO
- Arquivo commitado (verificar .gitignore)
- Chaves expostas

---

### 5. ⚠️ MÉDIO - Senha de Banco Fraca

**Senha Atual:** `Cacula@2020`

**Problemas:**
- Baseada em informações previsíveis
- Ano antigo (2020)
- Pode estar em dicionários

**Recomendação:**
- Usar senha com 16+ caracteres
- Mix de maiúsculas, minúsculas, números, especiais
- Sem palavras do dicionário

---

### 6. ⚠️ MÉDIO - Falta de Rate Limiting

**Arquivos Afetados:**
- `streamlit_app.py`
- `core/llm_adapter.py`
- `core/auth.py`

**Riscos:**
- Ataques de força bruta
- Abuso de API
- DDoS

---

### 7. ⚠️ BAIXO - Logs Podem Expor Dados

**Arquivo:** `core/database/sql_server_auth_db.py`

```python
logger.info(f"Usuário {username} logado com sucesso")
```

**Problema:**
- Logs podem conter informações sensíveis
- Não há rotação de logs configurada

---

## 📋 PLANO DE AÇÃO IMEDIATO

### Fase 1: EMERGÊNCIA (Hoje - 1 hora)

#### ✅ 1.1 Revogar API Keys Expostas

```bash
# Google Gemini
# 1. Acesse: https://aistudio.google.com/app/apikey
# 2. Revogue: AIzaSyDf92aZaYWrdh_kctKGIwUCyxDIqJfazig
# 3. Crie nova key

# DeepSeek
# 1. Acesse: https://platform.deepseek.com/api_keys
# 2. Revogue: sk-af1bc8f63e6b4789876ab7eda11901f5
# 3. Crie nova key

# OpenAI
# 1. Acesse: https://platform.openai.com/api-keys
# 2. Revogue: sk-proj-Y8KqLQa43bPO6mng5N5y...
# 3. Crie nova key
```

#### ✅ 1.2 Limpar Histórico Git

```bash
# CUIDADO: Isso reescreve o histórico
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env .streamlit/secrets.toml" \
  --prune-empty --tag-name-filter cat -- --all

# Forçar push (APENAS se for repo privado)
git push origin --force --all
```

#### ✅ 1.3 Corrigir .gitignore

```bash
# Adicionar ao .gitignore
.env
.env.local
.env.*.local
.streamlit/secrets.toml
*.key
*.pem
*.p12
credentials.json
```

#### ✅ 1.4 Remover Bypass Hardcoded

```python
# Usar variável de ambiente
ENABLE_DEV_BYPASS = os.getenv("ENABLE_DEV_BYPASS", "false").lower() == "true"

if ENABLE_DEV_BYPASS and username == 'admin' and password == 'bypass':
    # ...
```

---

### Fase 2: CRÍTICO (Hoje - 4 horas)

#### 2.1 Implementar Rate Limiting

```python
# core/security/rate_limiter.py
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_calls=5, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    def is_allowed(self, key):
        now = time.time()
        # Limpar chamadas antigas
        self.calls[key] = [t for t in self.calls[key] if now - t < self.period]

        if len(self.calls[key]) < self.max_calls:
            self.calls[key].append(now)
            return True
        return False

# Uso
login_limiter = RateLimiter(max_calls=5, period=300)  # 5 tentativas em 5 min
```

#### 2.2 Validação de Inputs

```python
# core/security/input_validator.py
import re

def sanitize_username(username):
    """Remove caracteres perigosos"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', username)

def validate_sql_injection(text):
    """Detecta padrões de SQL injection"""
    dangerous = ['--', ';', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC']
    text_upper = text.upper()
    for pattern in dangerous:
        if pattern in text_upper:
            raise ValueError(f"Padrão suspeito detectado: {pattern}")
    return text
```

#### 2.3 Segurança de Sessão

```python
# Adicionar em streamlit_app.py
import secrets

# Gerar session ID único
if 'session_id' not in st.session_state:
    st.session_state.session_id = secrets.token_urlsafe(32)

# Timeout de sessão mais curto
SESSION_TIMEOUT = 1800  # 30 minutos
```

---

### Fase 3: IMPORTANTE (Amanhã - 8 horas)

#### 3.1 Criptografia de Dados Sensíveis

```python
# core/security/encryption.py
from cryptography.fernet import Fernet
import os

class DataEncryption:
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Gerar em produção e guardar em secrets
            key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

#### 3.2 Auditoria Completa

```python
# core/security/audit_logger.py
import logging
import json
from datetime import datetime

class SecurityAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("security_audit")

    def log_auth_attempt(self, username, success, ip_address=None):
        self.logger.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "event": "auth_attempt",
            "username": username,
            "success": success,
            "ip": ip_address
        }))

    def log_permission_denied(self, username, resource):
        self.logger.warning(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "event": "permission_denied",
            "username": username,
            "resource": resource
        }))
```

#### 3.3 Headers de Segurança

```python
# Para usar com Streamlit/FastAPI
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
```

---

### Fase 4: MELHORIAS (Esta Semana)

#### 4.1 Testes de Segurança Automatizados

```python
# tests/security/test_auth_security.py
def test_sql_injection_prevention():
    malicious_inputs = [
        "admin'; DROP TABLE usuarios--",
        "1' OR '1'='1",
        "admin'--",
    ]
    for inp in malicious_inputs:
        assert validate_sql_injection(inp) raises ValueError

def test_rate_limiting():
    limiter = RateLimiter(max_calls=3, period=10)
    for i in range(3):
        assert limiter.is_allowed("test_user")
    assert not limiter.is_allowed("test_user")
```

#### 4.2 Monitoramento de Segurança

```python
# core/security/monitor.py
class SecurityMonitor:
    def __init__(self):
        self.failed_logins = defaultdict(int)

    def track_failed_login(self, username):
        self.failed_logins[username] += 1
        if self.failed_logins[username] >= 5:
            self.alert_admin(f"Múltiplas tentativas falhas: {username}")

    def alert_admin(self, message):
        # Enviar email, SMS, ou notificação
        logger.critical(f"SECURITY ALERT: {message}")
```

#### 4.3 Backup e Recuperação

```python
# scripts/security/backup_encrypted.py
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.db.enc"

    # Backup criptografado
    encryption = DataEncryption()
    with open("database.db", "rb") as f:
        data = f.read()

    encrypted = encryption.encrypt(data.decode())

    with open(backup_file, "w") as f:
        f.write(encrypted)
```

---

## 🔒 CONFIGURAÇÕES DE SEGURANÇA RECOMENDADAS

### Variáveis de Ambiente Seguras

```bash
# .env.example (SEM VALORES REAIS)
GEMINI_API_KEY=your_gemini_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENAI_API_KEY=your_openai_key_here

DB_HOST=your_db_host
DB_PORT=1433
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_strong_password_here

# Segurança
ENABLE_DEV_BYPASS=false
ENCRYPTION_KEY=generate_with_fernet
SESSION_TIMEOUT=1800
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_PERIOD=300
```

### Checklist de Deploy

```markdown
## Antes de Deploy em Produção

- [ ] Revogar todas API keys de desenvolvimento
- [ ] Gerar novas API keys para produção
- [ ] Trocar senha do banco de dados
- [ ] Desabilitar bypass de autenticação
- [ ] Configurar HTTPS
- [ ] Ativar firewall
- [ ] Configurar backup automático
- [ ] Testar rate limiting
- [ ] Revisar logs de segurança
- [ ] Configurar alertas
- [ ] Documentar credenciais em cofre seguro
```

---

## 📊 MATRIZ DE RISCOS

| Vulnerabilidade | Risco | Impacto | Probabilidade | Prioridade |
|-----------------|-------|---------|---------------|------------|
| API Keys Expostas | 🔴 Crítico | Alto | Alta | P0 - Imediato |
| Bypass Hardcoded | 🔴 Crítico | Alto | Média | P0 - Imediato |
| Senha Fraca DB | 🟠 Alto | Alto | Média | P1 - Hoje |
| .gitignore Quebrado | 🟠 Alto | Médio | Alta | P1 - Hoje |
| Sem Rate Limiting | 🟡 Médio | Médio | Média | P2 - Amanhã |
| Logs Sensíveis | 🟡 Médio | Baixo | Baixa | P3 - Esta Semana |
| Sem Criptografia | 🟡 Médio | Médio | Baixa | P3 - Esta Semana |

---

## 🛡️ BOAS PRÁTICAS DE SEGURANÇA

### 1. Princípio do Menor Privilégio
```python
# Usuários só devem ter acesso ao mínimo necessário
if role == "user":
    allowed_pages = ["consultas", "visualizacao"]
elif role == "admin":
    allowed_pages = ["all"]
```

### 2. Defesa em Profundidade
```python
# Múltiplas camadas de segurança
1. Autenticação (login)
2. Autorização (permissões)
3. Validação de entrada
4. Rate limiting
5. Auditoria
```

### 3. Fail Secure
```python
# Em caso de erro, negar acesso
try:
    verify_permissions(user, resource)
except Exception:
    return False  # ← NEGAR, não permitir
```

### 4. Never Trust User Input
```python
# SEMPRE validar e sanitizar
username = sanitize_username(raw_username)
query = validate_sql_injection(raw_query)
```

---

## 🔍 FERRAMENTAS DE SEGURANÇA RECOMENDADAS

### Análise de Código
```bash
# Bandit - Python security linter
pip install bandit
bandit -r core/ pages/

# Safety - Vulnerabilidades em dependências
pip install safety
safety check
```

### Testes de Penetração
```bash
# OWASP ZAP - Scanner de vulnerabilidades web
# https://www.zaproxy.org/

# SQLMap - SQL injection testing
# https://sqlmap.org/
```

### Monitoramento
```bash
# Sentry - Error tracking
# https://sentry.io/

# New Relic - Application monitoring
# https://newrelic.com/
```

---

## 📚 RECURSOS E REFERÊNCIAS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Streamlit Security](https://docs.streamlit.io/library/advanced-features/security-reminders)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

## 📞 CONTATOS DE EMERGÊNCIA

**Em caso de incidente de segurança:**

1. Revogar credenciais comprometidas
2. Notificar equipe de segurança
3. Documentar o incidente
4. Implementar correções
5. Fazer post-mortem

---

**Próxima Revisão:** Mensal
**Responsável:** Equipe de Desenvolvimento
**Aprovação:** Gerência de TI

---

## ✅ AÇÕES IMPLEMENTADAS NESTE PLANO

- [ ] Revogar API keys expostas
- [ ] Corrigir .gitignore
- [ ] Remover bypass de auth
- [ ] Implementar rate limiting
- [ ] Adicionar validação de inputs
- [ ] Melhorar logging de segurança
- [ ] Criar testes de segurança
- [ ] Documentar procedimentos
- [ ] Configurar monitoramento
- [ ] Treinar equipe

---

**Status:** 🔴 AÇÃO IMEDIATA NECESSÁRIA
**Última Atualização:** 2025-10-05
