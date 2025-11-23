✅ Checklist de Validação - .env para SQL Server
Arquivo: 
C:\Users\André\Documents\Agent_Solution_BI.env

📋 Variáveis OBRIGATÓRIAS
1. DATABASE_URL (SQL Server)
# Formato:
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
# Exemplos:
# Local com SQL Auth:
DATABASE_URL=mssql+pyodbc://sa:SuaSenha@localhost/agentbi?driver=ODBC+Driver+17+for+SQL+Server
# Local com Windows Auth:
DATABASE_URL=mssql+pyodbc://localhost/agentbi?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
# Remoto:
DATABASE_URL=mssql+pyodbc://user:pass@servidor.empresa.com/agentbi?driver=ODBC+Driver+17+for+SQL+Server
# Com instância nomeada:
DATABASE_URL=mssql+pyodbc://user:pass@localhost\\SQLEXPRESS/agentbi?driver=ODBC+Driver+17+for+SQL+Server
✅ Verificar:

 URL está no formato correto
 Username e password estão corretos
 Nome do servidor está correto
 Nome do database existe
 Driver ODBC está instalado
2. SECRET_KEY
SECRET_KEY=sua-chave-secreta-forte-min-32-caracteres-aqui
✅ Verificar:

 Tem pelo menos 32 caracteres
 É única (não usar a padrão)
 É aleatória e forte
3. BACKEND_CORS_ORIGINS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
✅ Verificar:

 Inclui http://localhost:3000 (frontend)
 Inclui http://localhost:8000 (docs)
🔧 Variáveis OPCIONAIS (mas recomendadas)
4. App Config
APP_NAME="Agent BI Backend"
DEBUG=true
ENVIRONMENT=development
5. Database Pool
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
6. Redis (Opcional - comentar se não tiver)
# REDIS_URL=redis://localhost:6379/0
# REDIS_CACHE_TTL=3600
7. Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
8. Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_AUTH_PER_MINUTE=5
9. Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
🧪 Como Testar a Configuração
Teste 1: Verificar se .env está sendo lido
cd C:\Users\André\Documents\Agent_Solution_BI\backend
poetry run python -c "from app.config.settings import get_settings; s = get_settings(); print(f'App: {s.APP_NAME}'); print(f'DB: {s.DATABASE_URL}')"
Deve mostrar:

Nome do app
Connection string (com senha mascarada)
Teste 2: Testar conexão com SQL Server
poetry run python -c "
from app.config.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('✅ Conexão OK!')
asyncio.run(test())
"
Deve mostrar:

✅ Conexão OK!
Teste 3: Verificar ODBC Driver
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
Deve mostrar:

ODBC Driver 17 for SQL Server (ou superior)
📝 Template Completo .env
Se quiser recriar do zero, use este template:

# App
APP_NAME="Agent BI Backend"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development
# API
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
# Database - SQL Server
DATABASE_URL=mssql+pyodbc://SEU_USER:SUA_SENHA@localhost/agentbi?driver=ODBC+Driver+17+for+SQL+Server
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
# Redis (Opcional - comentar se não tiver)
# REDIS_URL=redis://localhost:6379/0
# REDIS_CACHE_TTL=3600
# Security (TROCAR EM PRODUÇÃO!)
SECRET_KEY=sua-chave-secreta-forte-min-32-caracteres-aqui-trocar-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_AUTH_PER_MINUTE=5
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
# Sentry (opcional)
# SENTRY_DSN=
# SENTRY_ENVIRONMENT=development
# Metrics
METRICS_ENABLED=true
⚠️ Problemas Comuns
DATABASE_URL incorreta
Sintomas:

Erro ao conectar
"Cannot open database"
Soluções:

Verificar nome do servidor
Verificar nome do database
Verificar credenciais
Verificar se SQL Server está rodando
ODBC Driver não encontrado
Sintomas:

"ODBC Driver not found"
"Data source name not found"
Solução:

Instalar ODBC Driver 17: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
SECRET_KEY muito curta
Sintomas:

Erro ao iniciar backend
"Secret key too short"
Solução:

Gerar chave forte:
python -c "import secrets; print(secrets.token_urlsafe(32))"
✅ Checklist Final
 DATABASE_URL configurada corretamente
 SQL Server acessível
 Database existe
 ODBC Driver instalado
 SECRET_KEY forte (32+ chars)
 BACKEND_CORS_ORIGINS inclui frontend
 Redis comentado (se não tiver)
 Teste de conexão passou
 Backend inicia sem erros