# 🚀 Quick Start - Backend FastAPI

## Início Rápido (5 minutos)

### 1. Clonar e Navegar
```bash
cd backend
```

### 2. Copiar Environment
```bash
cp .env.example .env
```

### 3. Subir Docker
```bash
docker-compose up -d
```

### 4. Aguardar PostgreSQL
```bash
# Aguardar ~10 segundos para PostgreSQL inicializar
```

### 5. Instalar Dependências
```bash
# Instalar Poetry (se não tiver)
pip install poetry

# Instalar dependências
poetry install
```

### 6. Criar Tabelas
```bash
# Criar tabelas do banco
poetry run python -c "
import asyncio
from app.config.database import engine, Base
from app.infrastructure.database.models import User, Report, AuditLog

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Tables created')

asyncio.run(create_tables())
"
```

### 7. Seed Admin User
```bash
poetry run python scripts/seed_admin.py
```

### 8. Rodar Backend
```bash
poetry run uvicorn main:app --reload
```

### 9. Testar
```bash
# Abrir Swagger
open http://localhost:8000/docs

# Fazer login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## ✅ Pronto!

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050 (admin@agentbi.com / admin)
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 📝 Credenciais Padrão

- **Username:** admin
- **Password:** admin123
- **Email:** admin@agentbi.com

⚠️ **Trocar senha após primeiro login!**
