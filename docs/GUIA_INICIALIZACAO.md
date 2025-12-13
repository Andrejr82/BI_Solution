# 🚀 Guia de Inicialização - AgentBI

Sistema simplificado de inicialização usando **concurrently** para melhor experiência de desenvolvimento.

---

## 🎯 Melhorias Implementadas

### ❌ Antes (Problemas)
- ✗ 3 terminais separados (difícil de acompanhar)
- ✗ Logs espalhados
- ✗ Difícil gerenciar processos
- ✗ Precisa fechar 3 janelas manualmente

### ✅ Agora (Soluções)
- ✓ **1 terminal único** com saídas coloridas
- ✓ **Logs agregados** em tempo real (opcional)
- ✓ **Gerenciamento automático** de processos
- ✓ **Ctrl+C encerra tudo** de uma vez
- ✓ **Cores por serviço** (Backend azul, Frontend verde)

---

## 📋 Opções de Inicialização

### 1️⃣ Modo Padrão (Recomendado) - 1 Terminal

```bash
# Windows - Batch
run.bat

# Windows - PowerShell (moderno)
.\run.ps1

# Ou via NPM
npm run dev
# ou
npm start
```

**Características:**
- ✅ 1 único terminal
- ✅ Logs coloridos por serviço
- ✅ Fácil de acompanhar
- ✅ Ctrl+C encerra tudo

**Saída:**
```
[BACKEND]  2024-01-15 10:30:00 - INFO - Application startup
[FRONTEND] VITE v5.0.0  ready in 543 ms
[BACKEND]  2024-01-15 10:30:01 - INFO - Uvicorn running on http://0.0.0.0:8000
[FRONTEND] ➜  Local:   http://localhost:3000/
```

---

### 2️⃣ Modo com Logs Agregados - 2 Terminais

```bash
run-with-logs.bat
```

**Características:**
- ✅ Terminal 1: Sistema (Backend + Frontend)
- ✅ Terminal 2: Logs agregados de todos os arquivos
- ✅ Visualização em tempo real de:
  - 📊 Logs de aplicação
  - 🌐 Logs de API
  - 🔒 Logs de segurança
  - 💬 Logs de chat
  - ❌ Logs de erros

**Terminal de Logs mostra:**
```
[APP     ] 2024-01-15T10:30:00.123Z INFO     Application started
[API     ] 2024-01-15T10:30:01.456Z INFO     GET /api/v1/health - 200
[SECURITY] 2024-01-15T10:30:05.789Z INFO     User logged in
[CHAT    ] 2024-01-15T10:30:10.012Z INFO     Chat interaction
[ERROR   ] 2024-01-15T10:30:15.345Z ERROR    Database connection failed
```

---

### 3️⃣ Modo Manual (Avançado)

```bash
# 1. Limpar portas e processos
npm run clean

# 2. Limpar apenas portas
npm run clean:port

# 3. Iniciar sistema
npm run dev

# 4. Visualizar logs (terminal separado)
npm run logs
```

---

## 🔧 Scripts NPM Disponíveis

| Script | Descrição |
|--------|-----------|
| `npm run dev` | Inicia Backend + Frontend em 1 terminal |
| `npm start` | Alias para `npm run dev` |
| `npm run clean` | Limpa processos e cache |
| `npm run clean:processes` | Mata processos Python e Node |
| `npm run clean:cache` | Limpa cache Python |
| `npm run clean:port` | Libera portas 8000 e 3000 |
| `npm run logs` | Visualiza logs agregados |
| `npm run logs:api` | Visualiza logs de API |
| `npm run logs:errors` | Visualiza logs de erros |
| `npm run logs:security` | Visualiza logs de segurança |

---

## 🎨 Cores dos Logs

### Terminal Principal (concurrently)
- 🔵 **BACKEND** - Azul em negrito
- 🟢 **FRONTEND** - Verde em negrito

### Visualizador de Logs
- 🔷 **APP** - Ciano
- 🟢 **API** - Verde
- 🔴 **ERROR** - Vermelho
- 🟡 **SECURITY** - Amarelo
- 🟣 **CHAT** - Magenta

### Níveis de Log
- 🟢 **INFO** - Verde
- 🟡 **WARN** - Amarelo
- 🔴 **ERROR** - Vermelho
- ⚪ **DEBUG** - Branco (dim)

---

## 🛠️ Tecnologia Utilizada

### Concurrently
Ferramenta recomendada pelo Context7 para executar múltiplos processos:

- ✅ **Alto desempenho**: Executa processos em paralelo
- ✅ **Saídas organizadas**: Prefixos coloridos automáticos
- ✅ **Kill-on-error**: Encerra todos se um falhar
- ✅ **Cross-platform**: Funciona em Windows, Linux, Mac
- 🏆 **Reputation**: High
- 📊 **42 code snippets** disponíveis
- 🔗 [Documentação](https://github.com/open-cli-tools/concurrently)

---

## 📁 Estrutura de Arquivos

```
Agent_Solution_BI/
├── run.bat                  # Novo launcher simplificado (1 terminal)
├── run.ps1                  # Launcher PowerShell moderno
├── run-with-logs.bat        # Launcher com logs agregados (2 terminais)
├── run.bat.old              # Backup do launcher antigo
├── package.json             # Scripts NPM e dependências
├── scripts/
│   ├── clean-port.js        # Limpa portas 8000 e 3000
│   └── show-logs.js         # Visualizador de logs agregado
└── logs/                    # Diretório de logs
    ├── app/
    ├── api/
    ├── security/
    ├── chat/
    ├── errors/
    └── audit/
```

---

## 🚨 Troubleshooting

### Porta já em uso

```bash
# Limpar portas manualmente
npm run clean:port

# Ou verificar e matar processos
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### Processos não encerram

```bash
# Limpar todos os processos
npm run clean

# Ou manualmente
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Logs não aparecem

```bash
# Verificar se diretórios existem
ls logs/

# Criar manualmente se necessário
mkdir -p logs/{app,api,security,chat,errors,audit}

# Reiniciar sistema
npm run dev
```

### Concurrently não instalado

```bash
# Instalar dependências
npm install

# Ou instalar manualmente
npm install -D concurrently
```

---

## 💡 Dicas de Uso

### 1. Desenvolvimento Diário

Use o modo padrão para desenvolvimento:
```bash
run.bat
```

### 2. Debugging de Problemas

Use o modo com logs para debugging:
```bash
run-with-logs.bat
```

### 3. Monitorar Erros

Abra terminal dedicado para erros:
```bash
npm run logs:errors
```

### 4. Análise de Segurança

Monitore eventos de segurança:
```bash
npm run logs:security
```

### 5. Performance

Monitore logs de API para performance:
```bash
npm run logs:api
```

---

## 🔄 Comparação: Antes vs Depois

### Antes (run.bat.old)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Terminal 1 │  │  Terminal 2 │  │  Terminal 3 │
│   Backend   │  │  Frontend   │  │  Navegador  │
└─────────────┘  └─────────────┘  └─────────────┘
     ❌              ❌              ❌
   Separado       Separado         Abre sozinho
```

### Depois (run.bat)

```
┌───────────────────────────────┐
│       Terminal Único          │
│  ┌─────────┐  ┌─────────┐    │
│  │ Backend │  │Frontend │    │
│  │ (azul)  │  │(verde)  │    │
│  └─────────┘  └─────────┘    │
└───────────────────────────────┘
           ✅
    Tudo junto e colorido
```

---

## 📊 Benefícios Mensuráveis

- ⏱️ **67% menos janelas** (3 → 1)
- 🎯 **100% mais fácil** de acompanhar (cores + prefixos)
- 🔄 **Encerramento instantâneo** (1 Ctrl+C vs fechar 3 janelas)
- 📈 **Produtividade aumentada** (menos alternância de janelas)
- 🎨 **Melhor DX** (Developer Experience)

---

## 🎓 Próximos Passos

1. ✅ Usar `run.bat` para iniciar o sistema
2. ✅ Experimentar `run-with-logs.bat` para ver logs agregados
3. ✅ Familiarizar-se com os scripts NPM
4. ✅ Usar `npm run logs` quando precisar debug detalhado

---

## 📚 Referências

- [Concurrently Documentation](https://github.com/open-cli-tools/concurrently)
- [Context7 Analysis](https://context7.com)
- [Sistema de Logging](./SISTEMA_LOGGING.md)

---

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique a seção Troubleshooting acima
2. Consulte `SISTEMA_LOGGING.md` para logs
3. Consulte `LOGGING_QUICK_START.md` para referência rápida

---

**Desenvolvido com ❤️ usando melhores práticas do Context7**
