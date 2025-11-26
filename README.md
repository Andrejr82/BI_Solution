
# Agent Solution BI

**Uma interface de Business Intelligence conversacional com tecnologia Gemini.**

Este projeto é uma aplicação full-stack que combina um frontend moderno em React com um backend robusto em FastAPI. Ele permite que os usuários façam perguntas em linguagem natural e obtenham respostas e visualizações de dados a partir de um conjunto de dados analíticos.

## arquitetura

*   **Frontend**: React (Next.js) com TypeScript, usando Axios para comunicação com a API.
*   **Backend**: FastAPI com Python, Pydantic para validação de dados e SQLAlchemy para interação com o banco de dados.
*   **Banco de Dados**: SQL Server para autenticação e metadados, e arquivos Parquet para os dados analíticos principais.
*   **Modelo de Linguagem**: Google Gemini 2.5 Flash.

## 🚀 Como Executar o Projeto

Siga os passos abaixo para executar o projeto em seu ambiente de desenvolvimento.

### Pré-requisitos

*   Python 3.11+
*   Node.js 20+
*   SQL Server com o driver "ODBC Driver 17 for SQL Server" instalado.

### Configurando o Ambiente Virtual

Para evitar conflitos de dependências e garantir um ambiente de desenvolvimento limpo, é altamente recomendável usar um ambiente virtual.

1.  **Crie o ambiente virtual:**
    Na raiz do projeto, execute o seguinte comando:
    ```bash
    python -m venv .venv
    ```

2.  **Ative o ambiente virtual:**
    *   No Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   No macOS e Linux:
        ```bash
        source .venv/bin/activate
        ```
    Você saberá que o ambiente está ativo quando o nome `(.venv)` aparecer no início do seu prompt de comando.

3.  **Instale as dependências dentro do ambiente virtual:**
    Com o ambiente ativo, instale as dependências do backend:
    ```bash
    pip install -r requirements.txt
    ```

#### Verificando a Instalação das Dependências

Se você suspeitar que as dependências não foram instaladas corretamente, você pode verificar de duas maneiras:

1.  **Listar os pacotes instalados:**
    Com o ambiente virtual ativo, execute o comando:
    ```bash
    pip list
    ```
    Isso mostrará todos os pacotes instalados no ambiente virtual. Você pode verificar se os pacotes do `requirements.txt` estão na lista.

2.  **Tentar instalar novamente:**
    Execute o comando de instalação novamente:
    ```bash
    pip install -r requirements.txt
    ```
    Se todos os pacotes já estiverem instalados, você verá a mensagem "Requirement already satisfied" para cada um deles. Se algum pacote estiver faltando, o `pip` tentará instalá-lo.

### ⚠️ Solução para o Problema de Inicialização do Backend

Durante a análise, foi identificado que o backend pode não iniciar corretamente se a variável de ambiente `DATABASE_URL` estiver configurada incorretamente no seu sistema.

**Causa Raiz:** Uma variável de ambiente `DATABASE_URL` pré-existente no sistema estava forçando o backend a usar uma configuração de banco de dados SQLite, o que causava um erro silencioso na inicialização.

**Solução:**

Você **deve garantir que a variável de ambiente `DATABASE_URL` não esteja definida** no terminal que você usa para executar o projeto.

**Como verificar e limpar a variável no Windows (PowerShell):**

1.  **Verifique se a variável está definida:**
    ```powershell
    $env:DATABASE_URL
    ```
    Se este comando retornar qualquer valor, você precisa limpá-lo.

2.  **Limpe a variável para a sessão atual do terminal:**
    ```powershell
    $env:DATABASE_URL = ""
    ```
    Ou, de forma mais explícita:
    ```powershell
    Remove-Item Env:DATABASE_URL
    ```

3.  **Para remover a variável permanentemente do sistema (requer privilégios de administrador):**
    ```powershell
    [System.Environment]::SetEnvironmentVariable("DATABASE_URL", $null, "Machine")
    ```
    Após remover a variável, reinicie o seu terminal.

### Passos para Execução

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Agent_Solution_BI
    ```

2.  **Configure o Backend:**
    *   Navegue até a pasta `backend`.
    *   Crie um arquivo chamado `.env` (você pode copiar o `.env.example`).
    *   No arquivo `.env`, adicione a seguinte linha para garantir que o SQL Server seja usado:
        ```
        USE_SQL_SERVER=True
        ```
    *   **Importante:** Certifique-se de que a `DATABASE_URL` definida em `backend/app/config/settings.py` aponta para o seu banco de dados SQL Server e que as credenciais estão corretas.

3.  **Instale as dependências:**
    *   **Backend:**
        ```bash
        pip install -r requirements.txt
        ```
    *   **Frontend:**
        ```bash
        cd frontend-react
        pnpm install
        ```

4.  **Execute o projeto:**
    *   Na raiz do projeto, execute o script `RUN.bat`:
        ```bash
        
        ```
    Este script irá:
    *   Verificar as dependências.
    *   Limpar processos antigos na porta 8000.
    *   Iniciar o backend FastAPI na porta 8000.
    *   Iniciar o frontend React na porta 3000.
    *   Abrir o navegador automaticamente em `http://localhost:3000`.

## 📝 TODO

- [ ] Adicionar mais testes de integração.
- [ ] Implementar um sistema de cache mais robusto com Redis.
- [ ] Expandir o suporte para mais tipos de visualizações de dados.
