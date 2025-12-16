# Code Chat - Agente Fullstack Completo

## 🎯 O que é?

Um **agente de IA fullstack** que pode responder qualquer pergunta sobre seu projeto usando RAG (Retrieval-Augmented Generation) com Gemini 2.5 Flash.

## ✨ Funcionalidades

- 🔍 **Busca Semântica** - Encontra código relevante em todo o projeto
- 💬 **Chat Inteligente** - Responde perguntas sobre arquitetura, funções, classes
- 📊 **Referências de Código** - Mostra trechos relevantes com scores
- 🎨 **UI Context7** - Interface moderna com KPIs e sidebar
- ⚡ **Performance** - Custo ~$0.0003 por consulta

---

## 📦 Instalação

### 1. Instalar Dependências Backend

```bash
cd backend
pip install -r requirements-code-chat.txt
```

**Dependências:**
- `llama-index-core` - Framework RAG
- `llama-index-llms-gemini` - Integração Gemini
- `llama-index-embeddings-gemini` - Embeddings
- `llama-index-vector-stores-faiss` - Vector store
- `faiss-cpu` - Busca vetorial

### 2. Configurar GEMINI_API_KEY

Edite `backend/.env`:
```bash
GEMINI_API_KEY="sua_chave_aqui"
```

Obtenha em: https://makersuite.google.com/app/apikey

### 3. Gerar Índice de Código

```bash
python scripts/index_codebase.py
```

**O que faz:**
- Indexa todo código Python e TypeScript
- Gera embeddings com Gemini
- Cria índice FAISS em `./storage/`
- Tempo: ~5-10 minutos (primeira vez)

**Output esperado:**
```
🚀 Code Indexer - Generating RAG Index
📂 Loading code files...
  Scanning: backend/app
  Scanning: frontend-solid/src
✅ Loaded 250 files
   Total lines: 45,000
   Functions: 1,200
   Classes: 180
🔨 Creating FAISS index...
✅ Index saved to ./storage
✅ Indexing complete!
```

---

## 🚀 Uso

### 1. Iniciar Sistema

```bash
# Na raiz do projeto
npm run dev
```

Ou use o `start.bat` (Windows).

### 2. Acessar Code Chat

1. Faça login como **admin**
2. Navegue para: http://localhost:3000/code-chat
3. Faça perguntas sobre o código!

### 3. Exemplos de Perguntas

**Estrutura:**
- "Quais são os principais módulos do backend?"
- "Qual é a estrutura do diretório frontend-solid/src?"

**Funcionalidades:**
- "Como funciona o sistema de autenticação?"
- "Onde está implementado o cache de respostas?"
- "Como o chat processa mensagens?"

**Código Específico:**
- "Quais funções existem em llm_adapter.py?"
- "Mostre a classe User do backend"
- "Como funciona o componente Chat.tsx?"

**Debugging:**
- "Onde pode estar o bug no login?"
- "Por que o frontend não conecta ao backend?"

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────┐
│  Frontend (SolidJS)                         │
│  ┌────────────────────────────────────┐    │
│  │ CodeChat.tsx                       │    │
│  │ - UI Context7                      │    │
│  │ - KPIs Header                      │    │
│  │ - Sidebar com exemplos             │    │
│  │ - Exibição de referências          │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                    ↓ HTTP POST
┌─────────────────────────────────────────────┐
│  Backend (FastAPI)                          │
│  ┌────────────────────────────────────┐    │
│  │ /api/v1/code-chat/query            │    │
│  │ - Valida mensagem                  │    │
│  │ - Chama CodeRAGService             │    │
│  └────────────────────────────────────┘    │
│  ┌────────────────────────────────────┐    │
│  │ CodeRAGService                     │    │
│  │ - Lazy loading do índice           │    │
│  │ - Busca semântica (FAISS)          │    │
│  │ - Gera resposta (Gemini)           │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Storage (./storage/)                       │
│  - FAISS Index (embeddings)                 │
│  - index_stats.json (metadados)             │
└─────────────────────────────────────────────┘
```

---

## 💰 Custos

### Indexação (uma vez)
- ~50M tokens para embeddings
- Custo: **$5-10** (única vez)

### Consultas
- Input: ~2K-10K tokens
- Output: ~500-2K tokens
- Custo: **$0.0003-0.002** por consulta

### Mensal (estimativa)
- 10-20 consultas/dia: **$0.10-0.50/mês**
- 50-100 consultas/dia: **$0.50-2.00/mês**
- 200-500 consultas/dia: **$2.00-10.00/mês**

**Conclusão:** Muito barato! 💰

---

## 🔧 Manutenção

### Reindexar Código

Quando adicionar/modificar muito código:

```bash
python scripts/index_codebase.py
```

**Quando reindexar:**
- Após grandes refatorações
- Novos módulos adicionados
- A cada 1-2 semanas (opcional)

### Limpar Índice

```bash
rm -rf storage/
python scripts/index_codebase.py
```

---

## 🐛 Troubleshooting

### Erro: "GEMINI_API_KEY not configured"
**Solução:** Configure a chave em `backend/.env`

### Erro: "Índice não disponível"
**Solução:** Execute `python scripts/index_codebase.py`

### Erro: "Missing dependencies"
**Solução:** `pip install -r requirements-code-chat.txt`

### Respostas ruins/irrelevantes
**Solução:** 
1. Reindexe o código
2. Faça perguntas mais específicas
3. Aumente `similarity_top_k` em `code_rag_service.py`

---

## 📝 Próximas Melhorias

- [ ] Suporte a mais linguagens (Java, Go, etc.)
- [ ] Filtros por diretório/linguagem
- [ ] Navegação para arquivo completo
- [ ] Syntax highlighting nos trechos
- [ ] Sugestões automáticas de perguntas
- [ ] Exportar conversas
- [ ] Cache de embeddings

---

## 🎓 Recursos

- **LlamaIndex:** https://docs.llamaindex.ai/
- **Gemini API:** https://ai.google.dev/
- **FAISS:** https://github.com/facebookresearch/faiss

---

**Versão:** 1.0.0  
**Data:** 2025-12-15  
**Autor:** Antigravity AI
