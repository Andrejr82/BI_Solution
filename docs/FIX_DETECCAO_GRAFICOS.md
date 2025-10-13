# Fix: Detecção de Gráficos e Respostas Repetidas

## Problema Identificado

O agente 100% IA apresentava dois problemas críticos:

1. **Não identificava pedidos de gráficos**: Perguntas como "gere um gráfico de barras" não eram reconhecidas corretamente
2. **Respostas idênticas para queries similares**: "ranking tecidos" e "ranking papelaria" retornavam o mesmo resultado

## Análise da Causa Raiz

### Problema 1: Detecção de Ferramentas Genérica

**Arquivo**: `core/agents/caculinha_bi_agent.py` (linhas 218-237)

O prompt de seleção de ferramentas era muito genérico:
```python
# ANTES - Prompt genérico
"- `generate_and_execute_python_code`: Para análises complexas, cálculos, agregações ou geração de gráficos que exigem código Python."
```

**Problema**: Não havia palavras-chave explícitas para detectar pedidos de visualização.

### Problema 2: Cache Ingênuo

**Arquivo**: `core/agents/code_gen_agent.py` (linha 161)

```python
# ANTES - Cache simples
cache_key = hash(prompt + json.dumps(raw_data, sort_keys=True) if raw_data else "")
```

**Problema**: Queries como "ranking X" tinham estrutura similar e podiam gerar a mesma chave de cache.

### Problema 3: Prompt do CodeGen Sem Instruções Visuais

**Arquivo**: `core/agents/code_gen_agent.py` (linha 212)

O prompt do CodeGenAgent não tinha instruções específicas sobre quando e como gerar gráficos.

## Soluções Implementadas

### 1. Prompt de Seleção de Ferramentas Aprimorado

**Arquivo**: `core/agents/caculinha_bi_agent.py:218-251`

```python
# DEPOIS - Prompt explícito e detalhado
tool_selection_prompt = ChatPromptTemplate.from_messages([
    ("system", """
**FERRAMENTAS DISPONÍVEIS:**

3. `generate_and_execute_python_code`: Para análises complexas, rankings, agregações e visualizações
   - **SEMPRE USE ESTA FERRAMENTA QUANDO O USUÁRIO MENCIONAR:**
     - Palavras-chave: gráfico, chart, visualização, plotar, plot, barras, pizza, linhas, scatter
     - Análises: ranking, top N, top 10, maiores, menores, comparação, agregação
     - Cálculos: soma, média, total, percentual, proporção, estatísticas

**REGRA CRÍTICA:**
- Se a consulta contém "ranking", "top", "gráfico", "chart", "visualização" → SEMPRE use `generate_and_execute_python_code`
    """)
])
```

**Benefícios**:
- ✅ Lista explícita de palavras-chave de visualização
- ✅ Exemplos concretos de quando usar cada ferramenta
- ✅ Regra crítica destacada para cases mais comuns

### 2. Cache Inteligente com Intent Markers

**Arquivo**: `core/agents/code_gen_agent.py:160-178`

```python
# DEPOIS - Cache com contexto de intenção
query_lower = user_query.lower()
intent_markers = []

# Detectar tipo de análise
if any(word in query_lower for word in ['gráfico', 'chart', 'visualização', 'plot']):
    intent_markers.append('viz')
if any(word in query_lower for word in ['ranking', 'top']):
    intent_markers.append('rank')

# Detectar segmento específico (extrair para evitar cache cruzado)
segment_match = regex_module.search(r'(tecido|papelaria|armarinho|...)', query_lower)
if segment_match:
    intent_markers.append(f'seg_{segment_match.group(1)}')

# Gerar chave de cache única baseada em query + intenção
cache_key = hash(prompt + '_'.join(intent_markers) + (json.dumps(raw_data, sort_keys=True) if raw_data else ""))
```

**Benefícios**:
- ✅ "ranking tecidos" → cache_key: `hash("...rank_seg_tecido...")`
- ✅ "ranking papelaria" → cache_key: `hash("...rank_seg_papelaria...")`
- ✅ "gráfico de vendas" → cache_key: `hash("...viz...")`
- ✅ Evita colisões de cache entre queries semanticamente diferentes

### 3. Prompt do CodeGen com Instruções Visuais

**Arquivo**: `core/agents/code_gen_agent.py:229-252`

```python
# DEPOIS - Instruções explícitas para gráficos
system_prompt = f"""
**🎯 DETECÇÃO DE GRÁFICOS - REGRA ABSOLUTA:**
Se o usuário mencionar qualquer uma destas palavras-chave, você DEVE gerar um gráfico Plotly:
- Palavras-chave visuais: "gráfico", "chart", "visualização", "plotar", "plot", "barras", "pizza", "linhas", "scatter"
- Palavras-chave analíticas: "ranking", "top N", "top 10", "maiores", "menores", "comparação"

**FORMATO DE CÓDIGO PARA GRÁFICOS:**
```python
df = load_data()
# ... filtros e processamento ...
result = px.bar(df_filtered, x='coluna_x', y='coluna_y', title='Título do Gráfico')
```

**TIPOS DE GRÁFICOS DISPONÍVEIS:**
- px.bar() - Gráfico de barras (use para rankings, comparações)
- px.pie() - Gráfico de pizza (use para proporções)
- px.line() - Gráfico de linhas (use para tendências temporais)
- px.scatter() - Gráfico de dispersão (use para correlações)

**EXEMPLO COMPLETO - RANKING:**
```python
df = load_data()
df_filtered = df[df['NOMESEGMENTO'] == 'TECIDOS'].nlargest(10, 'VENDA_30DD')
result = px.bar(df_filtered, x='NOME', y='VENDA_30DD', title='Top 10 Produtos - Segmento Tecidos')
```
"""
```

**Benefícios**:
- ✅ Regra absoluta: se mencionar "gráfico", "ranking", "top" → GERAR GRÁFICO
- ✅ Exemplos concretos de código Plotly
- ✅ Mapeamento de tipos de análise → tipos de gráficos

## Testes Esperados

### Cenário 1: Detecção de Gráficos Explícitos

**Input**: "gere um gráfico de barras das vendas no segmento tecidos"

**Comportamento Esperado**:
1. ✅ Tool selection detecta "gráfico" → escolhe `generate_and_execute_python_code`
2. ✅ CodeGen detecta "gráfico" + "barras" → gera código com `px.bar()`
3. ✅ Retorna tipo "chart" com JSON do Plotly

### Cenário 2: Detecção de Gráficos Implícitos (Rankings)

**Input**: "ranking top 10 de vendas na papelaria"

**Comportamento Esperado**:
1. ✅ Tool selection detecta "ranking" + "top 10" → escolhe `generate_and_execute_python_code`
2. ✅ CodeGen detecta "ranking" → gera código com `px.bar()` e `.nlargest(10, 'VENDA_30DD')`
3. ✅ Retorna gráfico de barras com os top 10 produtos

### Cenário 3: Diferenciação de Segmentos

**Input 1**: "ranking vendas tecidos"
**Input 2**: "ranking vendas papelaria"

**Comportamento Esperado**:
1. ✅ Cache keys diferentes devido a `seg_tecido` vs `seg_papelaria`
2. ✅ Código gerado usa filtro correto: `df['NOMESEGMENTO'] == 'TECIDOS'` vs `'PAPELARIA'`
3. ✅ Resultados diferentes para cada segmento

## Métricas de Sucesso

1. **Taxa de Detecção de Gráficos**: 100% quando usuário menciona palavras-chave visuais
2. **Taxa de Cache Hit Correto**: 0% de falsos positivos (resultados errados do cache)
3. **Diferenciação de Segmentos**: 100% de acurácia ao distinguir segmentos diferentes

## Arquivos Modificados

1. ✅ `core/agents/caculinha_bi_agent.py` (linhas 218-251)
   - Prompt de seleção de ferramentas aprimorado

2. ✅ `core/agents/code_gen_agent.py` (linhas 160-178)
   - Sistema de cache inteligente

3. ✅ `core/agents/code_gen_agent.py` (linhas 229-252)
   - Instruções visuais no prompt do CodeGen

## Como Testar

```bash
# 1. Reiniciar a aplicação
python run_streamlit.py

# 2. Testar queries variadas:
# - "gere um gráfico de barras de vendas no segmento tecidos"
# - "ranking top 10 papelaria"
# - "ranking top 10 festas"
# - "compare vendas entre tecidos e papelaria" (deve gerar gráfico comparativo)

# 3. Verificar nos logs:
# - "🎯 Exemplos contextuais injetados no prompt" (se pattern_matcher ativo)
# - "Decisão da ferramenta: generate_and_execute_python_code"
# - "Resultado: Gráfico Plotly."
```

## Próximos Passos (Opcional)

1. **Adicionar fallback visual**: Se CodeGen não gerar gráfico quando esperado, tentar novamente com prompt reforçado
2. **Métricas de satisfação**: Logar se resultado foi tipo esperado (chart vs dataframe vs text)
3. **A/B testing**: Comparar taxa de sucesso antes/depois do fix

---

**Data**: 2025-10-12
**Status**: ✅ Implementado
**Impacto**: Alto - Resolve 2 problemas críticos de UX
