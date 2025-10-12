# Agent BI: Plataforma de Business Intelligence Conversacional

![Status](https://img.shields.io/badge/status-ativo-green)
![Versão](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Frameworks](https://img.shields.io/badge/frameworks-Streamlit_|_FastAPI-orange)

O **Agent BI** é uma plataforma de business intelligence que permite aos usuários interagir com dados de negócios usando linguagem natural. Construído com Python, Streamlit para o frontend e FastAPI para o backend, o sistema se integra com LLMs (como Gemini e DeepSeek) e pode se conectar a bancos de dados SQL Server e arquivos Parquet.

## ✨ Funcionalidades Principais

- **Interface Conversacional**: Interaja com seus dados através de um chat, fazendo perguntas em português.
- **Visualização Dinâmica de Dados**: Gere gráficos e tabelas automaticamente a partir de suas perguntas.
- **Dashboard Personalizável**: Salve e organize os gráficos mais importantes em um dashboard pessoal.
- **Motor de Consulta Híbrido**: O sistema otimiza os custos usando um motor de consulta que prioriza cache e consultas diretas, utilizando LLMs apenas quando necessário.
- **Painel de Administração**: Gerencie usuários, permissões e monitore a saúde do sistema.
- **Diagnóstico e Testes**: Ferramentas integradas para diagnosticar problemas de conexão e testar a funcionalidade do sistema.

## 🏛️ Arquitetura

O projeto segue uma arquitetura modular, com uma separação clara entre a lógica de negócios, a interface do usuário e o backend.

- **Frontend**: Construído com **Streamlit**, localizado no diretório `pages` e no arquivo principal `streamlit_app.py`.
- **Backend**: Uma API **FastAPI** (`main.py`) serve como gateway para o núcleo do sistema.
- **Núcleo (`core/`)**: Contém a lógica de negócios, incluindo:
  - **`agents/`**: Agentes de IA especializados para diferentes tarefas.
  - **`business_intelligence/`**: O motor de consulta híbrido e o classificador de intenção.
  - **`connectivity/`**: Adaptadores para fontes de dados (SQL Server, Parquet).
  - **`graph/`**: O grafo de conversação (LangGraph) que orquestra o fluxo de trabalho.
- **Dados (`data/`)**: Armazena arquivos de dados, catálogos, templates e histórico de consultas.
- **Scripts (`scripts/`)**: Ferramentas de linha de comando para manutenção, testes e diagnóstico.
- **Testes (`tests/`)**: Testes automatizados para garantir a qualidade e a estabilidade do projeto.
- **Documentação (`docs/`)**: Documentação técnica, relatórios e guias.

## 🚀 Começando

Siga os passos abaixo para configurar e executar o projeto localmente.

### Pré-requisitos

- Python 3.11+
- Git

### 1. Clone o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Agent_Solution_BI
```

### 2. Crie e Ative o Ambiente Virtual

```bash
# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente
# No Windows:
.venv\Scripts\activate
# No macOS/Linux:
source .venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Copie o arquivo `.env.example` para um novo arquivo chamado `.env` e preencha com suas credenciais:

```env
# Chaves de API para os Modelos de Linguagem
GEMINI_API_KEY="sua_chave_gemini"
DEEPSEEK_API_KEY="sua_chave_deepseek"

# Modelo de Linguagem a ser usado
LLM_MODEL_NAME="gemini-2.5-flash"

# Configurações do Banco de Dados SQL Server (Opcional)
USE_SQL_SERVER=true
MSSQL_SERVER="seu_servidor"
MSSQL_DATABASE="seu_banco"
MSSQL_USER="seu_usuario"
MSSQL_PASSWORD="sua_senha"
```

### 5. Execute a Aplicação

Use o script de inicialização para executar o backend e o frontend na ordem correta:

```bash
# No Windows
start_app.bat

# No macOS/Linux
./start_app.sh
```

A aplicação estará disponível em `http://localhost:8501`.

## 🧪 Testando

O projeto inclui uma suíte de testes para garantir a qualidade e a estabilidade. Para executar os testes, use o `pytest`:

```bash
pytest
```

Você também pode executar scripts de diagnóstico individuais localizados no diretório `scripts/`, como:

```bash
# Verificar a saúde geral do sistema
python scripts/health_check.py

# Testar a conexão com o banco de dados
python scripts/test_hybrid_connection.py
```

## 📄 Documentação Adicional

Para mais detalhes sobre a arquitetura, guias de desenvolvimento e relatórios, consulte o diretório `docs/`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o nosso (futuro) `CONTRIBUTING.md` para saber como você pode participar.

## 📜 Licença

Este projeto é licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.