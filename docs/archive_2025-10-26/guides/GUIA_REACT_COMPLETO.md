# 🚀 Guia Completo - Agent BI React Frontend

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação](#instalação)
4. [Inicialização Rápida](#inicialização-rápida)
5. [Estrutura do Projeto](#estrutura-do-projeto)
6. [Funcionalidades](#funcionalidades)
7. [Solução de Problemas](#solução-de-problemas)
8. [API Endpoints](#api-endpoints)

---

## 🎯 Visão Geral

O **Agent BI** é um sistema de Business Intelligence com:

- **Frontend**: React + TypeScript + Vite + Shadcn/UI + TailwindCSS
- **Backend**: FastAPI (Python)
- **Banco de Dados**: PostgreSQL + Parquet
- **IA**: LangGraph Agents + RAG System

---

## ⚙️ Pré-requisitos

Certifique-se de ter instalado:

- ✅ **Python 3.9+**
- ✅ **Node.js 18+**
- ✅ **PostgreSQL** (se usar banco de dados)
- ✅ **Git**

---

## 📦 Instalação

### 1. Backend (Python)

```bash
# Instalar dependências Python
pip install -r requirements.txt
```

### 2. Frontend (React)

```bash
# Navegar para pasta frontend
cd frontend

# Instalar dependências
npm install
```

---

## 🚀 Inicialização Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
# Windows
start_react_system_fixed.bat

# Linux/Mac
chmod +x start_react_system_fixed.sh
./start_react_system_fixed.sh
```

### Opção 2: Manual

**Terminal 1 - Backend:**
```bash
python -m uvicorn api_server:app --host 0.0.0.0 --port 5000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 🌐 Acessar o Sistema

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs

### 🔐 Credenciais Padrão

- **Usuário**: `admin`
- **Senha**: `admin123`

---

## 📁 Estrutura do Projeto

```
Agent_Solution_BI/
├── frontend/                    # Frontend React
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   │   ├── ui/            # Componentes Shadcn/UI
│   │   │   ├── AppSidebar.tsx # Sidebar principal
│   │   │   ├── Header.tsx     # Header com menu
│   │   │   └── ...
│   │   ├── contexts/          # Contexts (Auth, etc)
│   │   ├── lib/               # Utilitários
│   │   │   └── api.ts        # Service API centralizado ⭐
│   │   ├── pages/             # Páginas/Rotas
│   │   │   ├── Login.tsx
│   │   │   ├── Index.tsx      # Dashboard principal
│   │   │   ├── Metricas.tsx
│   │   │   └── ...
│   │   ├── App.tsx            # App principal
│   │   └── main.tsx           # Entry point
│   ├── public/                # Assets estáticos
│   ├── package.json
│   ├── vite.config.ts         # Config Vite
│   └── tsconfig.json
├── api_server.py              # Backend FastAPI ⭐
├── core/                      # Core do sistema
│   ├── agents/               # LangGraph agents
│   ├── connectivity/         # Adapters DB
│   ├── factory/             # Component Factory
│   └── ...
├── data/                     # Dados (Parquet, exemplos)
└── requirements.txt
```

---

## 🎨 Funcionalidades

### 1. Dashboard Principal (/)
- Chat interativo com IA
- Geração automática de SQL
- Visualização de dados
- Gráficos dinâmicos

### 2. Métricas (/metricas)
- KPIs do sistema
- Performance
- Estatísticas de uso

### 3. Gráficos Salvos (/graficos-salvos)
- Biblioteca de visualizações
- Reutilização de análises

### 4. Monitoramento (/monitoramento)
- Status do sistema
- Health checks
- Logs

### 5. Exemplos (/exemplos)
- Queries de exemplo
- Templates prontos
- Guias de uso

### 6. Admin (/admin)
- Gerenciamento de usuários
- Configurações
- Permissões

---

## 🔧 Solução de Problemas

### ❌ Erro: "Cannot GET /api/..."

**Causa**: Backend não está rodando

**Solução**:
```bash
python -m uvicorn api_server:app --host 0.0.0.0 --port 5000 --reload
```

---

### ❌ Erro: "EADDRINUSE: porta 8080 já em uso"

**Solução Windows**:
```bash
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Solução Linux/Mac**:
```bash
lsof -ti:8080 | xargs kill -9
```

---

### ❌ Erro: "Module not found" no React

**Solução**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### ❌ Build falha com erros TypeScript

**Solução**:
```bash
cd frontend
npm run build -- --mode development
```

---

### ❌ Proxy não funciona (404 na API)

**Verificar**:
1. Backend rodando na porta 5000?
2. Vite config proxy correto? (`vite.config.ts`)
3. Endpoint começa com `/api`?

---

### ❌ Assets não carregam (logo, imagens)

**Solução**:
1. Verificar se arquivos estão em `frontend/public/`
2. Importar corretamente:
```typescript
// ✅ Correto
import logo from '@/assets/logo.png'

// ❌ Incorreto
<img src="/logo.png" />
```

---

## 📡 API Endpoints

### Autenticação

**POST** `/api/login`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "success": true,
  "token": "...",
  "user": {
    "username": "admin",
    "role": "admin",
    "permissions": ["read", "write", "admin"]
  }
}
```

---

### Chat

**POST** `/api/chat`
```json
{
  "message": "Mostre vendas por UNE",
  "session_id": "user_123"
}
```

**Response**:
```json
{
  "success": true,
  "response": {
    "sql_generated": "SELECT ...",
    "results": [...],
    "viz_code": "..."
  },
  "timestamp": "2025-10-25T..."
}
```

---

### Métricas

**GET** `/api/metrics`

**Response**:
```json
{
  "success": true,
  "metrics": {
    "total_queries": 150,
    "successful_queries": 145,
    "failed_queries": 5,
    "avg_response_time": 1.2
  }
}
```

---

### Health Check

**GET** `/api/health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "backend": {
    "database_connected": true,
    "agents_initialized": true,
    "rag_available": true
  }
}
```

---

## 🎯 Uso do Service API

No frontend, use o service centralizado:

```typescript
import { api } from '@/lib/api';

// Login
const response = await api.login('admin', 'admin123');

// Chat
const chat = await api.sendMessage('Mostre vendas por UNE');

// Métricas
const metrics = await api.getMetrics();

// Health
const health = await api.health();
```

---

## 🛠️ Scripts Disponíveis

### Frontend

```bash
cd frontend

# Desenvolvimento
npm run dev

# Build produção
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

### Backend

```bash
# Desenvolvimento
python -m uvicorn api_server:app --reload

# Produção
python -m uvicorn api_server:app --host 0.0.0.0 --port 5000
```

---

## 📊 Performance

- ⚡ **Build**: ~6-8 segundos
- ⚡ **Hot Reload**: <100ms
- ⚡ **Bundle Size**: ~500KB (gzipped)
- ⚡ **First Load**: <2 segundos

---

## 🔒 Segurança

- ✅ JWT tokens
- ✅ CORS configurado
- ✅ Input validation (Pydantic)
- ✅ SQL injection protection
- ✅ XSS protection (React)

---

## 📝 Notas Importantes

1. **Sempre inicie o backend ANTES do frontend**
2. **Use o service API centralizado** (`@/lib/api`)
3. **Verifique as portas** (5000 e 8080)
4. **Assets devem estar em** `frontend/public/` ou importados
5. **Proxy Vite só funciona em desenvolvimento**

---

## 🤝 Suporte

Problemas? Verifique:

1. ✅ Backend rodando?
2. ✅ Frontend rodando?
3. ✅ Portas corretas?
4. ✅ Dependências instaladas?
5. ✅ .env configurado?

---

## 📈 Próximos Passos

- [ ] Implementar testes E2E
- [ ] Deploy em produção
- [ ] CI/CD pipeline
- [ ] Documentação API completa
- [ ] Monitoramento avançado

---

**Desenvolvido com ❤️ pela equipe Lojas Caçula**
