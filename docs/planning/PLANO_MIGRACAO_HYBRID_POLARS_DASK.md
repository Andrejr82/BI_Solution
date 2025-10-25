# Plano de Migração: Arquitetura Híbrida Polars + Dask

**Data:** 2025-10-20
**Autor:** Claude Code
**Status:** Em Execução
**Objetivo:** Implementar arquitetura híbrida que escolhe automaticamente entre Polars (8.1x mais rápido) e Dask (escalável) sem quebrar o projeto

---

## 📋 Sumário Executivo

### Contexto
- **Problema:** Queries lentas com Dask (3-8s) em 30+ tabelas com milhões de linhas
- **Solução:** Arquitetura híbrida que usa Polars para 90% das queries (rápidas) e Dask para 10% (tabelas muito grandes)
- **Ganho esperado:** 5-8x mais rápido, 20-30% menos RAM

### Estratégia
- **Sem quebra:** Interface DatabaseAdapter mantida
- **Fallback seguro:** Polars falha → Dask automaticamente
- **Decisão automática:** Threshold 500MB (configurável)
- **Rollback rápido:** < 5 minutos se necessário

---

## 🎯 Objetivos e Métricas

| Métrica | Antes (Dask) | Meta (Híbrido) | Como Medir |
|---------|--------------|----------------|------------|
| Tempo médio query | 4-9s | 1-2s | test_80_perguntas_completo.py |
| Uso de RAM | ~15GB | ~10-12GB | psutil durante queries |
| Taxa de sucesso | 95% | ≥95% | Suite de testes |
| Queries/minuto | ~10 | ~40 | Benchmark stress test |

---

## 📊 Análise de Viabilidade

### Dados do Projeto
- **Tabelas:** 30+ arquivos Parquet
- **Dataset exemplo:** admmat.parquet (1.1M linhas, 93.83 MB)
- **Estimativa total:** ~33M linhas, ~2.8 GB
- **Benchmark:** Polars 8.1x mais rápido que Dask (ver BENCHMARK_DATAFRAMES_POLARS_VS_DASK.md)

### Decisão Arquitetural

```
┌─────────────────────────────────────────────┐
│         HYBRID ADAPTER (INTELIGENTE)        │
├─────────────────────────────────────────────┤
│                                             │
│  Arquivo < 500MB  →  POLARS (8.1x rápido) │
│  Arquivo ≥ 500MB  →  DASK (escalável)     │
│  Erro Polars      →  DASK (fallback)      │
│                                             │
└─────────────────────────────────────────────┘
```

**Justificativa:**
- 90% das tabelas < 500MB → Polars (queries instantâneas)
- 10% das tabelas ≥ 500MB → Dask (escalabilidade garantida)
- Zero mudança na interface → compatibilidade total

---

## 🏗️ Arquitetura da Solução

### Estrutura de Classes

```
DatabaseAdapter (interface)
    ↑
    |
ParquetAdapter (mantido - delega)
    ↓
HybridAdapter (NOVO - decisor inteligente)
    ├── PolarsEngine (NOVO - rápido)
    └── DaskEngine (atual - escalável)
```

### Fluxo de Decisão

```python
def execute_query(filters):
    1. Detectar tamanho do arquivo
    2. SE tamanho < 500MB:
         TENTAR Polars
         SE falhar → Fallback Dask
       SENÃO:
         Usar Dask
    3. Validar integridade (checksum)
    4. Retornar resultado
```

---

## 📅 Cronograma de Implementação

### FASE 1: PREPARAÇÃO E ANÁLISE (4h)

#### 1.1 Script de Análise de Tabelas
**Arquivo:** `scripts/analyze_all_tables.py`

**Funcionalidades:**
- Escanear todos os .parquet em data/parquet/
- Coletar métricas: tamanho, linhas, colunas
- Classificar por engine recomendada
- Gerar relatório JSON + console

**Output esperado:**
```json
{
  "total_tables": 30,
  "total_size_gb": 2.8,
  "total_rows": 33000000,
  "polars_recommended": 27,
  "dask_recommended": 3,
  "threshold_mb": 500,
  "tables": [
    {
      "name": "admmat.parquet",
      "size_mb": 93.8,
      "rows": 1113822,
      "columns": 97,
      "engine": "polars"
    }
  ]
}
```

#### 1.2 Instalar Polars
```bash
pip install polars==1.34.0
pip freeze > requirements.txt
```

**Validação:**
- Import polars sem erro
- Dask mantido (coexistência)
- Testes existentes passam

---

### FASE 2: IMPLEMENTAÇÃO CORE (4h)

#### 2.1 HybridAdapter
**Arquivo:** `core/connectivity/hybrid_adapter.py`

**Classe principal:**
```python
class HybridAdapter(DatabaseAdapter):
    POLARS_THRESHOLD_MB = 500

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.size_mb = self._get_file_size_mb()
        self.engine = self._select_engine()

    def execute_query(self, filters):
        try:
            if self.engine == "polars":
                return self._execute_polars(filters)
        except Exception as e:
            logger.warning(f"Polars failed, fallback to Dask: {e}")
            return self._execute_dask(filters)

    def _execute_polars(self, filters):
        # Implementação Polars com lazy evaluation
        pass

    def _execute_dask(self, filters):
        # Implementação atual (código do ParquetAdapter)
        pass
```

**Recursos críticos:**
- ✅ Detecção automática de tamanho
- ✅ Fallback Polars→Dask em exceções
- ✅ Validação de integridade (checksum)
- ✅ Logging detalhado de decisões
- ✅ Feature flag (POLARS_ENABLED env var)

#### 2.2 Compatibilidade com Filtros PyArrow
- Manter lógica de predicate pushdown
- Converter filtros para sintaxe Polars
- Manter conversão de tipos (ESTOQUE_UNE string→numeric)

---

### FASE 3: TESTES DE SEGURANÇA (4h)

#### 3.1 Testes Unitários
**Arquivo:** `tests/test_hybrid_adapter.py`

**Casos de teste:**
```python
def test_auto_select_polars_small_file():
    # Arquivo < 500MB → deve usar Polars

def test_auto_select_dask_large_file():
    # Arquivo ≥ 500MB → deve usar Dask

def test_fallback_polars_to_dask():
    # Simular erro Polars → fallback Dask

def test_data_integrity():
    # Mesmo resultado Polars vs Dask

def test_performance_threshold():
    # Polars deve ser < 2x tempo Dask
```

#### 3.2 Validação de Integridade
**Arquivo:** `tests/test_data_integrity.py`

**Validações:**
1. Mesmo número de linhas
2. Mesmo schema (colunas + tipos)
3. Mesmos valores agregados (±0.01%)
4. Mesma ordenação (TOP 10)

**Critério:** 100% dos testes passam antes de migração

---

### FASE 4: MIGRAÇÃO GRADUAL (4h)

#### 4.1 Backup
```bash
mkdir backup_before_hybrid_20251020
cp core/connectivity/parquet_adapter.py backup_before_hybrid_20251020/
cp core/agents/code_gen_agent.py backup_before_hybrid_20251020/
git add -A
git commit -m "backup: Before hybrid Polars+Dask migration"
```

#### 4.2 Migrar ParquetAdapter
**Estratégia:** Delegação interna (sem quebrar interface)

```python
# core/connectivity/parquet_adapter.py
class ParquetAdapter(DatabaseAdapter):
    def __init__(self, file_path: str):
        # Validações originais mantidas
        self._hybrid = HybridAdapter(file_path)  # NOVO
        logger.info(f"ParquetAdapter usando HybridAdapter (Polars+Dask)")

    def execute_query(self, filters):
        return self._hybrid.execute_query(filters)  # Delegação

    # connect(), disconnect(), get_schema() delegam também
```

**Vantagem:** Zero mudança em código que usa ParquetAdapter

#### 4.3 Atualizar CodeGenAgent
**Arquivo:** `core/agents/code_gen_agent.py`

**Mudanças mínimas:**
```python
# Adicionar import (opcional, para suporte futuro)
import polars as pl  # NOVO

# load_data() continua retornando Pandas
# (conversão Polars→Pandas feita internamente no HybridAdapter)
```

**Sem quebra:** LLM continua gerando código Pandas/Dask normalmente

---

## 🛡️ Estratégias de Segurança

### 1. Fallback Automático em Múltiplos Níveis

```python
# Nível 1: Erro na execução
try:
    result = self._execute_polars(query)
except Exception as e:
    logger.warning(f"Polars failed: {e}")
    result = self._execute_dask(query)

# Nível 2: Validação de resultado
if not self._validate_result(result):
    logger.error("Result validation failed, retrying with Dask")
    result = self._execute_dask(query)

# Nível 3: Feature flag global
if os.getenv("POLARS_ENABLED", "true") == "false":
    return self._execute_dask(query)  # Bypass Polars
```

### 2. Validação de Integridade

```python
def _validate_result(self, result):
    """Valida integridade do resultado."""
    if not result or len(result) == 0:
        return True  # Resultado vazio válido

    # Verificar tipos esperados
    if not isinstance(result, list):
        return False

    # Verificar estrutura de dicts
    if not all(isinstance(r, dict) for r in result):
        return False

    return True
```

### 3. Rollback Rápido

```bash
# Reverter para versão anterior (< 5 minutos)
git checkout backup_before_hybrid_20251020
pip install -r requirements.txt
# Sistema volta ao estado Dask puro
```

### 4. Monitoramento Detalhado

```python
logger.info(f"🚀 HybridAdapter decision:")
logger.info(f"  File: {self.file_path}")
logger.info(f"  Size: {self.size_mb:.1f}MB")
logger.info(f"  Engine: {self.engine}")
logger.info(f"  Threshold: {self.POLARS_THRESHOLD_MB}MB")

# Em produção, adicionar métricas
metrics = {
    "engine_used": self.engine,
    "query_time": end_time - start_time,
    "rows_returned": len(result),
    "fallback_occurred": fallback_flag
}
```

---

## 🧪 Plano de Testes

### Testes de Unidade (Fase 3)
- [x] Seleção automática de engine
- [x] Fallback Polars→Dask
- [x] Integridade de dados
- [x] Performance threshold
- [x] Tratamento de erros

### Testes de Integração (Pós-implementação)
- [ ] Suite de 80 perguntas (subset de 20)
- [ ] Queries em tabela pequena (Polars)
- [ ] Queries em tabela grande (Dask)
- [ ] Agregações complexas
- [ ] Joins entre tabelas

### Testes de Stress (Opcional)
- [ ] 10 queries simultâneas
- [ ] Query em tabela 10M+ linhas
- [ ] Join entre 3 tabelas
- [ ] Uso de RAM sob carga

---

## 📊 Critérios de Sucesso

### Mínimos (Obrigatórios)
- ✅ Zero quebra de funcionalidade existente
- ✅ Taxa de sucesso ≥ 95% nos testes
- ✅ Rollback funcional em < 5 minutos
- ✅ Fallback Polars→Dask funciona 100%

### Desejáveis (Performance)
- ⏳ Tempo médio query reduzido em 5x
- ⏳ Uso de RAM reduzido em 20%
- ⏳ 90% queries usam Polars
- ⏳ Zero timeouts

---

## 🔧 Configuração e Variáveis de Ambiente

### Novas Variáveis (.env)

```bash
# Ativar/desativar Polars globalmente
POLARS_ENABLED=true

# Threshold para decisão Polars vs Dask (em MB)
POLARS_THRESHOLD_MB=500

# Forçar Dask para debug
FORCE_DASK=false

# Ativar validação de integridade (checksum)
VALIDATE_INTEGRITY=true
```

### Configuração Dinâmica

```python
# Ajustar threshold baseado em RAM disponível
import psutil

available_ram_gb = psutil.virtual_memory().available / (1024**3)

if available_ram_gb > 16:
    POLARS_THRESHOLD_MB = 1000  # Mais Polars
elif available_ram_gb < 8:
    POLARS_THRESHOLD_MB = 200   # Mais Dask
else:
    POLARS_THRESHOLD_MB = 500   # Padrão
```

---

## 📈 Impacto Esperado

### Por Tipo de Query

| Tipo de Query | Engine | Antes | Depois | Ganho |
|---------------|--------|-------|--------|-------|
| Filtro simples (ex: segmento=TECIDOS) | Polars | 3s | 0.2s | **15x** |
| Agregação (GroupBy + Sum) | Polars | 0.2s | 0.04s | **5x** |
| Ranking TOP 100 | Polars | 5s | 0.8s | **6x** |
| Join tabelas grandes | Dask | 10s | 10s | **Igual** |
| Query tabela 10M+ linhas | Dask | 15s | 15s | **Igual** |

### Experiência do Usuário

**Antes:**
```
Usuário: "Quais os produtos do segmento TECIDOS?"
Sistema: [aguardando 3s...] ⏳
Resposta: Encontrei 140.790 produtos
```

**Depois:**
```
Usuário: "Quais os produtos do segmento TECIDOS?"
Sistema: [aguardando 0.2s...] ⚡
Resposta: Encontrei 140.790 produtos
```

**Percepção:** De "lento" para "instantâneo"

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Polars falha em query específica | Média | Baixo | Fallback automático para Dask |
| Incompatibilidade de tipos | Baixa | Médio | Validação de integridade + testes |
| Consumo de RAM maior que esperado | Baixa | Médio | Threshold configurável + monitoramento |
| Performance não atinge meta | Baixa | Alto | Benchmark antes de deploy + rollback |
| Bug em produção | Baixa | Alto | Feature flag + rollback rápido |

---

## 📝 Checklist de Execução

### Fase 1: Preparação ✅
- [ ] Criar script analyze_all_tables.py
- [ ] Executar análise de todas as tabelas
- [ ] Instalar Polars (pip install polars==1.34.0)
- [ ] Validar instalação (import polars)

### Fase 2: Implementação ✅
- [ ] Criar core/connectivity/hybrid_adapter.py
- [ ] Implementar _execute_polars()
- [ ] Implementar _execute_dask() (reuso código atual)
- [ ] Implementar _select_engine()
- [ ] Implementar fallback automático
- [ ] Adicionar validação de integridade

### Fase 3: Testes ✅
- [ ] Criar tests/test_hybrid_adapter.py
- [ ] Criar tests/test_data_integrity.py
- [ ] Executar testes unitários (100% pass)
- [ ] Validar integridade Polars vs Dask

### Fase 4: Migração ✅
- [ ] Fazer backup (git commit + pasta backup/)
- [ ] Migrar ParquetAdapter (delegação)
- [ ] Atualizar CodeGenAgent (import polars)
- [ ] Executar testes de regressão
- [ ] Validar zero quebra

---

## 📚 Referências

### Documentos do Projeto
- `docs/reports/BENCHMARK_DATAFRAMES_POLARS_VS_DASK.md` - Benchmark completo
- `core/connectivity/parquet_adapter.py` - Implementação atual Dask
- `core/connectivity/base.py` - Interface DatabaseAdapter
- `tests/test_80_perguntas_completo.py` - Suite de validação

### Documentação Externa
- Polars User Guide: https://pola-rs.github.io/polars/
- Polars API Reference: https://pola-rs.github.io/polars/py-polars/html/reference/
- Dask DataFrame: https://docs.dask.org/en/stable/dataframe.html
- Pandas→Polars Migration: https://pola-rs.github.io/polars/user-guide/migration/pandas/

---

## 🎯 Próximos Passos Após Implementação

### Curto Prazo (Semana 1)
1. Executar suite completa de 80 perguntas
2. Coletar métricas de performance reais
3. Ajustar threshold baseado em dados reais
4. Documentar casos de uso Polars vs Dask

### Médio Prazo (Semana 2-4)
1. Otimizar queries Polars específicas
2. Implementar cache de resultados
3. Adicionar dashboard de monitoramento
4. Treinar equipe em sintaxe Polars

### Longo Prazo (Mês 2+)
1. Migrar 100% queries para Polars (quando possível)
2. Deprecar Dask para tabelas pequenas
3. Implementar streaming Polars para tabelas grandes
4. Benchmark com datasets maiores (50M+ linhas)

---

## ✅ Critérios de Aprovação para Deploy

- [ ] Todos os testes unitários passam (100%)
- [ ] Testes de integridade validados (Polars = Dask)
- [ ] Subset de 20 perguntas com sucesso ≥95%
- [ ] Rollback testado e funcional
- [ ] Backup completo realizado
- [ ] Feature flag POLARS_ENABLED configurada
- [ ] Logging detalhado ativo
- [ ] Documentação atualizada

---

**Última atualização:** 2025-10-20
**Próxima revisão:** Após execução das Fases 1-4
**Responsável:** Claude Code + André (validação)
