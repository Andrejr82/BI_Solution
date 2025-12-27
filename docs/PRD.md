# Product Requirements Document (PRD)
# Agent Solution BI - Lojas Caçula

**Versão:** 2.0
**Data:** 21 de Dezembro de 2025
**Status:** Em Produção
**Proprietário do Produto:** Gerência de BI & Engenharia de IA

---

## 1. Visão do Produto

### 1.1 Resumo Executivo

O **Agent Solution BI** é uma plataforma de Business Intelligence conversacional que combina Inteligência Artificial Generativa (Google Gemini 3.0 Flash) com processamento de dados de alta performance (Polars + DuckDB) para transformar mais de 1 milhão de registros de vendas e estoque da rede Lojas Caçula em insights acionáveis através de linguagem natural.

A solução elimina a necessidade de expertise técnica em SQL ou BI tradicional, permitindo que gestores de categoria, gerentes de loja e a diretoria executiva obtenham análises complexas através de perguntas simples como "Quais produtos de Tecidos estão em ruptura na UNE 1?".

### 1.2 Problema a Resolver

**Desafios Atuais:**
- **Latência Decisória:** Gestores aguardam horas/dias para receber relatórios de BI, perdendo janelas de oportunidade.
- **Complexidade Técnica:** Análises avançadas exigem conhecimento de SQL/Excel avançado, limitando autonomia operacional.
- **Ruptura de Gôndola:** Falta de visibilidade em tempo real sobre produtos com estoque em CD mas ausentes nas lojas (perda de vendas estimada em 15-20%).
- **Gestão de Mix Ineficiente:** Dificuldade em identificar os produtos "Classe A" que sustentam 80% do faturamento (Princípio de Pareto).
- **Imobilização de Capital:** Excesso de estoque de itens de baixo giro sem visibilidade clara.

### 1.3 Proposta de Valor

**Para Gestores de Categoria:**
- Análises de desempenho de segmento/categoria em segundos via chat.
- Alertas proativos de ruptura com sugestões de ação.
- Visão clara da Curva ABC para priorização de compras.

**Para Gerentes de Loja (UNE):**
- Monitoramento de estoque e vendas da sua unidade.
- Sugestões inteligentes de transferência CD → Loja.
- Indicadores de saúde operacional (cobertura, giro).

**Para Diretoria:**
- Dashboard estratégico consolidado com KPIs de todas as UNEs.
- Análise de tendências de crescimento MoM/YoY.
- Visão holística da eficiência de capital de giro.

---

## 2. Objetivos do Negócio

### 2.1 Objetivos Primários

| ID | Objetivo | Métrica de Sucesso | Prazo |
|----|----------|-------------------|-------|
| OBJ-01 | Reduzir Taxa de Ruptura de Gôndola | Queda de 15% a 20% em rupturas críticas | 3 meses |
| OBJ-02 | Aumentar Eficiência Operacional | 80% das análises realizadas em < 5 segundos | Imediato |
| OBJ-03 | Democratizar Acesso a Dados | 90% dos gestores acessando BI sem suporte técnico | 6 meses |
| OBJ-04 | Otimizar Capital de Giro | Redução de 10% em estoque imobilizado (Classe C) | 6 meses |

### 2.2 KPIs de Produto

- **Adoção:** 80% dos gestores usando o sistema semanalmente.
- **Satisfação:** Net Promoter Score (NPS) > 8.0.
- **Performance:** 95% das consultas completadas em < 3 segundos.
- **Confiabilidade:** 99.5% de disponibilidade (uptime).
- **Precisão:** Taxa de sucesso de respostas da IA > 95% (validação via feedback).

---

## 3. Usuários-Alvo e Personas

### Persona 1: Gestor de Categoria
**Nome:** Maria Silva
**Cargo:** Gerente de Categoria - Tecidos
**Necessidades:**
- Análise rápida de performance de produtos do seu segmento.
- Identificação de tendências de crescimento/queda.
- Visão de estoque e cobertura por produto.

**Dores:**
- Dependência de equipe de BI para relatórios customizados.
- Dificuldade em cruzar dados de vendas, estoque e margem.

**Jornada no Sistema:**
1. Login com credenciais segmentadas (acesso apenas a dados de Tecidos).
2. Pergunta no chat: "Quais produtos de Tecidos cresceram mais de 10% no último mês?".
3. Recebe gráfico interativo e tabela com dados.
4. Exporta relatório para apresentação à diretoria.

---

### Persona 2: Gerente de Loja (UNE)
**Nome:** João Santos
**Cargo:** Gerente - Loja Caçula UNE 1
**Necessidades:**
- Monitoramento diário de estoque da sua unidade.
- Alertas de produtos próximos à ruptura.
- Sugestões de transferência para evitar perda de vendas.

**Dores:**
- Ruptura de produtos com demanda mas sem estoque na loja (enquanto há disponibilidade no CD).
- Processos manuais para solicitar transferências.

**Jornada no Sistema:**
1. Acessa Dashboard de Rupturas.
2. Visualiza lista priorizada de produtos em risco.
3. Clica em "Sugestões de Transferência".
4. Valida e aprova transferência automática de 50 unidades do CD para sua loja.

---

### Persona 3: Diretor Executivo
**Nome:** Carlos Mendes
**Cargo:** Diretor de Operações
**Necessidades:**
- Visão consolidada de performance de toda a rede.
- Identificação de UNEs ou categorias com problemas.
- Análise de Pareto para foco estratégico.

**Dores:**
- Excesso de relatórios fragmentados.
- Dificuldade em identificar prioridades rapidamente.

**Jornada no Sistema:**
1. Acessa Dashboard Executivo.
2. Visualiza KPIs: Valor Total de Estoque, Taxa de Ruptura Média, Mix de Produtos.
3. Pergunta no chat: "Quais UNEs tiveram queda de mais de 5% nas vendas no último mês?".
4. Recebe análise detalhada com gráficos de tendência.
5. Exporta dados para reunião de diretoria.

---

## 4. Requisitos Funcionais

### 4.1 Autenticação e Autorização

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-01 | Login via usuário/senha com JWT | P0 | ✅ Implementado |
| RF-02 | Controle de acesso baseado em segmento | P0 | ✅ Implementado |
| RF-03 | Integração com Supabase Auth (opcional) | P2 | ✅ Implementado |
| RF-04 | Expiração de token em 60 minutos | P1 | ✅ Implementado |
| RF-05 | Refresh token para renovação automática | P1 | ✅ Implementado |

**Detalhamento:**
- Gestores têm acesso apenas aos dados dos segmentos permitidos (ex: "ARMARINHO E CONFECÇÃO").
- Diretoria possui `allowed_segments: []` (acesso global).
- Mascaramento automático de PII (CPF, email, telefone) em todas as respostas.

---

### 4.2 Chat BI Conversacional

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-06 | Interface de chat com histórico de sessão | P0 | ✅ Implementado |
| RF-07 | Processamento de linguagem natural via Gemini | P0 | ✅ Implementado |
| RF-08 | Streaming de respostas (SSE) | P0 | ✅ Implementado |
| RF-09 | Geração automática de gráficos Plotly | P0 | ✅ Implementado |
| RF-10 | Suporte a tabelas markdown em respostas | P1 | ✅ Implementado |
| RF-11 | Cache semântico de respostas (6h TTL) | P1 | ✅ Implementado |
| RF-12 | Sistema de feedback (positivo/negativo) | P1 | ✅ Implementado |
| RF-13 | Exportação de gráficos (PNG/SVG) | P2 | 🟡 Planejado |

**Capacidades do Chat:**
- **Consultas Analíticas:** "Top 10 produtos por vendas no último mês na UNE 2".
- **Comparações:** "Compare vendas de Tecidos vs Papelaria nos últimos 3 meses".
- **Rupturas:** "Quais produtos estão em ruptura mas têm estoque no CD?".
- **Transferências:** "Sugira transferências para a UNE 5 baseadas em vendas".
- **Pareto:** "Mostre a curva ABC de produtos por receita".

**Tipos de Resposta:**
1. **Texto Narrativo:** Explicações e insights da IA.
2. **Gráficos Interativos:** Bar, Line, Pie, Scatter, Pareto (Plotly).
3. **Tabelas Markdown:** Dados tabulares formatados.
4. **Código Python:** Exibição opcional do código gerado (modo debug).

---

### 4.3 Dashboard Estratégico

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-14 | KPIs em tempo real (Valor Estoque, Ruptura, Mix) | P0 | ✅ Implementado |
| RF-15 | Filtros por segmento/categoria/UNE | P1 | ✅ Implementado |
| RF-16 | Gráfico de tendência de vendas (30 dias) | P1 | ✅ Implementado |
| RF-17 | Análise de Pareto (80/20) por receita | P0 | ✅ Implementado |
| RF-18 | Mapa de calor de performance por UNE | P2 | 🟡 Planejado |

**KPIs Exibidos:**
- **Valor Total de Estoque:** Soma de `ESTOQUE_UNE * PRECO_CUSTO`.
- **Taxa de Ruptura:** Percentual de produtos com `ESTOQUE_UNE = 0` e `VENDA_30DD > 0`.
- **Mix de Produtos:** Distribuição por segmento/categoria.
- **Cobertura Média:** Média de `ESTOQUE_UNE / VENDA_30DD * 30`.

---

### 4.4 Gestão de Rupturas

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-19 | Lista de rupturas críticas com priorização | P0 | ✅ Implementado |
| RF-20 | Drill-down por UNE/Segmento/Categoria | P1 | ✅ Implementado |
| RF-21 | Identificação de produtos com estoque em CD | P0 | ✅ Implementado |
| RF-22 | Cálculo de perda de receita estimada | P1 | ✅ Implementado |
| RF-23 | Alertas automáticos (email/notificação) | P2 | 🟡 Planejado |

**Critérios de Ruptura Crítica:**
- `ESTOQUE_UNE = 0` (sem estoque na loja).
- `VENDA_30DD > 0` (teve venda nos últimos 30 dias).
- `ESTOQUE_CD > 0` (há disponibilidade no CD para transferência).
- Priorização por `VENDA_30DD DESC` (produtos de maior giro primeiro).

---

### 4.5 Sugestões de Transferência

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-24 | Algoritmo de sugestão CD → Loja | P0 | ✅ Implementado |
| RF-25 | Validação de regras de negócio (MC, ICMS) | P1 | ✅ Implementado |
| RF-26 | Histórico de transferências solicitadas | P2 | ✅ Implementado |
| RF-27 | Aprovação workflow (gestor → logística) | P2 | 🟡 Planejado |
| RF-28 | Integração com ERP para execução | P3 | 📋 Backlog |

**Lógica de Sugestão:**
```python
# Pseudocódigo
if (ESTOQUE_UNE == 0 and VENDA_30DD > 0 and ESTOQUE_CD > 0):
    quantidade_sugerida = min(VENDA_30DD / 30 * 7, ESTOQUE_CD)  # 7 dias de cobertura
    if valida_mc(produto) and valida_icms(une_origem, une_destino):
        criar_sugestao(produto, quantidade_sugerida)
```

---

### 4.6 AI Insights Proativos

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-29 | Análise automática de crescimento MoM | P1 | ✅ Implementado |
| RF-30 | Identificação de produtos com excesso de estoque | P1 | ✅ Implementado |
| RF-31 | Sugestões de ação baseadas em padrões | P2 | 🟡 Planejado |
| RF-32 | Alertas de anomalias (quedas abruptas) | P2 | 🟡 Planejado |

**Exemplos de Insights:**
- "A categoria Papelaria teve queda de 12% nas vendas nas UNEs 3, 5 e 7. Considere revisar mix ou campanhas promocionais."
- "O produto X tem 90 dias de cobertura de estoque. Avalie promoção ou devolução ao fornecedor."

---

### 4.7 Sistema de Aprendizado (RAG)

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RF-33 | Busca semântica de queries similares (FAISS) | P1 | ✅ Implementado |
| RF-34 | Coleta de exemplos de sucesso para RAG | P1 | ✅ Implementado |
| RF-35 | Auto-correção de código (Self-Healing) | P1 | ✅ Implementado |
| RF-36 | Fine-tuning do modelo com dados da Caçula | P3 | 📋 Backlog |

**Funcionamento:**
1. Usuário faz pergunta complexa.
2. Sistema busca queries similares bem-sucedidas no índice FAISS.
3. Exemplos são injetados no prompt do Gemini.
4. Código gerado é executado; se houver erro, sistema tenta corrigir automaticamente.

---

## 5. Requisitos Não-Funcionais

### 5.1 Performance

| ID | Requisito | Métrica | Prioridade |
|----|-----------|---------|-----------|
| RNF-01 | Consultas analíticas < 3 segundos (p95) | 95% < 3s | P0 |
| RNF-02 | Geração de gráficos < 5 segundos | 95% < 5s | P0 |
| RNF-03 | Carregamento de dashboard < 2 segundos | p95 < 2s | P1 |
| RNF-04 | Suporte a 1M+ linhas em queries Polars | ✅ Testado | P0 |
| RNF-05 | Cache hit rate > 40% | Redução de custos LLM | P1 |

**Otimizações Implementadas:**
- **Motor Polars:** Processamento paralelo de DataFrames.
- **DuckDB:** Queries SQL sobre Parquet com push-down de predicados.
- **Cache Semântico:** Reduz chamadas redundantes ao Gemini.
- **Lazy Loading:** Importações pesadas carregadas sob demanda.

---

### 5.2 Escalabilidade

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RNF-06 | Suporte a 100 usuários simultâneos | P1 | ✅ Validado |
| RNF-07 | Processamento de datasets > 5GB | P2 | ✅ Validado |
| RNF-08 | Arquitetura stateless para clustering | P2 | ✅ Implementado |
| RNF-09 | Auto-scaling em cloud (CPU/RAM) | P3 | 📋 Planejado |

---

### 5.3 Segurança

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RNF-10 | Autenticação JWT com expiração | P0 | ✅ Implementado |
| RNF-11 | Mascaramento de PII (CPF, email) | P0 | ✅ Implementado |
| RNF-12 | Rate limiting (10 req/min por usuário) | P1 | ✅ Implementado |
| RNF-13 | Sanitização de inputs contra injection | P0 | ✅ Implementado |
| RNF-14 | Execução de código em sandbox isolado | P1 | 🟡 Parcial |
| RNF-15 | Auditoria de ações sensíveis (logs) | P1 | ✅ Implementado |
| RNF-16 | HTTPS obrigatório em produção | P0 | ✅ Implementado |

**Controles Implementados:**
- **Segment-Based Access Control:** Usuários veem apenas dados permitidos.
- **Code Execution Sandbox:** Código Python executado com escopo limitado (sem imports maliciosos).
- **Structured Logging:** Auditoria completa com níveis `INFO`, `WARNING`, `ERROR`.

---

### 5.4 Confiabilidade

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RNF-17 | Uptime 99.5% (< 3.6h downtime/mês) | P0 | 🟡 Em Monitoramento |
| RNF-18 | Fallback automático Parquet → SQL Server | P1 | ✅ Implementado |
| RNF-19 | Fallback LLM: Gemini → DeepSeek | P1 | ✅ Implementado |
| RNF-20 | Health checks (`/health` endpoint) | P0 | ✅ Implementado |
| RNF-21 | Graceful degradation em caso de falha | P1 | ✅ Implementado |

---

### 5.5 Usabilidade

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RNF-22 | Interface responsiva (desktop/tablet) | P1 | ✅ Implementado |
| RNF-23 | Tempo de aprendizado < 30 min | P1 | ✅ Validado |
| RNF-24 | Acessibilidade WCAG 2.1 AA | P2 | 🟡 Parcial |
| RNF-25 | Suporte a português brasileiro | P0 | ✅ Implementado |

---

### 5.6 Manutenibilidade

| ID | Requisito | Prioridade | Status |
|----|-----------|-----------|--------|
| RNF-26 | Cobertura de testes > 70% | P1 | 🟡 Em Progresso |
| RNF-27 | Documentação de API (OpenAPI/Swagger) | P1 | ✅ Implementado |
| RNF-28 | Logs estruturados com correlação | P0 | ✅ Implementado |
| RNF-29 | Code style: PEP8 (backend), ESLint (frontend) | P1 | ✅ Implementado |

---

## 6. Casos de Uso Principais

### UC-01: Análise de Performance de Categoria
**Ator:** Gestor de Categoria
**Pré-condição:** Usuário autenticado com acesso ao segmento "Tecidos".
**Fluxo Principal:**
1. Usuário acessa página de Chat.
2. Digita: "Mostre os top 10 produtos de Tecidos por vendas no último mês".
3. Sistema processa query via Gemini.
4. Sistema executa código Polars para agregar dados.
5. Sistema retorna gráfico de barras + tabela com dados.
6. Usuário visualiza e exporta gráfico.

**Pós-condição:** Query registrada para aprendizado do sistema.

---

### UC-02: Resolução de Ruptura Crítica
**Ator:** Gerente de Loja (UNE 1)
**Pré-condição:** Produto X está em ruptura na UNE 1 mas disponível no CD.
**Fluxo Principal:**
1. Usuário acessa Dashboard de Rupturas.
2. Sistema exibe lista priorizada de produtos em ruptura.
3. Usuário identifica Produto X no topo da lista.
4. Usuário clica em "Ver Sugestões de Transferência".
5. Sistema calcula quantidade ideal baseada em histórico de vendas.
6. Usuário valida sugestão e clica em "Aprovar Transferência".
7. Sistema registra solicitação para processamento logístico.

**Pós-condição:** Transferência agendada; estoque da UNE será reposto.

---

### UC-03: Análise Estratégica de Pareto
**Ator:** Diretor Executivo
**Pré-condição:** Usuário autenticado com acesso global.
**Fluxo Principal:**
1. Usuário acessa Dashboard de Analytics.
2. Seleciona filtro "Curva ABC por Receita".
3. Sistema gera gráfico de Pareto (barras + linha acumulada).
4. Sistema destaca:
   - Classe A: 20% dos produtos (80% da receita) - Verde.
   - Classe B: 30% dos produtos (15% da receita) - Amarelo.
   - Classe C: 50% dos produtos (5% da receita) - Vermelho.
5. Usuário identifica foco estratégico em Classe A.
6. Usuário exporta dados para apresentação.

**Pós-condição:** Decisão de priorizar compras/campanhas em produtos Classe A.

---

### UC-04: Feedback de Resposta da IA
**Ator:** Qualquer usuário
**Pré-condição:** IA forneceu uma resposta a uma query.
**Fluxo Principal:**
1. Usuário visualiza resposta da IA.
2. Usuário clica em 👍 (feedback positivo) ou 👎 (feedback negativo).
3. Se negativo, sistema exibe campo para comentário opcional.
4. Sistema registra feedback com metadados (query, resposta, timestamp).
5. Sistema atualiza índice RAG com exemplo (se positivo).

**Pós-condição:** IA aprende com feedback para melhorar respostas futuras.

---

## 7. Stack Tecnológica

### 7.1 Frontend

| Componente | Tecnologia | Versão | Justificativa |
|-----------|-----------|--------|--------------|
| Framework | SolidJS | 1.8+ | Performance superior (sem Virtual DOM), reatividade fina |
| Estilização | TailwindCSS | 3.x | Produtividade, consistência visual |
| Gráficos | Plotly.js | 2.x | Interatividade, suporte a múltiplos tipos de gráficos |
| HTTP Client | Axios | 1.x | API familiar, interceptors para auth |
| Streaming | EventSource | Nativo | SSE para chat em tempo real |
| Build | Vite | 5.x | Build rápido, HMR eficiente |
| Testes | Vitest + Testing Library | - | Compatibilidade com SolidJS |

---

### 7.2 Backend

| Componente | Tecnologia | Versão | Justificativa |
|-----------|-----------|--------|--------------|
| Framework | FastAPI | 0.104+ | Performance, validação automática, OpenAPI |
| Runtime | Python | 3.11+ | Type hints, asyncio nativo |
| Processamento | Polars | 0.19+ | Velocidade 10-100x superior ao Pandas |
| Query Engine | DuckDB | 0.9+ | SQL sobre Parquet, push-down otimizações |
| LLM | Google Gemini | 3.0 Flash | Native function calling, custo-benefício |
| Orquestração | LangGraph | 0.2+ | Workflows de agentes multi-etapa |
| Embeddings | Sentence-Transformers | 2.x | Busca semântica de queries |
| Vector Store | FAISS | 1.x | Similaridade eficiente |
| Auth | JWT (python-jose) | 3.x | Stateless, escalável |
| Logging | Structlog | 23.x | Logs estruturados, correlação de requests |
| Validação | Pydantic | 2.x | Schemas type-safe |

---

### 7.3 Infraestrutura

| Componente | Tecnologia | Ambiente Prod |
|-----------|-----------|--------------|
| Web Server | Uvicorn (ASGI) | + Nginx reverse proxy |
| Database | SQL Server 2019+ | Dados transacionais/auth |
| Analytics Storage | Apache Parquet | Arquivos colunares |
| Cache | In-memory TTL Cache | Redis (futuro) |
| Deployment | Docker + Docker Compose | Kubernetes (futuro) |
| CI/CD | GitHub Actions | - |
| Monitoring | Estruturado (a definir) | Prometheus + Grafana (futuro) |

---

## 8. Roadmap de Produto

### Fase 1: MVP ✅ CONCLUÍDO (Q4 2024)

**Objetivos:** Validar conceito de BI conversacional com funcionalidades core.

**Entregas:**
- ✅ Autenticação JWT com controle de segmento.
- ✅ Chat BI básico com Gemini.
- ✅ Geração de gráficos (bar, line, pie).
- ✅ Dashboard de KPIs.
- ✅ Gestão de rupturas críticas.
- ✅ Sugestões de transferência.
- ✅ Integração Parquet (admmat.parquet).

**Métricas de Sucesso:**
- 10 usuários pilotos (gestores de categoria).
- 80% de satisfação em testes de usabilidade.
- Consultas em < 5 segundos (p95).

---

### Fase 2: Otimização & Scale ✅ CONCLUÍDO (Q1 2025)

**Objetivos:** Melhorar performance, confiabilidade e adicionar features avançadas.

**Entregas:**
- ✅ Migração para DuckDB (queries 5x mais rápidas).
- ✅ Cache semântico (redução de 40% em custos LLM).
- ✅ Análise de Pareto (Curva ABC).
- ✅ AI Insights proativos (crescimento MoM, excesso de estoque).
- ✅ Sistema de feedback e aprendizado (RAG).
- ✅ Fallback automático (Gemini → DeepSeek, Parquet → SQL).
- ✅ Structured logging e auditoria.

**Métricas de Sucesso:**
- 50 usuários ativos.
- Consultas em < 3 segundos (p95).
- Cache hit rate > 40%.
- Uptime 99.5%.

---

### Fase 3: Expansão de Capacidades 🟡 EM ANDAMENTO (Q2-Q3 2025)

**Objetivos:** Adicionar features de IA avançada e integração operacional.

**Planejadas:**
- 🟡 Alertas automáticos (email/push) para rupturas críticas.
- 🟡 Previsão de demanda com ML (ARIMA/Prophet).
- 🟡 Análise de sazonalidade (identificação de picos/quedas cíclicas).
- 🟡 Integração com ERP para execução automática de transferências.
- 🟡 Workflow de aprovação multi-nível (gestor → logística → execução).
- 🟡 Exportação avançada (Excel, PDF com logo Caçula).
- 🟡 Dashboard mobile-first (app nativo ou PWA).

**Métricas de Sucesso:**
- 100+ usuários ativos.
- Redução de 15% em rupturas (vs baseline Q1).
- NPS > 8.0.

---

### Fase 4: IA Autônoma 📋 BACKLOG (Q4 2025)

**Objetivos:** Evolução para agente autônomo que toma decisões operacionais.

**Conceito:**
- **Agente Autônomo de Transferências:** IA executa transferências automaticamente baseada em regras pré-aprovadas (ex: "sempre transferir produtos Classe A em ruptura com estoque CD > 10 unidades").
- **Assistente Executivo:** IA prepara relatórios diários personalizados para cada gestor.
- **Anomaly Detection:** Alertas inteligentes de comportamentos anômalos (ex: queda abrupta de 30% em vendas).

**Requisitos:**
- Auditoria completa de ações autônomas.
- Sistema de rollback (desfazer transferências incorretas).
- Aprovação da diretoria para autonomia crítica.

---

## 9. Métricas de Sucesso

### 9.1 Métricas de Produto (Observáveis no Sistema)

| Métrica | Definição | Meta | Frequência |
|---------|-----------|------|-----------|
| Daily Active Users (DAU) | Usuários únicos por dia | 80% dos gestores | Diário |
| Query Success Rate | % de queries completadas sem erro | > 95% | Semanal |
| Average Response Time | Tempo médio de resposta (p95) | < 3s | Diário |
| Cache Hit Rate | % de queries atendidas via cache | > 40% | Diário |
| Feedback Score | Média de feedbacks positivos/total | > 85% | Semanal |
| Feature Adoption | % uso de features (Rupturas, Pareto, etc) | > 60% | Mensal |

---

### 9.2 Métricas de Negócio (Impacto Operacional)

| Métrica | Definição | Meta | Frequência |
|---------|-----------|------|-----------|
| Taxa de Ruptura Crítica | % produtos Classe A em ruptura | < 5% | Semanal |
| Cobertura de Estoque Otimizada | % produtos com 7-30 dias cobertura | > 70% | Mensal |
| Redução de Tempo de Análise | Tempo médio para obter insights | -80% vs manual | Trimestral |
| Capital Imobilizado | Valor estoque Classe C com > 60d cobertura | -10% vs baseline | Trimestral |
| NPS (Net Promoter Score) | Recomendação do sistema (0-10) | > 8.0 | Trimestral |

---

## 10. Riscos e Mitigações

### Riscos Técnicos

| ID | Risco | Probabilidade | Impacto | Mitigação | Status |
|----|-------|--------------|---------|-----------|--------|
| RT-01 | Falha de API do Gemini | Média | Alto | Fallback automático para DeepSeek | ✅ Implementado |
| RT-02 | Queries lentas em datasets grandes | Baixa | Médio | DuckDB + Parquet otimizado | ✅ Implementado |
| RT-03 | Execução de código malicioso | Baixa | Alto | Sandbox de execução + sanitização | 🟡 Parcial |
| RT-04 | Downtime do SQL Server | Média | Médio | Fallback para Parquet | ✅ Implementado |
| RT-05 | Escalabilidade (> 200 usuários simultâneos) | Média | Médio | Arquitetura stateless + auto-scaling | 📋 Planejado |

---

### Riscos de Negócio

| ID | Risco | Probabilidade | Impacto | Mitigação | Status |
|----|-------|--------------|---------|-----------|--------|
| RN-01 | Baixa adoção por resistência a IA | Média | Alto | Treinamento + comunicação de valor | 🟡 Em Andamento |
| RN-02 | Imprecisão da IA gera decisões incorretas | Média | Alto | Feedback loop + validação humana crítica | ✅ Implementado |
| RN-03 | Custos elevados de API LLM | Baixa | Médio | Cache agressivo + modelos menores | ✅ Implementado |
| RN-04 | Dependência de qualidade de dados | Alta | Alto | Validação de schema + alertas de qualidade | 🟡 Parcial |
| RN-05 | Complexidade operacional (manutenção) | Média | Médio | Documentação extensiva + equipe treinada | ✅ Implementado |

---

### Riscos de Segurança/Compliance

| ID | Risco | Probabilidade | Impacto | Mitigação | Status |
|----|-------|--------------|---------|-----------|--------|
| RS-01 | Vazamento de dados via queries indevidas | Baixa | Alto | Segment-based access + mascaramento PII | ✅ Implementado |
| RS-02 | Ataque de injection (SQL/Code) | Baixa | Alto | Sanitização + queries parametrizadas | ✅ Implementado |
| RS-03 | Acesso não autorizado | Média | Alto | JWT + rate limiting + auditoria | ✅ Implementado |
| RS-04 | Exposição de credenciais em logs | Baixa | Alto | Redação automática de secrets em logs | ✅ Implementado |

---

## 11. Dependências e Integrações

### Sistemas Internos
- **SQL Server (ADMMAT):** Fonte primária de dados transacionais.
- **Parquet Files:** Armazenamento analítico de alta performance.
- **Supabase (Opcional):** Auth alternativa e sincronização de usuários.

### Serviços Externos
- **Google Gemini API:** Processamento de linguagem natural e geração de código.
- **DeepSeek API (Fallback):** LLM alternativo em caso de quota/rate limit.

### Integrações Futuras
- **ERP Caçula:** Execução automática de transferências.
- **Sistema de Notificações:** Emails/push para alertas.
- **Data Warehouse:** Sincronização bidirecional para histórico consolidado.

---

## 12. Requisitos de Deployment

### Ambientes

**Desenvolvimento:**
- Execução local via `start.bat` (Windows) ou `npm run dev`.
- Backend: `http://127.0.0.1:8000`.
- Frontend: `http://localhost:3000`.

**Homologação:**
- Deploy via Docker Compose.
- Dados de teste/mock.
- SSL com certificado self-signed.

**Produção:**
- Deploy em servidor dedicado ou cloud (Azure/AWS).
- Nginx como reverse proxy (terminação SSL).
- Backup automático de Parquet e banco de dados.
- Monitoramento via Prometheus + Grafana.

### Configuração de Ambiente

**Variáveis Críticas (.env):**
```env
# Gemini
GEMINI_API_KEY=<chave_api>
LLM_MODEL_NAME=gemini-3-flash-preview

# Segurança
SECRET_KEY=<gerado_via_openssl>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
SQL_SERVER_CONNECTION_STRING=<dsn_sql_server>

# Optional: Supabase
USE_SUPABASE_AUTH=true
SUPABASE_URL=<url>
SUPABASE_ANON_KEY=<key>
```

---

## 13. Critérios de Aceitação (DoD - Definition of Done)

### Para Features
- [ ] Requisito funcional implementado conforme especificação.
- [ ] Testes unitários com cobertura > 70%.
- [ ] Testes manuais executados e aprovados.
- [ ] Documentação atualizada (README, API docs).
- [ ] Code review aprovado.
- [ ] Sem regressões em funcionalidades existentes.
- [ ] Performance dentro das métricas (< 3s para queries).

### Para Releases
- [ ] Todas as features planejadas entregues.
- [ ] Bugs críticos resolvidos (P0).
- [ ] Testes de integração executados.
- [ ] Deploy em homologação validado.
- [ ] Changelog atualizado.
- [ ] Comunicação aos stakeholders.

---

## 14. Glossário

| Termo | Definição |
|-------|-----------|
| **UNE** | Unidade de Negócio (Loja física da rede Caçula). |
| **CD** | Centro de Distribuição. |
| **Ruptura** | Produto sem estoque na loja (ESTOQUE_UNE = 0). |
| **Ruptura Crítica** | Ruptura + vendas recentes + estoque disponível no CD. |
| **Classe A/B/C** | Classificação Pareto: A (80% receita), B (15%), C (5%). |
| **MC** | Margem de Contribuição (markup mínimo exigido). |
| **Cobertura** | Dias de estoque baseado em vendas médias (ESTOQUE / VENDA_DIA). |
| **RAG** | Retrieval-Augmented Generation (busca semântica + LLM). |
| **SSE** | Server-Sent Events (streaming HTTP). |
| **Parquet** | Formato de arquivo colunar para analytics. |
| **Polars** | Motor de DataFrames multi-threaded (alternativa ao Pandas). |
| **DuckDB** | OLAP database in-process para queries SQL em Parquet. |

---

## 15. Contatos e Responsabilidades

| Área | Responsável | Email | Função |
|------|------------|-------|--------|
| Product Owner | [Nome] | [email] | Priorização de backlog, validação de entregas |
| Tech Lead | [Nome] | [email] | Arquitetura, code reviews, decisões técnicas |
| Backend Dev | [Nome] | [email] | Implementação de APIs, agentes, ferramentas |
| Frontend Dev | [Nome] | [email] | Interface SolidJS, dashboards, UX |
| Data Engineer | [Nome] | [email] | Pipelines de dados, otimização Parquet/SQL |
| DevOps | [Nome] | [email] | Deploy, CI/CD, monitoramento |
| QA | [Nome] | [email] | Testes manuais/automatizados, validação de qualidade |

---

## 16. Apêndices

### A. Datasets de Referência

**Arquivo Principal:** `backend/data/parquet/admmat.parquet`
- **Registros:** 1,113,822
- **Colunas:** 97
- **Tamanho:** ~150MB
- **Schema:** Ver `docs/PARQUET_SCHEMA_REFERENCE.md`

**Colunas Chave:**
- `PRODUTO`, `NOME`, `UNE`, `UNE_NOME`
- `NOMESEGMENTO`, `NOMECATEGORIA`, `NOMEFABRICANTE`
- `ESTOQUE_UNE`, `ESTOQUE_CD`, `VENDA_30DD`
- `PRECO_VENDA`, `PRECO_CUSTO`, `MC_MINIMO`

---

### B. Exemplos de Queries Suportadas

**Análise de Vendas:**
- "Top 10 produtos por vendas no último mês"
- "Compare vendas de Tecidos vs Papelaria nos últimos 3 meses"
- "Produtos com crescimento acima de 20% MoM"

**Gestão de Estoque:**
- "Produtos com mais de 60 dias de cobertura"
- "Quais produtos estão em ruptura na UNE 5?"
- "Mostre a curva ABC por receita"

**Operacional:**
- "Sugira transferências para a UNE 2"
- "Produtos com estoque no CD mas em ruptura nas lojas"
- "Categorias com maior taxa de ruptura"

---

### C. Temas Visuais (Lojas Caçula)

**Paleta de Cores:**
```css
--primary: #8B7355;        /* Marrom Caçula */
--accent: #C9A961;         /* Dourado/Bronze */
--success: #166534;        /* Verde Classe A */
--warning: #CA8A04;        /* Amarelo Classe B */
--danger: #991B1B;         /* Vermelho Classe C/D */
--background: #FAFAFA;     /* Fundo Claro */
--text: #1F2937;           /* Texto Escuro */
```

**Tipografia:**
- **Títulos:** Inter, peso 600-700
- **Corpo:** Inter, peso 400-500
- **Código:** Fira Code, monospace

---

## 17. Histórico de Versões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2024-11-15 | [Nome] | Versão inicial do PRD |
| 1.5 | 2024-12-10 | [Nome] | Adição de Pareto, AI Insights, RAG |
| 2.0 | 2025-12-21 | [Nome] | Atualização completa pós-migração DuckDB, features Fase 2 |

---

**Documento aprovado por:**
- [ ] Diretor de Operações
- [ ] Gerente de BI
- [ ] Tech Lead
- [ ] Product Owner

**Próxima revisão:** Trimestral (Março 2026)

---

**Lojas Caçula © 2025 - Transformando dados em decisões estratégicas.**
