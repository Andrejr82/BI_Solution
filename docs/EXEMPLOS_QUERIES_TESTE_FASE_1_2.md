# EXEMPLOS DE QUERIES PARA TESTE - FASE 1.2
## Sistema de Detecção de Queries Amplas

**Data:** 2025-10-29
**Versão:** 2.1.0

---

## 🎯 OBJETIVO DOS TESTES

Validar que o sistema detecta corretamente:
- ✅ Queries amplas que causam timeout (DEVEM ser bloqueadas)
- ✅ Queries específicas válidas (NÃO devem ser bloqueadas)

---

## ❌ QUERIES AMPLAS (Devem ser BLOQUEADAS)

### Categoria 1: Keywords de Amplitude Explícitas

| # | Query | Razão Esperada |
|---|-------|----------------|
| 1 | "Mostre todos os produtos" | Keyword "todos" sem filtros |
| 2 | "Liste todas as vendas" | Keyword "todas" sem filtros |
| 3 | "Quero ver tudo de estoque" | Keyword "tudo" sem filtros |
| 4 | "Análise geral de produtos" | Keyword "geral" sem filtros |
| 5 | "Todos os dados disponíveis" | Keyword "todos" sem filtros |
| 6 | "Dados completos de estoque" | Keyword "completos" sem filtros |
| 7 | "Mostre tudo sobre vendas" | Keyword "tudo" sem filtros |
| 8 | "Informações totais de produtos" | Keyword "totais" sem filtros |

**Mensagem esperada:**
```
🔍 Query Muito Ampla Detectada
[...mensagem educativa com exemplos...]
```

---

### Categoria 2: Ranking/Comparação Sem Limite

| # | Query | Razão Esperada |
|---|-------|----------------|
| 9 | "Ranking de todas as UNEs" | Ranking sem limite numérico |
| 10 | "Comparar todos os segmentos" | Comparação sem limite |
| 11 | "Ranking geral de produtos" | Ranking sem filtros específicos |
| 12 | "Comparação de todas as vendas" | Comparação ampla |

**Mensagem esperada:**
```
🔍 Query Muito Ampla Detectada
💡 Sugestão: Tente 'Top 15 UNEs por volume de vendas'
```

---

### Categoria 3: Queries Genéricas Sem Filtros

| # | Query | Razão Esperada |
|---|-------|----------------|
| 13 | "Mostre os produtos" | Sem UNE, limite ou filtros |
| 14 | "Liste as vendas" | Sem período, UNE ou filtros |
| 15 | "Dados de estoque" | Sem UNE ou filtros específicos |
| 16 | "Análise de produtos" | Sem contexto ou limite |

**Nota:** Estas podem ser casos limítrofes - validar comportamento.

---

## ✅ QUERIES ESPECÍFICAS (NÃO devem ser bloqueadas)

### Categoria 1: Com Limite Numérico (Top N)

| # | Query | Por Que É Válida |
|---|-------|-----------------|
| 1 | "Top 10 produtos mais vendidos da UNE NIG" | Limite + UNE específica |
| 2 | "Top 20 clientes com maior faturamento" | Limite numérico claro |
| 3 | "5 fornecedores com maior volume" | Número específico |
| 4 | "Últimos 15 pedidos da UNE BEL" | Limite + UNE |
| 5 | "Primeiros 30 produtos em estoque" | Limite numérico |

**Comportamento esperado:** Gerar código normalmente.

---

### Categoria 2: Com Filtros Específicos

| # | Query | Por Que É Válida |
|---|-------|-----------------|
| 6 | "Produtos do segmento ARMARINHO com estoque < 10" | Filtro de segmento + condição |
| 7 | "Produtos da categoria FERRAMENTAS com preço > 100" | Categoria + condição |
| 8 | "Produtos em falta de estoque da UNE RIO" | UNE + condição específica |
| 9 | "Itens com estoque crítico (< 5 unidades)" | Condição numérica |
| 10 | "Produtos com preço entre 50 e 200 reais" | Range específico |

**Comportamento esperado:** Gerar código normalmente.

---

### Categoria 3: Com UNE Específica

| # | Query | Por Que É Válida |
|---|-------|-----------------|
| 11 | "Vendas da UNE BEL nos últimos 30 dias" | UNE + período |
| 12 | "Estoque atual da UNE SAO" | UNE específica |
| 13 | "Análise de vendas da UNE NIG" | UNE identificada |
| 14 | "Produtos mais vendidos da UNE RIO" | UNE específica |
| 15 | "Faturamento da unidade BEL este mês" | UNE + período |

**Comportamento esperado:** Gerar código normalmente.

---

### Categoria 4: Com Período Definido

| # | Query | Por Que É Válida |
|---|-------|-----------------|
| 16 | "Vendas dos últimos 7 dias" | Período específico |
| 17 | "Produtos vendidos hoje" | Período definido |
| 18 | "Análise do mês atual" | Período claro |
| 19 | "Dados da última semana" | Período específico |
| 20 | "Vendas de janeiro de 2025" | Período bem definido |

**Comportamento esperado:** Gerar código normalmente.

---

## 🧪 SCRIPT DE TESTE MANUAL

### Como Testar via Streamlit

```bash
# 1. Iniciar aplicação
streamlit run streamlit_app.py

# 2. Na interface, testar as queries acima
# 3. Observar comportamento:
#    - Queries amplas: mostrar mensagem educativa
#    - Queries específicas: gerar e executar código
```

---

### Como Testar via Script Python

```python
# Arquivo: scripts/test_manual_queries.py

from core.agents.code_gen_agent import CodeGenAgent

# Criar agente (sem LLM para teste rápido)
agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

# Testar queries amplas
broad_queries = [
    "Mostre todos os produtos",
    "Liste todas as vendas",
    "Ranking de todas as UNEs"
]

print("TESTANDO QUERIES AMPLAS:")
print("=" * 60)
for query in broad_queries:
    is_broad, reason = agent.detect_broad_query(query)
    print(f"Query: {query}")
    print(f"Detectada como ampla: {is_broad}")
    print(f"Razão: {reason}")
    print()

# Testar queries específicas
specific_queries = [
    "Top 10 produtos da UNE NIG",
    "Vendas da UNE BEL últimos 30 dias",
    "Produtos com estoque < 10"
]

print("\nTESTANDO QUERIES ESPECÍFICAS:")
print("=" * 60)
for query in specific_queries:
    is_broad, reason = agent.detect_broad_query(query)
    print(f"Query: {query}")
    print(f"Detectada como ampla: {is_broad} (esperado: False)")
    print(f"Razão: {reason}")
    print()
```

---

## 📊 CASOS ESPECIAIS

### Casos Limítrofes (Gray Area)

Estas queries podem ter comportamento ambíguo:

| Query | Pode Ser Válida? | Depende De |
|-------|-----------------|------------|
| "Produtos vendidos" | Talvez | Se tiver contexto implícito |
| "Estoque disponível" | Talvez | Se interface já filtrou UNE |
| "Análise de vendas" | Talvez | Se período já selecionado |

**Recomendação:** Para casos ambíguos, priorizar **educação** do usuário.

---

### Queries Multi-Intenção

Queries que combinam múltiplos conceitos:

| # | Query | Decisão Esperada |
|---|-------|-----------------|
| 1 | "Top 10 de todos os produtos" | ✅ Específica (tem Top 10) |
| 2 | "Todos os top 20 produtos" | ✅ Específica (tem Top 20) |
| 3 | "Ranking completo limitado a 15" | ✅ Específica (tem limite) |

---

## 📈 MÉTRICAS DE SUCESSO

### Critérios de Validação

| Métrica | Meta | Como Medir |
|---------|------|------------|
| Acurácia geral | ≥ 90% | (Corretos / Total) × 100 |
| Falsos positivos | < 10% | Válidas bloqueadas / Total válidas |
| Falsos negativos | < 20% | Amplas não detectadas / Total amplas |
| Tempo de resposta | < 100ms | Tempo de detect_broad_query() |

---

### Como Calcular Acurácia

```python
# Total de casos de teste
total_broad = 16      # Queries amplas
total_specific = 20   # Queries específicas
total = total_broad + total_specific  # 36 queries

# Executar testes
correct_broad = 0     # Amplas detectadas corretamente
correct_specific = 0  # Específicas não bloqueadas

# Calcular
correct = correct_broad + correct_specific
accuracy = (correct / total) * 100

print(f"Acurácia: {accuracy:.1f}%")
```

---

## 🔍 DEBUGGING

### Verificar Detecção Individual

```python
from core.agents.code_gen_agent import CodeGenAgent

agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

# Testar uma query específica
query = "Mostre todos os produtos"
is_broad, reason = agent.detect_broad_query(query)

print(f"Query: {query}")
print(f"É ampla? {is_broad}")
print(f"Razão: {reason}")

# Se ampla, ver mensagem educativa
if is_broad:
    message = agent.get_educational_message(query, reason)
    print("\nMensagem educativa:")
    print(message)
```

---

### Verificar Log de Detecções

```python
import json
from pathlib import Path

log_file = Path("data/learning/broad_queries_detected.jsonl")

if log_file.exists():
    with open(log_file, "r", encoding="utf-8") as f:
        detections = [json.loads(line) for line in f if line.strip()]

    print(f"Total de detecções: {len(detections)}")
    print("\nÚltimas 5 detecções:")
    for detection in detections[-5:]:
        print(f"  - {detection['question']}")
        print(f"    Razão: {detection['reason']}")
        print()
```

---

### Verificar Estatísticas

```python
from core.agents.code_gen_agent import CodeGenAgent

agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

stats = agent.get_broad_query_statistics()

print("Estatísticas de Detecção:")
print(f"Total detectado: {stats['total_detected']}")
print(f"\nRazões:")
for reason, count in stats['detection_reasons'].items():
    print(f"  - {reason}: {count}")
```

---

## 📝 CHECKLIST DE TESTES

### Antes de Colocar em Produção

- [ ] Executar `python scripts/test_broad_query_detection.py`
- [ ] Validar acurácia ≥ 90%
- [ ] Testar 5 queries amplas manualmente via Streamlit
- [ ] Testar 5 queries específicas manualmente via Streamlit
- [ ] Verificar mensagem educativa é clara
- [ ] Confirmar que log está sendo criado
- [ ] Testar estatísticas: `agent.get_broad_query_statistics()`
- [ ] Validar casos limítrofes
- [ ] Conferir documentação completa

### Durante 1ª Semana em Produção

- [ ] Monitorar log diariamente
- [ ] Coletar feedback dos usuários
- [ ] Identificar falsos positivos
- [ ] Ajustar keywords se necessário
- [ ] Medir redução de timeouts
- [ ] Validar meta de 60% de redução

---

## 🎓 BOAS PRÁTICAS

### Para Usuários

1. **Sempre especifique uma UNE**
   - ✅ "Produtos da UNE NIG"
   - ❌ "Produtos"

2. **Use limites numéricos**
   - ✅ "Top 10 vendas"
   - ❌ "Todas as vendas"

3. **Adicione filtros**
   - ✅ "Produtos com estoque < 10"
   - ❌ "Produtos em estoque"

4. **Defina períodos**
   - ✅ "Vendas dos últimos 30 dias"
   - ❌ "Vendas"

---

## 🚀 EXEMPLOS PRONTOS PARA COPIAR/COLAR

### Queries Garantidamente Válidas

```
Top 10 produtos mais vendidos da UNE NIG
Produtos do segmento ARMARINHO com estoque menor que 10
Vendas da UNE BEL nos últimos 30 dias
5 fornecedores com maior volume de compras
Produtos da categoria FERRAMENTAS com preço acima de R$ 100
Estoque atual da UNE SAO para produtos críticos
Top 20 clientes com maior faturamento
Produtos em falta de estoque da UNE RIO
Análise de vendas por segmento (limitado a 15 segmentos)
Ranking de UNEs por volume de vendas (últimos 90 dias)
```

### Queries Garantidamente Bloqueadas

```
Mostre todos os produtos
Liste todas as vendas
Quero ver tudo de estoque
Análise geral de produtos
Todos os dados disponíveis
Ranking de todas as UNEs
Comparar todos os segmentos
Dados completos
```

---

**Documento criado por:** Code Agent
**Data:** 2025-10-29
**Versão:** 1.0
**Para:** FASE 1.2 - Sistema de Detecção de Queries Amplas
