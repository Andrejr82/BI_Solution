# 🧹 GUIA DE LIMPEZA PRÉ-IMPLEMENTAÇÃO REACT

**Data:** 22/11/2025  
**Objetivo:** Preparar o projeto Agent_Solution_BI para implementação React  
**Tempo estimado:** 1-2 dias

---

## 🎯 POR QUE LIMPAR ANTES?

### Benefícios

✅ **Organização clara** - Separação entre Streamlit (dev) e React (produção)  
✅ **Menos conflitos** - Evita misturar dependências e configurações  
✅ **Performance** - Remove arquivos desnecessários  
✅ **Manutenibilidade** - Código mais fácil de entender  
✅ **Deploy otimizado** - Builds menores e mais rápidos

---

## 📋 CHECKLIST DE LIMPEZA

```markdown
### Fase 1: Backup e Análise
- [ ] Criar backup completo do projeto
- [ ] Documentar estado atual
- [ ] Listar arquivos a manter vs remover

### Fase 2: Reorganização de Estrutura
- [ ] Criar pasta `streamlit-dev/` (mover Streamlit)
- [ ] Criar pasta `frontend-react/` (novo React)
- [ ] Manter `core/` no root (compartilhado)
- [ ] Organizar `data/` e `reports/`

### Fase 3: Limpeza de Dependências
- [ ] Separar requirements (Streamlit vs Backend)
- [ ] Remover dependências não utilizadas
- [ ] Criar requirements.txt específicos

### Fase 4: Limpeza de Arquivos
- [ ] Remover arquivos temporários
- [ ] Limpar cache (.pyc, __pycache__)
- [ ] Organizar documentação
- [ ] Atualizar .gitignore

### Fase 5: Configuração
- [ ] Separar variáveis de ambiente
- [ ] Atualizar configurações
- [ ] Documentar nova estrutura
```

---

## 🗂️ ESTRUTURA PROPOSTA (PÓS-LIMPEZA)

### Estrutura Atual (Antes da Limpeza)

```
Agent_Solution_BI/
├── streamlit_app.py              ⚠️ Misturado no root
├── pages/                        ⚠️ Misturado no root
├── core/                         ✅ OK (compartilhado)
├── data/                         ✅ OK
├── frontend/ (React existente)   ⚠️ Nome genérico
├── api_server.py                 ✅ OK
├── requirements.txt              ⚠️ Tudo misturado
└── ...
```

### Estrutura Recomendada (Após Limpeza)

```
Agent_Solution_BI/
│
├── 📁 backend/                   # Backend Python (FastAPI)
│   ├── api_server.py
│   ├── requirements.txt          # Deps backend
│   └── config/
│
├── 📁 core/                      # Código compartilhado
│   ├── agents/
│   ├── connectivity/
│   ├── security/
│   ├── llm_adapter.py
│   └── ...                       # Mantém tudo que existe
│
├── 📁 streamlit-dev/             # Streamlit (dev/demos)
│   ├── app.py                    # streamlit_app.py renomeado
│   ├── pages/                    # 13 páginas Streamlit
│   ├── requirements.txt          # Deps Streamlit
│   └── README.md
│
├── 📁 frontend-react/            # React (PRODUÇÃO)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...                       # Estrutura Next.js
│
├── 📁 data/                      # Dados (compartilhado)
│   ├── parquet/
│   ├── query_history/
│   └── ...
│
├── 📁 docs/                      # Documentação
│   ├── GUIA_IMPLEMENTACAO_REACT_COMPLETO.md
│   ├── ANALISE_REACT_PRODUCAO.md
│   ├── README.md
│   └── ...
│
├── 📁 scripts/                   # Scripts utilitários
│   └── ...
│
├── 📄 .gitignore                 # Atualizado
├── 📄 README.md                  # Visão geral
├── 📄 docker-compose.yml         # Deploy completo
└── 📄 .env.example               # Template env vars
```

---

## 🚀 PASSO A PASSO DA LIMPEZA

### Passo 1: Criar Backup

```bash
# Navegar para pasta pai
cd c:\Users\André\Documents

# Criar backup compactado (com data no nome)
$BackupName = "Agent_Solution_BI_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Compress-Archive -Path "Agent_Solution_BI" -DestinationPath "$BackupName.zip"

# Verificar que backup foi criado
Test-Path "$BackupName.zip"
# Deve retornar True
```

**Importante:** Guardar este backup em local seguro (OneDrive, Google Drive, etc)

---

### Passo 2: Criar Nova Estrutura de Pastas

```bash
cd c:\Users\André\Documents\Agent_Solution_BI

# Criar novas pastas
New-Item -ItemType Directory -Path "streamlit-dev" -Force
New-Item -ItemType Directory -Path "backend" -Force
New-Item -ItemType Directory -Path "docs" -Force

# frontend-react será criado depois (via pnpm create next-app)
```

---

### Passo 3: Mover Arquivos Streamlit

```bash
# Mover app principal
Move-Item -Path "streamlit_app.py" -Destination "streamlit-dev/app.py" -Force

# Mover páginas
Move-Item -Path "pages" -Destination "streamlit-dev/pages" -Force

# Mover configuração Streamlit
Move-Item -Path ".streamlit" -Destination "streamlit-dev/.streamlit" -Force

# Criar README para Streamlit
@"
# Streamlit Dev Interface

Interface de desenvolvimento e demos do Agent Solution BI.

## Como executar

\`\`\`bash
cd streamlit-dev
pip install -r requirements.txt
streamlit run app.py
\`\`\`

## Uso

- **Desenvolvimento:** Protótipos rápidos e testes
- **Demos:** Apresentações internas
- **Debug:** Testes de funcionalidades do backend
"@ | Out-File -FilePath "streamlit-dev/README.md" -Encoding UTF8
```

---

### Passo 4: Organizar Backend

```bash
# Mover API server
Move-Item -Path "api_server.py" -Destination "backend/api_server.py" -Force

# Mover scripts de backend
Move-Item -Path "caculinha_backend.py" -Destination "backend/" -Force

# Criar README para backend
@"
# Backend API (FastAPI)

API REST do Agent Solution BI.

## Como executar

\`\`\`bash
cd backend
pip install -r requirements.txt
python api_server.py
\`\`\`

Acesse: http://localhost:5000/docs
"@ | Out-File -FilePath "backend/README.md" -Encoding UTF8
```

---

### Passo 5: Organizar Documentação

```bash
# Mover documentos técnicos para docs/
$DocsFiles = @(
    "ANALISE_REACT_PRODUCAO.md",
    "RELATORIO_CUSTO_MIGRACAO_DETALHADO.md",
    "GUIA_IMPLEMENTACAO_REACT_COMPLETO.md",
    "GUIA_LIMPEZA_PRE_IMPLEMENTACAO.md",
    "MIGRATION_PLAN.md",
    "MIGRATION_PLAN_PT.md",
    "ANALISE_PERFORMANCE_PROFUNDA.md",
    "CORRECOES_APLICADAS.md",
    "QUICK_WINS_IMPLEMENTADOS.md",
    "RESULTADO_FINAL_TESTES.md"
)

foreach ($file in $DocsFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs/" -Force
    }
}
```

---

### Passo 6: Separar Dependências

#### requirements.txt do Backend

```bash
# Criar backend/requirements.txt
@"
# Backend API - FastAPI
fastapi==0.116.1
uvicorn==0.35.0
pydantic==2.11.7
pydantic-settings==2.10.1

# Python Core
python-dotenv==1.1.1
python-decouple==3.8
python-jose[cryptography]==3.5.0
python-multipart==0.0.20
passlib[bcrypt]==1.7.4
cryptography==45.0.6

# Database
sqlalchemy==2.0.43
alembic==1.16.4
pyodbc==5.2.0

# Data Processing
pandas==2.2.2
polars==1.34.0
pyarrow==16.1.0
fastparquet==2024.11.0
dask[array,dataframe]==2024.5.1

# AI/LLM
langchain==0.3.27
langchain-core==0.3.74
langchain-community==0.3.27
langchain-openai==0.3.30
langgraph==0.6.4
openai==1.99.9

# Monitoring
sentry-sdk==2.35.0
structlog==25.5.0

# Utils
requests==2.32.4
tqdm==4.67.1
colorama==0.4.6
"@ | Out-File -FilePath "backend/requirements.txt" -Encoding UTF8
```

#### requirements.txt do Streamlit

```bash
# Criar streamlit-dev/requirements.txt
@"
# Streamlit Frontend
streamlit==1.48.0
plotly==6.3.0
altair==5.5.0

# Python Core (compartilhado com backend via core/)
python-dotenv==1.1.1

# O resto das dependências vem via importação do core/
# Instalar também: ../backend/requirements.txt
"@ | Out-File -FilePath "streamlit-dev/requirements.txt" -Encoding UTF8
```

---

### Passo 7: Limpar Arquivos Temporários

```bash
# Remover cache Python
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force

# Remover logs antigos (opcional - fazer backup antes se necessário)
# Remove-Item -Path "logs/*" -Recurse -Force

# Remover arquivos temporários do Streamlit
Remove-Item -Path ".streamlit/cache" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Passo 8: Atualizar .gitignore

```bash
# Criar/atualizar .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv_new/
ENV/

# Streamlit
.streamlit/secrets.toml
.streamlit/cache/

# Next.js / React
frontend-react/.next/
frontend-react/out/
frontend-react/build/
frontend-react/node_modules/
frontend-react/.env*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Environment
.env
.env.local
secrets.toml

# Backups
backups/
*.backup
*.bak

# Data (se não quiser versionar)
# data/parquet/*.parquet
# reports/*.html

# Dependências
node_modules/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
```

---

### Passo 9: Criar docker-compose.yml (Opcional)

```bash
# Criar docker-compose.yml para deploy completo
@"
version: '3.8'

services:
  # Backend FastAPI
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
      - DATABASE_URL=\${DATABASE_URL}
    volumes:
      - ./core:/app/core
      - ./data:/app/data
    restart: unless-stopped

  # Frontend React (produção)
  frontend:
    build: ./frontend-react
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:5000
    depends_on:
      - backend
    restart: unless-stopped

  # Streamlit (dev) - Opcional, só para desenvolvimento
  streamlit:
    build: ./streamlit-dev
    ports:
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
    volumes:
      - ./core:/app/core
      - ./data:/app/data
    profiles:
      - dev
    restart: unless-stopped
"@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
```

---

### Passo 10: Atualizar README.md Principal

```bash
# Criar README.md atualizado
@"
# 🤖 Agent Solution BI - Multi-Interface

Sistema de Business Intelligence com IA - Arquitetura Multi-Interface

## 📁 Estrutura do Projeto

\`\`\`
Agent_Solution_BI/
├── backend/           # API FastAPI
├── frontend-react/    # Interface de Produção (React/Next.js)
├── streamlit-dev/     # Interface de Desenvolvimento (Streamlit)
├── core/              # Código compartilhado (IA, conectividade)
├── data/              # Dados (Parquet)
└── docs/              # Documentação
\`\`\`

## 🚀 Quick Start

### Opção 1: Produção (React + FastAPI)

\`\`\`bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python api_server.py

# Terminal 2: Frontend React
cd frontend-react
pnpm install
pnpm dev

# Acesse: http://localhost:3000
\`\`\`

### Opção 2: Desenvolvimento (Streamlit)

\`\`\`bash
cd streamlit-dev
pip install -r requirements.txt
streamlit run app.py

# Acesse: http://localhost:8501
\`\`\`

### Opção 3: Docker (Tudo junto)

\`\`\`bash
docker-compose up
# Produção: http://localhost:3000
# Backend API: http://localhost:5000/docs
\`\`\`

## 📚 Documentação

- **Implementação React:** \`docs/GUIA_IMPLEMENTACAO_REACT_COMPLETO.md\`
- **Análise de Custos:** \`docs/ANALISE_REACT_PRODUCAO.md\`
- **Arquitetura:** \`docs/ARQUITETURA_MULTI_INTERFACE.md\`

## 🔧 Configuração

Criar \`.env\` no root:

\`\`\`env
GEMINI_API_KEY=sua_chave
DATABASE_URL=sua_url
\`\`\`

## 🤝 Contribuindo

Ver \`docs/CONTRIBUTING.md\`

---

**Made with ❤️ by Agent Solution BI Team**
"@ | Out-File -FilePath "README.md" -Encoding UTF8 -Force
```

---

## ✅ VALIDAÇÃO PÓS-LIMPEZA

### Checklist de Verificação

```bash
# 1. Estrutura de pastas
Test-Path "backend" -PathType Container
Test-Path "streamlit-dev" -PathType Container
Test-Path "core" -PathType Container
Test-Path "data" -PathType Container
Test-Path "docs" -PathType Container

# 2. Arquivos-chave
Test-Path "backend/api_server.py"
Test-Path "streamlit-dev/app.py"
Test-Path "backend/requirements.txt"
Test-Path "streamlit-dev/requirements.txt"
Test-Path ".gitignore"
Test-Path "README.md"

# 3. Backend funciona?
cd backend
pip install -r requirements.txt
python api_server.py  # Deve iniciar sem erros

# 4. Streamlit funciona?
cd ../streamlit-dev
pip install -r requirements.txt
streamlit run app.py  # Deve abrir navegador

# Tudo OK? Pronto para implementar React!
```

---

## 🎯 PRÓXIMOS PASSOS

Após a limpeza estar completa:

1. ✅ Confirmar que backend e Streamlit funcionam
2. ✅ Commit das mudanças no Git
3. ✅ Criar branch para desenvolvimento React
4. 🚀 Seguir **GUIA_IMPLEMENTACAO_REACT_COMPLETO.md**

```bash
# Commit da limpeza
git add .
git commit -m "refactor: reorganização de estrutura - separação backend/frontend"

# Criar branch para React
git checkout -b feature/react-production-frontend

# Agora sim, implementar React!
cd ../  # Voltar para root
# Seguir Passo 1.1 do GUIA_IMPLEMENTACAO_REACT_COMPLETO.md
```

---

## ⚠️ AVISOS IMPORTANTES

### NÃO Remover

- ❌ Pasta `core/` (compartilhada por todos os frontends)
- ❌ Pasta `data/` (dados em Parquet)
- ❌ Configurações de ambiente (`.env`, mas criar `.env.example`)
- ❌ Histórico Git (`.git/`)

### Fazer Backup Antes

- 💾 Banco de dados (se houver)
- 💾 Arquivos de configuração personalizados  
- 💾 Logs importantes
- 💾 Chaves de API (mover para .env)

### Testar Após Limpeza

- ✅ Backend FastAPI inicia sem erros
- ✅ Streamlit funciona normalmente
- ✅ Dados Parquet acessíveis
- ✅ LLM (Gemini) conecta

---

## 📞 Problemas?

Se algo não funcionar após a limpeza:

1. **Restaurar backup**
   ```bash
   cd c:\Users\André\Documents
   Expand-Archive -Path "Agent_Solution_BI_backup_*.zip" -DestinationPath "Agent_Solution_BI_RESTORED"
   ```

2. **Comparar estruturas**
   ```bash
   # Ver diferenças entre backup e versão limpa
   ```

3. **Refazer passo a passo**
   - Seguir este guia novamente com atenção

---

## 🎉 RESULTADO ESPERADO

Ao final da limpeza você terá:

✅ Projeto organizado e modular  
✅ Separação clara: Backend / Streamlit-dev / React (a criar)  
✅ Dependências separadas e otimizadas  
✅ Documentação centralizada  
✅ Pronto para implementação React profissional  
✅ Manutenção facilitada  
✅ Deploy simplificado (Docker)  

---

**Tempo Total Estimado:** 2-4 horas (com cuidado e validação)

**Última Atualização:** 22/11/2025  
**Versão:** 1.0.0
