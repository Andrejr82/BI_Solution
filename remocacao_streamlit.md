💰 Análise de Custo - Remoção do Streamlit
Data: 23/11/2025
Objetivo: Limpar projeto removendo Streamlit e dependências

📊 Situação Atual
Dependências do Streamlit
Analisando 
requirements.txt
, o Streamlit traz 20 dependências exclusivas:

streamlit==1.48.0
├── altair (visualizações)
├── blinker (sinais)
├── cachetools (cache)
├── gitpython (git integration)
├── numpy (já usado por outros)
├── pandas (já usado por outros)
├── pillow (já usado por outros)
├── protobuf (protocol buffers)
├── pydeck (mapas 3D)
├── tenacity (retry logic - já usado)
├── toml (config)
├── tornado (web server)
└── watchdog (file watching)
Dependências que PODEM ser removidas:
streamlit - 50MB
altair - 5MB (visualizações - não usado no React)
pydeck - 10MB (mapas 3D - não usado)
tornado - 5MB (web server - não necessário)
watchdog - 2MB (file watching - não necessário)
gitpython - 8MB (git - não necessário)
protobuf - 5MB (se não usado por outros)
toml - 1MB (se não usado por outros)
Total Economizado: ~150MB de dependências

🗂️ Arquivos a Remover
1. Arquivos Streamlit (3 arquivos)
streamlit_app.py                    # 81KB - App principal
core/config/streamlit_settings.py   # Config Streamlit
core/utils/streamlit_stability.py   # Utils Streamlit
2. Diretórios Streamlit
.streamlit/                         # Config folder
pages/                              # Páginas Streamlit (se existir)
ui/                                 # UI components Streamlit (se existir)
3. Arquivos de Configuração
.streamlit/config.toml              # Config Streamlit
.streamlit/secrets.toml             # Secrets (migrar para .env)
💸 Custo de Remoção
Tempo Estimado
Tarefa	Tempo
Remover arquivos Streamlit	30 min
Limpar requirements.txt	1 hora
Testar dependências restantes	1 hora
Migrar secrets para .env	30 min
Atualizar documentação	30 min
TOTAL	3.5 horas
Benefícios
✅ Redução de ~150MB em dependências
✅ Projeto mais limpo e focado
✅ Build mais rápido (menos deps)
✅ Menor superfície de ataque (segurança)
✅ Manutenção simplificada

📋 Plano de Remoção (Passo a Passo)
Fase 1: Backup (5 min)
# Criar backup do projeto
git commit -am "Backup antes de remover Streamlit"
git tag streamlit-backup
Fase 2: Remover Arquivos (15 min)
# Remover app Streamlit
rm streamlit_app.py
# Remover configs Streamlit
rm -rf .streamlit/
rm core/config/streamlit_settings.py
rm core/utils/streamlit_stability.py
# Remover páginas/UI (se existir)
rm -rf pages/
rm -rf ui/
Fase 3: Limpar Dependencies (1 hora)
Criar novo 
requirements.in
 SEM Streamlit:

# Backend Core
fastapi>=0.116.0
uvicorn[standard]>=0.35.0
pydantic>=2.11.0
pydantic-settings>=2.10.0
python-dotenv>=1.1.0
python-jose[cryptography]>=3.5.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.20
# Database
sqlalchemy>=2.0.43
alembic>=1.16.4
pyodbc>=5.2.0
# Data Processing
pandas>=2.2.2
numpy>=1.26.4
polars>=1.34.0
pyarrow>=16.1.0
fastparquet>=2024.11.0
dask[array,dataframe]>=2024.5.1
# AI/ML
langchain>=0.3.27
langchain-core>=0.3.74
langchain-community>=0.3.27
langchain-openai>=0.3.30
langgraph>=0.6.4
langgraph-checkpoint-sqlite>=2.0.11
openai>=1.99.0
sentence-transformers>=5.1.0
faiss-cpu>=1.12.0
# Utilities
requests>=2.32.4
tqdm>=4.67.0
psutil>=7.0.0
structlog>=25.5.0
sentry-sdk>=2.35.0
# Testing
pytest>=8.4.0
pytest-cov>=6.2.0
# Development
pyngrok>=7.3.0
Recompilar:

pip-compile requirements.in
pip install -r requirements.txt
Fase 4: Migrar Secrets (30 min)
De 
.streamlit/secrets.toml
 para 
.env
:

# .env (backend)
DATABASE_URL=mssql+pyodbc://...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
JWT_SECRET_KEY=...
Fase 5: Testar (1 hora)
# Testar backend FastAPI
cd backend
uvicorn main:app --reload
# Testar frontend React
cd frontend-react
pnpm dev
# Rodar testes
pytest
pnpm test
Fase 6: Documentação (30 min)
 Atualizar README.md
 Remover referências ao Streamlit
 Documentar novo fluxo (React + FastAPI)
⚠️ Dependências Compartilhadas (NÃO REMOVER)
Estas dependências são usadas tanto pelo Streamlit quanto pelo backend:

✅ pandas - Usado pelo backend
✅ numpy - Usado pelo backend
✅ pillow - Usado por sentence-transformers
✅ requests - Usado pelo backend
✅ tenacity - Usado por langchain
✅ click - Usado por dask
🎯 Resultado Final
Antes (Com Streamlit)
Total Dependencies: ~80 pacotes
Total Size: ~800MB
Main Files: streamlit_app.py + backend
Depois (Sem Streamlit)
Total Dependencies: ~60 pacotes (-25%)
Total Size: ~650MB (-150MB)
Main Files: backend FastAPI apenas
✅ Checklist de Limpeza
 Backup do projeto (git tag)
 Remover streamlit_app.py
 Remover .streamlit/
 Remover core/config/streamlit_settings.py
 Remover core/utils/streamlit_stability.py
 Limpar requirements.in
 Recompilar requirements.txt
 Migrar secrets para .env
 Testar backend isoladamente
 Testar frontend React
 Atualizar documentação
 Commit final