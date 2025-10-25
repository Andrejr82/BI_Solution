# ANÁLISE PROFUNDA - PRECISÃO DA LLM

**Data:** 2025-10-13
**Objetivo:** Identificar e corrigir TODOS os problemas de precisão na geração de código pela LLM

---

## 📊 RESUMO EXECUTIVO

Analisando os logs de erro (data/learning/error_log_*.jsonl) e queries bem-sucedidas, identifiquei **5 PROBLEMAS CRÍTICOS** que afetam a precisão da LLM:

### Problemas Já Corrigidos ✅
1. ✅ **Colunas duplicadas 'UNE'** - Corrigido em load_data() (commit edf6b5c)
2. ✅ **`.head()` em gráficos Plotly** - Corrigido em _validate_top_n() (commit edf6b5c)

### Problemas Pendentes ❌
3. ❌ **P0 - LLM gera `.head()` incorretamente em gráficos** (erro original da LLM, não do validador)
4. ❌ **P1 - Prompt DESATUALIZADO com instruções antigas**
5. ❌ **P2 - Falta de exemplos explícitos de gráficos Plotly**

---

## 🔍 ANÁLISE DETALHADA DOS PROBLEMAS

### **PROBLEMA #3 [P0 - CRÍTICO]**
**LLM Gera Código Incorreto: `.head()` após `px.bar()`**

**Evidência:**
```
error_log_20251013.jsonl:2
{
  "code": "result = px.bar(top_10_papelaria, x='NOME', y='VENDA_30DD', title='Top 10 Produtos de Papelaria')\n\n# Passo 3: Salvar resultado\nresult = result.head(10)",
  "error": "'Figure' object has no attribute 'head'"
}
```

**Causa Raiz:**
A LLM está gerando **DUAS linhas de atribuição a `result`**:
1. `result = px.bar(...)`  ✅ Correto
2. `result = result.head(10)`  ❌ ERRADO! (tenta .head() em Figure)

**Localização:** `core/agents/code_gen_agent.py:233-280` (system_prompt)

**Por que acontece:**
O system prompt tem instruções conflitantes:
- Linha 255: "**FORMATO DE CÓDIGO PARA GRÁFICOS:**"
- Linha 268: "**EXEMPLO COMPLETO - RANKING:**" com `.nlargest(10,` ANTES do px.bar()

Mas não há **INSTRUÇÃO EXPLÍCITA** dizendo:
> "NUNCA adicione `.head()` ou `.nlargest()` DEPOIS de criar o gráfico Plotly"

**Solução:**
Adicionar seção no system_prompt:

```python
**⚠️ ATENÇÃO - GRÁFICOS PLOTLY:**
Se você está gerando um gráfico Plotly (px.bar, px.pie, px.line, etc.):
1. Aplique TODOS os filtros (.nlargest, .head, filtros por coluna) ANTES do px.bar()
2. NUNCA adicione .head() ou .nlargest() DEPOIS do px.bar()
3. A última linha deve ser apenas: result = px.bar(...)

❌ ERRADO:
```python
result = px.bar(df, x='NOME', y='VENDA')
result = result.head(10)  # Figure não tem .head()!
```

✅ CORRETO:
```python
df_top10 = df.nlargest(10, 'VENDA')
result = px.bar(df_top10, x='NOME', y='VENDA')
```
```

---

### **PROBLEMA #4 [P1 - ALTO]**
**Prompt Desatualizado com Instruções Antigas**

**Evidência:**
```python
# core/agents/code_gen_agent.py:155-202
system_prompt = f"""Você é um especialista em análise de dados Python...
```

O prompt atual na linha 155 é **MUITO DIFERENTE** dos prompts nos logs de sucesso!

**Comparação:**

| **Logs de Sucesso (funciona)**  | **Código Atual (code_gen_agent.py:155)** |
|----------------------------------|-------------------------------------------|
| "**TAREFA:** Você deve escrever..." | "Você é um especialista..." |
| "**INSTRUÇÕES OBRIGATÓRIAS:**" com 3 passos claros | Instruções espalhadas em múltiplas seções |
| "**REGRAS PARA RANKINGS/TOP N:**" | Não existe no código atual! |
| "**EXEMPLOS CORRETOS:**" com 3 exemplos | "**EXEMPLO COMPLETO:**" com apenas 1 exemplo |

**Causa Raiz:**
O system_prompt foi refatorado e **PERDEU** as instruções mais eficazes dos prompts antigos.

**Solução:**
Reintroduzir o formato dos prompts bem-sucedidos.

---

### **PROBLEMA #5 [P2 - MÉDIO]**
**Falta Cobertura de Exemplos para Gráficos Plotly**

**Evidência:**
Dos 9 successful_queries, apenas 0 eram gráficos! Todos eram DataFrames.

**Causa Raiz:**
- Linha 268-272: Apenas 1 exemplo de gráfico (px.bar com ranking)
- Faltam exemplos de px.pie, px.line, px.scatter
- Faltam exemplos de gráficos SEM "top N"

**Solução:**
Adicionar mais exemplos de gráficos no system_prompt.

---

## 🎯 PLANO DE CORREÇÃO PRIORIZADO

### **Fase 1 - Correções Críticas (30 min)**

#### **CORREÇÃO #1 [P0]** - Adicionar Aviso Explícito Sobre `.head()` em Gráficos

**Arquivo:** `core/agents/code_gen_agent.py`
**Linha:** Após linha 272 (depois do exemplo de ranking)

```python
**⚠️ REGRA CRÍTICA - GRÁFICOS PLOTLY:**
Quando gerar gráficos Plotly (px.bar, px.pie, px.line):
1. Filtre e limite os dados ANTES de criar o gráfico
2. NUNCA use .head() ou .nlargest() DEPOIS de px.bar()
3. A variável result deve conter o objeto Figure diretamente

❌ ERRADO (causa erro 'Figure' object has no attribute 'head'):
```python
df_top = df.nlargest(10, 'VENDA')
result = px.bar(df_top, x='NOME', y='VENDA')
result = result.head(10)  # ❌ Figure não tem .head()!
```

✅ CORRETO:
```python
df_top = df.nlargest(10, 'VENDA')  # Limite ANTES
result = px.bar(df_top, x='NOME', y='VENDA')  # result é Figure
```
```

#### **CORREÇÃO #2 [P1]** - Reintroduzir "REGRAS PARA RANKINGS/TOP N"

**Arquivo:** `core/agents/code_gen_agent.py`
**Linha:** Após linha 248 (depois de "USE OS EXEMPLOS ACIMA")

```python
**REGRAS PARA RANKINGS/TOP N:**
- Se a pergunta mencionar "ranking", "top", "maior", "mais vendido" → você DEVE fazer groupby + sum + sort_values
- Se mencionar "top 10", "top 5" → adicione .head(N) ou .nlargest(N) ANTES de criar gráfico
- SEMPRE agrupe por NOME (nome do produto) para rankings de produtos
- SEMPRE ordene por VENDA_30DD (vendas em 30 dias) de forma DECRESCENTE (ascending=False)
- Use .reset_index() no final para criar um DataFrame limpo

**IMPORTANTE:** NÃO retorne apenas o filtro! Sempre faça o groupby quando houver ranking/top!
```

#### **CORREÇÃO #3 [P2]** - Adicionar Mais Exemplos de Gráficos

**Arquivo:** `core/agents/code_gen_agent.py`
**Linha:** Após linha 272 (substituir o exemplo único)

```python
**EXEMPLOS COMPLETOS DE GRÁFICOS:**

1. **Gráfico de Barras - Top 10:**
```python
df = load_data()
df_filtered = df[df['NOMESEGMENTO'] == 'TECIDOS']
df_top10 = df_filtered.nlargest(10, 'VENDA_30DD')
result = px.bar(df_top10, x='NOME', y='VENDA_30DD', title='Top 10 Produtos - Tecidos')
```

2. **Gráfico de Pizza - Distribuição por Segmento:**
```python
df = load_data()
vendas_por_segmento = df.groupby('NOMESEGMENTO')['VENDA_30DD'].sum().reset_index()
result = px.pie(vendas_por_segmento, names='NOMESEGMENTO', values='VENDA_30DD', title='Vendas por Segmento')
```

3. **Gráfico de Barras - Comparação de Grupos:**
```python
df = load_data()
papelaria = df[df['NOMESEGMENTO'] == 'PAPELARIA']
vendas_por_grupo = papelaria.groupby('NOMEGRUPO')['VENDA_30DD'].sum().sort_values(ascending=False).head(5).reset_index()
result = px.bar(vendas_por_grupo, x='NOMEGRUPO', y='VENDA_30DD', title='Top 5 Grupos - Papelaria')
```
```

---

## 📈 IMPACTO ESPERADO

### Antes das Correções:
- ❌ 2/3 queries falharam (66% de erro)
- Erros: DuplicateError, AttributeError

### Após Correções:
- ✅ Taxa de sucesso esperada: **95%+**
- ✅ Erros eliminados:
  - `.head()` em Figure
  - Rankings sem groupby
  - Gráficos mal formatados

---

## 🚀 PRÓXIMOS PASSOS

1. **Implementar Correções #1, #2, #3** (30 min)
2. **Limpar cache novamente** para forçar regeneração
3. **Testar as 3 queries críticas**:
   - "qual é o preço do produto 369947"
   - "ranking de vendas do tecido"
   - "top 10 produtos de papelaria"
4. **Validar em produção** (Streamlit Cloud)
5. **Monitorar logs de erro** por 48h para confirmar melhoria

---

## 📝 APÊNDICE - OUTROS ERROS NOS LOGS

### KeyError: 'NOMESEGMENTO' (4 ocorrências)
**Causa:** Colunas não normalizadas (nome em minúsculas no Parquet)
**Status:** ✅ **JÁ CORRIGIDO** em load_data() com column_mapping

### AttributeError: 'ParquetAdapter' object has no attribute 'load_data' (1 ocorrência)
**Causa:** Bug antigo na injeção de load_data()
**Status:** ✅ **JÁ CORRIGIDO** - load_data() agora é função injetada no escopo

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após implementar correções, validar:

- [ ] Query "top 10 produtos de papelaria" gera gráfico de barras ✅
- [ ] Query "ranking de vendas do tecido" retorna DataFrame com groupby ✅
- [ ] Query "qual é o preço do produto 369947" retorna valor único ✅
- [ ] Nenhum erro de `.head()` em gráficos Plotly
- [ ] Nenhum erro de colunas duplicadas
- [ ] Taxa de sucesso > 95% em 10 queries variadas
