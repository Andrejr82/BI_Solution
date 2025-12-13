# 🚀 Logging - Guia Rápido

## Backend (FastAPI)

### Uso Básico

```python
import structlog

logger = structlog.get_logger("agentbi")

# Info
logger.info("user_action", user_id=123, action="login")

# Error
logger.error("operation_failed", error=str(e), exc_info=True)

# Warning
logger.warning("slow_query", duration=3.5, query="SELECT ...")
```

### Loggers Disponíveis

```python
# Logger geral
logger = structlog.get_logger("agentbi")

# Logger de API
import logging
api_logger = logging.getLogger("agentbi.api")

# Logger de segurança
security_logger = logging.getLogger("agentbi.security")

# Logger de chat
chat_logger = logging.getLogger("agentbi.chat")

# Logger de auditoria
audit_logger = logging.getLogger("agentbi.audit")
```

## Frontend (SolidJS)

### Uso Básico

```typescript
import { log } from '@/services/logger.service';

// Info
log.info('User logged in', { method: 'password' });

// Error
log.error('API call failed', { endpoint: '/api/data' }, error);

// Page view
log.pageView('Dashboard');

// User action
log.userAction('button_clicked', { button: 'export' });

// API call
log.apiCall('GET', '/api/data', 200, 1.5);

// Performance
log.performance('page_load', 2.3, { page: 'dashboard' });
```

## Estrutura de Logs

```
logs/
├── app/           # Logs gerais
├── api/           # Logs de API
├── security/      # Logs de segurança
├── chat/          # Logs de chat
├── errors/        # Logs de erros
└── audit/         # Logs de auditoria
```

## Visualizar Logs

```bash
# Todos os logs em tempo real
tail -f logs/app/app.log

# Logs de API
tail -f logs/api/api.log

# Logs de erro
tail -f logs/errors/errors.log

# Filtrar por usuário
grep "user-123" logs/app/app.log
```

## Níveis de Log

| Nível | Quando Usar |
|-------|-------------|
| DEBUG | Informações detalhadas para debugging |
| INFO | Eventos normais (login, ações, etc) |
| WARN | Avisos (requisições lentas, etc) |
| ERROR | Erros que precisam atenção |
| CRITICAL | Erros críticos do sistema |

## ⚠️ Importante

- ✅ Sempre inclua contexto relevante nos logs
- ✅ Use `exc_info=True` ao logar exceções
- ✅ Logs são rotacionados automaticamente (10MB, 10 versões)
- ❌ NUNCA logue dados sensíveis (senhas, tokens)
- ❌ NÃO use `print()`, use o sistema de logging

## 📚 Documentação Completa

Veja `docs/SISTEMA_LOGGING.md` para documentação detalhada.
