# Sistema de Logging - AgentBI

Sistema completo de logging para backend (FastAPI) e frontend (SolidJS) com integração entre ambos.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Backend - Configuração](#backend---configuração)
3. [Backend - Uso](#backend---uso)
4. [Frontend - Configuração](#frontend---configuração)
5. [Frontend - Uso](#frontend---uso)
6. [Estrutura de Logs](#estrutura-de-logs)
7. [Visualização e Análise](#visualização-e-análise)

---

## Visão Geral

O sistema de logging foi projetado para:

- ✅ **Rastreabilidade completa**: Todos os eventos são registrados
- ✅ **Performance**: Logs rotativos e assíncronos
- ✅ **Segurança**: Logs separados para eventos de segurança
- ✅ **Auditoria**: Rastreamento de todas as operações importantes
- ✅ **Debugging**: Níveis de log configuráveis por ambiente
- ✅ **Integração**: Frontend envia logs importantes para o backend

### Níveis de Log

| Nível | Valor | Uso |
|-------|-------|-----|
| DEBUG | 0/10 | Informações detalhadas para debugging |
| INFO | 1/20 | Eventos normais do sistema |
| WARN | 2/30 | Avisos que não são erros |
| ERROR | 3/40 | Erros que precisam atenção |
| CRITICAL | 4/50 | Erros críticos que afetam o sistema |

---

## Backend - Configuração

### Estrutura de Diretórios

```
logs/
├── app/           # Logs gerais da aplicação
│   └── app.log
├── api/           # Logs de requisições API
│   └── api.log
├── security/      # Logs de segurança
│   └── security.log
├── chat/          # Logs de conversas do ChatBI
│   └── chat.log
├── errors/        # Logs de erros
│   ├── errors.log
│   └── critical.log
└── audit/         # Logs de auditoria
    └── audit.log
```

### Inicialização

O sistema de logging é inicializado automaticamente no `main.py`:

```python
from app.core.logging_config import setup_application_logging

# Setup logging
loggers = setup_application_logging(environment=settings.ENVIRONMENT)
```

### Middlewares Disponíveis

1. **RequestLoggingMiddleware**: Registra todas as requisições HTTP
2. **PerformanceLoggingMiddleware**: Identifica requisições lentas
3. **SecurityLoggingMiddleware**: Monitora eventos de segurança
4. **AuditLoggingMiddleware**: Registra operações de escrita
5. **ErrorLoggingMiddleware**: Captura todos os erros

Todos são adicionados automaticamente no `main.py`.

---

## Backend - Uso

### Logging Básico

```python
import logging
import structlog

# Logger estruturado (recomendado)
logger = structlog.get_logger("agentbi")

logger.info("user_logged_in", user_id=user.id, ip_address=request.client.host)
logger.error("database_connection_failed", error=str(e))

# Logger tradicional
logger = logging.getLogger("agentbi.api")
logger.info("API call received")
logger.error("Error processing request", exc_info=True)
```

### Logging por Módulo

```python
# Logger específico para API
api_logger = logging.getLogger("agentbi.api")

# Logger específico para segurança
security_logger = logging.getLogger("agentbi.security")

# Logger específico para chat
chat_logger = logging.getLogger("agentbi.chat")

# Logger específico para auditoria
audit_logger = logging.getLogger("agentbi.audit")
```

### Funções Auxiliares

#### Log de Requisição API

```python
from app.core.logging_config import log_api_request

log_api_request(
    logger=api_logger,
    method="POST",
    endpoint="/api/v1/chat",
    user_id=user.id,
    ip_address=request.client.host,
    request_id="abc-123"
)
```

#### Log de Resposta API

```python
from app.core.logging_config import log_api_response

log_api_response(
    logger=api_logger,
    method="POST",
    endpoint="/api/v1/chat",
    status_code=200,
    duration=0.523,  # segundos
    user_id=user.id,
    request_id="abc-123"
)
```

#### Log de Evento de Segurança

```python
from app.core.logging_config import log_security_event

log_security_event(
    logger=security_logger,
    event_type="login_attempt",
    user_id=user.id,
    ip_address=request.client.host,
    details={"method": "password"},
    success=True
)
```

#### Log de Auditoria

```python
from app.core.logging_config import log_audit_event

log_audit_event(
    logger=audit_logger,
    action="user_created",
    user_id=current_user.id,
    resource="user",
    resource_id=new_user.id,
    changes={"email": "novo@email.com"},
    ip_address=request.client.host
)
```

#### Log de Interação de Chat

```python
from app.core.logging_config import log_chat_interaction

log_chat_interaction(
    logger=chat_logger,
    user_id=user.id,
    message="Mostre as vendas de hoje",
    response="Aqui estão as vendas...",
    tokens_used=150,
    duration=1.2,
    model="gpt-4"
)
```

### Exemplo em Endpoint

```python
from fastapi import APIRouter, Depends
import structlog

router = APIRouter()
logger = structlog.get_logger("agentbi.api")

@router.post("/items")
async def create_item(item: Item, user: User = Depends(get_current_user)):
    logger.info(
        "creating_item",
        user_id=user.id,
        item_name=item.name
    )

    try:
        result = await create_item_in_db(item)

        logger.info(
            "item_created",
            user_id=user.id,
            item_id=result.id
        )

        return result

    except Exception as e:
        logger.error(
            "item_creation_failed",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )
        raise
```

---

## Frontend - Configuração

### Inicialização

No arquivo de entrada da aplicação (`index.tsx`):

```typescript
import { getLogger, LogLevel } from './services/logger.service';

// Configurar logger
const logger = getLogger({
  minLevel: import.meta.env.DEV ? LogLevel.DEBUG : LogLevel.INFO,
  enableConsole: true,
  enableRemote: true,
  remoteEndpoint: '/api/v1/logs',
  maxBufferSize: 50,
  flushInterval: 10000, // 10 segundos
  includeStackTrace: import.meta.env.DEV,
  sanitizeData: true,
});
```

### Variáveis de Ambiente

```env
# .env
VITE_LOG_LEVEL=DEBUG
VITE_ENABLE_REMOTE_LOGGING=true
VITE_LOG_ENDPOINT=/api/v1/logs
```

---

## Frontend - Uso

### Logging Básico

```typescript
import { log } from '@/services/logger.service';

// Debug
log.debug('Component mounted', { componentName: 'Dashboard' });

// Info
log.info('User action completed', { action: 'filter_applied' });

// Warning
log.warn('API response slow', { endpoint: '/api/data', duration: 3.5 });

// Error
log.error('Failed to load data', { endpoint: '/api/data' }, error);

// Critical
log.critical('Application crash', { reason: 'Out of memory' }, error);
```

### Logging de Eventos Específicos

#### Page View

```typescript
import { log } from '@/services/logger.service';

log.pageView('Dashboard', {
  section: 'analytics',
  filters: { date: '2024-01-01' }
});
```

#### User Action

```typescript
log.userAction('button_clicked', {
  button: 'export_data',
  format: 'excel',
  recordCount: 1500
});
```

#### API Call

```typescript
const startTime = Date.now();

try {
  const response = await fetch('/api/data');
  const duration = Date.now() - startTime;

  log.apiCall(
    'GET',
    '/api/data',
    response.status,
    duration
  );
} catch (error) {
  const duration = Date.now() - startTime;

  log.apiCall(
    'GET',
    '/api/data',
    0,
    duration,
    error
  );
}
```

#### Performance Metric

```typescript
log.performance('page_load_time', loadTime, {
  page: 'dashboard',
  cached: false
});
```

### Integração com Componentes SolidJS

```typescript
import { createEffect, onMount, onCleanup } from 'solid-js';
import { log } from '@/services/logger.service';

function Dashboard() {
  onMount(() => {
    log.pageView('Dashboard');
    log.info('Dashboard component mounted');
  });

  const handleExport = () => {
    log.userAction('export_clicked', { format: 'excel' });

    try {
      // lógica de export
      log.info('Export completed successfully');
    } catch (error) {
      log.error('Export failed', { format: 'excel' }, error);
    }
  };

  return (
    <div>
      <button onClick={handleExport}>Export</button>
    </div>
  );
}
```

### Error Boundary

```typescript
import { ErrorBoundary } from 'solid-js';
import { log } from '@/services/logger.service';

function App() {
  return (
    <ErrorBoundary
      fallback={(error) => {
        log.critical('Application error boundary caught error', {
          component: 'App'
        }, error);

        return <div>Erro ao carregar aplicação</div>;
      }}
    >
      <YourApp />
    </ErrorBoundary>
  );
}
```

---

## Estrutura de Logs

### Formato JSON (Produção)

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "agentbi.api",
  "message": "API Request: POST /api/v1/chat",
  "module": "chat",
  "function": "chat_endpoint",
  "line": 45,
  "request_id": "abc-123-def",
  "user_id": "user-456",
  "ip_address": "192.168.1.1",
  "endpoint": "/api/v1/chat",
  "method": "POST",
  "duration": "1.234s"
}
```

### Formato Console (Desenvolvimento)

```
2024-01-15 10:30:00 - agentbi.api - INFO - API Request: POST /api/v1/chat
```

### Logs do Frontend

Os logs do frontend são enviados em lote para o backend:

```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00.123Z",
      "level": 1,
      "levelName": "INFO",
      "message": "User logged in",
      "context": {
        "method": "password"
      },
      "user": {
        "id": "user-123",
        "email": "user@example.com"
      },
      "session": {
        "id": "session-456",
        "duration": 12345
      },
      "page": {
        "url": "https://app.example.com/dashboard",
        "title": "Dashboard"
      },
      "browser": {
        "userAgent": "Mozilla/5.0...",
        "language": "pt-BR",
        "platform": "Win32"
      }
    }
  ]
}
```

---

## Visualização e Análise

### Visualizar Logs em Tempo Real

```bash
# Todos os logs
tail -f logs/app/app.log

# Logs de API
tail -f logs/api/api.log

# Logs de segurança
tail -f logs/security/security.log

# Logs de erro
tail -f logs/errors/errors.log
```

### Filtrar Logs

```bash
# Logs de um usuário específico
grep "user-123" logs/app/app.log

# Logs de erro
grep "ERROR" logs/app/app.log

# Logs de um endpoint específico
grep "/api/v1/chat" logs/api/api.log
```

### Análise com jq (logs JSON)

```bash
# Contar erros por tipo
cat logs/errors/errors.log | jq -r '.error' | sort | uniq -c

# Requisições mais lentas
cat logs/api/api.log | jq 'select(.duration != null) | {duration, endpoint}' | sort -k1 -rn | head -10

# Usuários mais ativos
cat logs/audit/audit.log | jq -r '.user_id' | sort | uniq -c | sort -rn | head -10
```

### Rotação de Logs

Os logs são automaticamente rotacionados quando atingem 10MB. São mantidas até 10 versões antigas de cada arquivo.

Estrutura de arquivos rotacionados:
```
logs/app/
├── app.log          # Log atual
├── app.log.1        # Rotação mais recente
├── app.log.2
...
└── app.log.10       # Rotação mais antiga
```

---

## Boas Práticas

### ✅ Faça

- Use níveis de log apropriados (DEBUG para desenvolvimento, INFO para produção)
- Inclua contexto relevante nos logs
- Use logs estruturados (JSON) em produção
- Sanitize dados sensíveis (senhas, tokens, etc.)
- Monitore logs de segurança e auditoria regularmente
- Use `exc_info=True` ao logar exceções

### ❌ Não Faça

- Não logue dados sensíveis (senhas, tokens, cartões de crédito)
- Não use `print()` ao invés do sistema de logging
- Não logue em níveis inapropriados (ERROR para eventos normais)
- Não ignore exceções sem logar
- Não crie logs excessivos que impactem performance

---

## Troubleshooting

### Logs não estão sendo criados

1. Verifique se os diretórios de logs existem
2. Verifique permissões de escrita
3. Verifique se o logging foi inicializado corretamente

### Logs do frontend não chegam ao backend

1. Verifique se o endpoint `/api/v1/logs` está acessível
2. Verifique CORS no backend
3. Verifique console do browser para erros
4. Verifique se `enableRemote` está `true`

### Performance afetada por logs

1. Aumente o `minLevel` para WARNING ou ERROR
2. Desabilite logs de debug em produção
3. Aumente o `flushInterval` do frontend
4. Use logs assíncronos

---

## Exemplos Práticos

### Rastreando Jornada do Usuário

```typescript
// Login
log.userAction('login', { method: 'password' });

// Navegar para dashboard
log.pageView('Dashboard');

// Aplicar filtro
log.userAction('filter_applied', {
  type: 'date_range',
  from: '2024-01-01',
  to: '2024-01-31'
});

// Exportar dados
log.userAction('export_data', { format: 'excel', rows: 1500 });

// Logout
log.userAction('logout');
```

### Debugging de Performance

```python
import time
import structlog

logger = structlog.get_logger("agentbi")

async def slow_operation():
    start = time.time()

    logger.debug("starting_slow_operation")

    # operação lenta
    await do_something()

    duration = time.time() - start

    if duration > 1.0:
        logger.warning(
            "slow_operation_detected",
            duration=f"{duration:.3f}s",
            threshold="1.0s"
        )
    else:
        logger.debug(
            "operation_completed",
            duration=f"{duration:.3f}s"
        )
```

### Auditoria de Mudanças

```python
from app.core.logging_config import log_audit_event

async def update_user(user_id: str, updates: dict, current_user: User):
    # Busca usuário atual
    old_user = await get_user(user_id)

    # Atualiza
    new_user = await update_user_in_db(user_id, updates)

    # Registra auditoria
    log_audit_event(
        logger=audit_logger,
        action="user_updated",
        user_id=current_user.id,
        resource="user",
        resource_id=user_id,
        changes={
            "old": old_user.dict(),
            "new": new_user.dict()
        },
        ip_address=request.client.host
    )

    return new_user
```

---

## Configuração por Ambiente

### Development

```python
# Backend
setup_application_logging(environment="development")
```

```typescript
// Frontend
const logger = getLogger({
  minLevel: LogLevel.DEBUG,
  enableConsole: true,
  enableRemote: false,  // Desabilita envio remoto em dev
  includeStackTrace: true,
});
```

### Production

```python
# Backend
setup_application_logging(environment="production")
```

```typescript
// Frontend
const logger = getLogger({
  minLevel: LogLevel.WARN,  // Só warnings e erros
  enableConsole: false,     // Sem logs no console
  enableRemote: true,       // Envia para backend
  includeStackTrace: false, // Sem stack traces
  sanitizeData: true,       // Sanitiza dados sensíveis
});
```

---

## Conclusão

O sistema de logging está pronto para uso em desenvolvimento e produção, oferecendo:

- 📊 **Rastreabilidade completa** de todas as operações
- 🔒 **Segurança** com logs dedicados e sanitização
- 🚀 **Performance** com rotação automática e buffering
- 🔍 **Debugging** facilitado com níveis configuráveis
- 📈 **Análise** através de logs estruturados em JSON

Para dúvidas ou problemas, consulte a equipe de desenvolvimento.
