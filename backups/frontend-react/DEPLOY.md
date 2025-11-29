# Guia de Deploy

## Pré-requisitos

- Conta Vercel ou Netlify
- Repositório GitHub
- Backend API rodando

## Deploy Staging (Vercel)

### 1. Conectar Repositório

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Importe seu repositório GitHub
4. Selecione a pasta `frontend-react`

### 2. Configurar Variáveis de Ambiente

No dashboard da Vercel, adicione:

```
NEXT_PUBLIC_API_URL=https://api-staging.seudominio.com
NEXT_PUBLIC_WS_URL=wss://api-staging.seudominio.com/ws
```

### 3. Deploy

- Branch `develop` → Deploy automático para staging
- Branch `main` → Deploy automático para produção

## Deploy Produção

### 1. Preparação

```bash
# Teste local de produção
pnpm build
pnpm start
```

### 2. Configurar Domínio

1. No dashboard Vercel, vá em "Settings" → "Domains"
2. Adicione seu domínio customizado
3. Configure DNS conforme instruções

### 3. Variáveis de Produção

```
NEXT_PUBLIC_API_URL=https://api.seudominio.com
NEXT_PUBLIC_WS_URL=wss://api.seudominio.com/ws
NODE_ENV=production
```

## Rollback

### Vercel

1. Acesse "Deployments"
2. Encontre o deploy anterior
3. Clique em "..." → "Promote to Production"

## Monitoramento

- **Vercel Analytics**: Ativado automaticamente
- **Logs**: Dashboard Vercel → "Logs"
- **Performance**: Lighthouse CI no GitHub Actions

## Checklist de Deploy

- [ ] Testes passando (`pnpm test`)
- [ ] Build sem erros (`pnpm build`)
- [ ] Variáveis de ambiente configuradas
- [ ] Backend API acessível
- [ ] SSL/HTTPS configurado
- [ ] Domínio configurado (produção)

## Troubleshooting

### Build Falha

```bash
# Limpar cache
rm -rf .next
pnpm install
pnpm build
```

### Variáveis não carregam

- Verifique prefixo `NEXT_PUBLIC_`
- Redeploy após adicionar variáveis
- Verifique logs no dashboard

## Comandos Úteis

```bash
# Build local
pnpm build

# Analisar bundle
ANALYZE=true pnpm build

# Testes antes do deploy
pnpm test:ci
```
