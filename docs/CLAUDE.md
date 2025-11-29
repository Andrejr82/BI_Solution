# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral do Projeto

Agent Solution BI é uma aplicação full-stack de Business Intelligence conversacional com tecnologia Gemini. O sistema usa uma arquitetura híbrida de dados (SQL Server + Parquet) com sistema de agentes LangGraph para processamento de consultas em linguagem natural.

**Stack Principal:**
- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+ + Uvicorn
- **LLM**: Google Gemini 2.5 Flash (via langchain-openai)
- **Dados**: SQL Server (autenticação/metadados) + Parquet (dados analíticos)
- **Agentes**: LangGraph + LangChain para processamento de queries
- **Cache**: Redis (em Docker)

## Comandos Essenciais

### Iniciar Sistema Completo
```bash
# Windows (recomendado)
python run.py

# Apenas backend
python run.py --backend-only

# Apenas frontend
python run.py --frontend-only

# Modo desenvolvimento (logs verbosos)
python run.py --dev
```

### Backend (FastAPI)
```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Rodar backend diretamente
python main.py

# Rodar com uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)
```bash
cd frontend-react

# Instalar dependências (preferencialmente com pnpm)
pnpm install
# ou: npm install

# Dev server
pnpm dev
# ou: npm run dev

# Build de produção
pnpm build

# Rodar testes
pnpm test
pnpm test:watch
pnpm test:coverage
```

### Docker
```bash
# Iniciar stack completa
docker-compose up -d

# Ver logs
docker-compose logs -f

# Rebuild sem cache
docker-compose build --no-cache

# Parar e remover containers
docker-compose down
```

### Utilitários
```bash
# Diagnóstico completo do sistema
python diagnose_system.py

# Limpar porta específica
python kill_port.py 8000
python kill_port.py 3000

# Testar login via API
python test_login.py
```

## Arquitetura

### Estrutura de Dados Híbrida

O sistema usa uma arquitetura **híbrida** crítica para entender:

1. **SQL Server** (`backend/app/config/settings.py`):
   - Usado para autenticação de usuários e metadados
   - Configurado via `DATABASE_URL` e `USE_SQL_SERVER=true`
   - **Importante**: Pode ser desabilitado sem quebrar o sistema (fallback automático)

2. **Parquet** (`data/parquet/`):
   - Fonte PRIMÁRIA para dados analíticos (`admmat.parquet`)
   - Fallback para autenticação (`users.parquet`)
   - Sempre disponível, sem dependências externas

3. **HybridDataAdapter** (`backend/app/infrastructure/data/hybrid_adapter.py`):
   - Gerencia fallback automático SQL Server → Parquet
   - FORÇADO a usar Parquet para queries de dados (linha 82)
   - Timeout configurável via `SQL_SERVER_TIMEOUT`

### Sistema de Agentes (LangGraph)

**Localização**: `backend/app/core/`

O sistema usa LangGraph para processamento de queries com múltiplos agentes especializados:

```
Query do Usuário
    ↓
Supervisor (supervisor_agent.py)
    ↓ (decide rota)
    ├─→ Direct Response (respostas simples)
    ├─→ Clarification (perguntas ambíguas)
    └─→ Caculinha BI Agent (queries complexas)
        ↓
        ├─→ BI Tools (execute_sql_query, generate_chart, etc.)
        └─→ Chart Tools (render_plotly_figure)
            ↓
        Response Final
```

**Arquivos Chave:**
- `backend/app/core/graph/graph_builder.py` - Define o grafo de execução
- `backend/app/core/agents/supervisor_agent.py` - Roteador principal
- `backend/app/core/agents/caculinha_bi_agent.py` - Agente de BI principal
- `backend/app/core/agent_state.py` - Estado compartilhado entre agentes

### Backend API Structure

**Rotas principais** (`backend/app/api/v1/endpoints/`):
- `/api/v1/auth/login` - Autenticação JWT
- `/api/v1/chat` - Interface de chat com BI agent (CRÍTICO)
- `/api/v1/analytics` - Endpoints de análises
- `/api/v1/reports` - CRUD de relatórios
- `/api/v1/metrics` - Métricas do dashboard
- `/api/v1/admin` - Administração de usuários

**Autenticação**:
- JWT com refresh tokens (`backend/app/config/security.py`)
- Middleware de autenticação em `backend/app/api/dependencies.py`
- Credenciais padrão: `admin` / `Admin@2024` (ver `CREDENTIALS.md`)

### Frontend Structure

**Arquitetura**: Next.js App Router com autenticação de rotas

- `frontend-react/src/app/(authenticated)/` - Rotas protegidas
  - `dashboard/` - Dashboard principal
  - `chat/` - Interface de chat com agente
  - `analytics/` - Análises customizadas
  - `reports/` - Gerenciamento de relatórios
  - `admin/` - Painel administrativo

- `frontend-react/src/components/` - Componentes reutilizáveis
  - `ui/` - Shadcn/ui components
  - `chat/` - Componentes de chat
  - `permissions/` - Sistema RBAC (RoleBasedRender, PermissionGate)

- `frontend-react/src/services/` - Camada de API
  - `auth.service.ts` - Autenticação e gestão de tokens
  - Estado global com Zustand

- `frontend-react/src/lib/api/client.ts` - Cliente Axios configurado

## Variáveis de Ambiente Críticas

### Backend (.env ou docker-compose.yml)
```env
# Database (Híbrido)
DATABASE_URL=mssql+aioodbc://user:pass@host:1433/db?driver=ODBC+Driver+17+for+SQL+Server
USE_SQL_SERVER=false  # Desabilitado por padrão para evitar timeouts
FALLBACK_TO_PARQUET=true
SQL_SERVER_TIMEOUT=2

# Gemini API
GEMINI_API_KEY=your-key-here  # OBRIGATÓRIO para agente funcionar

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (apenas Docker)
REDIS_URL=redis://localhost:6379/0
```

### Frontend (auto-configurado via run.py)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Problemas Comuns e Soluções

### Backend não inicia
1. Verifique se `DATABASE_URL` no ambiente do sistema está vazia:
   ```powershell
   $env:DATABASE_URL = ""
   ```
2. Execute: `python backend/main.py` e observe os logs
3. Se erro de Gemini API: Configure `GEMINI_API_KEY` no `.env`

### Frontend não conecta ao Backend
- Certifique-se que backend está rodando na porta 8000
- Verifique CORS em `backend/main.py` (linha 89-95)
- Frontend usa `http://127.0.0.1:8000` (não `localhost`)

### Erro de autenticação "Invalid credentials"
- Senha é case-sensitive: `Admin@2024` (não `admin123`)
- Verificar se `data/parquet/users.parquet` existe
- Rodar `python backend/scripts/create_parquet_users.py` se necessário

### Sistema de agentes não responde
1. Verificar `GEMINI_API_KEY` está configurada
2. Fallback automático para queries Parquet diretas está em `backend/app/api/v1/endpoints/chat.py` (linha 65+)
3. Logs do agente estão em nível INFO - verificar console

### Docker: Backend reiniciando constantemente
- SQL Server não acessível do container? Use `host.docker.internal` no Windows
- Ou desabilite SQL Server: `USE_SQL_SERVER=false` em `.env.docker`
- Verifique logs: `docker-compose logs backend`

## Desenvolvimento

### Adicionar nova rota de API
1. Criar endpoint em `backend/app/api/v1/endpoints/`
2. Importar e incluir router em `backend/app/api/v1/router.py`
3. Proteger com `Depends(get_current_active_user)` se necessário

### Adicionar nova ferramenta para o Agente
1. Criar função em `backend/app/core/tools/`
2. Decorar com `@tool` do LangChain
3. Adicionar à lista `bi_tools` em `backend/app/core/agents/caculinha_bi_agent.py`
4. Atualizar prompt do agente se necessário

### Adicionar nova página no Frontend
1. Criar em `frontend-react/src/app/(authenticated)/nova-pagina/page.tsx`
2. Adicionar link no Sidebar: `frontend-react/src/components/layout/Sidebar.tsx`
3. Usar `ProtectedRoute` se precisar permissões específicas

### Modificar schema de dados Parquet
1. Schema atual em: `backend/parquet_schema.txt`
2. Regenerar: `python backend/scripts/inspect_parquet.py`
3. Atualizar ferramentas do agente que usam colunas específicas

## Testes

### Backend
```bash
cd backend
pytest
pytest --cov  # com coverage
```

### Frontend
```bash
cd frontend-react
pnpm test
pnpm test:watch
pnpm test:coverage
```

## Migrações de Banco (Alembic)

```bash
cd backend

# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

**Nota**: Em desenvolvimento, tabelas são auto-criadas se `DEBUG=true` (via `backend/main.py` linha 44-48).

## Deployment

### Produção com Docker
1. Configurar `.env.docker` com valores de produção
2. Setar `ENVIRONMENT=production`
3. Gerar `SECRET_KEY` forte: `openssl rand -hex 32`
4. `docker-compose up -d`

### Build Frontend para produção
```bash
cd frontend-react
pnpm build
pnpm start  # Servidor Next.js otimizado
```

## Notas Importantes

- **Sempre interaja em Português PT-BR** conforme instruções do usuário
- O sistema foi migrado de Streamlit para React - não há mais interface Streamlit
- `run.py` é o launcher unificado - NÃO usar `RUN.bat` diretamente
- Parquet é SEMPRE a fonte de dados para queries analíticas (forçado em `hybrid_adapter.py`)
- O sistema de agentes tem fallback automático para queries diretas se LangGraph falhar
- Credenciais estão documentadas em `CREDENTIALS.md` e `DOCKER_README.md`
- Docker usa `host.docker.internal` para acessar SQL Server no host Windows
