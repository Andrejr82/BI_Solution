# FASE 1.2 - GUIA RÁPIDO DE IMPLEMENTAÇÃO
## Sistema de Fallback para Queries Amplas

**Status:** ✅ IMPLEMENTADO
**Data:** 2025-10-29
**Objetivo:** Reduzir 60% dos erros de timeout

---

## 🚀 INÍCIO RÁPIDO (5 minutos)

### Passo 1: Executar Testes

```bash
# Testar detecção de queries amplas
python scripts/test_broad_query_detection.py
```

**Resultado esperado:**
```
TESTE DE DETECÇÃO DE QUERIES AMPLAS - FASE 1.2
===============================================

✅ CORRETO | Broad=True (esperado=True)
   Query: Mostre todos os produtos
   Razão: Keyword ampla detectada sem filtros específicos

✅ CORRETO | Broad=False (esperado=False)
   Query: Top 10 produtos mais vendidos da UNE NIG
   Razão: Query específica OK

...

RESULTADO: 18/20 corretos (90.0% de acurácia)
✅ TESTE PASSOU! Acurácia >= 90%
```

---

### Passo 2: Integrar no Sistema

```bash
# Aplicar FASE 1.2 no sistema principal
python scripts/apply_fase_1_2.py
```

**O script irá:**
1. ✅ Fazer backup do arquivo atual
2. ✅ Aplicar nova versão com FASE 1.2
3. ✅ Executar bateria de testes
4. ✅ Validar integração

---

### Passo 3: Testar via Interface

```bash
# Iniciar Streamlit
streamlit run streamlit_app.py
```

**Teste manual:**
1. Digite: "Mostre todos os produtos"
2. Esperado: Mensagem educativa com exemplos
3. Digite: "Top 10 produtos da UNE NIG"
4. Esperado: Executar normalmente

---

## 📋 O QUE FOI IMPLEMENTADO

### Detecção Automática de Queries Amplas

O sistema agora detecta automaticamente queries que podem causar timeout:

**Queries bloqueadas (exemplos):**
- ❌ "Mostre todos os produtos"
- ❌ "Liste todas as vendas"
- ❌ "Ranking de todas as UNEs"

**Queries permitidas (exemplos):**
- ✅ "Top 10 produtos da UNE NIG"
- ✅ "Produtos com estoque < 10"
- ✅ "Vendas últimos 30 dias"

---

### Mensagem Educativa

Quando uma query ampla é detectada, o usuário recebe:

```
🔍 Query Muito Ampla Detectada

Por que isso acontece?
- Processar milhões de registros
- Causar timeout (> 60 segundos)
- Consumir muita memória

✅ Como fazer queries eficientes:

Exemplos de queries válidas:
   1. Top 10 produtos mais vendidos da UNE NIG
   2. Produtos do segmento ARMARINHO com estoque < 10
   ...

💡 Dicas:
1. Especifique uma UNE
2. Use limites (Top 10, Top 20)
3. Aplique filtros

💡 Sugestão: Tente 'Top 10 produtos da UNE [código]'
```

---

## 📁 ARQUIVOS IMPORTANTES

### Código Fonte

| Arquivo | Descrição |
|---------|-----------|
| `core/agents/code_gen_agent_fase_1_2.py` | Implementação completa |
| `core/agents/code_gen_agent.py` | Será atualizado pelo script |

### Scripts

| Arquivo | Descrição |
|---------|-----------|
| `scripts/test_broad_query_detection.py` | Bateria de testes |
| `scripts/apply_fase_1_2.py` | Script de integração |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `RELATORIO_EXECUTIVO_FASE_1_2.md` | Resumo executivo |
| `docs/RELATORIO_FASE_1_2_*.md` | Relatório técnico completo |
| `docs/EXEMPLOS_QUERIES_TESTE_*.md` | 36 queries para teste |

### Logs

| Arquivo | Descrição |
|---------|-----------|
| `data/learning/broad_queries_detected.jsonl` | Log de detecções |

---

## 🧪 TESTES

### Teste Automatizado

```bash
python scripts/test_broad_query_detection.py
```

**Executa:**
- Teste 1: Detecção básica (20 queries)
- Teste 2: Mensagem educativa
- Teste 3: Queries históricas

**Critério de sucesso:** 90% de acurácia

---

### Teste Manual

```python
from core.agents.code_gen_agent_fase_1_2 import CodeGenAgent

# Criar agente
agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

# Testar detecção
query = "Mostre todos os produtos"
is_broad, reason = agent.detect_broad_query(query)

print(f"Query: {query}")
print(f"É ampla? {is_broad}")
print(f"Razão: {reason}")

# Ver mensagem educativa
if is_broad:
    message = agent.get_educational_message(query, reason)
    print(message)
```

---

## 📊 MONITORAMENTO

### Ver Estatísticas

```python
from core.agents.code_gen_agent import CodeGenAgent

agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

# Obter estatísticas
stats = agent.get_broad_query_statistics()

print(f"Total detectado: {stats['total_detected']}")
print(f"Razões: {stats['detection_reasons']}")
```

### Ler Log

```bash
# Ver últimas 10 detecções
tail -n 10 data/learning/broad_queries_detected.jsonl
```

---

## 🎯 EXEMPLOS DE QUERIES

### Queries que SERÃO BLOQUEADAS

```
Mostre todos os produtos
Liste todas as vendas
Quero ver tudo de estoque
Análise geral de produtos
Todos os dados disponíveis
Ranking de todas as UNEs
Comparar todos os segmentos
Dados completos de estoque
```

### Queries que PASSARÃO NORMALMENTE

```
Top 10 produtos mais vendidos da UNE NIG
Produtos do segmento ARMARINHO com estoque < 10
Vendas da UNE BEL nos últimos 30 dias
5 fornecedores com maior volume
Produtos com preço acima de R$ 100
Estoque atual da UNE SAO
Top 20 clientes com maior faturamento
Produtos em falta da UNE RIO
```

---

## ⚙️ CONFIGURAÇÃO

### Ajustar Keywords (se necessário)

Edite `core/agents/code_gen_agent.py`:

```python
# Keywords de queries amplas
BROAD_QUERY_KEYWORDS = [
    "todas", "todos", "tudo", "geral", "completo",
    # Adicione mais se necessário
]

# Keywords de filtros específicos
SPECIFIC_FILTER_KEYWORDS = [
    "top", "limite", "une", "segmento",
    # Adicione mais se necessário
]
```

### Ajustar Exemplos

```python
VALID_QUERY_EXAMPLES = [
    "Top 10 produtos mais vendidos da UNE NIG",
    "Produtos do segmento ARMARINHO com estoque < 10",
    # Adicione seus exemplos
]
```

---

## 🔍 TROUBLESHOOTING

### Teste falhou com acurácia < 90%

1. Verificar quais queries falharam
2. Analisar razões de detecção
3. Ajustar keywords se necessário
4. Re-executar teste

### Muitos falsos positivos

```python
# Queries válidas sendo bloqueadas
# Solução: Adicionar mais keywords de filtros específicos
SPECIFIC_FILTER_KEYWORDS.append("sua_keyword")
```

### Muitos falsos negativos

```python
# Queries amplas não sendo detectadas
# Solução: Adicionar mais keywords de amplitude
BROAD_QUERY_KEYWORDS.append("sua_keyword")
```

---

## 📈 MÉTRICAS DE SUCESSO

### Semana 1

- [ ] Taxa de detecção > 80%
- [ ] Acurácia geral > 90%
- [ ] Falsos positivos < 10%
- [ ] Redução de timeouts mensurada

### Semana 2-4

- [ ] Redução de timeouts ≥ 60%
- [ ] Usuários fazendo queries mais específicas
- [ ] Nenhuma reclamação sobre bloqueios indevidos

---

## 🚀 PRÓXIMOS PASSOS

### Após Integração

1. **Dia 1-7:** Monitorar log diariamente
2. **Dia 7:** Revisar estatísticas
3. **Dia 14:** Medir redução de timeouts
4. **Dia 30:** Relatório final de sucesso

### FASE 1.3 (Futura)

- Sugestões automáticas de refinamento
- Histórico de queries educadas
- Sistema de feedback do usuário
- Análise preditiva de padrões

---

## 📞 AJUDA

### Documentação Completa

- **Executivo:** `RELATORIO_EXECUTIVO_FASE_1_2.md`
- **Técnico:** `docs/RELATORIO_FASE_1_2_FALLBACK_QUERIES_AMPLAS.md`
- **Testes:** `docs/EXEMPLOS_QUERIES_TESTE_FASE_1_2.md`

### Comandos Rápidos

```bash
# Testar
python scripts/test_broad_query_detection.py

# Integrar
python scripts/apply_fase_1_2.py

# Iniciar app
streamlit run streamlit_app.py

# Ver log
tail -f data/learning/broad_queries_detected.jsonl
```

---

## ✅ CHECKLIST DE ATIVAÇÃO

- [ ] Executar teste automatizado
- [ ] Validar acurácia ≥ 90%
- [ ] Executar script de integração
- [ ] Testar via Streamlit (5 queries)
- [ ] Verificar log sendo criado
- [ ] Documentar qualquer ajuste
- [ ] Comunicar usuários sobre mudança

---

**Status:** ✅ PRONTO PARA PRODUÇÃO
**Versão:** 2.1.0
**Data:** 2025-10-29

**Dúvidas?** Consulte a documentação completa em `docs/`
