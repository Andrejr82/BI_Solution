🔧 Configuração Backend com SQL Server
Objetivo: Conectar backend FastAPI ao SQL Server da empresa

✅ Vantagens de Usar SQL Server Existente
✅ Sem necessidade de Docker
✅ Usa infraestrutura existente da empresa
✅ Dados já podem estar no SQL Server
✅ Equipe já conhece SQL Server
📋 Pré-requisitos
1. SQL Server Instalado
SQL Server 2017+ (qualquer edição)
SQL Server Express (grátis) também funciona
2. ODBC Driver 17 para SQL Server
Verificar se está instalado:

Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
Se não estiver instalado:

Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
Instalar: ODBC Driver 17 for SQL Server
🔌 Configuração
Passo 1: Criar Database
Conectar ao SQL Server e executar:

-- Criar database
CREATE DATABASE agentbi;
GO
-- Criar login (se necessário)
CREATE LOGIN agentbi_user WITH PASSWORD = 'SuaSenhaSegura123!';
GO
-- Usar database
USE agentbi;
GO
-- Criar user e dar permissões
CREATE USER agentbi_user FOR LOGIN agentbi_user;
GO
ALTER ROLE db_owner ADD MEMBER agentbi_user;
GO
Passo 2: Configurar Connection String
Editar backend/.env:

# Formato geral:
# mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
# Exemplo 1: SQL Server local com autenticação SQL
DATABASE_URL=mssql+pyodbc://agentbi_user:SuaSenhaSegura123!@localhost/agentbi?driver=ODBC+Driver+17+for+SQL+Server
# Exemplo 2: SQL Server local com Windows Authentication
DATABASE_URL=mssql+pyodbc://localhost/agentbi?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
# Exemplo 3: SQL Server remoto
DATABASE_URL=mssql+pyodbc://user:pass@servidor.empresa.com:1433/agentbi?driver=ODBC+Driver+17+for+SQL+Server
# Exemplo 4: SQL Server com instância nomeada
DATABASE_URL=mssql+pyodbc://user:pass@localhost\\SQLEXPRESS/agentbi?driver=ODBC+Driver+17+for+SQL+Server
Passo 3: Instalar Dependências
cd C:\Users\André\Documents\Agent_Solution_BI\backend
poetry install
Passo 4: Criar Tabelas (Migrations)
# Criar migration inicial
poetry run alembic revision --autogenerate -m "Initial tables"
# Aplicar migrations
poetry run alembic upgrade head
Passo 5: Seed Admin User
poetry run python scripts\seed_admin.py
Passo 6: Iniciar Backend
poetry run uvicorn main:app --reload
✅ Backend rodando em: http://localhost:8000
✅ Docs em: http://localhost:8000/docs

🧪 Testar Conexão
Teste 1: Health Check
curl http://localhost:8000/health
Deve retornar:

{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
Teste 2: Login
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username": "admin", "password": "admin123"}'
Deve retornar:

{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
🐛 Troubleshooting
Erro: "ODBC Driver not found"
Solução:

Instalar ODBC Driver 17
Verificar nome exato do driver:
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL*"}
Ajustar connection string se necessário
Erro: "Login failed for user"
Solução:

Verificar credenciais
Verificar se user tem permissões
Testar conexão com SQL Server Management Studio
Erro: "Cannot open database"
Solução:

Verificar se database existe
Verificar nome do database na connection string
Criar database se necessário
Erro: "Connection timeout"
Solução:

Verificar se SQL Server está rodando
Verificar firewall
Verificar nome do servidor/porta
📊 Estrutura de Tabelas
Após rodar migrations, terá 3 tabelas:

-- Verificar tabelas criadas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
Tabelas:

users
 - Usuários do sistema
reports
 - Relatórios
audit_logs
 - Logs de auditoria
🔄 Próximos Passos
✅ SQL Server configurado
✅ Database criada
✅ Backend conectado
✅ Tabelas criadas
✅ Admin user criado
⏳ Testar integração com frontend
💡 Dicas
Usar SQL Server existente da empresa
Se já tem um SQL Server com dados:

Apontar para o servidor existente
Criar database agentbi separada
Ou usar database existente e ajustar models
Migrations incrementais
# Criar nova migration após alterar models
poetry run alembic revision --autogenerate -m "Add new field"
# Aplicar
poetry run alembic upgrade head
# Reverter última migration
poetry run alembic downgrade -1
Backup
-- Backup database
BACKUP DATABASE agentbi 
TO DISK = 'C:\Backup\agentbi.bak'
WITH FORMAT;
✅ Checklist Final
 ODBC Driver 17 instalado
 SQL Server acessível
 Database agentbi criada
 User com permissões criado
 Connection string configurada em 
.env
 Dependências instaladas (poetry install)
 Migrations aplicadas (alembic upgrade head)
 Admin user criado (
seed_admin.py
)
 Backend rodando (uvicorn main:app --reload)
 Health check funcionando
 Login funcionando