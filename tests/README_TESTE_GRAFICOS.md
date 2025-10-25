# 🎨 Teste de Validação de Gráficos

## 📋 Descrição

Teste específico para validar as correções implementadas em **19/10/2025**:

1. ✅ **max_tokens aumentado para 4096** - Permite que a LLM gere código Plotly completo
2. ✅ **load_data() usando Dask** - Lazy loading para evitar erros de memória
3. ✅ **Instruções sobre Dask no prompt** - LLM gera código otimizado com predicate pushdown

## 🎯 Objetivo

Executar **10 queries explícitas de gráfico** (em vez das 80 perguntas completas) para validar rapidamente:

- ✅ LLM consegue gerar código Plotly (max_tokens suficiente)
- ✅ Código usa Dask corretamente (.compute() após filtros)
- ✅ Sem erros de memória (malloc failed)
- ✅ Performance aceitável (<15s por query)

## 🚀 Como Executar

```bash
cd "C:\Users\André\Documents\Agent_Solution_BI"
python tests\test_validacao_graficos.py
```

## ⏱️ Tempo Estimado

**3-5 minutos** (vs 10-12 minutos do teste completo de 80 perguntas)

## 📊 Tipos de Gráficos Testados

O teste cobre os principais tipos de gráfico:

1. **Gráficos de Barras** (3 queries)
   - Vendas por período
   - Estoque de produtos
   - Vendas por dia

2. **Gráficos de Linha** (2 queries)
   - Evolução temporal
   - Tendências

3. **Gráficos de Pizza** (2 queries)
   - Distribuição por UNE
   - Participação de mercado

4. **Múltiplos Gráficos** (2 queries)
   - Comparações entre produtos
   - Comparações estoque vs venda

5. **Gráficos com Cálculo** (1 query)
   - Relações entre métricas

## 📈 Critérios de Sucesso

### ✅ Excelente
- Taxa de gráficos ≥ 70%
- Tempo médio ≤ 10s

### ✅ Bom
- Taxa de gráficos ≥ 50%
- Tempo médio ≤ 15s

### ⚠️ Aceitável
- Taxa de gráficos ≥ 20%

### ❌ Problema
- Taxa de gráficos < 20%
- Necessário investigar logs

## 📊 Saída do Teste

### Console
Exibe em tempo real:
- Progresso de cada query (1/10, 2/10, etc.)
- Status de sucesso/erro
- Tempo de execução
- Resumo final com análise

### Arquivo JSON
Salvo em: `tests/relatorio_validacao_graficos_[timestamp].json`

Contém:
```json
{
  "data": "2025-10-19T...",
  "objetivo": "Validar correções de max_tokens e Dask",
  "queries_executadas": 10,
  "metricas": {
    "graficos_gerados": 8,
    "taxa_graficos": 80.0,
    "taxa_sucesso": 100.0,
    "tempo_medio": 8.5,
    "tempo_total": 85.0
  },
  "baseline": {
    "taxa_graficos": 0,
    "tempo_medio": 17.45
  },
  "resultados_detalhados": [...]
}
```

## 🎯 Próximos Passos

O teste sugere automaticamente os próximos passos:

### Se PASSOU (≥50% gráficos)
```bash
python tests\test_80_perguntas_completo.py
```
Executar teste completo das 80 perguntas

### Se PARCIAL (20-50% gráficos)
- Analisar logs em `data/query_history/`
- Analisar logs em `data/learning/`
- Identificar padrões de falha

### Se FALHOU (<20% gráficos)
```bash
python tests\test_debug_grafico.py
```
Executar diagnóstico detalhado com uma única query

## 📋 Comparação com Baseline

### Baseline (Antes das Correções)
- Gráficos: **0%** (0/80)
- Tempo médio: **17.45s**
- Taxa de sucesso: 100%

### Esperado (Após Correções)
- Gráficos: **70-80%** (7-8/10)
- Tempo médio: **8-10s**
- Taxa de sucesso: 100%

## 🔍 Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Certifique-se de estar no diretório correto
cd "C:\Users\André\Documents\Agent_Solution_BI"

# Execute com python
python tests\test_validacao_graficos.py
```

### Erro: API Key não encontrada
Verifique se o arquivo `.env` contém:
```bash
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MAX_TOKENS=4096
```

### Timeout/Erro de Memória
Se persistir após as correções:
1. Verificar logs detalhados
2. Validar que `load_data()` está usando Dask
3. Verificar que `max_tokens=4096` está configurado

## 📚 Documentação Relacionada

- `CORRECOES_IMPLEMENTADAS_19_10_2025.md` - Detalhes completos das correções
- `tests/test_80_perguntas_completo.py` - Teste completo das 80 perguntas
- `tests/test_debug_grafico.py` - Diagnóstico de query única
- `MELHORIAS_IMPLEMENTADAS_V2.md` - Histórico de melhorias

---

**Criado em:** 19/10/2025
**Autor:** Sistema Agent_Solution_BI
**Versão:** 1.0
