# 🧪 Guia de Execução dos Testes de Regressão

**Data:** 30/10/2025
**Versão:** 1.0

---

## 📋 Visão Geral

Este diretório contém scripts de teste para validar as correções implementadas no roadmap LLM.

### Scripts Disponíveis

| Script | Queries | Tempo | Uso |
|--------|---------|-------|-----|
| `test_regression_validation.py` | 30 | 5-10 min | Teste completo |
| `test_regression_quick.py` | 3 | 1-2 min | Smoke test |

---

## ⚙️ Pré-requisitos

1. **Arquivo .env configurado** na raiz do projeto com:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

2. **Dependências instaladas:**
   ```bash
   pip install python-dotenv
   ```

---

## 🚀 Como Executar

### **Opção 1: Teste Completo (Recomendado)**

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python scripts/tests/test_regression_validation.py
```

**O que faz:**
- Testa 30 queries em 8 categorias
- Gera relatório detalhado
- Salva JSON e Markdown

**Saídas:**
- Console: Relatório ASCII formatado
- `data/reports/test_regression_results_YYYYMMDD_HHMMSS.json`
- `data/reports/test_regression_report_YYYYMMDD_HHMMSS.md`

**Tempo estimado:** 5-10 minutos

---

### **Opção 2: Teste Rápido (Smoke Test)**

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python scripts/tests/test_regression_quick.py
```

**O que faz:**
- Testa 3 queries essenciais
- Validação rápida
- Saída apenas no console

**Tempo estimado:** 1-2 minutos

---

## 📊 Interpretando os Resultados

### **Console Output**

```
================================================================================
                   RELATORIO DE TESTES DE REGRESSAO
                           30/10/2025 20:50:00
================================================================================

RESUMO GERAL
--------------------------------------------------------------------------------
  Total de Queries Testadas: 30
  [OK] Sucessos: 25 (83.3%)
  [FAIL] Falhas: 5 (16.7%)

  Meta do Roadmap: 95% de taxa de sucesso
  [AVISO] Faltam 11.7% para atingir meta

RESULTADOS POR CATEGORIA
--------------------------------------------------------------------------------

  [OK] GRAFICOS_TEMPORAIS
     Sucesso: 4/4 (100.0%)

  [OK] RANKINGS
     Sucesso: 4/4 (100.0%)

  [WARN] TOP_N
     Sucesso: 3/4 (75.0%)
```

### **Critérios de Sucesso**

| Status | Taxa | Significado |
|--------|------|-------------|
| [OK] | ≥ 90% | Excelente |
| [WARN] | 70-89% | Atenção necessária |
| [FAIL] | < 70% | Requer correção |

---

## 🐛 Troubleshooting

### **Erro: "GEMINI_API_KEY não encontrada"**

**Solução:**
1. Verificar arquivo `.env` na raiz do projeto
2. Confirmar que contém: `GEMINI_API_KEY=...`
3. Recarregar ou reiniciar terminal

---

### **Erro: "No module named 'dotenv'"**

**Solução:**
```bash
pip install python-dotenv
```

---

### **Erro: "No module named 'faiss'"**

**Solução:**
```bash
pip install faiss-cpu
```

---

### **Testes muito lentos**

**Causas possíveis:**
- Rate limit da API Gemini
- Cache desabilitado
- Muitas queries em paralelo

**Solução:**
- Use `test_regression_quick.py` para teste mais rápido
- Aguarde alguns minutos entre execuções
- Verifique `enable_cache=True` no código

---

## 📈 Categorias de Teste

### **1. Gráficos Temporais** (4 queries)
Valida correção de 30/10 para gráficos de evolução:
- `ValueError` de colunas ausentes
- Validações rígidas removidas
- Melhores práticas Plotly

### **2. Rankings** (4 queries)
Valida Few-Shot Learning:
- Rankings completos sem limite
- Ordenação correta
- Padrões reconhecidos

### **3. Top N** (4 queries)
Valida Column Validator:
- Limite correto (top 10 = 10 linhas)
- Validação de "top N"
- Extração de número

### **4. Agregações** (4 queries)
Valida operações básicas:
- Soma, média, total
- Filtros por segmento/UNE
- Resultados numéricos corretos

### **5. Comparações** (3 queries)
Valida comparações entre entidades:
- UNE vs UNE
- Segmento vs Segmento
- Múltiplos grupos

### **6. Validação de Colunas** (3 queries)
Valida correção automática:
- Maiúscula/minúscula
- Sinônimos (venda_30_d → venda_30dd)
- Colunas essenciais

### **7. Queries Amplas** (3 queries)
Valida fallback:
- Mensagem de clarificação
- Sugestões úteis
- Sem timeout

### **8. Gráficos Complexos** (3 queries)
Valida tipos de gráficos:
- Barras, pizza, dispersão
- Configurações Plotly
- Interatividade

---

## 📝 Logs Gerados

### **Durante Execução**
```
2025-10-30 20:50:00 - INFO - [START] INICIANDO TESTES DE REGRESSAO
2025-10-30 20:50:05 - INFO - [TEST] Testando [graficos_temporais]: gere um gráfico...
2025-10-30 20:50:12 - INFO - [OK] SUCESSO (3.2s) - Tipo: chart
```

### **Após Conclusão**
- `data/reports/test_regression_results_20251030_205000.json`
- `data/reports/test_regression_report_20251030_205000.md`

---

## 🎯 Métricas Esperadas

| Métrica | Baseline | Meta | Excelente |
|---------|----------|------|-----------|
| Taxa de Sucesso | 60% | 85% | 95% |
| Tempo Médio | 4.5s | 3.5s | 2.0s |
| Erros de Coluna | 33% | 3% | 0% |
| Erros de Timeout | 40% | 10% | 0% |

---

## 📚 Documentação Relacionada

1. [OPCAO_1_MONITORAMENTO_30102025.md](../../docs/reports/OPCAO_1_MONITORAMENTO_30102025.md) - Guia completo de monitoramento
2. [RESUMO_SESSAO_30102025.md](../../docs/reports/RESUMO_SESSAO_30102025.md) - Resumo da sessão
3. [CORRECAO_ERROS_GRAFICOS_20251030.md](../../docs/reports/CORRECAO_ERROS_GRAFICOS_20251030.md) - Correções implementadas

---

## ✅ Checklist de Execução

Antes de executar:
- [ ] Arquivo `.env` configurado com `GEMINI_API_KEY`
- [ ] Dependências instaladas (`python-dotenv`, `faiss-cpu`)
- [ ] Terminal na raiz do projeto

Durante execução:
- [ ] Acompanhar logs no console
- [ ] Verificar erros em tempo real
- [ ] Aguardar conclusão completa

Após execução:
- [ ] Verificar taxa de sucesso >= 85%
- [ ] Analisar erros (se houver)
- [ ] Revisar relatório markdown gerado
- [ ] Comparar com métricas baseline

---

## 🔄 Frequência Recomendada

- **Smoke Test (`quick`):** Diário (manhã)
- **Teste Completo (`validation`):** Semanal (segunda-feira)
- **Após Correções:** Sempre após mudanças no código

---

## 💡 Dicas

1. **Execute o smoke test primeiro** para validação rápida
2. **Aguarde alguns minutos** entre execuções para evitar rate limit
3. **Compare resultados** com execuções anteriores
4. **Documente anomalias** encontradas
5. **Compartilhe relatórios** com a equipe

---

**Última Atualização:** 30/10/2025 21:00
**Autor:** Claude Code & Equipe Agent_Solution_BI
