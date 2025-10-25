# 📊 Relatório de Teste - 80 Perguntas de Negócio

**Data:** 19/10/2025 10:30:45
**Versão do Sistema:** Agent Solution BI v2.0

---

## 📈 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de Perguntas** | 20 |
| **✅ Sucesso** | 19 (95.0%) |
| **❌ Erros** | 1 (5.0%) |
| **⚠️ Fallback** | 0 (0.0%) |
| **❓ Desconhecido** | 0 (0.0%) |
| **⏱️ Tempo Médio** | 5.32s |

---

## 🎯 Performance por Categoria

| Categoria | Total | ✅ Sucesso | ❌ Erro | ⚠️ Fallback | ❓ Desconhecido | Taxa Sucesso |
|-----------|-------|------------|---------|-------------|----------------|-------------|
| Vendas por Produto | 8 | 8 | 0 | 0 | 0 | 100.0% |
| Análises por Segmento | 8 | 7 | 1 | 0 | 0 | 87.5% |
| Análises por UNE/Loja | 4 | 4 | 0 | 0 | 0 | 100.0% |

---

## 📝 Resultados Detalhados

### 🎯 Vendas por Produto

#### ✅ [1/20] Gere um gráfico de vendas do produto 369947 na UNE SCR

- **Status:** `SUCCESS`
- **Tipo:** `chart`
- **Mensagem:** Processado como chart
- **Tempo:** 9.15s

#### ✅ [2/20] Mostre a evolução de vendas mensais do produto 369947 nos últimos 12 meses

- **Status:** `SUCCESS`
- **Tipo:** `text`
- **Mensagem:** Processado como text
- **Tempo:** 6.38s

#### ✅ [3/20] Compare as vendas do produto 369947 entre todas as UNEs

- **Status:** `SUCCESS`
- **Tipo:** `data`
- **Mensagem:** Dados retornados: 6 registros
- **Tempo:** 6.94s

#### ✅ [4/20] Quais são os 5 produtos mais vendidos na UNE SCR no último mês?

- **Status:** `SUCCESS`
- **Tipo:** `data`
- **Mensagem:** Dados retornados: 5 registros
- **Tempo:** 6.23s

#### ✅ [5/20] Análise de performance: produtos com vendas acima da média no segmento

- **Status:** `SUCCESS`
- **Tipo:** `data`
- **Mensagem:** Dados retornados: 342 registros
- **Tempo:** 4.29s

---

### 🏪 Análises por Segmento

#### ✅ [9/20] Quais são os 10 produtos que mais vendem no segmento TECIDOS?

- **Status:** `SUCCESS`
- **Tipo:** `data`
- **Mensagem:** Dados retornados: 10 registros
- **Tempo:** 5.82s

#### ❌ [10/20] Compare as vendas entre os segmentos ARMARINHO E CONFECÇÃO vs TECIDOS

- **Status:** `ERROR`
- **Tipo:** `null`
- **Mensagem:** Timeout na execução da query
- **Tempo:** 30.00s
- **⚠️ Erro:** `Timeout na execução da query`

---

## 🔍 Análise de Erros

**Total de Erros:** 1

- **[10]** Compare as vendas entre os segmentos ARMARINHO E CONFECÇÃO vs TECIDOS
  - Erro: `Timeout na execução da query`

---

## ⚠️ Perguntas que Requerem Fallback (LLM)

✅ **Nenhum fallback necessário!**

---

## 📊 Distribuição de Tipos de Resposta

| Tipo | Quantidade | Percentual |
|------|------------|------------|
| `data` | 14 | 70.0% |
| `text` | 5 | 25.0% |
| `chart` | 1 | 5.0% |

---

## 🎯 Conclusões

### ✅ **EXCELENTE!**

O sistema alcançou 95.0% de taxa de sucesso, demonstrando alta confiabilidade.

### Recomendações:

1. ⚠️ Investigar e corrigir 1 erros identificados
4. ⏱️ Otimizar performance (tempo médio: 5.32s)

---

**Relatório gerado automaticamente pelo Agent Solution BI**
*Timestamp: 2025-10-19T10:30:45.123456*
