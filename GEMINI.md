# GEMINI.md

## Visão Geral do Projeto

Este projeto, "Agent BI", é uma plataforma de business intelligence conversacional. Ele permite que os usuários interajam com dados de negócios usando linguagem natural. A aplicação é construída com Python e possui uma interface de usuário baseada em Streamlit, um backend FastAPI e se integra com Modelos de Linguagem Grandes (LLMs) como o GPT da OpenAI. O sistema pode se conectar a bancos de dados SQL Server e também trabalhar com arquivos Parquet.

O projeto é projetado com uma arquitetura modular, separando a lógica principal, a interface do usuário e os serviços de backend. Ele usa uma abordagem baseada em grafos com `langgraph` para gerenciar o fluxo conversacional e as tarefas do agente. O projeto também inclui recursos como um painel personalizável, gerenciamento de catálogo de dados, autenticação de usuário e monitoramento do sistema.

**Tecnologias Chave:**

*   **Backend:** Python, FastAPI, LangChain, LangGraph, SQLAlchemy
*   **Frontend:** Streamlit
*   **Dados:** Pandas, PyArrow, Parquet, SQL Server
*   **IA/LLM:** OpenAI, Sentence-Transformers, FAISS
*   **Implantação:** Streamlit Cloud, Docker (planejado)

## Compilando e Executando

### Desenvolvimento Local

1.  **Pré-requisitos:**
    *   Python 3.9+
    *   Git

2.  **Clone o repositório:**
    ```bash
    git clone <url_do_repositorio>
    cd Agent_Solution_BI
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto, baseado no arquivo `.env.example`. Preencha suas credenciais e configurações, por exemplo:
    ```
    OPENAI_API_KEY=sua_chave_aqui
    MSSQL_SERVER=seu_servidor_sql
    MSSQL_DATABASE=seu_banco_de_dados
    MSSQL_USER=seu_usuario
    MSSQL_PASSWORD=sua_senha
    DB_DRIVER={ODBC Driver 17 for SQL Server}
    ```

6.  **Execute a aplicação:**

    *   **Aplicação Principal (Múltiplas Páginas):**
        ```bash
        streamlit run streamlit_app.py
        ```

    *   **Backend FastAPI (API Gateway):**
        ```bash
        uvicorn main:app --reload
        ```

### Implantação (Streamlit Cloud)

O projeto é otimizado para implantação na Streamlit Cloud.

1.  **Repositório:** `https://github.com/devAndrejr/Agents_Solution_Business`
2.  **Branch:** `main`
3.  **Caminho do arquivo principal:** `streamlit_app.py`
4.  **Secrets:** Configure os seguintes segredos no painel da Streamlit Cloud:
    ```toml
    OPENAI_API_KEY = "sk-sua-chave-openai-aqui"
    LLM_MODEL_NAME = "gpt-4o"
    DB_SERVER = "seu-servidor-sql.database.windows.net"
    DB_NAME = "Projeto_Caculinha"
    DB_USER = "AgenteVirtual"
    DB_PASSWORD = "sua-senha-segura"
    DB_DRIVER = "ODBC Driver 17 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE = "yes"
    ```

## Convenções de Desenvolvimento

*   **Arquitetura:** O projeto segue uma arquitetura modular com uma clara separação de responsabilidades. O diretório `core` contém a lógica de negócios principal, incluindo agentes, conectividade com o banco de dados e adaptadores de LLM. O diretório `pages` contém as páginas do Streamlit e o diretório `api` contém o backend FastAPI.
*   **Gerenciamento de Estado:** O fluxo conversacional é gerenciado por uma máquina de estados construída com `langgraph`. O estado do agente é definido em `core/agent_state.py`.
*   **Configuração:** O projeto usa um sistema de configuração baseado em `pydantic-settings` com um mecanismo de fallback para carregar configurações de variáveis de ambiente, arquivos `.env` e valores padrão.
*   **Autenticação:** A autenticação do usuário é tratada pelo módulo `core/auth.py`, com um mecanismo de carregamento lento (lazy-loading) para melhorar o desempenho.
*   **Acesso a Dados:** Os dados são acessados através de um `ParquetAdapter` para arquivos Parquet e um adaptador baseado em SQLAlchemy para SQL Server.
*   **Testes:** O diretório `tests` contém testes para vários componentes da aplicação.
*   **Implantação:** O projeto é projetado para fácil implantação na Streamlit Cloud, com um arquivo `DEPLOY_STREAMLIT_CLOUD.md` dedicado que fornece instruções detalhadas.
*   **Estilo de Código:** O código segue as convenções padrão do Python (PEP 8).