# Variáveis de Ambiente

## Desenvolvimento Local

Copie este arquivo para `.env.local` e preencha os valores:

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Ambiente
NODE_ENV=development

# Bundle Analyzer (opcional)
ANALYZE=false
```

## Produção

```bash
# API Backend
NEXT_PUBLIC_API_URL=https://api.seudominio.com

# WebSocket
NEXT_PUBLIC_WS_URL=wss://api.seudominio.com/ws

# Ambiente
NODE_ENV=production
```

## Notas

- Variáveis com prefixo `NEXT_PUBLIC_` são expostas no browser
- Variáveis sem prefixo são apenas server-side
- Nunca commite `.env.local` no git
