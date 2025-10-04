# 🎯 Plano de Execução - Integração das Perguntas de Negócio

**Data**: 2025-10-03
**Objetivo**: Executar fielmente o plano de integração das 80 perguntas de negócio
**Estratégia**: Execução incremental e segura, com validações a cada etapa

---

## 📊 Análise de Viabilidade

### Escopo Total
- **80 perguntas** distribuídas em 10 categorias
- **4 fases** de implementação (Imediato → Longo prazo)
- **Tempo estimado**: 8-12 horas de desenvolvimento

### Riscos Identificados
1. ⚠️ Quebra de funcionalidades existentes
2. ⚠️ Crashes por falta de validação
3. ⚠️ Incompatibilidade de dados
4. ⚠️ Performance degradada

### Estratégia de Mitigação
✅ Implementação incremental (pequenos blocos testáveis)
✅ Validação após cada etapa
✅ Backup automático antes de mudanças críticas
✅ Testes com dados reais
✅ Rollback fácil se necessário

---

## 🚀 FASE 1 - Documentação e Usabilidade (IMEDIATO)

### 1.1 Criar Componente de Exemplos para UI
**Arquivo**: `pages/5_Exemplos_Perguntas.py`
**Tempo**: 30 min
**Risco**: Baixo

**Tarefas:**
- [x] Ler as 80 perguntas do arquivo MD
- [ ] Criar página Streamlit categorizada
- [ ] Adicionar filtros por categoria
- [ ] Adicionar botões "Tentar Esta Pergunta"
- [ ] Testar renderização

**Validação:**
```bash
streamlit run pages/5_Exemplos_Perguntas.py
```

---

### 1.2 Criar Página de Ajuda
**Arquivo**: `pages/6_Ajuda.py`
**Tempo**: 20 min
**Risco**: Baixo

**Tarefas:**
- [ ] Criar página de ajuda
- [ ] Adicionar guia de uso
- [ ] Adicionar FAQ
- [ ] Adicionar exemplos interativos

---

### 1.3 Implementar Quick Actions
**Arquivo**: `streamlit_app.py` (sidebar)
**Tempo**: 30 min
**Risco**: Médio

**Tarefas:**
- [ ] Adicionar sidebar com perguntas populares
- [ ] Botões clicáveis que preenchem o input
- [ ] Categorias expansíveis
- [ ] Testar integração

**Validação:**
- Clicar em quick action deve preencher o chat input
- Query deve ser executada automaticamente

---

## 🔍 FASE 2 - Validação e Inteligência (CURTO PRAZO)

### 2.1 Validar Cobertura Funcional
**Arquivo**: `tests/test_cobertura_perguntas_negocio.py`
**Tempo**: 1 hora
**Risco**: Alto (pode revelar gaps)

**Tarefas:**
- [ ] Criar matriz de cobertura (pergunta × funcionalidade)
- [ ] Testar cada categoria de pergunta
- [ ] Identificar gaps de funcionalidade
- [ ] Documentar queries não suportadas

**Validação:**
```bash
python tests/test_cobertura_perguntas_negocio.py
```

**Output esperado:**
```
Categoria: Vendas por Produto (8 perguntas)
  ✅ 6 suportadas (75%)
  ❌ 2 não suportadas

Total: 80 perguntas
  ✅ 62 suportadas (77.5%)
  ❌ 18 não suportadas (22.5%)
```

---

### 2.2 Expandir Patterns de Query
**Arquivo**: `data/query_patterns_training.json`
**Tempo**: 1 hora
**Risco**: Médio

**Tarefas:**
- [ ] Adicionar 20+ novos patterns baseados nas perguntas
- [ ] Cobrir todas as 10 categorias
- [ ] Testar cada pattern com regex
- [ ] Validar não quebra patterns existentes

**Patterns a Adicionar:**
1. Análises temporais (sazonalidade, tendências)
2. Análises de ABC
3. Análises de estoque
4. Comparações entre segmentos
5. Análises de fabricante

---

### 2.3 Melhorar Classificação de Intents
**Arquivo**: `core/business_intelligence/direct_query_engine.py`
**Tempo**: 1 hora
**Risco**: Alto

**Tarefas:**
- [ ] Adicionar validação de entidades (UNE, produto, segmento)
- [ ] Melhorar detecção de períodos temporais
- [ ] Adicionar fuzzy matching para nomes
- [ ] Testar com queries complexas

---

## 🧪 FASE 3 - Automação e Testes (MÉDIO PRAZO)

### 3.1 Criar Suite de Testes Automatizados
**Arquivo**: `tests/test_suite_80_perguntas.py`
**Tempo**: 2 horas
**Risco**: Baixo

**Tarefas:**
- [ ] Criar teste para cada uma das 80 perguntas
- [ ] Validar response type correto
- [ ] Validar dados retornados
- [ ] Gerar relatório de cobertura

---

### 3.2 Sistema de Autocomplete
**Arquivo**: `streamlit_app.py`
**Tempo**: 1 hora
**Risco**: Médio

**Tarefas:**
- [ ] Implementar autocomplete no chat input
- [ ] Sugestões baseadas em histórico
- [ ] Sugestões baseadas em popularidade
- [ ] Cache de sugestões

---

## 📈 FASE 4 - Dashboards Avançados (LONGO PRAZO)

### 4.1 Galeria de Dashboards
**Arquivo**: `pages/7_Dashboards.py`
**Tempo**: 3 horas
**Risco**: Médio

**Tarefas:**
- [ ] Templates de dashboards executivos
- [ ] Painéis de KPIs
- [ ] Alertas e monitoramento
- [ ] Exportação de relatórios

---

## ⚡ Plano de Execução Seguro

### Ordem de Execução (Evitar Crashes)

```
ETAPA 1: Preparação (10 min)
├── Criar backup do código atual
├── Validar ambiente Python
├── Testar dados disponíveis
└── Criar branch de desenvolvimento

ETAPA 2: FASE 1.1 - Componente Exemplos (30 min)
├── Criar arquivo pages/5_Exemplos_Perguntas.py
├── Testar renderização
├── Commit + Push
└── Validar funcionamento

ETAPA 3: FASE 1.2 - Página Ajuda (20 min)
├── Criar arquivo pages/6_Ajuda.py
├── Testar renderização
├── Commit + Push
└── Validar funcionamento

ETAPA 4: FASE 1.3 - Quick Actions (30 min)
├── Modificar streamlit_app.py (sidebar)
├── Testar integração
├── Commit + Push
└── Validar não quebrou nada

ETAPA 5: FASE 2.1 - Validação Cobertura (1h)
├── Criar test_cobertura_perguntas_negocio.py
├── Executar testes
├── Documentar resultados
└── Identificar gaps

ETAPA 6: FASE 2.2 - Expandir Patterns (1h)
├── Backup query_patterns_training.json
├── Adicionar novos patterns
├── Validar regex de cada pattern
├── Testar com DirectQueryEngine
└── Commit + Push

ETAPA 7: FASE 2.3 - Melhorar Intents (1h)
├── Backup direct_query_engine.py
├── Adicionar validações de entidades
├── Melhorar detecção de períodos
├── Testar com queries reais
└── Commit + Push

ETAPA 8: FASE 3 - Testes (2h)
├── Criar test_suite_80_perguntas.py
├── Executar e gerar relatório
└── Documentar cobertura final

ETAPA 9: Documentação Final (30 min)
├── Criar relatório de implementação
├── Atualizar README
├── Criar CHANGELOG
└── Commit final
```

---

## 🛡️ Checkpoints de Validação

Após cada etapa, validar:

1. ✅ **Código compila** sem erros
2. ✅ **Testes passam** (se aplicável)
3. ✅ **Streamlit roda** sem crashes
4. ✅ **Funcionalidades existentes** continuam funcionando
5. ✅ **Performance** não degradou significativamente

Se qualquer checkpoint falhar:
- ❌ STOP imediatamente
- 🔄 Rollback para último commit estável
- 🔍 Investigar e corrigir problema
- ✅ Re-executar checkpoint

---

## 📊 Métricas de Sucesso

### FASE 1 (Documentação e Usabilidade)
- ✅ Página de exemplos funcionando
- ✅ 80 perguntas categorizadas e exibidas
- ✅ Quick actions implementados
- ✅ UI intuitiva e sem crashes

### FASE 2 (Validação e Inteligência)
- ✅ Cobertura funcional > 70% das perguntas
- ✅ 20+ novos patterns adicionados
- ✅ Classificação de intents melhorada
- ✅ Validação de entidades funcionando

### FASE 3 (Automação e Testes)
- ✅ 80 testes automatizados criados
- ✅ Relatório de cobertura gerado
- ✅ CI/CD pipeline configurado

### FASE 4 (Dashboards Avançados)
- ✅ 5+ templates de dashboards
- ✅ Exportação de relatórios
- ✅ Sistema de alertas

---

## 🎯 Estimativa de Tempo

| Fase | Tempo | Risco | Prioridade |
|------|-------|-------|------------|
| FASE 1 | 1.5h | Baixo | 🔴 Alta |
| FASE 2 | 3h | Médio | 🟡 Média |
| FASE 3 | 3h | Baixo | 🟢 Baixa |
| FASE 4 | 4h | Médio | 🟢 Baixa |
| **TOTAL** | **11.5h** | - | - |

---

## 🚦 Semáforo de Execução

- 🟢 **Verde**: Pode executar sem riscos
- 🟡 **Amarelo**: Executar com atenção e validações
- 🔴 **Vermelho**: Alto risco, requer backup e testes extensivos

**Status Atual**: 🟢 Pronto para iniciar FASE 1

---

## 📝 Logs de Execução

Criar arquivo `logs/integracao_perguntas.log` para rastrear:
- Timestamp de cada etapa
- Sucesso/Falha
- Erros encontrados
- Tempo de execução
- Cobertura alcançada

---

**Desenvolvido por**: Claude Code
**Baseado em**: `docs/plano_integracao_perguntas_negocio.md`
**Status**: 🚀 Pronto para execução
