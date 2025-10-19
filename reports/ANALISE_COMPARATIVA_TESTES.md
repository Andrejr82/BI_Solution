# 📊 ANÁLISE COMPARATIVA - TESTES ANTES vs DEPOIS DAS MELHORIAS

**Data da Análise:** 19/10/2025
**Teste ANTES:** 09:13:38 (relatorio_teste_80_perguntas_20251019_091338.md)
**Teste DEPOIS:** 10:46:30 (relatorio_teste_80_perguntas_20251019_104630.md)

---

## 🎯 RESUMO EXECUTIVO

| Métrica | ANTES | DEPOIS | Variação | Avaliação |
|---------|-------|--------|----------|-----------|
| **Taxa de Sucesso** | 100% (80/80) | 100% (80/80) | **0%** | ✅ Mantém |
| **Tempo Médio** | 10.77s | 17.45s | **+62%** 🔴 | ❌ **PIOROU** |
| **Tempo Total** | ~14.4 min | ~23.2 min | **+61%** 🔴 | ❌ PIOROU |
| **Gráficos** | 1 (1.2%) | 0 (0%) | **-100%** 🔴 | ❌ **PIOROU** |
| **Tipo text** | 62 (77.5%) | 49 (61.3%) | **-21%** ✅ | ✅ Melhorou |
| **Tipo data** | 17 (21.2%) | 31 (38.8%) | **+82%** ✅ | ✅ Melhorou |

---

## ❌ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 🔴 **PROBLEMA #1: ZERO Gráficos Gerados**

#### Esperado vs Obtido:
- **Meta:** 16-24 gráficos (20-30%)
- **Obtido:** 0 gráficos (0%)
- **Status:** ❌ **CRÍTICO - Pior que antes**

#### Evidências:

**Queries que EXPLICITAMENTE pediram gráficos:**

| # | Query | Tipo Obtido | Tipo Esperado |
|---|-------|-------------|---------------|
| 1 | "**Gere um gráfico** de vendas do produto 369947..." | `text` ❌ | `chart` |
| 2 | "Mostre a **evolução** de vendas mensais..." | `text` ❌ | `chart` |
| 3 | "**Compare** as vendas do produto 369947..." | `text` ❌ | `chart` |
| 13 | "**Distribuição** de vendas por categoria..." | `text` ❌ | `chart` |
| 25 | "**Análise de sazonalidade**..." | `text` ❌ | `chart` |

**ANTES (teste 09:13):** Query #13 retornou `chart` ✅
**DEPOIS (teste 10:46):** Query #13 retornou `text` ❌

#### Diagnóstico:

As melhorias de detecção de intenção **NÃO surtiram efeito** ou foram sobrescritas por outro problema.

**Possíveis causas:**

1. **Classificação de intenção ignorando as novas regras**
   - Modificamos `bi_agent_nodes.py` mas pode não estar sendo usado
   - LLM pode estar ignorando os novos exemplos

2. **CodeGenAgent não está gerando código Plotly**
   - Mesmo com max_tokens=2048, LLM prefere respostas textuais
   - Prompt do sistema pode estar conflitando

3. **Cache do GraphBuilder**
   - Pode estar usando cache antigo que não tem gráficos

---

### 🔴 **PROBLEMA #2: Performance 62% PIOR**

#### Esperado vs Obtido:
- **Meta:** Reduzir de 10.77s → 7-8s (-26% a -35%)
- **Obtido:** Aumentou para 17.45s (+62%)
- **Status:** ❌ **CRÍTICO - Oposto do esperado**

#### Análise de Outliers:

**Top 5 Queries Mais Lentas (DEPOIS):**

| # | Query | Tempo | Registros | Análise |
|---|-------|-------|-----------|---------|
| 78 | Previsão demanda próximos 3 meses | **31.32s** | 1,113,822 | 🔴 Extremo |
| 79 | Simulação impacto preço/exposição | **22.68s** | - | 🔴 Muito lento |
| 8 | Padrão sazonal segmento FESTAS | **18.94s** | 6,201 | ⚠️ Lento |
| 7 | Top 10 margem crescimento | **18.81s** | - | ⚠️ Lento |
| 1 | Gráfico vendas produto 369947 | **17.83s** | - | ⚠️ Lento |

**Comparação com ANTES:**

| # | Query | ANTES | DEPOIS | Variação |
|---|-------|-------|--------|----------|
| 1 | Gráfico produto 369947 | 13.61s | **17.83s** | **+31%** ❌ |
| 4 | Top 5 produtos mais vendidos | 14.85s | **14.12s** | **-5%** ✅ |
| 78 | Previsão demanda | N/A | **31.32s** | 🔴 Novo outlier |

#### Diagnóstico:

**Causa Principal:** max_tokens=2048 está permitindo LLM gerar código **MAIS COMPLEXO** e **MENOS OTIMIZADO**.

**Evidências:**

1. **Query #78 processou 1.1M registros**
   - ANTES: Provavelmente falhava ou retornava poucos dados
   - DEPOIS: LLM gerando código que processa dataset inteiro sem filtros
   - **Predicate pushdown NÃO está funcionando**

2. **Queries simples ficaram mais lentas**
   - Query #1: "Gráfico de vendas" 13.61s → 17.83s (+31%)
   - LLM gerando código mais verboso/ineficiente

3. **Tempo médio geral subiu 62%**
   - Cache normalizado NÃO está melhorando performance
   - Pode estar PIORANDO por invalidar cache válido

---

## ✅ PONTOS POSITIVOS

### 1. **Taxa de Sucesso 100% Mantida**
- 80/80 queries bem-sucedidas ✅
- Zero erros ✅
- Zero fallbacks ✅
- **Sistema robusto e confiável**

### 2. **Melhor Distribuição de Tipos**

| Tipo | ANTES | DEPOIS | Melhoria |
|------|-------|--------|----------|
| `text` | 77.5% (62) | 61.3% (49) | **-21%** ✅ |
| `data` | 21.2% (17) | 38.8% (31) | **+82%** ✅ |
| `chart` | 1.2% (1) | 0% (0) | **-100%** ❌ |

**Análise:**
- Sistema retornando **mais dados estruturados** (+82% em `data`)
- Menos respostas puramente textuais (-21% em `text`)
- **MAS perdeu a capacidade de gerar gráficos** (-100%)

### 3. **Queries Retornando Mais Dados**

Exemplos de queries com mais registros DEPOIS:

| Query | ANTES | DEPOIS | Variação |
|-------|-------|--------|----------|
| #6: Variação vendas >20% | N/A | 1 | ✅ Dados encontrados |
| #8: Padrão sazonal FESTAS | N/A | 6,201 | ✅ Análise profunda |
| #78: Previsão demanda | N/A | 1,113,822 | ⚠️ **Demais?** |

**Interpretação:**
- LLM está gerando código que busca **mais dados**
- Pode ser positivo (análises mais completas)
- **MAS** está causando problemas de performance

---

## 🔍 DIAGNÓSTICO TÉCNICO PROFUNDO

### Por que as melhorias NÃO funcionaram?

#### 1. **max_tokens=2048: Efeito Colateral**

**Hipótese:** Mais tokens permitiram LLM gerar código mais complexo, mas não necessariamente mais eficiente.

**Evidência:**
- Queries simples ficaram mais lentas
- Query #78 processou 1.1M registros (provavelmente desnecessário)
- Tempo médio subiu 62%

**Causa provável:**
- LLM tem "espaço" para gerar código verboso
- Não está seguindo princípio de código mínimo/otimizado
- Predicate pushdown instruído no prompt está sendo ignorado

#### 2. **Detecção de Gráficos: Não Aplicada**

**Hipótese:** Modificações em `bi_agent_nodes.py` não estão sendo usadas OU LLM está ignorando.

**Evidência:**
- Queries explícitas como "Gere um gráfico" → `text` ❌
- ANTES: Query #13 gerou `chart`
- DEPOIS: Mesma query gerou `text`

**Possíveis causas:**
1. **GraphBuilder não recarregou** o código modificado
2. **LLM classificando tudo como `python_analysis`** em vez de `gerar_grafico`
3. **CodeGenAgent recebendo intenção errada** e gerando texto

#### 3. **Cache Normalizado: Contraproducente?**

**Hipótese:** Normalização de queries pode estar invalidando cache útil.

**Evidência:**
- Performance PIOROU em vez de melhorar
- Queries iguais deveriam ser mais rápidas (cache hit)

**Causa provável:**
- Normalização mudando hash de cache
- Cache anterior (bom) invalidado
- Novo cache ainda vazio

#### 4. **Predicate Pushdown: Ignorado pela LLM**

**Hipótese:** LLM não está seguindo instruções de aplicar filtros early.

**Evidência:**
- Query #78: 1.1M registros processados
- Deveria filtrar ANTES de processar

**Causa provável:**
- Prompt muito longo (muitas instruções)
- LLM priorizando outras diretrizes
- Instruções de predicate pushdown no final do prompt (ignoradas)

---

## 📋 RECOMENDAÇÕES PRIORITÁRIAS

### 🔴 **URGENTE: Reverter max_tokens**

**Ação Imediata:**
```bash
# Reverter para 1024 temporariamente
# Arquivo: core/llm_adapter.py
max_tokens=1024  # (linhas 47, 165, 248)
```

**Justificativa:**
- max_tokens=2048 causou **mais problemas que soluções**
- Performance piorou 62%
- Código gerado ficou mais complexo/ineficiente

**Alternativa:**
- Usar max_tokens=1536 (meio termo)
- Testar se melhora gráficos SEM piorar performance

---

### 🔴 **URGENTE: Investigar Classificação de Intenção**

**Ação:**
1. Adicionar logging em `bi_agent_nodes.py`:
   ```python
   logger.info(f"[CLASSIFY_INTENT] Query: '{user_query}'")
   logger.info(f"[CLASSIFY_INTENT] Intent classificada: '{intent}'")
   ```

2. Executar teste de 1 query específica:
   ```bash
   # Testar: "Gere um gráfico de vendas..."
   # Verificar logs: qual intent foi classificada?
   ```

**Objetivo:**
- Confirmar se `gerar_grafico` está sendo detectada
- OU se está caindo em `python_analysis`

---

### 🟡 **IMPORTANTE: Simplificar Prompt do CodeGenAgent**

**Problema:** Prompt muito longo pode estar confundindo LLM.

**Ação:**
1. Mover instruções de predicate pushdown para o **TOPO** do prompt
2. Reduzir exemplos de mapeamento de segmentos
3. Focar em 3 instruções principais:
   - Filtros early (predicate pushdown)
   - Código mínimo/otimizado
   - Gerar gráficos quando pedido

---

### 🟡 **IMPORTANTE: Testar Cache**

**Ação:**
```bash
# Limpar cache e testar
rm -rf data/cache/*
rm -rf data/cache_agent_graph/*

# Executar teste rápido
python tests/test_rapido_100_llm.py
```

**Objetivo:**
- Ver se cache limpo + normalização melhora
- OU se normalização está atrapalhando

---

### 🟢 **OPCIONAL: A/B Test de max_tokens**

**Ação:**
Testar 3 cenários:
1. max_tokens=1024 (original)
2. max_tokens=1536 (meio termo)
3. max_tokens=2048 (atual)

**Métrica:** Para cada um, medir:
- Taxa de gráficos gerados
- Tempo médio
- P90

---

## 🎯 CONCLUSÃO

### ❌ **As melhorias NÃO atingiram os objetivos**

| Objetivo | Meta | Resultado | Status |
|----------|------|-----------|--------|
| Aumentar gráficos | 20-30% | **0%** | ❌ **Falhou** |
| Reduzir tempo médio | -26% a -35% | **+62%** | ❌ **Oposto** |
| Aumentar cache hit | +200-300% | ⚠️ **Desconhecido** | ⚠️ Não medido |
| Manter sucesso | 100% | **100%** | ✅ **OK** |

### 🔍 **Lições Aprendidas**

1. **max_tokens maior ≠ melhor**
   - Mais tokens permitem código complexo
   - Mas não necessariamente otimizado
   - LLM precisa de **restrições** para gerar código eficiente

2. **Detecção de intenção precisa de validação**
   - Modificar prompt não garante que LLM vai seguir
   - Necessário **testar e validar** com logs
   - Pode precisar de exemplos mais fortes (few-shot)

3. **Cache normalizado pode ter trade-offs**
   - Invalidar cache antigo pode piorar performance inicial
   - Precisa de período de "aquecimento"

4. **Prompts longos diluem instruções importantes**
   - Predicate pushdown no final foi ignorado
   - Instruções críticas devem vir no TOPO

---

## 🚀 PRÓXIMOS PASSOS

### Passo 1: Reverter max_tokens para 1024
**Urgência:** 🔴 CRÍTICA
**Tempo:** 2 min
**Objetivo:** Recuperar performance anterior

### Passo 2: Adicionar Logging de Classificação
**Urgência:** 🔴 CRÍTICA
**Tempo:** 5 min
**Objetivo:** Entender por que gráficos não são gerados

### Passo 3: Executar Teste de 1 Query
**Urgência:** 🔴 CRÍTICA
**Tempo:** 2 min
**Objetivo:** Validar classificação de intent com logs

### Passo 4: Ajustar Prompt (se necessário)
**Urgência:** 🟡 IMPORTANTE
**Tempo:** 15 min
**Objetivo:** Corrigir detecção de gráficos

### Passo 5: Re-testar
**Urgência:** 🟡 IMPORTANTE
**Tempo:** 10-15 min
**Objetivo:** Validar correções

---

**Análise concluída em:** 19/10/2025 11:15
**Recomendação:** Reverter mudanças e re-investigar com abordagem incremental.
