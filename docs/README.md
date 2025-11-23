# 🤖 Agent Solution BI

##Sistema de Business Intelligence com IA - Multi-Interface

**3 Interfaces. 1 Backend. Infinitas Possibilidades.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 O Que É?

Agent Solution BI é uma plataforma completa de **Business Intelligence com Inteligência Artificial** que permite analisar dados através de **conversação em linguagem natural**.

**Pergunte em português, receba análises completas!**

```
Você: "Top 10 produtos mais vendidos"
IA:   📊 Gráfico de barras + tabela + insights automáticos
```

## ✨ Funcionalidades Principais

- 🗣️ **Chat com IA** - Perguntas em português, respostas inteligentes
- 📊 **Gráficos Automáticos** - Visualizações geradas pela IA
- 📈 **Dashboards Interativos** - Métricas em tempo real
- 💾 **Cache Inteligente** - Respostas instantâneas
- 📝 **Histórico Completo** - Todas suas análises salvas
- 🎨 **3 Interfaces** - Escolha a melhor para você

## 🚀 Quick Start (5 minutos)

```bash
# 1. Clone e instale
git clone <repo> Agent_Solution_BI
cd Agent_Solution_BI
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure (criar .env)
echo "GEMINI_API_KEY=sua_chave" > .env

# 3. Escolha sua interface:

# Opção A: React (Produção)
python api_server.py &
cd frontend && npm install && npm run dev

# Opção B: Streamlit (Dev/Demo)
streamlit run streamlit_app.py

# Opção C: API (Integração)
python api_server.py
```

**Pronto!** Acesse:
- React: http://localhost:8080
- Streamlit: http://localhost:8501
- API: http://localhost:5000/docs

## 🎨 3 Interfaces Disponíveis

### 1. 🎨 Frontend React - **Para Produção**

Interface moderna e profissional com **14 páginas**:

- Chat BI com IA
- Dashboard de Métricas
- Gráficos Salvos
- Monitoramento
- Painel Admin
- Diagnóstico DB
- Gemini Playground
- Sistema de Aprendizado
- E mais...

**Tecnologias**: React 18, TypeScript, Tailwind CSS, shadcn/ui

**Quando usar**: Produção, múltiplos usuários, interface profissional

### 2. ⚡ Streamlit - **Para Desenvolvimento**

Interface rápida para prototipagem e demos:

- Chat BI simplificado
- Gráficos Plotly
- Análises rápidas
- Zero configuração frontend

**Tecnologias**: Streamlit, Python puro

**Quando usar**: Protótipos, demos, desenvolvimento interno

### 3. 🔌 API FastAPI - **Para Integração**

Endpoints REST documentados:

- `/api/chat` - Processar mensagens
- `/api/metrics` - Obter métricas
- `/api/examples` - Exemplos de queries
- `/docs` - Documentação Swagger
- E mais...

**Tecnologias**: FastAPI, Uvicorn, Pydantic

**Quando usar**: Mobile apps, integrações, webhooks

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│     INTERFACES (Escolha uma ou mais)         │
├──────────────┬──────────────┬───────────────┤
│    React     │  Streamlit   │  Outras Apps  │
│  (Port 8080) │ (Port 8501)  │   (via API)   │
└──────┬───────┴──────┬───────┴───────┬───────┘
       │              │               │
       │         HTTP/REST         Python API
       │              │               │
┌──────▼──────────────▼───────────────▼───────┐
│          API FastAPI (Port 5000)             │
│              Backend Python                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│     LangGraph + Gemini + Polars/Dask        │
│            Parquet Data Lake                 │
└──────────────────────────────────────────────┘
```

## 📊 Exemplos de Uso

```
"Top 10 produtos mais vendidos"
→ Gráfico de barras + tabela

"Evolução de vendas dos últimos 12 meses"
→ Gráfico de linha temporal

"Compare vendas da UNE 261 com UNE 262"
→ Gráfico comparativo + análise

"Produtos sem movimento no último mês"
→ Tabela filtrada + alerta

"Análise ABC dos produtos"
→ Classificação + visualização
```

## 🛠️ Tecnologias

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **LangChain** - IA framework
- **LangGraph** - Agent orchestration
- **Google Gemini** - LLM
- **Polars/Dask** - Data processing
- **Pandas** - Data analysis

### Frontend React
- **React 18.3** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Components
- **Recharts** - Charts
- **TanStack Query** - State

### Infraestrutura
- **Parquet** - Data storage
- **Uvicorn** - ASGI server
- **Redis** - Cache (opcional)

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [QUICK_START_ATUALIZADO.md](QUICK_START_ATUALIZADO.md) | Início rápido (5 min) |
| [ARQUITETURA_MULTI_INTERFACE.md](ARQUITETURA_MULTI_INTERFACE.md) | Arquitetura completa |
| [frontend/README_FRONTEND.md](frontend/README_FRONTEND.md) | Docs do React |
| [api_server.py](api_server.py) | API FastAPI (docstrings) |
| [streamlit_app.py](streamlit_app.py) | Streamlit (comentários) |

## 🔧 Configuração

### Variáveis de Ambiente (`.env`)

```env
# Obrigatório
GEMINI_API_KEY=sua_chave_gemini

# Opcional
PORT=5000
HOST=0.0.0.0
SQL_SERVER=localhost  # Se usar SQL Server
SQL_DATABASE=db_name
SQL_USERNAME=user
SQL_PASSWORD=pass
```

## 🎯 Casos de Uso

- 📊 **Análise de Vendas** - Rankings, top produtos, comparações
- 📦 **Gestão de Estoque** - Rupturas, giro, previsões
- 🏪 **Performance de Lojas** - Comparações entre UNEs
- 🎯 **Inteligência de Mercado** - Tendências, segmentação
- 📈 **KPIs Executivos** - Dashboards gerenciais

## 🐛 Troubleshooting

### API não inicia?
```bash
pip install fastapi uvicorn
python api_server.py
```

### Frontend erro?
```bash
cd frontend
npm install
npm run dev
```

### Gemini API key?
Obter em: https://makersuite.google.com/app/apikey

### Mais ajuda?
Ver [ARQUITETURA_MULTI_INTERFACE.md](ARQUITETURA_MULTI_INTERFACE.md#troubleshooting)

## 🤝 Contribuindo

1. Fork o projeto
2. Criar branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📊 Roadmap

- [x] Backend com LangGraph + Gemini
- [x] Processamento Polars/Dask
- [x] API FastAPI completa
- [x] Frontend React (14 páginas)
- [x] Streamlit interface
- [x] Cache inteligente
- [x] Query history
- [ ] Autenticação JWT
- [ ] Deploy Docker
- [ ] Mobile app
- [ ] Análises preditivas

## 📄 Licença

MIT License - Ver [LICENSE](LICENSE)

## 👥 Equipe

**Agent Solution BI Team**
- Backend & IA
- Frontend & UX
- DevOps & Deploy

## 📞 Contato

- **Email**: suporte@agentsolutionbi.com
- **Docs**: https://docs.agentsolutionbi.com
- **Issues**: GitHub Issues

## 🙏 Agradecimentos

- [claude-share-buddy](https://github.com/Agents-Solution-BI/claude-share-buddy-83501) - Frontend base
- [LangChain](https://langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)

---

**Made with ❤️ by Agent Solution BI Team**

**Version**: 1.0.0 | **Date**: 2025-10-25 | **Status**: ✅ Production Ready

[⭐ Star us on GitHub](https://github.com/your-repo) | [📖 Read the Docs](ARQUITETURA_MULTI_INTERFACE.md) | [🚀 Quick Start](QUICK_START_ATUALIZADO.md)
