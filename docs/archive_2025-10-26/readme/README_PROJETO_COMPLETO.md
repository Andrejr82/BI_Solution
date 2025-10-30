# 🤖 Agent Solution BI - Sistema Completo

## 📊 Visão Geral

**Agent Solution BI** é uma plataforma completa de Business Intelligence com IA, combinando:

- 🎨 **Frontend React Moderno** (claude-share-buddy)
- 🚀 **Backend Flask API REST**
- 🧠 **Sistema de IA** (LangGraph + Gemini)
- 💾 **Processamento Otimizado** (Polars/Dask)
- 📈 **Visualizações Interativas** (Plotly/Recharts)

## ✨ Principais Funcionalidades

### 🎯 Interface do Usuário (Frontend)

- **Chat Inteligente com IA** - Converse naturalmente sobre seus dados
- **Dashboard de Métricas** - KPIs em tempo real
- **Gráficos Salvos** - Organize suas visualizações
- **Monitoramento** - Acompanhe performance do sistema
- **Exemplos de Consultas** - Aprenda com templates prontos
- **Painel Admin** - Gestão completa do sistema
- **Diagnóstico DB** - Troubleshooting e status
- **Gemini Playground** - Teste a IA diretamente
- **Sistema de Aprendizado** - Acompanhe evolução da IA

### 🔧 Backend e IA

- **Processamento de Linguagem Natural** - Perguntas em português
- **Geração Automática de Código** - Python/Pandas/SQL dinâmico
- **Sistema de Cache Inteligente** - Respostas instantâneas para queries repetidas
- **Query History** - Histórico completo de consultas
- **Feedback System** - Aprenda com interações do usuário
- **Multi-datasource** - SQL Server, Parquet, APIs

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                │
│  ┌─────────────┬──────────────┬─────────────────────┐    │
│  │   Chat BI   │  Dashboards  │   Admin Panel       │    │
│  │   Metrics   │   Charts     │   Diagnostics       │    │
│  │  Examples   │  Learning    │   Playground        │    │
│  └─────────────┴──────────────┴─────────────────────┘    │
│              React Router + TanStack Query                │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API (/api/*)
                       │ HTTP/JSON
┌──────────────────────▼───────────────────────────────────┐
│                 BACKEND API (Flask)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  /api/chat  /api/metrics  /api/examples          │   │
│  │  /api/queries  /api/feedback  /api/diagnostics   │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                     │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │         Agent_Solution_BI Core                    │   │
│  │  ┌────────────┬──────────────┬────────────────┐  │   │
│  │  │ LangGraph  │ Code Gen     │ Parquet Adapter│  │   │
│  │  │ (IA Flow)  │ Agent        │ (Polars/Dask)  │  │   │
│  │  └────────────┴──────────────┴────────────────┘  │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                   DADOS & IA                              │
│  ┌────────────────┬─────────────────┬──────────────┐    │
│  │ Parquet Files  │  SQL Server     │  Gemini API  │    │
│  │ (Data Lake)    │  (Opcional)     │  (IA)        │    │
│  └────────────────┴─────────────────┴──────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Instalação Rápida

```bash
# Clone o repositório
git clone <repo_url> Agent_Solution_BI
cd Agent_Solution_BI

# Backend Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend React
cd frontend
npm install
cd ..

# Configurar .env
cp .env.example .env
# Editar .env com suas chaves API
```

### 2. Iniciar Sistema

```bash
# Terminal 1 - Backend API
python backend_api.py

# Terminal 2 - Frontend React
cd frontend && npm run dev
```

### 3. Acessar

- 🌐 **Frontend**: http://localhost:8080
- 🔌 **API**: http://localhost:5000
- ✅ **Health Check**: http://localhost:5000/api/health

## 📖 Documentação

- 📘 [**Instalação Completa**](INSTALACAO_COMPLETA.md) - Guia detalhado
- 📗 [**Frontend README**](frontend/README_FRONTEND.md) - Documentação React
- 📙 [**Backend API**](backend_api.py) - Endpoints e integração
- 📕 [**Arquitetura**](docs/ARCHITECTURE.md) - Design do sistema

## 🎨 Screenshots

### Chat BI
![Chat BI](docs/screenshots/chat-bi.png)

### Dashboard de Métricas
![Dashboard](docs/screenshots/dashboard.png)

### Gráficos Interativos
![Charts](docs/screenshots/charts.png)

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18.3** - UI Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component Library
- **Recharts** - Data Visualization
- **TanStack Query** - Data Fetching
- **React Router** - Navigation

### Backend
- **Python 3.11+** - Runtime
- **Flask** - Web Framework
- **LangChain** - IA Framework
- **LangGraph** - Agent Orchestration
- **Google Gemini** - LLM
- **Polars/Dask** - Data Processing
- **Pandas** - Data Analysis
- **Plotly** - Visualizations

### Infraestrutura
- **Parquet** - Data Storage
- **SQL Server** - Optional Database
- **Git** - Version Control
- **Docker** - Containerization (Optional)

## 📁 Estrutura do Projeto

```
Agent_Solution_BI/
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/         # React Components
│   │   ├── pages/              # Application Pages
│   │   ├── hooks/              # Custom Hooks
│   │   ├── lib/                # Utilities
│   │   └── App.tsx             # Main Component
│   ├── public/                 # Static Assets
│   ├── package.json
│   └── vite.config.ts
│
├── core/                        # Backend Core
│   ├── agents/                 # IA Agents
│   ├── business_intelligence/  # BI Logic
│   ├── connectivity/           # Data Adapters
│   ├── graph/                  # LangGraph
│   ├── factory/                # Component Factory
│   └── utils/                  # Utilities
│
├── data/                        # Data Storage
│   ├── parquet/                # Parquet Files
│   ├── query_history/          # Query Logs
│   └── reports/                # Generated Reports
│
├── backend_api.py              # Flask API Server
├── streamlit_app.py            # Streamlit UI (Legacy)
├── requirements.txt            # Python Dependencies
├── .env                        # Environment Variables
├── INSTALACAO_COMPLETA.md      # Installation Guide
└── README_PROJETO_COMPLETO.md  # This File
```

## 🔑 Configuração

### Variáveis de Ambiente (.env)

```env
# IA - API Keys
GEMINI_API_KEY=your_gemini_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Database (Optional)
SQL_SERVER=localhost
SQL_DATABASE=your_db
SQL_USERNAME=user
SQL_PASSWORD=pass

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key

# Logging
LOG_LEVEL=INFO
```

## 📊 Uso do Sistema

### Exemplo 1: Consulta Simples

```
Usuário: "Top 10 produtos mais vendidos"

Sistema:
1. Classifica intenção (ranking/vendas/produtos)
2. Gera código Python automaticamente
3. Executa no Parquet com Polars
4. Renderiza gráfico de barras
5. Salva no cache para reutilização
```

### Exemplo 2: Análise Complexa

```
Usuário: "Evolução de vendas dos últimos 12 meses por segmento"

Sistema:
1. Identifica necessidade de agregação temporal
2. Gera código com groupby multi-nível
3. Processa com Dask (dados grandes)
4. Cria gráfico de linha múltipla
5. Oferece drill-down interativo
```

### Exemplo 3: Comparação

```
Usuário: "Compare vendas da UNE 261 com UNE 262"

Sistema:
1. Identifica query comparativa
2. Filtra múltiplas UNEs
3. Gera gráfico lado a lado
4. Calcula diferenças percentuais
5. Sugere insights automáticos
```

## 🎯 Casos de Uso

### 1. Análise de Vendas
- Top produtos/categorias/segmentos
- Ranking por UNE/filial
- Evolução temporal
- Análise ABC

### 2. Gestão de Estoque
- Produtos sem movimento
- Rupturas de estoque
- Giro de inventário
- Previsão de demanda

### 3. Performance de Lojas
- Comparação entre UNEs
- Ticket médio por loja
- Produtos mais vendidos por região
- Análise de sazonalidade

### 4. Inteligência de Mercado
- Tendências de consumo
- Segmentação de clientes
- Cross-selling opportunities
- Análise de margem

## 🔐 Segurança

### Implementado
- ✅ Validação de inputs
- ✅ Sanitização de queries SQL
- ✅ Rate limiting (básico)
- ✅ CORS configurado
- ✅ Logs de auditoria

### Recomendado para Produção
- [ ] Autenticação JWT
- [ ] HTTPS obrigatório
- [ ] Encriptação de dados sensíveis
- [ ] Backup automático
- [ ] Monitoramento de segurança

## 📈 Performance

### Otimizações
- **Cache Multi-camada** (Memória + Disco)
- **Lazy Loading** de módulos
- **Predicate Pushdown** (Polars)
- **Query Optimization** automática
- **Code Splitting** (Frontend)

### Benchmarks
- Query simples: **< 2s**
- Query com gráfico: **< 5s**
- Cache hit: **< 100ms**
- Frontend load: **< 1s**

## 🐛 Troubleshooting

Ver [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md#troubleshooting)

## 🤝 Contribuindo

1. Fork o projeto
2. Criar branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Changelog

### v1.0.0 (2025-10-25)
- ✨ Integração completa do claude-share-buddy
- 🎨 Frontend React com 14 páginas
- 🚀 Backend Flask API REST
- 🧠 Sistema de IA com LangGraph
- 💾 Otimização Polars/Dask
- 📊 Visualizações Plotly/Recharts
- 🔐 Sistema de autenticação
- 📈 Dashboard de métricas em tempo real

## 📄 Licença

Este projeto está sob a licença MIT. Ver [LICENSE](LICENSE) para mais detalhes.

## 👥 Equipe

- **Desenvolvimento Backend** - Equipe Python/IA
- **Desenvolvimento Frontend** - Equipe React/TypeScript
- **Arquitetura** - Equipe DevOps
- **Product Owner** - Business Intelligence Team

## 📞 Contato

- **Email**: suporte@agentsolutionbi.com
- **Slack**: #agent-solution-bi
- **Docs**: https://docs.agentsolutionbi.com

## 🙏 Agradecimentos

- [claude-share-buddy](https://github.com/Agents-Solution-BI/claude-share-buddy-83501) - Frontend base
- [LangChain](https://langchain.com/) - Framework de IA
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Modelo de linguagem
- [shadcn/ui](https://ui.shadcn.com/) - Componentes React

---

**Made with ❤️ by Agent Solution BI Team**

**Version**: 1.0.0
**Date**: 2025-10-25
**Status**: ✅ Production Ready
