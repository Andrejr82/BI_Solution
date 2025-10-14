1️⃣ CACULINHA_BI_AGENT (bi-agent)

Objetivo: gerar relatórios e insights de BI.

Exemplos de request:

# Relatório semanal de vendas
request = "gerar relatório semanal de vendas"

# Análise de estoque e rupturas
request = "analisar produtos com ruptura no PDV da semana"

# KPI de performance por região
request = "calcular KPI de vendas por região"


O que esperar:

Tabelas resumidas com vendas, estoque, rupturas.

Métricas e insights de tendência (ex.: produtos em risco de falta).

2️⃣ CACULINHA_DEV_AGENT (code-agent)

Objetivo: gerar automações, scripts ou funções.

Exemplos de request:

# Criar script Python para enviar emails diários
request = "criar script para enviar relatório de vendas diário por email"

# Gerar função para atualizar planilha de estoque
request = "criar função Python para atualizar planilha de estoque automaticamente"

# Automatizar cópia de arquivos entre pastas
request = "gerar script Python para copiar arquivos CSV de uma pasta para outra"


O que esperar:

Código Python pronto ou parcialmente pronto.

Mensagens de confirmação ou logs de execução.

3️⃣ DATA_SYNC_AGENT (data-agent)

Objetivo: sincronizar, limpar e transformar dados.

Exemplos de request:

# Sincronizar tabela de vendas para SQL Server
request = "sincronizar tabela de vendas da semana para SQL Server"

# Limpar dados de estoque removendo duplicatas
request = "limpar dados de estoque, remover duplicatas e preencher valores nulos"

# Converter CSV de produtos para Parquet
request = "converter CSV de produtos para Parquet e salvar na pasta processed_data"


O que esperar:

Confirmação de que o ETL foi realizado.

Logs detalhando as operações (linhas processadas, erros, status).

Arquivos transformados ou atualizados em SQL/Parquet.

🔹 Dica de execução

No run_agents.py, você pode copiar qualquer um desses exemplos como input quando o script pedir:

Escolha o agente para executar:
1 - bi-agent
2 - code-agent
3 - data-agent
Digite o número do agente: 1
Digite a request/input do usuário: gerar relatório semanal de vendas


O mesmo vale para os outros agentes.

| Agente                  | Número no `run_agents.py` | Request de teste                                                        |
| ----------------------- | ------------------------- | ----------------------------------------------------------------------- |
| **CACULINHA_BI_AGENT**  | 1                         | gerar relatório semanal de vendas                                       |
|                         |                           | analisar produtos com ruptura no PDV da semana                          |
|                         |                           | calcular KPI de vendas por região                                       |
| **CACULINHA_DEV_AGENT** | 2                         | criar script para enviar relatório de vendas diário por email           |
|                         |                           | criar função Python para atualizar planilha de estoque automaticamente  |
|                         |                           | gerar script Python para copiar arquivos CSV de uma pasta para outra    |
| **DATA_SYNC_AGENT**     | 3                         | sincronizar tabela de vendas da semana para SQL Server                  |
|                         |                           | limpar dados de estoque, remover duplicatas e preencher valores nulos   |
|                         |                           | converter CSV de produtos para Parquet e salvar na pasta processed_data |
