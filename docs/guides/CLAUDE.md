# CLAUDE.md

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com código neste repositório.

## Visão Geral do Projeto

Agent_BI é uma plataforma de inteligência de negócios conversacional construída em Python que permite interação em linguagem natural com dados de negócios. O sistema combina um frontend Streamlit com backend FastAPI, integrando com LLMs (Gemini/DeepSeek), bancos de dados SQL Server e arquivos Parquet através de uma arquitetura de máquina de estados baseada em LangGraph.

## Comandos de Desenvolvimento

### Configuração do Ambiente
```bash
# Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Instalar dependências
pip install -r requirements.txt
```

### Executando a Aplicação
```bash
# Aplicação principal Streamlit (interface primária)
streamlit run streamlit_app.py

# Backend FastAPI (opcional - para acesso via API)
python main.py
# ou
uvicorn main:app --reload
```

### Testes e Qualidade
```bash
# Executar testes (pytest configurado)
pytest

# Gerar relatório de cobertura
coverage run -m pytest && coverage report

# Verificar qualidade do código (se ferramentas estiverem disponíveis)
ruff check .
black . --check
```

### Dados e Configuração
```bash
# A aplicação usa arquivos de dados no diretório data/parquet/
# Dataset principal: data/parquet/admmat.parquet
# Arquivos de configuração estão no diretório data/ (catálogos JSON, templates)
```

## Visão Geral da Arquitetura

### Componentes Principais
- **Frontend**: Aplicação Streamlit (`streamlit_app.py`) com interface multi-páginas
- **Backend**: Aplicação FastAPI (`main.py`) servindo como gateway de API
- **Máquina de Estados**: Workflow baseado em LangGraph em `core/graph/`
- **Adaptadores LLM**: Suporte a múltiplos LLMs (Gemini, DeepSeek) com lógica de fallback
- **Camada de Dados**: Adaptadores Parquet e SQL Server em `core/connectivity/`
- **Business Intelligence**: Motor de consultas inteligente em `core/business_intelligence/`

### Padrões Arquiteturais Principais
- **Clean Architecture**: Separação clara de responsabilidades com adaptadores e casos de uso
- **Factory Pattern**: `ComponentFactory` gerencia criação de adaptadores LLM e fallback
- **State Machine**: LangGraph orquestra o workflow de consultas BI
- **Lazy Loading**: Configurações e componentes carregados sob demanda para compatibilidade com cloud

### Estrutura de Diretórios
```
core/
├── agents/           # Agentes de IA especializados (BI, geração de código, etc.)
├── business_intelligence/  # Motor de consultas diretas e processamento híbrido
├── config/           # Gerenciamento de configurações com carregamento seguro
├── connectivity/     # Adaptadores de dados (Parquet, SQL Server)
├── factory/          # Fábrica de componentes para injeção de dependência
├── graph/           # Construtor de máquina de estados LangGraph
├── tools/           # Várias utilidades e ferramentas
├── utils/           # Utilitários comuns (logging, cache, segurança)
└── visualization/   # Componentes de geração de gráficos

pages/               # Componentes multi-página do Streamlit
data/               # Arquivos de dados, catálogos e configurações
docs/               # Documentação
migrations/         # Migrações de banco de dados
ui/                 # Componentes de UI
api/                # Endpoints FastAPI
```

## Configuração e Ambiente

### Variáveis de Ambiente Obrigatórias
```bash
# Configuração LLM (uma destas)
GEMINI_API_KEY=sua_chave_gemini        # LLM principal
DEEPSEEK_API_KEY=sua_chave_deepseek    # LLM de fallback
LLM_MODEL_NAME=gemini-2.5-flash-lite  # Modelo mais rápido e barato

# Banco de dados (opcional)
DB_SERVER=seu_servidor_sql
DB_NAME=seu_banco_dados
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### Arquivos de Configuração
- `.env` - Variáveis de ambiente locais
- `streamlit_secrets.toml` - Secrets do Streamlit Cloud
- `data/config.json` - Configuração da aplicação
- `data/data_catalog.json` - Definições de schema de dados

## Diretrizes de Desenvolvimento

### Estilo de Código e Padrões
- Seguir convenções Python PEP 8
- Usar lazy loading para compatibilidade com cloud (imports, configurações)
- Implementar tratamento adequado de erros com mecanismos de fallback
- Usar `ComponentFactory` para criar adaptadores LLM e outros componentes
- Preservar padrões de autenticação existentes em `core/auth.py`

### Integração LLM
- **LLM principal**: Gemini 2.5 Flash-Lite (887 tok/s, $0.10/$0.40 por 1M tokens)
- **LLM de fallback**: DeepSeek (fallback automático em rate limits/quota)
- **Fallback inteligente**: Detecção automática de rate limit → troca para DeepSeek
- Sempre usar `ComponentFactory.get_llm_adapter()` para obter instâncias LLM
- Cache de respostas ativo para reduzir custos de API

### Padrões de Acesso a Dados
- Usar `ParquetAdapter` para arquivos de dados locais
- Usar `DirectQueryEngine` para consultas rápidas e simples
- Usar `HybridQueryEngine` para análises complexas
- Sempre validar filtros e consultas de dados

### Gerenciamento de Estado
- LangGraph gerencia o workflow principal de BI
- Session state no Streamlit para interações do usuário
- Histórico de consultas armazenado em `data/query_history/`
- Sessões de usuário armazenadas em `data/sessions/`

### Abordagem de Testes
- Testes unitários para componentes principais
- Testes de integração para o workflow completo
- Dados mock disponíveis para cenários de teste
- Configuração de testes em `config/pytest.ini`

## Implantação

### Streamlit Cloud
- Branch principal: `main`
- Ponto de entrada: `streamlit_app.py`
- Dependências: `requirements.txt`
- Secrets configurados no dashboard do Streamlit Cloud

### Desenvolvimento Local
- Usar arquivo `.env` para secrets locais
- Arquivos Parquet devem estar em `data/parquet/`
- Verificar `DEPLOY_STREAMLIT_CLOUD.md` para detalhes de implantação

## Notas de Implementação Importantes

### Workflow LangGraph
O sistema usa uma máquina de estados com estes nós principais:
1. `classify_intent` - Determina o tipo de consulta
2. `clarify_requirements` - Solicita esclarecimento se necessário
3. `generate_parquet_query` - Cria filtros de dados
4. `execute_query` - Executa a consulta
5. `generate_plotly_spec` - Cria visualizações
6. `format_final_response` - Formata a saída

### Tratamento de Erros
- Degradação gradual quando componentes falham
- Fallback automático de LLM (Gemini → DeepSeek)
- Mensagens de erro amigáveis ao usuário
- Logging abrangente em todo o sistema

### Otimizações de Performance
- Cache de respostas para chamadas LLM
- Lazy loading de dependências pesadas
- Otimização de memória para datasets grandes
- Processamento em chunks para consultas grandes