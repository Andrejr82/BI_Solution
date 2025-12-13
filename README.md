# Agent Solution BI

**Uma interface de Business Intelligence conversacional de alta performance com tecnologia Gemini.**

Este projeto é uma aplicação full-stack moderna que combina um frontend reativo em **SolidJS** com um backend robusto em **FastAPI**. Ele permite que os usuários interajam com dados analíticos complexos usando linguagem natural, recebendo respostas precisas, visualizações interativas e sugestões de negócio.

---

## 🏗️ Arquitetura

*   **Frontend**: [SolidJS](https://www.solidjs.com/) com TypeScript e TailwindCSS. Focado em performance extrema e reatividade fina. Utiliza `Plotly.js` para visualizações avançadas e `Axios` para comunicação eficiente com a API.
*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+). Implementa uma arquitetura modular com injeção de dependência, tratamento de erros centralizado e segurança robusta.
*   **Agentes de IA**: Sistema multi-agente orquestrado para BI:
    *   **CaculinhaBIAgent**: Roteamento inteligente e interpretação de intenção.
    *   **CodeGenAgent**: Geração e execução segura de código Python (Polars) para análise de dados, com auto-correção (Self-Healing).
*   **Dados**:
    *   **Parquet**: Arquivos columnar de alta performance para o dataset analítico principal.
    *   **SQL Server** (Opcional): Para autenticação corporativa e dados transacionais legados.
    *   **Supabase Auth**: Integração para autenticação moderna e segura.
*   **Otimizações**:
    *   **Caching Híbrido**: Cache em memória e disco para respostas de LLM e grafos de agentes.
    *   **RAG (Retrieval Augmented Generation)**: Sistema de aprendizado contínuo que indexa queries passadas bem-sucedidas para melhorar a precisão futura.
    *   **Streaming (SSE)**: Respostas em tempo real via Server-Sent Events.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

*   Python 3.11+
*   Node.js 20+
*   (Opcional) SQL Server com "ODBC Driver 17 for SQL Server".

### 1. Configuração do Backend

Recomendamos o uso de um ambiente virtual Python.

```bash
# Na raiz do projeto
python -m venv .venv

# Ativar ambiente
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Instalar dependências
pip install -r backend/requirements.txt
```

### 2. Configuração do Frontend

```bash
# Navegue para a pasta do frontend SolidJS
cd frontend-solid

# Instale as dependências
npm install 
# ou pnpm install / yarn install
```

### 3. Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/` baseado no `.env.example`. As variáveis críticas são:

```env
# Backend
PROJECT_NAME="Agent BI"
API_V1_STR="/api/v1"

# IA & Gemini
GEMINI_API_KEY="sua_chave_api_aqui"
LLM_MODEL_NAME="models/gemini-1.5-flash"

# Segurança
SECRET_KEY="gere_uma_chave_segura_aqui"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Cache & Dados
LEARNING_EXAMPLES_PATH="data/learning/"
LEARNING_FEEDBACK_PATH="data/feedback/"
```

### 4. Executando a Aplicação

Para iniciar todo o sistema (Backend + Frontend) em modo de desenvolvimento:

**Windows:**
Execute o script `run.bat` na raiz do projeto.

**Manual:**

Terminal 1 (Backend):
```bash
cd backend
python main.py
# O servidor iniciará em http://localhost:8000
```

Terminal 2 (Frontend):
```bash
cd frontend-solid
npm run dev
# O frontend iniciará em http://localhost:3000
```

---

## ✨ Funcionalidades Principais

*   **Chat BI Inteligente**: Converse com seus dados. O assistente entende perguntas sobre vendas, estoque, produtos e muito mais.
*   **Dashboards em Tempo Real**: Painéis de controle que se atualizam automaticamente com os dados mais recentes.
*   **Gestão de Transferências**: Sugestões automáticas de transferência de produtos entre unidades (UNEs) para evitar rupturas de estoque, baseadas em regras de negócio complexas.
*   **Análise de Rupturas**: Identificação proativa de produtos críticos com risco de falta.
*   **Gráficos Dinâmicos**: O agente pode gerar gráficos (barras, linhas, pizza, etc.) sob demanda dentro do chat.
*   **Exportação de Dados**: Baixe os resultados de suas análises em JSON ou CSV diretamente da interface.
*   **Feedback e Aprendizado**: O sistema aprende com o feedback do usuário (👍/👎), melhorando suas respostas ao longo do tempo via RAG.

## 🛡️ Segurança

*   **Autenticação Híbrida**: Suporte a Login via Supabase ou SQL Server/Parquet local.
*   **Mascaramento de Dados (PII)**: Dados sensíveis como CPF, e-mail e telefone são automaticamente mascarados nas respostas.
*   **Execução Segura**: O código gerado pela IA é executado em um ambiente controlado com limitações de escopo.
*   **Validação de Input**: Sanitização rigorosa de todas as entradas do usuário para prevenir injeções.

## 📝 TODO

- [ ] Containerização completa com Docker e Docker Compose.
- [ ] Testes E2E (End-to-End) com Cypress ou Playwright.
- [ ] Integração de métricas de performance com Prometheus/Grafana.
