# 📦 Instalação Completa - Agent Solution BI com Frontend React

## 🎯 Visão Geral

Este guia detalha a instalação completa do sistema **Agent Solution BI** com o novo frontend React (claude-share-buddy integrado).

### Arquitetura

```
┌─────────────────────────────────────────┐
│         Frontend React (Port 8080)       │
│    - Interface moderna e responsiva      │
│    - 14 páginas funcionais               │
│    - Chat com IA, Dashboards, etc.       │
└──────────────┬──────────────────────────┘
               │ HTTP Requests (/api/*)
               ↓
┌─────────────────────────────────────────┐
│      Backend Flask API (Port 5000)       │
│    - Endpoints REST                      │
│    - Integração com Agent_Graph          │
│    - Processamento de IA                 │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      Agent_Solution_BI Backend           │
│    - LangGraph + Gemini                  │
│    - ParquetAdapter (Polars/Dask)        │
│    - Sistema de Cache                    │
│    - Query History                       │
└─────────────────────────────────────────┘
```

## 📋 Pré-requisitos

### Sistema Operacional
- ✅ Windows 10/11, Linux ou macOS

### Software Necessário

1. **Python 3.11+**
   ```bash
   python --version  # Deve mostrar 3.11 ou superior
   ```

2. **Node.js 18+** (para o frontend)
   ```bash
   node --version  # Deve mostrar v18 ou superior
   npm --version   # Deve mostrar 9 ou superior
   ```

   - Instalar com [nvm](https://github.com/nvm-sh/nvm) (recomendado):
   ```bash
   nvm install 18
   nvm use 18
   ```

3. **Git**
   ```bash
   git --version
   ```

## 🚀 Instalação Passo a Passo

### 1. Clonar o Repositório

```bash
cd ~/Documents  # ou seu diretório preferido
git clone <URL_DO_REPOSITORIO> Agent_Solution_BI
cd Agent_Solution_BI
```

### 2. Configurar Backend Python

#### 2.1. Criar Ambiente Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2.2. Instalar Dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3. Configurar Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here  # Opcional

# Database (se usar SQL Server)
SQL_SERVER=localhost
SQL_DATABASE=your_database
SQL_USERNAME=your_username
SQL_PASSWORD=your_password

# Flask API
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

#### 2.4. Verificar Dados Parquet

Certifique-se de que os arquivos Parquet estão em:

```
data/parquet/
├── admmat.parquet
├── produtos.parquet
├── vendas.parquet
└── ...
```

### 3. Configurar Frontend React

#### 3.1. Navegar para pasta frontend

```bash
cd frontend
```

#### 3.2. Instalar Dependências Node.js

```bash
npm install
# ou se preferir usar bun
bun install
```

#### 3.3. Verificar Configuração

Arquivo `vite.config.ts` já está configurado com proxy para:
- Backend API: `http://localhost:5000/api/*`

### 4. Iniciar Serviços

#### Opção A: Iniciar Manualmente (Recomendado para Desenvolvimento)

**Terminal 1 - Backend Flask API:**
```bash
# Na raiz do projeto
python backend_api.py
```
- API estará rodando em: `http://localhost:5000`
- Health check: `http://localhost:5000/api/health`

**Terminal 2 - Frontend React:**
```bash
cd frontend
npm run dev
```
- Frontend estará rodando em: `http://localhost:8080`

#### Opção B: Script de Inicialização (Ambos juntos)

**Windows:**
```bash
# Criar arquivo start.bat
@echo off
echo Iniciando Agent Solution BI...
start cmd /k "python backend_api.py"
timeout /t 3
start cmd /k "cd frontend && npm run dev"
```

**Linux/Mac:**
```bash
# Criar arquivo start.sh
#!/bin/bash
echo "Iniciando Agent Solution BI..."
python backend_api.py &
sleep 3
cd frontend && npm run dev
```

Tornar executável:
```bash
chmod +x start.sh
./start.sh
```

### 5. Verificar Instalação

#### 5.1. Testar Backend API

```bash
curl http://localhost:5000/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T...",
  "version": "1.0.0"
}
```

#### 5.2. Testar Frontend

Abrir navegador em: `http://localhost:8080`

Você deve ver:
- ✅ Interface do claude-share-buddy
- ✅ Menu lateral com 14 páginas
- ✅ Chat BI funcional
- ✅ Dashboard de métricas

#### 5.3. Testar Integração

No chat, enviar uma pergunta:
```
Top 10 produtos mais vendidos
```

Deve retornar:
- ✅ Resposta da IA processada
- ✅ Gráfico ou tabela com dados
- ✅ Tempo de processamento

## 🔧 Configurações Avançadas

### Production Build

#### Backend (Flask com Gunicorn)

```bash
pip install gunicorn

# Iniciar com Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend_api:app
```

#### Frontend (Build Otimizado)

```bash
cd frontend
npm run build

# Servir com servidor estático
npm install -g serve
serve -s dist -l 8080
```

### Docker (Opcional)

Criar `Dockerfile` na raiz:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend (pre-built)
COPY frontend/dist ./frontend/dist

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend_api:app"]
```

Build e Run:
```bash
docker build -t agent-solution-bi .
docker run -p 5000:5000 -p 8080:8080 agent-solution-bi
```

### Nginx Reverse Proxy (Produção)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### Problema: Backend não inicia

**Erro:** `ModuleNotFoundError: No module named 'flask'`

**Solução:**
```bash
pip install flask flask-cors
```

### Problema: Frontend não conecta ao backend

**Erro:** `Network Error` ou `CORS Error`

**Solução:**
1. Verificar se backend está rodando em `http://localhost:5000`
2. Verificar proxy em `frontend/vite.config.ts`
3. Adicionar `flask-cors` ao backend:
   ```bash
   pip install flask-cors
   ```

### Problema: Porta já em uso

**Backend (5000):**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**Frontend (8080):**
```bash
# Alterar porta em vite.config.ts
server: {
  port: 3000  # usar porta diferente
}
```

### Problema: GEMINI_API_KEY não encontrada

**Erro:** `ValueError: Nenhuma chave LLM encontrada`

**Solução:**
1. Criar arquivo `.env` na raiz
2. Adicionar: `GEMINI_API_KEY=your_key_here`
3. Reiniciar backend

### Problema: Parquet não encontrado

**Erro:** `FileNotFoundError: data/parquet/admmat.parquet`

**Solução:**
1. Verificar se pasta `data/parquet/` existe
2. Executar script de exportação (se necessário):
   ```bash
   python dev_tools/scripts/export_sqlserver_to_parquet.py
   ```

## 📊 Monitoramento

### Logs do Backend

```bash
# Ver logs em tempo real
tail -f logs/app_activity/*.log

# Erros
tail -f logs/errors/*.log
```

### Performance do Frontend

Abrir DevTools do navegador:
- Network tab: verificar chamadas `/api/*`
- Console: verificar erros JavaScript
- Performance: analisar carregamento

## 🔒 Segurança

### Produção Checklist

- [ ] Alterar `SECRET_KEY` no `.env`
- [ ] Desabilitar `FLASK_DEBUG=False`
- [ ] Usar HTTPS (certificado SSL)
- [ ] Configurar CORS restritivamente
- [ ] Implementar rate limiting
- [ ] Adicionar autenticação JWT
- [ ] Sanitizar inputs do usuário

## 📚 Próximos Passos

1. ✅ **Testar todas as páginas**
   - Chat BI
   - Gráficos Salvos
   - Monitoramento
   - Métricas
   - Exemplos
   - Admin
   - Diagnóstico DB
   - Gemini Playground
   - Sistema de Aprendizado

2. ✅ **Personalizar Interface**
   - Logo da empresa
   - Cores do tema
   - Textos e mensagens

3. ✅ **Configurar Autenticação**
   - Integrar com sistema de login existente
   - Adicionar JWT tokens
   - Controle de permissões

4. ✅ **Deploy em Produção**
   - Configurar servidor
   - Setup de domínio
   - CI/CD pipeline

## 📖 Documentação Adicional

- [README Frontend](frontend/README_FRONTEND.md)
- [Documentação Backend API](backend_api.py)
- [Arquitetura do Sistema](docs/ARCHITECTURE.md)

## 🤝 Suporte

Em caso de problemas:

1. Verificar logs: `logs/app_activity/`
2. Consultar troubleshooting acima
3. Abrir issue no GitHub
4. Contatar equipe de desenvolvimento

---

**Versão:** 1.0.0
**Data:** 2025-10-25
**Autor:** Equipe Agent Solution BI
