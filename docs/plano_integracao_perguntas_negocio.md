# 📋 Plano de Integração das Perguntas de Negócio

## Objetivo
Integrar os 80 exemplos de perguntas de negócio do arquivo `exemplos_perguntas_negocio.md` ao projeto Agent_BI para melhorar a experiência do usuário e validar a cobertura funcional do sistema.

---

## **1. Criar Suite de Testes de Validação**
- Desenvolver módulo de testes automatizados usando as 80 perguntas como casos de teste
- Validar capacidade do sistema em interpretar e responder cada tipo de pergunta
- Garantir cobertura dos principais casos de uso (vendas, estoque, ABC, temporal, etc.)

## **2. Ampliar Documentação do Usuário**
- Adicionar seção "Exemplos de Perguntas" na interface Streamlit
- Criar página dedicada com perguntas categorizadas e exemplos reais
- Implementar sistema de busca/filtro de exemplos por categoria

## **3. Melhorar Classificação de Intents**
- Enriquecer o `classify_intent` no LangGraph com padrões das 80 perguntas
- Treinar/ajustar prompts para reconhecer os 10 tipos principais de análise
- Adicionar validação de entidades mencionadas (produtos, UNEs, segmentos, períodos)

## **4. Implementar Sugestões Inteligentes**
- Sistema de autocomplete baseado nas perguntas mais comuns
- Sugestões contextuais baseadas no histórico do usuário
- "Quick Actions" com perguntas pré-formatadas clicáveis

## **5. Validar Cobertura de Funcionalidades**
- Auditar cada categoria de pergunta (vendas, segmento, UNE, temporal, ABC, estoque, etc.)
- Identificar gaps de funcionalidade no sistema atual
- Priorizar implementação de features faltantes

## **6. Criar Galeria de Dashboards Pré-Configurados**
- Templates de dashboards baseados nas perguntas 65-72 (executivos)
- Painéis prontos para KPIs principais, alertas e monitoramento
- Exportação de relatórios padrão

---

## **Priorização Sugerida**

### **Fase 1 (Imediato)** - Documentação e Usabilidade
- Adicionar exemplos na UI Streamlit
- Criar página de ajuda com perguntas categorizadas
- Implementar quick actions clicáveis

### **Fase 2 (Curto prazo)** - Validação e Inteligência
- Validar cobertura funcional de cada categoria
- Melhorar classificação de intents no LangGraph
- Adicionar validação de entidades

### **Fase 3 (Médio prazo)** - Automação e Testes
- Implementar sugestões inteligentes
- Criar suite de testes automatizados
- Sistema de autocomplete

### **Fase 4 (Longo prazo)** - Dashboards Avançados
- Galeria de dashboards pré-configurados
- Templates de relatórios executivos
- Exportação de relatórios padrão

---

## **Categorias de Perguntas Cobertas**

1. 🎯 **Análises de Vendas por Produto** (Perguntas 1-8)
2. 🏪 **Análises por Segmento** (Perguntas 9-16)
3. 🏬 **Análises por UNE/Loja** (Perguntas 17-24)
4. 📈 **Análises Temporais** (Perguntas 25-32)
5. 💰 **Análises de Performance e ABC** (Perguntas 33-40)
6. 📦 **Análises de Estoque e Logística** (Perguntas 41-48)
7. 🏭 **Análises por Fabricante** (Perguntas 49-56)
8. 🎨 **Análises por Categoria/Grupo** (Perguntas 57-64)
9. 📊 **Dashboards e Relatórios Executivos** (Perguntas 65-72)
10. 🔍 **Análises Específicas e Personalizadas** (Perguntas 73-80)

---

## **Notas de Implementação**

- Priorizar perguntas mais frequentes baseadas em analytics de uso
- Garantir que todas as perguntas funcionem com os dados disponíveis (`admmatao.parquet`)
- Manter exemplos atualizados conforme novas features sejam adicionadas
- Usar perguntas como base para testes de regressão

---

*Documento criado em: 2025-10-02*
*Baseado em: `docs/exemplos_perguntas_negocio.md`*
