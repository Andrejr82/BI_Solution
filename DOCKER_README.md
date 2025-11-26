# 🐳 Docker - Agent Solution BI

Guia completo para executar o Agent Solution BI usando Docker.

## 📋 Pré-requisitos

- **Docker Desktop** instalado e rodando (ícone verde)
- **SQL Server** rodando localmente (para autenticação)
- **Gemini API Key** ([obtenha aqui](https://makersuite.google.com/app/apikey))

## 🚀 Início Rápido

### Windows

1. **Execute o script de inicialização:**
   ```bash
   docker-start.bat
   ```

2. **Configure as variáveis de ambiente** (se for a primeira vez):
   - O script criará `.env.docker` automaticamente
   - Edite o arquivo e configure:
     - `DATABASE_URL`: Conexão com seu SQL Server
     - `GEMINI_API_KEY`: Sua chave da API Gemini
     - `SECRET_KEY`: Gere uma chave forte de 32+ caracteres

3. **Aguarde a inicialização:**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - O navegador abrirá automaticamente

### Linux/Mac

1. **Copie o template de configuração:**
   ```bash
   cp .env.docker.example .env.docker
   ```

2. **Edite as variáveis de ambiente:**
   ```bash
   nano .env.docker  # ou seu editor preferido
   ```

3. **Inicie os containers:**
   ```bash
   docker-compose up -d
   ```

4. **Acompanhe os logs:**
   ```bash
   docker-compose logs -f
   ```

## ⚙️ Configuração

### Autenticação Híbrida

O sistema usa **autenticação híbrida** com fallback automático:

#### 1. SQL Server (Prioridade)
Se `USE_SQL_SERVER=true` no `.env.docker`, o sistema tentará autenticar via SQL Server primeiro.

Configure a conexão em `.env.docker`:
```env
DATABASE_URL=mssql+aioodbc://AgenteVirtual:Cacula@2020@host.docker.internal:1433/Projeto_Caculinha?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
USE_SQL_SERVER=true
```

**Importante:** Use `host.docker.internal` para acessar SQL Server rodando no Windows host.

#### 2. Parquet (Fallback Automático)
Se SQL Server falhar ou estiver desabilitado, o sistema usa automaticamente `data/parquet/users.parquet`.

**Credenciais padrão do Parquet:**
```
Usuário: admin
Senha: admin123
```

> [!TIP]
> **Recomendação**: Para desenvolvimento, use apenas Parquet (mais simples):
> ```env
> USE_SQL_SERVER=false
> FALLBACK_TO_PARQUET=true
> ```

### Dados Analíticos (Parquet)

Os dados analíticos estão em arquivos Parquet na pasta `data/parquet/`:
- `admmat.parquet` - Dados principais para consultas do agente
- `users.parquet` - Usuários para autenticação (fallback)

Eles são montados automaticamente no container backend como somente leitura.

### Gemini API Key

Obtenha sua chave em: https://makersuite.google.com/app/apikey

Configure em `.env.docker`:
```env
GEMINI_API_KEY=sua-chave-aqui
```

## 📊 Serviços

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| Backend | 8000 | http://localhost:8000 | FastAPI REST API |
| API Docs | 8000 | http://localhost:8000/docs | Swagger UI |
| Frontend | 3000 | http://localhost:3000 | React/Next.js UI |
| Redis | 6379 | localhost:6379 | Cache |

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar sistema
docker-compose up -d

# Parar sistema
docker-compose down

# Reiniciar sistema
docker-compose restart

# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Build e Rebuild

```bash
# Rebuild completo (sem cache)
docker-compose build --no-cache

# Rebuild e reiniciar
docker-compose up -d --build

# Rebuild apenas um serviço
docker-compose build backend
```

### Limpeza

```bash
# Parar e remover containers, networks
docker-compose down

# Parar e remover containers, networks e volumes
docker-compose down -v

# Remover imagens não utilizadas
docker image prune -a
```

## 🐛 Troubleshooting

### Backend não inicia

**Sintoma:** Container `agentbi-backend` fica reiniciando.

**Soluções:**
1. Verifique os logs:
   ```bash
   docker-compose logs backend
   ```

2. Verifique a conexão com SQL Server:
   - SQL Server está rodando?
   - Firewall permite conexão na porta 1433?
   - Credenciais em `DATABASE_URL` estão corretas?

3. Teste a conexão manualmente:
   ```bash
   docker-compose exec backend python -c "from app.config.database import engine; print('OK')"
   ```

### Frontend não carrega

**Sintoma:** Página em branco ou erro 502.

**Soluções:**
1. Aguarde mais tempo (primeiro build pode demorar 2-3 minutos)

2. Verifique se backend está healthy:
   ```bash
   docker-compose ps
   ```
   Status deve ser "healthy" para backend.

3. Verifique logs do frontend:
   ```bash
   docker-compose logs frontend
   ```

### Erro de permissão no volume

**Sintoma:** `Permission denied` ao acessar arquivos Parquet.

**Solução:**
```bash
# Windows: Execute PowerShell como Administrador
icacls "data" /grant Everyone:F /T

# Linux/Mac
chmod -R 755 data/
```

### Redis não conecta

**Sintoma:** Erros de conexão Redis nos logs.

**Solução:**
```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Reiniciar Redis
docker-compose restart redis

# Testar conexão
docker-compose exec backend python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### Build muito lento

**Sintoma:** `docker-compose build` demora muito.

**Soluções:**
1. Verifique conexão com internet (downloads de dependências)

2. Aumente recursos do Docker Desktop:
   - Settings → Resources
   - CPU: 4+ cores
   - Memory: 4+ GB

3. Use cache do Docker:
   ```bash
   docker-compose build  # sem --no-cache
   ```

## 🔐 Credenciais Padrão

### Autenticação via Parquet (Fallback)
```
Usuário: admin
Senha: admin123
```

### Autenticação via SQL Server
Se você configurou `USE_SQL_SERVER=true`, as credenciais dependem dos usuários cadastrados no seu SQL Server.

> [!IMPORTANT]
> **Nota sobre senhas**: O arquivo `CREDENTIALS.md` menciona `Admin@2024`, mas essa senha é para SQL Server. 
> Para autenticação via Parquet (fallback), use `admin123`.

## 📝 Arquitetura Docker

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │ Frontend │  │ Backend  │  │ Redis │ │
│  │  :3000   │→ │  :8000   │→ │ :6379 │ │
│  └──────────┘  └──────────┘  └───────┘ │
│                     ↓                   │
│                     ↓                   │
└─────────────────────┼───────────────────┘
                      ↓
              ┌───────────────┐
              │  SQL Server   │
              │ (Host Windows)│
              │     :1433     │
              └───────────────┘
                      ↓
              ┌───────────────┐
              │ Parquet Files │
              │   ./data/     │
              └───────────────┘
```

## 🎯 Próximos Passos

Após iniciar o sistema:

1. **Acesse o frontend:** http://localhost:3000
2. **Faça login** com as credenciais padrão
3. **Teste o Chat BI** fazendo uma pergunta
4. **Explore o dashboard** e relatórios

## 📚 Documentação Adicional

- [README.md](README.md) - Visão geral do projeto
- [CREDENTIALS.md](CREDENTIALS.md) - Guia de credenciais
- [QUICK_START.md](QUICK_START.md) - Início rápido sem Docker
