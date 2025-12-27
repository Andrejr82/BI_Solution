# Guia de Migração - Agent BI Solution

## 📋 Resumo das Mudanças

O sistema de inicialização foi modernizado de scripts Python customizados (707 linhas) para ferramentas padrão da indústria com npm scripts e Taskfile.yml (~50 linhas).

### Antes ❌
```bash
python run.py              # 707 linhas de código custom
run.bat                    # Script batch específico Windows
```

### Agora ✅
```bash
npm run dev                # Inicia tudo (backend + frontend)
npm run dev:backend        # Apenas backend
npm run dev:frontend       # Apenas frontend
```

---

## 🎯 Principais Melhorias

### 1. **Arquivo .env Criado**
- ✅ SECRET_KEY segura gerada automaticamente
- ✅ DATABASE_URL vazio para evitar timeout (usa Parquet)
- ✅ Configurações prontas para desenvolvimento

### 2. **Endpoint /health com Timeout**
- ✅ `/api/v1/health` - Health check completo
- ✅ `/api/v1/health/live` - Liveness probe
- ✅ `/api/v1/health/ready` - Readiness probe
- ✅ Timeout de 5 segundos configurável
- ✅ Cache de 30 segundos para performance

### 3. **package.json na Raiz**
- ✅ Scripts npm padronizados
- ✅ Dependências de desenvolvimento (concurrently, kill-port)
- ✅ Validação de .env
- ✅ Limpeza automática de portas

### 4. **Taskfile.yml (Opcional)**
- ✅ Task runner moderno (alternativa ao run.py)
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ YAML declarativo
- ✅ Tasks paralelas e dependentes

### 5. **Script clean-ports.js Melhorado**
- ✅ Cross-platform (Windows/Linux/macOS)
- ✅ Detecta OS automaticamente
- ✅ Mata processos nas portas 8000 e 3000

### 6. **Correções Críticas**
- ✅ Supabase client com lazy loading
- ✅ Dependências faltantes instaladas:
  - `supabase` (2.25.1)
  - `google-generativeai` (0.8.5)
  - `langchain-google-genai` (4.0.0)
  - `aioodbc` (0.5.0)
- ✅ PyTorch removido (DLL problems no Windows)

---

## 🚀 Como Usar

### Primeira Vez (Setup)

```bash
# 1. Instalar dependências
npm install

# 2. Validar .env
npm run validate:env

# 3. Instalar dependências do backend (se necessário)
npm run install:backend

# 4. Instalar dependências do frontend (se necessário)
npm run install:frontend
```

### Desenvolvimento Diário

```bash
# Iniciar tudo (recomendado)
npm run dev

# OU iniciar serviços individualmente:
npm run dev:backend    # Apenas backend (porta 8000)
npm run dev:frontend   # Apenas frontend (porta 3000)
```

### Outros Comandos Úteis

```bash
# Limpar portas 8000 e 3000
npm run clean:ports

# Validar arquivo .env
npm run validate:env

# Testes do backend
npm run test:backend

# Lint do backend
npm run lint:backend

# Format do backend
npm run format:backend
```

---

## 📦 Scripts npm Disponíveis

| Script | Descrição |
|--------|-----------|
| `npm run dev` | Inicia backend + frontend com logs coloridos |
| `npm run dev:backend` | Inicia apenas FastAPI backend |
| `npm run dev:frontend` | Inicia apenas SolidJS frontend |
| `npm run clean:ports` | Mata processos nas portas 8000 e 3000 |
| `npm run install` | Instala todas as dependências |
| `npm run install:backend` | Instala dependências Python |
| `npm run install:frontend` | Instala dependências Node.js |
| `npm run validate:env` | Valida se .env existe |
| `npm run test:backend` | Executa testes do backend |
| `npm run lint:backend` | Lint do código Python |
| `npm run format:backend` | Formata código Python |

---

## 🔧 Taskfile (Opcional - Requer Instalação)

Se preferir usar Taskfile em vez de npm:

### Instalar Taskfile

**Windows (Scoop):**
```bash
scoop install task
```

**Windows (Go):**
```bash
go install github.com/go-task/task/v3/cmd/task@latest
```

**Linux/macOS:**
```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

### Usando Taskfile

```bash
# Listar todas as tasks
task --list

# Iniciar dev
task dev

# Apenas backend
task dev:backend

# Apenas frontend
task dev:frontend

# Limpar portas
task clean:ports

# Health check
task health
```

---

## 🏥 Endpoints de Saúde

### `/health` (Root - sem autenticação)
```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### `/api/v1/health` (Completo com checks)
```bash
curl http://localhost:8000/api/v1/health
```

Resposta:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-12-13T15:22:51.218911",
  "checks": {
    "database": {
      "status": "disabled",
      "message": "SQL Server disabled, using Parquet fallback"
    },
    "data_adapter": {
      "status": "healthy",
      "source": "parquet",
      "message": "Parquet file accessible: admmat.parquet"
    },
    "environment": {
      "status": "healthy",
      "message": "Environment configured"
    }
  }
}
```

### `/api/v1/health/live` (Liveness probe)
```bash
curl http://localhost:8000/api/v1/health/live
```

### `/api/v1/health/ready` (Readiness probe)
```bash
curl http://localhost:8000/api/v1/health/ready
```

---

## ⚙️ Variáveis de Ambiente (.env)

O arquivo `backend/.env` foi criado automaticamente com:

### Críticas (ALTERE ANTES DE USAR)
```bash
GEMINI_API_KEY="sua_chave_api_gemini_aqui"  # ⚠️ Configure sua chave
```

### Já Configuradas ✅
```bash
SECRET_KEY="..."  # Gerada automaticamente (64 caracteres)
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=  # Vazio = usa apenas Parquet (evita timeout)
USE_SQL_SERVER=false
FALLBACK_TO_PARQUET=true
```

### Opcionais
```bash
SUPABASE_URL=""
SUPABASE_ANON_KEY=""
USE_SUPABASE_AUTH=false
```

---

## 🐛 Troubleshooting

### Backend não inicia

**Problema:** Port 8000 ocupada
```bash
npm run clean:ports
```

**Problema:** Módulo não encontrado
```bash
cd backend
.venv\Scripts\pip.exe install <módulo>
```

**Problema:** .env não existe
```bash
npm run validate:env
# Se falhar, copie manualmente:
copy backend\.env.example backend\.env
```

### Frontend não inicia

**Problema:** Port 3000 ocupada
```bash
npm run clean:ports
```

**Problema:** node_modules não existe
```bash
npm run install:frontend
```

### Logs e Debug

**Ver logs do backend:**
```bash
npm run dev:backend
# Logs aparecem com prefixo [backend]
```

**Ver logs do frontend:**
```bash
npm run dev:frontend
# Logs aparecem com prefixo [frontend]
```

**Ver logs de ambos (recomendado):**
```bash
npm run dev
# Logs coloridos: backend (azul), frontend (verde)
```

---

## 📊 Comparativo: Antes vs Depois

| Aspecto | Antes (run.py) | Depois (npm scripts) |
|---------|----------------|----------------------|
| **Linhas de código** | 707 linhas Python | ~50 linhas YAML/JSON |
| **Dependências** | Script custom | Ferramentas padrão |
| **Venv management** | Manual (197 linhas) | Automático (.venv) |
| **Process management** | subprocess.Popen | concurrently |
| **Limpeza de portas** | Script Node.js custom | kill-port (npm package) |
| **Logs** | Threading manual | concurrently built-in |
| **Inicialização** | `python run.py` | `npm run dev` |
| **Cross-platform** | Código condicional | Nativo |
| **Manutenibilidade** | Baixa | Alta |
| **DX (Developer Experience)** | Complexo | Simples |

---

## 🎓 Próximos Passos Recomendados

### 1. Configure sua API Key do Gemini
Edite `backend/.env` e adicione sua chave:
```bash
GEMINI_API_KEY="sua_chave_real_aqui"
```

Obtenha em: https://makersuite.google.com/app/apikey

### 2. (Opcional) Instale Taskfile
Para uma experiência ainda melhor:
```bash
scoop install task  # Windows
```

### 3. (Opcional) Migre para Poetry
Poetry oferece melhor gerenciamento de dependências:
```bash
# Instalar Poetry
pip install poetry

# Usar Poetry
cd backend
poetry install
poetry run uvicorn main:app --reload
```

### 4. Configure CI/CD
Use os novos scripts npm para integração contínua:
```yaml
# .github/workflows/ci.yml
- run: npm install
- run: npm run validate:env
- run: npm run test:backend
```

---

## 📝 Notas Importantes

### Scripts Antigos (Deprecados)
Os seguintes arquivos ainda existem mas **NÃO devem ser usados**:

- ❌ `run.py` - Use `npm run dev` em vez disso
- ❌ `run.bat` - Use `npm run dev` em vez disso

**Por quê deprecar?**
- Complexidade desnecessária (707 linhas)
- Difícil manutenção
- Não usa ferramentas padrão
- Código Windows-specific

### Dependências Removidas
- ❌ `torch` - Removido devido a problemas de DLL no Windows
  - Se precisar de PyTorch, instale manualmente após resolver dependências de C++ runtime

### Compatibilidade
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS (Big Sur+)
- ✅ Python 3.11+
- ✅ Node.js 18+

---

## 📞 Suporte

### Documentação
- FastAPI: https://fastapi.tiangolo.com
- SolidJS: https://solidjs.com
- Concurrently: https://www.npmjs.com/package/concurrently
- Taskfile: https://taskfile.dev

### Problemas Conhecidos
1. **PyTorch DLL Error no Windows**
   - Solução: PyTorch foi removido. Se necessário, instale Visual C++ Redistributable

2. **Timeout no SQL Server**
   - Solução: `DATABASE_URL=""` no .env (usa Parquet)

3. **Supabase não configurado**
   - Solução: `USE_SUPABASE_AUTH=false` no .env

---

## ✅ Checklist de Validação

Antes de começar a desenvolver, verifique:

- [ ] `.env` existe em `backend/`
- [ ] `GEMINI_API_KEY` configurada no `.env`
- [ ] `npm install` executado sem erros
- [ ] `npm run validate:env` retorna ✓
- [ ] `npm run dev:backend` inicia sem erros
- [ ] `curl http://localhost:8000/health` retorna JSON
- [ ] Frontend `node_modules` instalado

---

**Última atualização:** 2025-12-13
**Versão do sistema:** 1.0.0
