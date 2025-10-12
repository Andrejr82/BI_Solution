# Relatório de Estrutura do Projeto: Agent BI

## Visão Geral do Projeto

O Agent BI é uma plataforma de business intelligence conversacional que permite aos usuários interagir com dados de negócios usando linguagem natural. A aplicação é construída com Python, utilizando Streamlit para o frontend e FastAPI para o backend. Ele se integra com Modelos de Linguagem Grandes (LLMs) como Gemini e DeepSeek, e pode se conectar a bancos de dados SQL Server e arquivos Parquet.

A aplicação é modular, com uma separação clara entre a lógica de negócios, a interface do usuário e o backend. O núcleo da aplicação é um agente conversacional que pode responder a perguntas, gerar gráficos e fornecer insights de dados.

## Estrutura de Arquivos e Diretórios

A seguir, uma descrição das principais pastas e arquivos do projeto:

### Raiz do Projeto

*   `.env.example`: Arquivo de exemplo para configurar as variáveis de ambiente.
*   `.gitignore`: Especifica arquivos e pastas que o Git deve ignorar.
*   `CHANGELOG.md`: Um registro de todas as alterações notáveis feitas no projeto.
*   `GEMINI.md`: Fornece uma visão geral do projeto, instruções de construção e convenções de desenvolvimento.
*   `README.md`: Descreve as alterações mais recentes e como instalar e testá-las.
*   `requirements.in`: Lista as dependências diretas do Python para o projeto.
*   `requirements.txt`: Lista todas as dependências do Python, geradas a partir do `requirements.in`.
*   `start_app.bat`, `start_app.py`, `start_app.sh`: Scripts para iniciar a aplicação em diferentes sistemas operacionais.
*   `streamlit_app.py`: O ponto de entrada principal para a aplicação frontend do Streamlit.
*   `style.css`: Arquivo de folha de estilo para a interface do usuário.

### Diretórios Principais

*   `core/`: Contém a lógica de negócios principal da aplicação.
    *   `agents/`: Define os agentes de conversação e seus nós.
    *   `business_intelligence/`: Lógica para consulta de dados, cache e classificação de intenção.
    *   `connectivity/`: Adaptadores para conectar a fontes de dados como SQL Server e Parquet.
    *   `graph/`: Constrói o grafo de conversação que orquestra os agentes.
    *   `utils/`: Funções utilitárias usadas em todo o projeto.
*   `data/`: Armazena dados usados pela aplicação, como templates, catálogos e histórico de consultas.
*   `docs/`: Contém a documentação do projeto, incluindo relatórios de análise, guias e planos de implementação.
*   `pages/`: Contém as diferentes páginas da aplicação Streamlit.
*   `scripts/`: Scripts para várias tarefas de desenvolvimento e manutenção.
*   `tests/`: Contém os testes automatizados para o projeto.
*   `assets/`: Contém arquivos estáticos, como folhas de estilo.
*   `backup_lint/`, `backup_unused/`: Backups de arquivos de código.
*   `config/`: Arquivos de configuração para o projeto.
*   `dev_tools/`: Ferramentas e scripts para desenvolvimento.
*   `logs/`: Armazena logs da aplicação.
*   `reports/`: Relatórios gerados, como análises de código e gráficos.
*   `ui/`: Componentes de interface do usuário.
