# Guia de Configuração do TestSprite

## 📋 Visão Geral

Este guia explica como configurar e usar o TestSprite para testes automatizados end-to-end do Agent Solution BI.

## 🎯 O que é TestSprite?

TestSprite é uma ferramenta de testes orientada por IA que:
- Gera testes automaticamente analisando seu código
- Cria scripts de teste executáveis (Playwright)
- Executa testes em ambiente cloud seguro
- Fornece relatórios detalhados com screenshots e vídeos
- Sugere correções automáticas para bugs encontrados

## 🔧 Pré-requisitos

- Node.js 20+
- Python 3.11+
- Conta TestSprite (criar em [testsprite.com](https://testsprite.com))
- API Key do TestSprite

## 📦 Instalação

### 1. Instalar Dependências do Playwright

```bash
cd c:\Users\André\Documents\Agent_Solution_BI
npm install
```

### 2. Instalar Navegadores do Playwright

```bash
npm run testsprite:install
```

Isso instalará os navegadores Chromium, Firefox e WebKit necessários para os testes.

### 3. Configurar o Servidor MCP do TestSprite

O TestSprite se integra via Model Context Protocol (MCP). Você precisa adicionar a configuração no arquivo MCP:

**Localização**: `C:\Users\André\.gemini\antigravity\mcp_config.json`

**Adicione esta configuração**:

```json
{
  "mcpServers": {
    "testsprite": {
      "command": "npx",
      "args": ["-y", "@testsprite/mcp-server"],
      "env": {
        "TESTSPRITE_API_KEY": "sua-api-key-aqui"
      }
    }
  }
}
```

### 4. Obter API Key do TestSprite

1. Acesse [testsprite.com](https://testsprite.com)
2. Crie uma conta ou faça login
3. Vá em Settings → API Keys
4. Gere uma nova API key
5. Copie e cole no `mcp_config.json`

## 🚀 Usando o TestSprite

### Opção 1: Via MCP Server (Recomendado)

Com o servidor MCP configurado, você pode usar o TestSprite diretamente através do seu IDE:

1. **Gerar Testes**: O TestSprite analisará o PRD (`TESTSPRITE_PRD.md`) e seu código
2. **Criar Scripts**: Gerará arquivos de teste Playwright em `tests/e2e/`
3. **Executar Testes**: Rodará os testes em ambiente cloud
4. **Revisar Resultados**: Fornecerá relatórios detalhados

### Opção 2: Executar Testes Localmente

Após o TestSprite gerar os testes, você pode executá-los localmente:

#### Iniciar Backend e Frontend

```bash
# Terminal 1 - Backend
cd c:\Users\André\Documents\Agent_Solution_BI\backend
.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend
cd c:\Users\André\Documents\Agent_Solution_BI\frontend-solid
pnpm dev
```

#### Executar Todos os Testes

```bash
# Terminal 3 - Testes
cd c:\Users\André\Documents\Agent_Solution_BI
npm run test:e2e
```

#### Executar Testes com Interface Visual

```bash
npm run test:e2e:ui
```

#### Executar Testes em Modo Debug

```bash
npm run test:e2e:debug
```

#### Ver Relatório de Testes

```bash
npm run test:e2e:report
```

## 📁 Estrutura de Arquivos

```
Agent_Solution_BI/
├── tests/
│   └── e2e/                    # Testes gerados pelo TestSprite
│       ├── auth.spec.ts        # Testes de autenticação
│       ├── dashboard.spec.ts   # Testes do dashboard
│       ├── chatbi.spec.ts      # Testes do Chat BI
│       ├── admin.spec.ts       # Testes do painel admin
│       ├── reports.spec.ts     # Testes de relatórios
│       └── components.spec.ts  # Testes de componentes UI
├── playwright-report/          # Relatórios HTML gerados
├── test-results/              # Resultados em JSON
├── playwright.config.ts       # Configuração do Playwright
├── testsprite.config.json     # Configuração do TestSprite
└── TESTSPRITE_PRD.md         # Documento de requisitos
```

## 🧪 Cenários de Teste Cobertos

### Autenticação
- ✅ Login com credenciais válidas
- ✅ Login com credenciais inválidas
- ✅ Logout
- ✅ Proteção de rotas privadas
- ✅ Expiração de token JWT

### Dashboard
- ✅ Carregamento de métricas
- ✅ Renderização de gráficos
- ✅ Atualização em tempo real

### Chat BI
- ✅ Envio de query em linguagem natural
- ✅ Processamento via Gemini
- ✅ Streaming de resposta
- ✅ Visualização de dados

### Admin
- ✅ Listagem de usuários
- ✅ Criar novo usuário
- ✅ Editar usuário
- ✅ Deletar usuário
- ✅ Logs de auditoria

### Relatórios
- ✅ Listagem de relatórios
- ✅ Visualização de relatório
- ✅ Geração de relatório
- ✅ Exportação de dados

### Componentes UI
- ✅ Todos os 18+ componentes SolidJS
- ✅ Interações (clicks, inputs)
- ✅ Validações de formulário
- ✅ Tema light/dark

## 📊 Interpretando Resultados

### Relatório HTML

Após executar os testes, abra `playwright-report/index.html` no navegador:

- **Verde**: Teste passou ✅
- **Vermelho**: Teste falhou ❌
- **Amarelo**: Teste pulado ⚠️

### Screenshots e Vídeos

Para testes que falharam:
- Screenshots são salvos em `test-results/`
- Vídeos são salvos em `test-results/`
- Traces podem ser visualizados com `npx playwright show-trace`

## 🔍 Comandos Úteis

```bash
# Executar apenas testes de autenticação
npx playwright test auth.spec.ts

# Executar testes em modo headed (ver navegador)
npm run test:e2e:headed

# Executar testes em navegador específico
npx playwright test --project=chromium

# Gerar relatório de cobertura
npx playwright test --reporter=html

# Limpar resultados anteriores
rm -rf test-results playwright-report
```

## 🐛 Troubleshooting

### Erro: "Backend não está disponível"

**Solução**: Verifique se o backend está rodando na porta 8000:
```bash
curl http://127.0.0.1:8000/health
```

### Erro: "Timeout waiting for page"

**Solução**: Aumente o timeout no `playwright.config.ts`:
```typescript
use: {
  actionTimeout: 30000, // 30 segundos
}
```

### Erro: "Browser not found"

**Solução**: Reinstale os navegadores:
```bash
npx playwright install --force
```

### Erro: "Port 3000 already in use"

**Solução**: Mate o processo na porta 3000:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
```

## 🔄 Workflow Recomendado

### Desenvolvimento Diário

1. **Smoke Tests**: Execute testes críticos antes de começar
```bash
npx playwright test auth.spec.ts dashboard.spec.ts
```

2. **Desenvolvimento**: Faça suas alterações

3. **Testes Locais**: Execute testes relacionados
```bash
npm run test:e2e:headed
```

### Antes de Commit

```bash
# Execute suite completa
npm run test:e2e

# Verifique relatório
npm run test:e2e:report
```

### CI/CD (Futuro)

Os testes serão executados automaticamente em cada PR via GitHub Actions.

## 📚 Recursos Adicionais

- [Documentação TestSprite](https://docs.testsprite.com)
- [Documentação Playwright](https://playwright.dev)
- [TESTSPRITE_PRD.md](./TESTSPRITE_PRD.md) - Especificação completa dos testes
- [TESTSPRITE_WORKFLOW.md](./TESTSPRITE_WORKFLOW.md) - Workflow detalhado

## 🎯 Próximos Passos

1. ✅ Configurar MCP Server
2. ✅ Obter API Key
3. ⏳ Gerar testes via TestSprite
4. ⏳ Executar testes localmente
5. ⏳ Revisar e ajustar testes
6. ⏳ Integrar com CI/CD
