# Agent BI: Assistente de Inteligência de Negócios Conversacional

> Última atualização: Setembro/2025

## 🚀 Descrição do Projeto

O **Agent BI** é uma plataforma de **business intelligence conversacional** que permite interação com dados de negócio em **linguagem natural**.  
Construído em **Python** com **Streamlit (frontend)** e **FastAPI (backend)**, integra-se a **LLMs (OpenAI, Sentence-Transformers)**, bancos de dados **SQL Server** e arquivos **Parquet**.

A aplicação é modular, separando a lógica de negócio, interface do usuário e backend. Conta com:
- **Chat de BI conversacional**
- **Dashboards personalizáveis**
- **Gestão de catálogo de dados**
- **Painel de administração e monitoramento**
- **Conexão com SQL Server e Parquet**
- **Autenticação de usuário**
- **Arquitetura baseada em grafos com `langgraph`**

---

## 🛠️ Tecnologias Principais

- **Backend:** Python, FastAPI, LangChain, LangGraph, SQLAlchemy  
- **Frontend:** Streamlit  
- **Dados:** Pandas, PyArrow, Parquet, SQL Server  
- **IA/LLM:** OpenAI, Sentence-Transformers, FAISS  
- **Implantação:** Streamlit Cloud, Docker (em planejamento)  

---

## ⚙️ Setup (Desenvolvimento Local)

### 1. Pré-requisitos
- Python 3.9+
- Git

### 2. Clone o repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd Agent_Solution_BI
3. Crie e ative o ambiente virtual
bash
Copiar código
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
4. Instale as dependências
bash
Copiar código
pip install -r requirements.txt
5. Configure variáveis de ambiente
Crie um arquivo .env baseado no .env.example:

env
Copiar código
OPENAI_API_KEY=sua_chave_aqui
MSSQL_SERVER=seu_servidor_sql
MSSQL_DATABASE=seu_banco_de_dados
MSSQL_USER=seu_usuario
MSSQL_PASSWORD=sua_senha
DB_DRIVER={ODBC Driver 17 for SQL Server}
6. Execute a aplicação
App Principal (multi-páginas):

bash
Copiar código
streamlit run streamlit_app.py
Backend FastAPI (API Gateway):

bash
Copiar código
uvicorn main:app --reload
🧪 Testes
Rodar testes unitários e de integração:

bash
Copiar código
pytest
Gerar relatório de cobertura:

bash
Copiar código
coverage run -m pytest && coverage report
📂 Estrutura do Projeto
rust
Copiar código
core/       -> lógica principal (agentes, banco, LLMs)
pages/      -> páginas do Streamlit
api/        -> backend FastAPI
scripts/    -> utilitários de dados e automação
data/       -> catálogos e arquivos estáticos
tests/      -> suíte de testes
🔐 Convenções de Desenvolvimento
Código segue PEP 8

Estado do agente gerenciado com langgraph

Configuração via pydantic-settings + .env

Autenticação em core/auth.py

Deploy otimizado para Streamlit Cloud

☁️ Implantação (Streamlit Cloud)
Repositório: https://github.com/devAndrejr/Agents_Solution_Business

Branch: main

Arquivo principal: streamlit_app.py

Secrets necessários (exemplo):

toml
Copiar código
OPENAI_API_KEY = "sk-sua-chave"
LLM_MODEL_NAME = "gpt-4o"
DB_SERVER = "servidor-sql.database.windows.net"
DB_NAME = "Projeto_Caculinha"
DB_USER = "AgenteVirtual"
DB_PASSWORD = "senha"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_TRUST_SERVER_CERTIFICATE = "yes"