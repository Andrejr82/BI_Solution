# Agent BI Backend

Backend FastAPI moderno para Agent Solution BI.

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# Copiar .env.example para .env
cp .env.example .env

# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Acessar API
open http://localhost:8000/docs
```

### Sem Docker (Local)

```bash
# Instalar Poetry
pip install poetry

# Instalar dependências
poetry install

# Copiar .env
cp .env.example .env

# Rodar PostgreSQL e Redis localmente
# (ou ajustar DATABASE_URL e REDIS_URL no .env)

# Rodar migrations
poetry run alembic upgrade head

# Rodar servidor
poetry run uvicorn main:app --reload
```

## 📚 Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🏗️ Arquitetura

```
backend/
├── app/
│   ├── api/              # Endpoints HTTP
│   ├── core/             # Business logic
│   ├── infrastructure/   # Database, cache, etc
│   ├── schemas/          # Pydantic schemas
│   └── config/           # Settings
├── tests/                # Tests
├── main.py               # FastAPI app
└── docker-compose.yml    # Docker setup
```

## 🔐 Autenticação

Todos os endpoints (exceto `/auth/login`) requerem JWT token:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Usar token
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testes

```bash
# Rodar todos os testes
poetry run pytest

# Com coverage
poetry run pytest --cov=app

# Apenas unit tests
poetry run pytest tests/unit
```

## 📦 Dependências Principais

- **FastAPI** - Framework web async
- **SQLAlchemy 2.0** - ORM async
- **PostgreSQL** - Database
- **Redis** - Cache
- **Pydantic** - Validação de dados
- **JWT** - Autenticação

## 🔧 Desenvolvimento

```bash
# Formatar código
poetry run black app tests

# Lint
poetry run ruff check app tests

# Type check
poetry run mypy app
```

## 🚢 Deploy

Ver `DEPLOY.md` para instruções de deploy em produção.

## 📝 License

MIT
