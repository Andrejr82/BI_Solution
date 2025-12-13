# MANUAL TEST CHECKLIST - Agent Solution BI (SolidJS + FastAPI)

Este checklist cobre os principais fluxos da aplicação para validação manual.

---

## 🎯 OBJETIVO

Validar a funcionalidade completa da aplicação após a implementação da migração para SolidJS + FastAPI, garantindo que todas as funcionalidades, regras de negócio e integrações estão operacionais e performando como esperado.

---

## 📝 INSTRUÇÕES

1.  **Ambiente:** Certifique-se de que o backend FastAPI e o frontend SolidJS estão rodando localmente.
2.  **Autenticação:** Tenha um usuário de teste válido (e.g., `testuser/password`).
3.  **Execução:** Siga os passos para cada cenário e registre o resultado (Pass/Fail/N/A).
4.  **Evidências:** Se possível, anexe screenshots ou logs para falhas.
5.  **Falhas:** Para cada falha, registre um `issue` detalhado com passos para reproduzir.

---

## ✅ CHECKLIST DE TESTES

### 1. Autenticação e Acesso

| ID    | Cenário de Teste                          | Passos de Execução                                                 | Resultado Esperado                                                                 | Status (Pass/Fail/N/A) | Observações |
| :---- | :---------------------------------------- | :----------------------------------------------------------------- | :--------------------------------------------------------------------------------- | :--------------------- | :---------- |
| **A1** | Login com Credenciais Válidas            | 1. Acessar `http://localhost:3000`. <br> 2. Inserir `testuser`/`password`. <br> 3. Clicar em "Login". | Redirecionamento para a Dashboard ou Chat. Token armazenado (inspecionar).       |                        |             |
| **A2** | Login com Credenciais Inválidas          | 1. Acessar `http://localhost:3000`. <br> 2. Inserir `invalid`/`password`. <br> 3. Clicar em "Login". | Mensagem de erro "Credenciais inválidas" ou similar. Permanece na tela de Login. |                        |             |
| **A3** | Acesso sem Autenticação (Frontend)        | 1. Tentar acessar `/dashboard` ou `/chat` diretamente sem login.   | Redirecionamento para a tela de Login.                                             |                        |             |
| **A4** | Acesso sem Autenticação (Backend - API)   | 1. Usar ferramenta como Postman/Insomnia. <br> 2. Chamar `/api/v1/analytics/kpis` sem token de autorização. | Resposta `401 Unauthorized`.                                                       |                        |             |
| **A5** | Logout                                    | 1. Fazer Login. <br> 2. Clicar no botão "Logout".                  | Redirecionamento para a tela de Login. Token removido.                             |                        |             |

### 2. Chat BI (Agente Principal)

| ID    | Cenário de Teste                          | Passos de Execução                                                                                                                                                 | Resultado Esperado                                                                                                 | Status (Pass/Fail/N/A) | Observações |
| :---- | :---------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- | :--------------------- | :---------- |
| **B1** | Query de Texto Simples                    | 1. No Chat, digitar: "Qual o total de vendas do mês passado?".                                                                                             | Resposta textual relevante.                                                                                        |                        |             |
| **B2** | Query com Geração de Gráfico              | 1. No Chat, digitar: "Me mostre um gráfico de barras das vendas por segmento.".                                                                            | Resposta textual seguida da renderização de um gráfico Plotly.                                                     |                        |             |
| **B3** | Query com Geração de Tabela               | 1. No Chat, digitar: "Liste os 5 produtos mais vendidos com seus valores.".                                                                               | Resposta textual seguida da renderização de uma tabela de dados.                                                   |                        |             |
| **B4** | Query de Ferramenta (UNE - Abastecimento) | 1. No Chat, digitar: "Calcule a necessidade de abastecimento para a UNE 1 no segmento A.".                                                                 | Resposta textual formatada com os resultados da ferramenta `calcular_abastecimento_une`.                           |                        |             |
| **B5** | Query de Ferramenta (UNE - Rupturas)      | 1. No Chat, digitar: "Encontre as rupturas críticas.".                                                                                                    | Resposta textual formatada com os resultados da ferramenta `encontrar_rupturas_criticas`.                         |                        |             |
| **B6** | Feedback Positivo                         | 1. Receber uma resposta do assistente. <br> 2. Clicar no botão "👍" (like).                                                                                | Console log indicando o envio do feedback. Sem erro na UI.                                                         |                        |             |
| **B7** | Download de Dados                         | 1. Receber uma resposta com dados tabulares (`data`). <br> 2. Clicar no botão "Baixar Dados (JSON)".                                                      | Download de um arquivo JSON contendo os dados da resposta.                                                         |                        |             |
| **B8** | Resposta de Erro do Agente                | 1. No Chat, digitar uma query que cause um erro conhecido no backend (e.g., query complexa com coluna inexistente). <br> 2. Verificar o log do backend. | Mensagem de erro amigável no chat (ex: "Erro ao processar sua solicitação").                                       |                        |             |

### 3. Página de Dashboard

| ID    | Cenário de Teste                          | Passos de Execução                                 | Resultado Esperado                                                          | Status (Pass/Fail/N/A) | Observações |
| :---- | :---------------------------------------- | :------------------------------------------------- | :-------------------------------------------------------------------------- | :--------------------- | :---------- |
| **C1** | Carregamento Inicial                      | 1. Acessar `/dashboard`.                           | Carregamento dos KPIs e da grade de "Top Queries". Sem erros no console. |                        |             |
| **C2** | Atualização dos KPIs                      | 1. Observar os cartões de KPI.                     | Valores dos KPIs atualizados a cada 5 segundos (se `isLive` ativo).         |                        |             |
| **C3** | Tabela de Top Queries                     | 1. Observar a seção "Top Queries".                 | Exibição de uma lista de queries, com nome da query e contagem.             |                        |             |
| **C4** | Botão "Live Sync"                         | 1. Clicar no botão "Live Sync".                    | Troca de estado para "Pausado". Gráficos e dados deixam de atualizar.       |                        |             |
| **C5** | Gráfico de Erros (se implementado)        | 1. Acessar `/analytics/error-trend` (API). <br> 2. Verificar resposta. | Resposta JSON com tendência de erros por data.                              |                        |             |

### 4. Página de Transferências

| ID    | Cenário de Teste                          | Passos de Execução                                                                                                                    | Resultado Esperado                                                                          | Status (Pass/Fail/N/A) | Observações |
| :---- | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------ | :--------------------- | :---------- |
| **D1** | Carregamento Inicial de Sugestões         | 1. Acessar `/transfers`.                                                                                                              | Exibição de sugestões de transferência. Cartões de estatísticas atualizados.                |                        |             |
| **D2** | Validação de Transferência (Sucesso)      | 1. Preencher formulário de validação com dados válidos (e.g., `prod_id=101`, `une_origem=1`, `une_destino=2`, `qtd=10`). <br> 2. Clicar em "Validar". | Mensagem de sucesso "Transferência validada e possível."                                  |                        |             |
| **D3** | Validação de Transferência (Estoque Insuf.) | 1. Preencher formulário com `qtd` maior que o estoque na `une_origem` (simular). <br> 2. Clicar em "Validar".                  | Mensagem de falha "Estoque insuficiente..."                                                |                        |             |
| **D4** | Criação de Solicitação de Transferência   | 1. Preencher formulário com dados válidos. <br> 2. Clicar em "Criar Solicitação".                                                   | Mensagem de sucesso "Transfer request created successfully" com `transfer_id`. Arquivo JSON criado em `data/transferencias`. |                        |             |
| **D5** | Relatório de Transferências (API)         | 1. Fazer algumas criações de solicitação. <br> 2. Chamar `/api/v1/transfers/report` (API) sem/com filtro de data.                 | Resposta JSON com as solicitações de transferência registradas.                             |                        |             |

---

### 5. Backend - Integridade e Logs

| ID    | Cenário de Teste                          | Passos de Execução                                                                      | Resultado Esperado                                                                                                 | Status (Pass/Fail/N/A) | Observações |
| :---- | :---------------------------------------- | :-------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- | :--------------------- | :---------- |
| **E1** | Logs de Segurança (Login)                 | 1. Fazer login com sucesso e com falha. <br> 2. Inspecionar `logs/security/security.log`. | Registros de "User logged in successfully" e "Failed login attempt" no arquivo de log.                              |                        |             |
| **E2** | Cache de Respostas (LLM)                  | 1. Fazer a mesma query repetidas vezes no chat. <br> 2. Inspecionar logs/comportamento. | A primeira query deve demorar mais. Queries subsequentes devem ser mais rápidas. Logs de "Cache hit" esperados. |                        |             |
| **E3** | Autocorreção (Self-Healing) do Agente CodeGen | 1. No Chat, enviar uma query que induza um erro de código no agente (e.g., `.compute()` em Polars). <br> 2. Observar o log do backend. | O agente deve tentar corrigir o código (e.g., remover `.compute()`) e reexecutar, se bem-sucedido.                  |                        |             |
| **E4** | RAG (Retrieval Augmented Generation)      | 1. No Chat, enviar uma query similar a uma já armazenada com sucesso. <br> 2. Observar o log do backend. | Logs indicando que exemplos similares foram encontrados e injetados no prompt do LLM.                           |                        |             |
| **E5** | Data Masking (PII)                      | 1. Em alguma funcionalidade que retorne dados, simular a presença de PII. <br> 2. Verificar se a PII é mascarada. | PII como CPF, email ou telefone deve ser mascarada nos outputs visíveis.                                            |                        |             |

---

## 🏁 CONCLUSÃO DO TESTE MANUAL

| Item                     | Total | Pass | Fail | N/A  |
| :----------------------- | :---- | :--- | :--- | :--- |
| **Cenários de Autenticação** | 5     |      |      |      |
| **Cenários de Chat BI**      | 8     |      |      |      |
| **Cenários de Dashboard**    | 4     |      |      |      |
| **Cenários de Transferências** | 5     |      |      |      |
| **Cenários de Backend**      | 5     |      |      |      |
| **TOTAL**                | **27**|      |      |      |

**Observações Finais:**
*   Registrar todas as falhas como issues no sistema de controle de versão.
*   Documentar quaisquer desvios do comportamento esperado.
*   Recomendar próximos passos (e.g., testes de performance, testes de carga, automação).
