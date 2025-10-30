# 🎯 PLANO DE CORREÇÃO DE ERROS E TREINAMENTO LLM

**Data de Criação:** 29 de Outubro de 2025
**Versão:** 1.0
**Status:** 📋 EM PLANEJAMENTO
**Responsável:** Equipe Agent_Solution_BI

---

## 📊 SITUAÇÃO ATUAL (29/10/2025)

### Análise de Erros (Últimos 3 dias)

| Tipo de Erro | Frequência | % Total | Severidade |
|--------------|-----------|---------|------------|
| ColumnValidationError/KeyError | 6 casos | 33% | 🔴 CRÍTICA |
| RuntimeError (Recursos) | 6 casos | 40% | ⚠️ ALTA |
| RuntimeError (Load Failed) | 4 casos | 27% | 🔸 MÉDIA |
| ValueError (Colunas) | 2 casos | 13% | 🔸 MÉDIA |

**Taxa de Erro Atual:** ~40%
**Tendência:** ⬆️ +140% (26/10 → 27/10)
**Objetivo:** ⬇️ Reduzir para 5% em 3 meses

### Estado do Roadmap LLM

**Progresso Geral:** 60% Concluído

- ✅ **Fase 1: Quick Wins** - 100% (3/3 implementados)
- ⏸️ **Pilar 2: Few-Shot Learning** - 0% (Prioridade CRÍTICA)
- ⏸️ **Pilar 3: Validador Avançado** - 50% (Código existe, não integrado)
- ⏸️ **Pilar 4: Análise de Logs** - 20% (Coleta feita, análise pendente)
- ⏸️ **Pilar 1: RAG System** - 0% (Complexo, baixa prioridade)

---

## 🎯 OBJETIVOS E METAS

### Metas de Curto Prazo (1 mês)

| Métrica | Baseline (29/10) | Meta (29/11) | Variação |
|---------|------------------|--------------|----------|
| Taxa de Erro Geral | 40% | 15% | ⬇️ -62.5% |
| Erros de Coluna | 33% | 3% | ⬇️ -90.9% |
| Erros de Recursos | 40% | 10% | ⬇️ -75% |
| Queries Bem-Sucedidas | 60% | 85% | ⬆️ +41.7% |
| Tempo Médio Resposta | 4.5s | 3.5s | ⬇️ -22% |

### Metas de Médio Prazo (3 meses)

| Métrica | Baseline (29/10) | Meta (29/01/2026) | Variação |
|---------|------------------|-------------------|----------|
| Taxa de Erro Geral | 40% | 5% | ⬇️ -87.5% |
| Erros de Coluna | 33% | 0% | ⬇️ -100% |
| Queries Bem-Sucedidas | 60% | 95% | ⬆️ +58% |
| Taxa de Cache Hit | 30% | 60% | ⬆️ +100% |
| Satisfação Usuário | 3.5/5 | 4.5/5 | ⬆️ +29% |

---

## 📅 CRONOGRAMA DETALHADO

### **SEMANA 1: 29/10 - 02/11/2025** 🔴 CRÍTICO

#### **Fase 1.1: Integração Column Validator**
**Data Início:** 29/10/2025 (Terça)
**Data Conclusão:** 31/10/2025 (Quinta)
**Duração:** 3 dias
**Prioridade:** 🔴 CRÍTICA

**Tarefas:**
- [ ] **Dia 1 (29/10)** - Análise e Preparação
  - [ ] Revisar código de `core/utils/column_validator.py` ✅ (já existe)
  - [ ] Revisar código de `core/config/column_mapping.py` ✅ (já existe)
  - [ ] Mapear pontos de integração em `core/agents/code_gen_agent.py`
  - [ ] Criar branch `feature/integrate-column-validator`
  - [ ] Backup do código atual

- [ ] **Dia 2 (30/10)** - Implementação
  - [ ] Importar `column_validator` em `code_gen_agent.py`
  - [ ] Adicionar validação ANTES da execução do código
  - [ ] Implementar auto-correção com retry (2 tentativas)
  - [ ] Adicionar logs detalhados de validação
  - [ ] Testes unitários para validação

- [ ] **Dia 3 (31/10)** - Testes e Validação
  - [ ] Testar com 20 queries conhecidas (erros históricos)
  - [ ] Validar correção automática funciona
  - [ ] Medir redução de erros de coluna
  - [ ] Code review
  - [ ] Merge para branch `develop`

**Critério de Sucesso:** ⬇️ 90% redução em erros de coluna
**Responsável:** Desenvolvedor Backend
**Dependências:** Nenhuma

---

#### **Fase 1.2: Fallback para Queries Amplas**
**Data Início:** 01/11/2025 (Sexta)
**Data Conclusão:** 01/11/2025 (Sexta)
**Duração:** 1 dia
**Prioridade:** 🔴 CRÍTICA

**Tarefas:**
- [ ] **Dia 1 (01/11)** - Implementação Completa
  - [ ] Detectar keywords de queries amplas ("todas", "todos", "geral")
  - [ ] Verificar ausência de filtros (UNE, segmento, top N)
  - [ ] Retornar mensagem de clarificação com sugestões
  - [ ] Adicionar exemplos de queries válidas
  - [ ] Testar com queries históricas que falharam por timeout
  - [ ] Documentar lista de keywords detectadas

**Critério de Sucesso:** ⬇️ 60% redução em erros de timeout
**Responsável:** Desenvolvedor Backend
**Dependências:** Nenhuma

---

#### **Fase 1.3: Validação Path do Parquet**
**Data Início:** 02/11/2025 (Sábado)
**Data Conclusão:** 02/11/2025 (Sábado)
**Duração:** 0.5 dia
**Prioridade:** 🔴 ALTA

**Tarefas:**
- [ ] **Dia 1 (02/11)** - Implementação
  - [ ] Adicionar verificação `Path.exists()` em `load_data()`
  - [ ] Verificar permissões de leitura (`os.access()`)
  - [ ] Mensagem de erro clara com path absoluto
  - [ ] Logging de tentativas de acesso
  - [ ] Testar com path inválido
  - [ ] Testar com permissões restritas

**Critério de Sucesso:** ⬇️ 100% eliminação de erros de load
**Responsável:** Desenvolvedor Backend
**Dependências:** Nenhuma

---

#### **Fase 1.4: Deploy e Monitoramento**
**Data:** 02/11/2025 (Sábado)
**Duração:** 0.5 dia

**Tarefas:**
- [ ] Merge de todas as branches para `main`
- [ ] Deploy em staging para testes
- [ ] Testes de regressão (30 queries)
- [ ] Deploy em produção (gradual: 10% → 50% → 100%)
- [ ] Monitorar logs por 24h
- [ ] Coletar métricas de baseline pós-correção

**Checkpoint:** Validar redução de 60% em taxa de erro geral

---

### **SEMANA 2-3: 04/11 - 15/11/2025** 🟡 ALTA

#### **Fase 2.1: Biblioteca de Padrões de Queries**
**Data Início:** 04/11/2025 (Segunda)
**Data Conclusão:** 08/11/2025 (Sexta)
**Duração:** 5 dias
**Prioridade:** 🟡 ALTA

**Tarefas:**
- [ ] **Dia 1-2 (04-05/11)** - Coleta de Padrões
  - [ ] Analisar logs de queries bem-sucedidas (últimos 30 dias)
  - [ ] Identificar 30 padrões mais comuns
  - [ ] Categorizar por tipo (ranking, top N, filtro, agregação, etc.)
  - [ ] Documentar exemplos reais para cada padrão
  - [ ] Validar código de cada exemplo

- [ ] **Dia 3-4 (06-07/11)** - Criação do JSON
  - [ ] Criar estrutura `data/query_patterns.json`
  - [ ] Adicionar 30 padrões com metadados
  - [ ] Incluir keywords para cada padrão
  - [ ] Adicionar 2-3 exemplos por padrão
  - [ ] Validar sintaxe JSON

- [ ] **Dia 5 (08/11)** - Validação
  - [ ] Revisar todos os padrões
  - [ ] Testar cada exemplo manualmente
  - [ ] Documentar uso do arquivo
  - [ ] Commit e push

**Entregável:** `data/query_patterns.json` com 30 padrões
**Critério de Sucesso:** Cobertura de 80% das queries comuns
**Responsável:** Analista de Dados + Desenvolvedor
**Dependências:** Fase 1 concluída

---

#### **Fase 2.2: Pattern Matcher**
**Data Início:** 11/11/2025 (Segunda)
**Data Conclusão:** 12/11/2025 (Terça)
**Duração:** 2 dias
**Prioridade:** 🟡 ALTA

**Tarefas:**
- [ ] **Dia 1 (11/11)** - Implementação Core
  - [ ] Criar `core/learning/pattern_matcher.py`
  - [ ] Implementar classe `PatternMatcher`
  - [ ] Método `match_pattern()` com scoring por keywords
  - [ ] Carregar padrões de `query_patterns.json`
  - [ ] Testes unitários (10 casos)

- [ ] **Dia 2 (12/11)** - Refinamento
  - [ ] Implementar fuzzy matching (opcional)
  - [ ] Adicionar cache de resultados
  - [ ] Logging de matches
  - [ ] Documentação completa
  - [ ] Code review

**Entregável:** `core/learning/pattern_matcher.py`
**Critério de Sucesso:** 90% acurácia em detectar padrão correto
**Responsável:** Desenvolvedor Backend
**Dependências:** Fase 2.1

---

#### **Fase 2.3: Integração Pattern Matcher → Code Gen Agent**
**Data Início:** 13/11/2025 (Quarta)
**Data Conclusão:** 15/11/2025 (Sexta)
**Duração:** 3 dias
**Prioridade:** 🟡 ALTA

**Tarefas:**
- [ ] **Dia 1 (13/11)** - Integração
  - [ ] Importar `PatternMatcher` em `code_gen_agent.py`
  - [ ] Chamar `match_pattern()` antes de gerar código
  - [ ] Injetar exemplos no prompt do sistema
  - [ ] Formatar exemplos de forma legível para LLM

- [ ] **Dia 2 (14/11)** - Testes
  - [ ] Testar com 50 queries variadas
  - [ ] Medir impacto na taxa de acerto
  - [ ] Ajustar prompt baseado em resultados
  - [ ] A/B test (50% com few-shot, 50% sem)

- [ ] **Dia 3 (15/11)** - Deploy
  - [ ] Code review final
  - [ ] Merge para `main`
  - [ ] Deploy em produção (gradual)
  - [ ] Monitorar por 48h
  - [ ] Documentar melhorias observadas

**Entregável:** Few-Shot Learning integrado
**Critério de Sucesso:** ⬆️ +20% em taxa de acerto
**Responsável:** Desenvolvedor Backend
**Dependências:** Fase 2.2

---

#### **Checkpoint da Semana 2-3:**
**Data:** 15/11/2025
**Validações:**
- [ ] Few-Shot Learning funcionando
- [ ] Taxa de erro < 20%
- [ ] Tempo de resposta < 4.0s
- [ ] 100 queries testadas com sucesso

---

### **SEMANA 4: 18/11 - 22/11/2025** 🟢 MÉDIA

#### **Fase 3.1: Error Analyzer**
**Data Início:** 18/11/2025 (Segunda)
**Data Conclusão:** 19/11/2025 (Terça)
**Duração:** 2 dias
**Prioridade:** 🟢 MÉDIA

**Tarefas:**
- [ ] **Dia 1 (18/11)** - Implementação
  - [ ] Criar `core/learning/error_analyzer.py`
  - [ ] Classe `ErrorAnalyzer` com método `analyze_errors()`
  - [ ] Carregar logs de erro dos últimos 7 dias
  - [ ] Agrupar erros por tipo (`KeyError`, `RuntimeError`, etc.)
  - [ ] Calcular frequência e ranking
  - [ ] Gerar sugestões de correção automaticamente

- [ ] **Dia 2 (19/11)** - Testes e Refinamento
  - [ ] Testar com logs históricos
  - [ ] Validar agrupamento correto
  - [ ] Exportar relatório JSON
  - [ ] Documentar uso da classe
  - [ ] Testes unitários

**Entregável:** `core/learning/error_analyzer.py`
**Critério de Sucesso:** Identificar top 5 erros com 100% precisão
**Responsável:** Desenvolvedor Backend
**Dependências:** Logs de erro existentes

---

#### **Fase 3.2: Dynamic Prompt**
**Data Início:** 20/11/2025 (Quarta)
**Data Conclusão:** 20/11/2025 (Quarta)
**Duração:** 1 dia
**Prioridade:** 🟢 MÉDIA

**Tarefas:**
- [ ] **Dia 1 (20/11)** - Implementação Completa
  - [ ] Criar `core/learning/dynamic_prompt.py`
  - [ ] Classe `DynamicPrompt` com método `get_enhanced_prompt()`
  - [ ] Integrar com `ErrorAnalyzer`
  - [ ] Adicionar avisos de erros comuns ao prompt
  - [ ] Formatar avisos de forma clara
  - [ ] Testar com queries problemáticas
  - [ ] Documentar comportamento

**Entregável:** `core/learning/dynamic_prompt.py`
**Critério de Sucesso:** Prompt evolui baseado em erros da semana
**Responsável:** Desenvolvedor Backend
**Dependências:** Fase 3.1

---

#### **Fase 3.3: Dashboard de Métricas**
**Data Início:** 21/11/2025 (Quinta)
**Data Conclusão:** 22/11/2025 (Sexta)
**Duração:** 2 dias
**Prioridade:** 🟢 MÉDIA

**Tarefas:**
- [ ] **Dia 1 (21/11)** - Backend
  - [ ] Criar `core/monitoring/metrics_dashboard.py`
  - [ ] Classe `MetricsDashboard`
  - [ ] Métricas: taxa de sucesso, tempo resposta, cache hit, top queries
  - [ ] Endpoint API `/api/metrics`
  - [ ] Exportar dados em JSON

- [ ] **Dia 2 (22/11)** - Frontend Streamlit
  - [ ] Criar página Streamlit `pages/Analytics.py`
  - [ ] Gráficos de evolução de métricas
  - [ ] Tabela de top erros
  - [ ] Filtros por período
  - [ ] Auto-refresh a cada 5 minutos
  - [ ] Deploy

**Entregável:** Dashboard de métricas funcional
**Critério de Sucesso:** Visibilidade completa de KPIs
**Responsável:** Desenvolvedor Full-Stack
**Dependências:** Fase 3.1, 3.2

---

#### **Checkpoint da Semana 4:**
**Data:** 22/11/2025
**Validações:**
- [ ] Sistema de análise de erros ativo
- [ ] Prompt evolui automaticamente
- [ ] Dashboard acessível
- [ ] Taxa de erro < 15%

---

### **SEMANA 5-7: 25/11 - 13/12/2025** 🔵 OPCIONAL

#### **Fase 4: RAG System (OPCIONAL)**
**Data Início:** 25/11/2025 (Segunda)
**Data Conclusão:** 13/12/2025 (Sexta)
**Duração:** 3 semanas
**Prioridade:** 🔵 BAIXA (Complexo)

**Pré-requisitos:**
- [ ] Fases 1, 2 e 3 concluídas com sucesso
- [ ] Taxa de erro < 10%
- [ ] Aprovação para instalar novas dependências

**Tarefas Resumidas:**
- [ ] **Semana 1:** Setup (instalar sentence-transformers, FAISS)
- [ ] **Semana 2:** Criar `query_examples.json` com embeddings
- [ ] **Semana 2-3:** Implementar `core/rag/query_retriever.py`
- [ ] **Semana 3:** Integrar busca semântica no code gen agent
- [ ] **Semana 3:** Testes e validação

**Impacto Esperado:** +30% precisão em queries similares
**Responsável:** Desenvolvedor Senior + Data Scientist

---

## 📋 CHECKLIST GERAL DE IMPLEMENTAÇÃO

### Antes de Começar (29/10/2025)
- [x] ✅ Análise completa de erros realizada
- [x] ✅ Roadmap LLM revisado
- [x] ✅ Plano documentado com datas
- [ ] Backup completo do código atual
- [ ] Criar branch `feature/llm-improvements-q4-2025`
- [ ] Comunicar equipe sobre cronograma
- [ ] Definir responsáveis para cada fase
- [ ] Configurar ferramentas de monitoramento

### Durante Implementação
- [ ] Realizar code review para cada fase
- [ ] Manter documentação atualizada
- [ ] Executar testes unitários (cobertura > 80%)
- [ ] Validar cada fase antes de prosseguir
- [ ] Registrar decisões técnicas no Git (commits descritivos)
- [ ] Atualizar este documento com progresso real
- [ ] Daily standup para acompanhamento

### Após Cada Fase
- [ ] Validar critérios de sucesso atingidos
- [ ] Deploy em staging primeiro (smoke tests)
- [ ] Testes com usuários beta (10-20 queries reais)
- [ ] Monitorar logs por 24-48h
- [ ] Coletar feedback qualitativo
- [ ] Deploy gradual em produção (10% → 50% → 100%)
- [ ] Documentar lições aprendidas

### Validação Final (22/11/2025)
- [ ] Taxa de erro geral < 15%
- [ ] Erros de coluna < 3%
- [ ] Queries bem-sucedidas > 85%
- [ ] Tempo médio resposta < 3.5s
- [ ] Dashboard de métricas funcional
- [ ] Documentação completa atualizada
- [ ] Treinamento da equipe realizado

---

## 🎯 MARCOS (MILESTONES)

| Marco | Data | Critério de Sucesso | Status |
|-------|------|---------------------|--------|
| **M1: Correções Críticas** | 02/11/2025 | Taxa erro < 25% | ⏳ Pendente |
| **M2: Few-Shot Implementado** | 15/11/2025 | Taxa acerto > 80% | ⏳ Pendente |
| **M3: Análise de Logs Ativa** | 22/11/2025 | Dashboard funcional | ⏳ Pendente |
| **M4: RAG System (Opcional)** | 13/12/2025 | +30% precisão | 🔵 Opcional |
| **M5: Objetivo Final** | 29/01/2026 | Taxa erro < 5% | ⏳ Pendente |

---

## 📊 ACOMPANHAMENTO DE PROGRESSO

### Métricas Semanais (Atualizar toda Segunda-feira)

| Semana | Data | Taxa Erro | Taxa Sucesso | Tempo Resp. | Notas |
|--------|------|-----------|--------------|-------------|-------|
| Baseline | 29/10 | 40% | 60% | 4.5s | Análise inicial |
| 1 | 04/11 | __%  | __%  | __s  | Fase 1 concluída |
| 2 | 11/11 | __%  | __%  | __s  | - |
| 3 | 18/11 | __%  | __%  | __s  | Fase 2 concluída |
| 4 | 25/11 | __%  | __%  | __s  | Fase 3 concluída |

---

## 🚨 RISCOS E MITIGAÇÕES

### Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Integração quebra funcionalidade existente | Média | Alto | Testes de regressão completos + deploy gradual |
| Few-Shot não melhora precisão | Baixa | Médio | Validar padrões com queries reais antes |
| Atraso no cronograma | Alta | Baixo | Buffer de 1 semana nas fases opcionais |
| Dependências externas (FAISS) | Baixa | Alto | Fase RAG é opcional, não crítica |
| Equipe sobrecarregada | Média | Médio | Priorizar fases críticas, adiar opcionais |

---

## 📞 COMUNICAÇÃO E REPORTING

### Reuniões de Acompanhamento

- **Daily Standups:** 9h00 (15 min) - Status, bloqueios, próximos passos
- **Code Reviews:** Assíncronos via Pull Requests
- **Demo das Fases:** Sexta-feira 16h (30 min)
- **Retrospectiva:** Final de cada fase (1h)

### Canais de Comunicação

- **Slack:** #agent-bi-improvements (atualizações diárias)
- **Jira/GitHub Projects:** Tracking de tarefas
- **Confluence/Docs:** Documentação técnica
- **Email:** Stakeholders (updates semanais)

### Relatórios

- **Semanal:** Segunda-feira 10h - Progresso, métricas, bloqueios
- **Por Fase:** Após conclusão - Resultados, aprendizados, próximos passos
- **Final:** 22/11/2025 - Relatório completo de impacto

---

## 📚 RECURSOS E REFERÊNCIAS

### Documentação Interna

- [PLANO_TREINAMENTO_LLM.md](./PLANO_TREINAMENTO_LLM.md)
- [ROADMAP_IMPLEMENTACOES_PENDENTES.md](./ROADMAP_IMPLEMENTACOES_PENDENTES.md)
- [PLANO_FINAL_FIX_RESPOSTAS_LLM.md](./PLANO_FINAL_FIX_RESPOSTAS_LLM.md)
- [column_validator.py](../../core/utils/column_validator.py)
- [column_mapping.py](../../core/config/column_mapping.py)

### Papers e Artigos

- **Few-Shot Learning:** "Language Models are Few-Shot Learners" (GPT-3)
- **RAG:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- **Prompt Engineering:** "Chain-of-Thought Prompting Elicits Reasoning"

### Ferramentas

- **Logging:** Python logging + JSON estruturado
- **Monitoramento:** Streamlit Dashboard customizado
- **Testes:** pytest + coverage
- **CI/CD:** GitHub Actions (quando disponível)

---

## ✅ CONCLUSÃO E PRÓXIMOS PASSOS

### Resumo do Plano

Este plano visa **reduzir a taxa de erro de 40% para 5%** em 3 meses através de 3 fases principais:

1. **Fase 1 (Semana 1):** Correções críticas - Eliminar 90% erros de coluna
2. **Fase 2 (Semanas 2-3):** Few-Shot Learning - +20% precisão
3. **Fase 3 (Semana 4):** Análise contínua - Melhoria incremental

**Fase 4 (RAG)** é opcional e depende do sucesso das fases anteriores.

### Próxima Ação Imediata

**HOJE (29/10/2025):**
1. Criar branch `feature/integrate-column-validator`
2. Backup do código atual
3. Revisar `column_validator.py` e `code_gen_agent.py`
4. Mapear pontos de integração
5. Comunicar equipe sobre início da Fase 1

**AMANHÃ (30/10/2025):**
1. Começar implementação da integração
2. Escrever primeiros testes unitários

---

## 📝 HISTÓRICO DE ATUALIZAÇÕES

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| 29/10/2025 | 1.0 | Criação inicial do plano | Claude Code + Equipe BI |
| ___/___/___ | 1.1 | Atualização após Fase 1 | ___________ |
| ___/___/___ | 1.2 | Atualização após Fase 2 | ___________ |
| ___/___/___ | 2.0 | Revisão completa pós-implementação | ___________ |

---

**🚀 Pronto para começar! Let's ship it! 🎯**

---

**Aprovações:**

- [ ] **Tech Lead:** _________________ Data: ___/___/___
- [ ] **Product Owner:** _________________ Data: ___/___/___
- [ ] **Equipe de QA:** _________________ Data: ___/___/___

---

*Documento vivo - Atualizar conforme progresso real*
