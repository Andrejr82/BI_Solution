# Agent Solution BI - Quick Start Guide

## Iniciar o Sistema Completo (1 Comando)

### Windows (Duplo Clique)
```
Duplo clique em: RUN.bat
```

### Windows/Linux/Mac (Terminal)
```bash
python run.py
```

---

## O Que Acontece?

O launcher `run.py` inicia **automaticamente** toda a stack:

1. **Backend FastAPI** (port 8000) - Inicialização em ~10s
   - API REST com documentação automática
   - Conexão com LLM (Gemini 2.5 Flash)
   - Acesso aos dados Parquet/SQL Server
   - Health checks automáticos

2. **Frontend React** (port 3000) - Inicialização em ~30s
   - Interface moderna Next.js 16
   - Chat conversacional com BI
   - Gráficos interativos Plotly
   - Hot reload em desenvolvimento

---

## URLs de Acesso

Após inicialização bem-sucedida:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend React** | http://localhost:3000 | Interface principal do usuário |
| **Chat BI** | http://localhost:3000/chat | Consultas em linguagem natural |
| **Backend API** | http://localhost:8000 | API REST FastAPI |
| **API Docs (Swagger)** | http://localhost:8000/docs | Documentação interativa da API |
| **API ReDoc** | http://localhost:8000/redoc | Documentação alternativa |

---

## Opções de Inicialização

### Modo Completo (Padrão)
Inicia backend + frontend:
```bash
python run.py
```

### Apenas Backend
Para desenvolvimento do backend ou uso via API:
```bash
python run.py --backend-only
```

Acesse: http://localhost:8000/docs

### Apenas Frontend
Se o backend já está rodando em outro terminal:
```bash
python run.py --frontend-only
```

### Modo Desenvolvimento (Logs Verbosos)
Para debug e troubleshooting:
```bash
python run.py --dev
```

---

## Primeira Consulta

### Via Interface Web (Recomendado)
1. Acesse: http://localhost:3000/chat
2. Digite sua pergunta:
   ```
   Mostre as vendas por região dos últimos 3 meses
   ```
3. O sistema irá:
   - Classificar a intenção (Gemini)
   - Gerar query nos dados (Parquet/SQL)
   - Criar visualização Plotly
   - Retornar resposta em linguagem natural

### Via API (cURL)
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vendas por região último trimestre",
    "user_id": "teste"
  }'
```

### Via Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analytics/query",
    json={
        "query": "Vendas totais por mês",
        "user_id": "teste"
    }
)

result = response.json()
print(result["text"])          # Resposta em texto
print(result["plotly_spec"])   # Especificação do gráfico
print(result["retrieved_data"]) # Dados brutos
```

---

## Encerrando o Sistema

### Método Graceful (Recomendado)
Pressione `Ctrl+C` no terminal onde rodou `run.py`

O launcher irá:
1. Capturar o sinal de interrupção
2. Encerrar frontend gracefully (5s timeout)
3. Encerrar backend gracefully (5s timeout)
4. Forçar encerramento se necessário
5. Exibir tempo de uptime

### Método Forçado
Se `Ctrl+C` não funcionar:

**Windows:**
```bash
# Encontrar PIDs
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Matar processos
taskkill /PID <pid> /F
```

**Linux/Mac:**
```bash
# Encontrar PIDs
lsof -i :8000
lsof -i :3000

# Matar processos
kill -9 <pid>
```

---

## Logs e Monitoramento

### Durante Execução
O launcher exibe logs consolidados:

```
[13:45:30] ============================================================
[13:45:30] INICIANDO BACKEND FASTAPI (Prioridade Alta)
[13:45:30] ============================================================
[13:45:30] Executando: python main.py
[13:45:30] Diretório: C:\...\backend
[13:45:31] Backend iniciado (PID: 12345)
[13:45:35] Backend está respondendo na porta 8000
[13:45:35] Backend URL: http://localhost:8000
[13:45:35] API Docs: http://localhost:8000/docs
[13:45:35] ============================================================
[13:45:35] INICIANDO FRONTEND REACT (Prioridade Média)
[13:45:35] ============================================================
...
[13:46:05] Frontend está respondendo na porta 3000
[13:46:05] Frontend URL: http://localhost:3000
[13:46:05] ============================================================
[13:46:05] SISTEMA INICIADO COM SUCESSO!
[13:46:05] ============================================================
[13:46:05] Tempo de inicialização: 35.21s
```

### Logs de Aplicação
Logs detalhados ficam em:
- Backend: `backend/logs/` (se configurado)
- Core: `logs/` (LLM, queries, cache)

---

## Troubleshooting

### Porta 8000 em Uso
```
[ERROR] Porta 8000 já está em uso!
```

**Solução:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

### Porta 3000 em Uso
```
[ERROR] Porta 3000 já está em uso!
```

**Solução:** Mesmo processo acima, mas para porta 3000

### Frontend Não Compila
```
[WARNING] Frontend não respondeu a tempo
[INFO] Pode estar ainda compilando. Aguarde mais alguns segundos.
```

**Causa:** Next.js demora ~30-60s na primeira compilação
**Solução:** Aguarde. Acesse http://localhost:3000 manualmente após 1 minuto

### Dependências do Frontend Faltando
```
[WARNING] node_modules não encontrado. Executando npm install...
```

**Solução:** O launcher instala automaticamente. Se falhar:
```bash
cd frontend-react
pnpm install  # ou npm install
```

### Backend Não Inicia
```
[ERROR] Erro ao iniciar backend: ...
```

**Verificações:**
1. Python 3.11+ instalado? `python --version`
2. Dependências instaladas? `pip install -r requirements.txt`
3. `.env` configurado? Veja `.env` na raiz do projeto

### Gemini API Não Responde
**Verificações:**
1. `.env` tem `GEMINI_API_KEY` configurado?
2. Chave é válida? Teste em: https://aistudio.google.com
3. Quota disponível?
4. Sistema automaticamente usa fallback DeepSeek se Gemini falhar

---

## Requisitos do Sistema

### Obrigatórios
- **Python**: 3.11 ou superior
- **Node.js**: 20+ (para frontend React)
- **RAM**: Mínimo 4GB, recomendado 8GB
- **Disco**: ~2GB livre (dependências + dados)

### Opcionais
- **pnpm**: Mais rápido que npm (instalável via `npm install -g pnpm`)
- **SQL Server**: Apenas se usar fallback SQL (configurado no `.env`)

---

## Estrutura de Diretórios

```
Agent_Solution_BI/
├── run.py                # ⭐ LAUNCHER PRINCIPAL
├── RUN.bat              # ⭐ LAUNCHER WINDOWS (duplo clique)
├── QUICKSTART.md        # Este arquivo
├── .env                 # Configurações (Gemini API, DB, etc)
│
├── backend/             # Backend FastAPI (port 8000)
│   ├── main.py         # Entry point FastAPI
│   └── app/            # Código da API
│
├── frontend-react/      # Frontend React (port 3000)
│   ├── package.json    # Dependências Node
│   └── src/            # Código React/Next.js
│
├── core/                # Business Logic Compartilhado
│   ├── agents/         # LangGraph AI agents
│   ├── connectivity/   # Data adapters (Parquet/SQL)
│   └── llm_adapter.py  # Interface com Gemini/DeepSeek
│
├── data/                # Dados e cache
│   ├── *.parquet       # Arquivos de dados
│   └── cache/          # Cache de respostas (6h TTL)
│
└── logs/                # Logs do sistema
```

---

## Próximos Passos

1. ✅ Inicie o sistema: `python run.py` ou duplo clique em `RUN.bat`
2. ✅ Acesse o frontend: http://localhost:3000/chat
3. ✅ Faça sua primeira pergunta em linguagem natural
4. ✅ Explore a API: http://localhost:8000/docs
5. ✅ Veja os logs em tempo real no terminal

**Divirta-se explorando seus dados com BI conversacional!** 🚀

---

## Suporte

- **Documentação Completa**: `docs/README.md`
- **Arquitetura**: `CLAUDE.md`
- **Issues**: GitHub Issues do projeto
- **Logs**: Verifique `logs/` para debug

---

**Última atualização**: 2025-11-23
**Versão do Sistema**: 3.1.0 (React + FastAPI + Extended Thinking)
