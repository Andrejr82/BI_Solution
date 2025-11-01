# Visão Geral do Projeto

Este projeto, **Agent BI**, é uma plataforma de business intelligence conversacional. Ele permite que os usuários interajam com dados de negócios usando linguagem natural. A aplicação é construída com Python, usando Streamlit para o frontend e FastAPI para o backend. Ele se integra com Modelos de Linguagem Grandes (LLMs) como Gemini e DeepSeek, e pode se conectar a bancos de dados SQL Server e arquivos Parquet.

A aplicação é modular, com uma separação clara entre a lógica de negócios, a interface do usuário e o backend. O núcleo da aplicação é um agente conversacional que pode responder a perguntas, gerar gráficos e fornecer insights de dados.

## Compilando e Executando

Para compilar e executar este projeto, siga estes passos:

1.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as variáveis de ambiente:**
    Copie o arquivo `.env.example` para um novo arquivo chamado `.env` e preencha as credenciais necessárias para os LLMs e o banco de dados SQL Server.

4.  **Execute a aplicação:**
    ```bash
    streamlit run streamlit_app.py
    ```
    A aplicação estará disponível em `http://localhost:8501`.

## Convenções de Desenvolvimento

*   **Arquitetura Modular:** O projeto segue uma arquitetura modular, com o código organizado nos diretórios `core`, `data`, `pages`, `scripts` e `tests`.
*   **Gerenciamento de Dependências:** O projeto usa `pip-compile` para gerenciar as dependências. O arquivo `requirements.in` lista as dependências diretas, e o arquivo `requirements.txt` é gerado a partir dele.
*   **Testes:** O projeto possui uma suíte de testes automatizados usando `pytest`. Os testes estão localizados no diretório `tests` e podem ser executados com o seguinte comando:
    ```bash
    pytest tests/
    ```
*   **Agente Conversacional:** O núcleo da aplicação é um agente conversacional construído com `langchain` e `langgraph`. A lógica do agente é definida em `core/graph/graph_builder.py` e `core/agents/bi_agent_nodes.py`.
*   **Frontend:** A interface do usuário é construída com `streamlit`. O arquivo principal da aplicação é `streamlit_app.py`, e páginas adicionais estão localizadas no diretório `pages`.
*   **Manipulação de Dados:** A aplicação pode ler dados tanto do SQL Server quanto de arquivos Parquet. O diretório `core/connectivity` contém os adaptadores para se conectar a essas fontes de dados.
