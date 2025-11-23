# 🔧 Configuração de Integração Frontend-Backend

## 1. Configurar Variáveis de Ambiente

Crie o arquivo `.env.local` na raiz do `frontend-react`:

```bash
cd frontend-react
```

Crie o arquivo `.env.local` com o seguinte conteúdo:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket URL (opcional)
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 2. Iniciar Backend

```bash
cd backend

# Subir PostgreSQL e Redis
docker-compose up -d

# Aguardar ~10 segundos

# Criar usuário admin (primeira vez)
poetry run python scripts/seed_admin.py

# Iniciar backend
poetry run uvicorn main:app --reload
```

Backend estará em: http://localhost:8000  
Docs: http://localhost:8000/docs

## 3. Iniciar Frontend

```bash
cd frontend-react
pnpm dev
```

Frontend estará em: http://localhost:3000

## 4. Testar Conexão

1. Abra http://localhost:3000
2. Faça login com:
   - **Username:** admin
   - **Password:** admin123
3. Verifique se o login funciona

## 5. Credenciais Padrão

- **Admin:**
  - Username: `admin`
  - Password: `admin123`
  - Email: `admin@agentbi.com`

⚠️ **Trocar senha após primeiro login!**

## 6. Troubleshooting

### Backend não inicia
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Ver logs
docker-compose logs -f db
```

### Frontend não conecta
- Verificar se `NEXT_PUBLIC_API_URL` está correto
- Verificar CORS no backend
- Abrir DevTools e verificar Network tab

### Erro de CORS
O backend já está configurado para aceitar `http://localhost:3000`.  
Se necessário, editar `backend/app/config/settings.py`.
