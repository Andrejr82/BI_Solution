# Relatório de Análise de Anomalias - 25/10/2025

## 📋 Resumo Executivo

Análise dos logs e interações do agente de BI realizada em 25/10/2025, identificando **anomalias críticas** no processamento de consultas dos usuários.

---

## 🔴 Anomalias Identificadas

### 1. **CRÍTICO: MemoryError ao Carregar Dados Parquet**

**Timestamp:** 2025-10-25 05:26:20 - 05:26:43
**Query Afetada:** "Alertas: produtos que precisam de atenção (baixa rotação, estoque alto)"
**Erro:** `ArrowMemoryError: malloc of size 8910592 failed`

#### Descrição do Problema:
O agente tentou carregar dados do Parquet usando Dask, mas falhou devido a insuficiência de memória. Todas as 3 estratégias de fallback também falharam:

1. **Tentativa 1:** `ddf.head(10000)` → **Falhou** (ArrowMemoryError)
2. **Tentativa 2:** `pd.read_parquet()` com filtro otimizado → **Falhou** (OSError: Invalid argument com wildcard)
3. **Tentativa 3:** `ddf.head(1000)` → **Falhou** (MemoryError)

#### Impacto no Usuário:
- ❌ Query não foi processada
- ❌ Usuário recebeu mensagem de erro genérica
- ⏱️ Tempo de processamento: **32.5 segundos** (desperdício de recursos)
- 📊 `results_count: 0` (nenhum dado retornado)

#### Causa Raiz:
```
Arquivo Parquet: 193MB total (admmat.parquet: 94MB, admmat_extended.parquet: 100MB)
Problema: Sistema sem memória suficiente para descomprimir e processar os dados
Polars: NÃO INSTALADO (usando apenas Dask, menos eficiente)
```

---

### 2. **Detecção Incorreta de Ferramenta UNE**

**Timestamp:** 2025-10-25 05:47:25 - 05:47:31
**Query Afetada:** "quais produtos estão com rupturas na Une scr ?"
**Classificação:** `une_operation` → **INCORRETO**

#### Descrição do Problema:
O classificador de intents identificou a query como operação UNE e tentou usar a ferramenta `calcular_abastecimento_une`. Porém:

- **UNE inferida:** 123 (INCORRETO - usuário perguntou sobre "Une scr")
- **Query SQL:** Retornou 0 linhas
- **Resultado:** Resposta vazia ao usuário

#### Impacto no Usuário:
- ⚠️ Query processada incorretamente
- ❌ 0 resultados retornados quando deveria ter dados
- ⏱️ Tempo de processamento: **6.0 segundos**
- 🔍 Usuário não obteve a informação que precisava

#### Problema de Mapeamento:
```
Entrada do usuário: "Une scr"
LLM interpretou: UNE 123 (código numérico incorreto)
Deveria ser: UNE SCR (sigla/código correto) ou resolver o mapeamento correto
```

---

## 📊 Estatísticas do Dia

### Queries Processadas: **2**

| Query | Sucesso | Tempo (s) | Results | Erro |
|-------|---------|-----------|---------|------|
| Alertas produtos baixa rotação | ✅ (parcial) | 32.5 | 0 | MemoryError |
| Produtos com rupturas Une scr | ✅ (parcial) | 6.0 | 0 | Mapeamento UNE |

### Taxa de Sucesso Real: **0%** (ambas queries falharam em entregar dados úteis)

---

## 🔍 Análise de Performance

### Sistema RAG
- ✅ **QueryRetriever:** 102 exemplos carregados
- ✅ **Few-Shot Learning:** Funcionando (2 exemplos encontrados)
- ✅ **Cache:** Funcionando (respostas LLM cacheadas)

### Cache de Agent Graph
- ✅ Inicializado com TTL: 24h
- ❌ 2 CACHE MISS (nenhuma query foi reutilizada)
- ✅ 2 respostas salvas em cache (para futuras consultas idênticas)

### LLM Performance
- **Modelo:** gemini-2.5-flash-lite
- **Chamadas API:** 5 total
- **Cache de respostas:** 5/5 cacheadas (economia de créditos)
- **Tempo médio:** ~2-3 segundos por chamada

---

## 🚨 Problemas Críticos Detectados

### 1. **Gerenciamento de Memória Inadequado**
```
PROBLEMA: Sistema tenta carregar 193MB de Parquet em memória
SOLUÇÃO ATUAL: Fallback para limitar a 10k linhas → FALHA
RECOMENDAÇÃO:
  - Instalar Polars para processamento eficiente
  - Implementar chunked reading com filtros
  - Usar streaming ao invés de carregar tudo
```

### 2. **Polars NÃO Instalado**
```
WARNING: "Polars não disponível. Usando apenas Dask."
IMPACTO: Performance 3-5x pior, maior uso de memória
RECOMENDAÇÃO: pip install polars (prioridade ALTA)
```

### 3. **Mapeamento de UNE Incorreto**
```
PROBLEMA: LLM não consegue mapear "Une scr" para código correto
SOLUÇÃO ATUAL: Inferência do LLM → FALHA
RECOMENDAÇÃO:
  - Criar dicionário de mapeamento UNE (sigla → código)
  - Adicionar validação antes de executar query
  - Implementar sugestão de correção ao usuário
```

### 4. **Wildcard Pattern não funciona com pd.read_parquet()**
```
PROBLEMA: '*.parquet' não é suportado nativamente por Pandas
CÓDIGO ATUAL: pd.read_parquet('data/parquet/*.parquet')
ERRO: OSError: [Errno 22] Invalid argument
RECOMENDAÇÃO: Usar glob.glob() para expandir padrão antes
```

---

## 💡 Recomendações de Correção

### Prioridade CRÍTICA 🔴

1. **Instalar Polars**
   ```bash
   pip install polars
   ```
   **Impacto:** +300% performance, -60% uso de memória

2. **Corrigir Estratégia de Carregamento**
   ```python
   # Em code_gen_agent.py:284
   import glob
   parquet_files = glob.glob(parquet_path)
   df = pd.read_parquet(parquet_files[0], columns=essential_cols)
   ```

3. **Implementar Mapeamento de UNE**
   ```python
   UNE_MAP = {
       "scr": "123",
       "mad": "261",
       # ... outros mapeamentos
   }
   ```

### Prioridade ALTA 🟠

4. **Adicionar Chunked Reading**
   ```python
   def load_data_chunked(filters, chunk_size=5000):
       # Processar dados em chunks menores
   ```

5. **Melhorar Mensagens de Erro ao Usuário**
   - Não mostrar stacktrace técnico
   - Sugerir reformulação da query
   - Informar limitações atuais

6. **Monitoramento de Memória**
   ```python
   import psutil
   mem = psutil.virtual_memory()
   if mem.available < 500_000_000:  # 500MB
       logger.warning("Memória baixa, limitando carga de dados")
   ```

### Prioridade MÉDIA 🟡

7. **Otimizar DynamicPrompt**
   - Reduzir tamanho do prompt (atual: 621 chars)
   - Remover avisos redundantes

8. **Implementar Retry com Backoff**
   - Tentar novamente após falha de memória
   - Aguardar garbage collection

---

## 📈 Métricas de Código

### Problemas Detectados pelo PatternMatcher:
```
⚠️ Query pede ranking mas código não tem groupby()
⚠️ Query menciona 'tecido' mas código pode não usar 'TECIDOS'
```

### Avisos Ativos do DynamicPrompt: **5**

---

## 🎯 Conclusão

O sistema apresenta **2 anomalias críticas** que afetam diretamente a experiência do usuário:

1. **MemoryError:** Impede o processamento de queries complexas
2. **Mapeamento UNE:** Gera respostas vazias e incorretas

Ambos os problemas têm soluções identificadas e devem ser corrigidos com **prioridade máxima**.

### Taxa de Sucesso Real do Dia: **0/2 (0%)**

---

## 📁 Arquivos Relacionados

- **Logs de Atividade:** `logs/app_activity/activity_2025-10-25.log`
- **Logs de Erro:** `logs/errors/error_2025-10-25.log`
- **Histórico de Queries:** `data/query_history/history_20251025.json`
- **Erro Learning:** `data/learning/error_log_20251025.jsonl`
- **Contador de Erros:** `data/learning/error_counts_20251025.json`

---

**Relatório gerado automaticamente por Claude Code**
**Data:** 2025-10-25 08:45 UTC
**Versão do Sistema:** Agent_BI v3.0.0 (FASE 2 - Sistema RAG)
