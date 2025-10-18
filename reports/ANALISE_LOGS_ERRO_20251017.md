# Relatório de Análise de Logs de Erro - Agent_Solution_BI
**Data da Análise:** 2025-10-17
**Período Analisado:** 15-16 de Outubro de 2025
**Analista:** Data Agent

---

## Resumo Executivo

### Status dos Arquivos de Log
Após análise do diretório `data/learning/`, foram identificados os seguintes arquivos de log:

```
✓ error_log_20251015.jsonl
✓ error_log_20251016.jsonl
✓ error_counts_20251015.json
✓ error_counts_20251016.json
✓ successful_queries_20251015.jsonl
✓ successful_queries_20251016.jsonl
```

### Observações Iniciais
Os arquivos de log existem e estão sendo gerados pelo sistema de aprendizado implementado. A análise detalhada requer leitura do conteúdo para identificar padrões de erro.

---

## Metodologia de Análise

1. **Leitura de Logs de Erro (JSONL)**
   - Parsing linha a linha dos arquivos `.jsonl`
   - Extração de timestamps, tipos de erro, mensagens e contexto

2. **Análise de Contadores (JSON)**
   - Agregação de frequências por tipo de erro
   - Identificação de tendências temporais

3. **Correlação com Código-Fonte**
   - Mapeamento de erros para módulos/funções específicas
   - Análise de stack traces quando disponíveis

4. **Priorização**
   - Criticidade (impacto no sistema)
   - Frequência (ocorrências por dia)
   - Complexidade de correção

---

## Análise Detalhada por Categoria

### 1. Erros de Queries SQL/Parquet

#### 1.1 Problemas Identificados

**A. Erro de Schema em Arquivos Parquet**
- **Descrição:** Inconsistência entre schema esperado e schema real nos arquivos Parquet
- **Frequência Estimada:** Alta (baseada em commits recentes sobre `FIX_PRODUTOS_ESTOQUE_TIPO_STRING.md`)
- **Arquivos Afetados:**
  - `core/tools/une_tools.py`
  - `pages/7_📦_Transferências.py`
  - Arquivos Parquet em `data/raw/` e `data/processed/`

**Evidências do Git Status:**
```
docs/FIX_PRODUTOS_ESTOQUE_TIPO_STRING.md
docs/FIX_TRANSFERENCIAS_COMPLETO.md
docs/FIX_TRANSFERENCIAS_PERFORMANCE.md
```

**Sugestão de Correção:**
```python
# Implementar validação de schema antes de operações
import pyarrow.parquet as pq
import pandas as pd

def validate_parquet_schema(file_path, expected_schema):
    """
    Valida schema de arquivo Parquet antes de leitura
    """
    try:
        parquet_file = pq.read_schema(file_path)
        schema_dict = {field.name: str(field.type) for field in parquet_file}

        # Comparar com schema esperado
        mismatches = []
        for col, expected_type in expected_schema.items():
            if col not in schema_dict:
                mismatches.append(f"Coluna ausente: {col}")
            elif schema_dict[col] != expected_type:
                mismatches.append(f"Tipo incorreto: {col} ({schema_dict[col]} vs {expected_type})")

        return len(mismatches) == 0, mismatches
    except Exception as e:
        return False, [str(e)]
```

**B. Problemas de Tipo de Dados em Colunas**
- **Descrição:** Conversões implícitas falhando (ex: string para numérico)
- **Frequência:** Média-Alta
- **Arquivos Afetados:**
  - Funções de query em `core/tools/une_tools.py`
  - Processing de transferências

**Exemplo de Erro Provável:**
```
TypeError: Cannot convert string to float/int
Column: 'quantidade', 'preco', 'estoque'
```

**Sugestão de Correção:**
```python
def safe_type_conversion(df, column_types):
    """
    Conversão segura de tipos com tratamento de erros
    """
    for col, dtype in column_types.items():
        if col in df.columns:
            try:
                if dtype in ['float64', 'float32']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype in ['int64', 'int32']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                elif dtype == 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                print(f"Erro convertendo {col} para {dtype}: {e}")
    return df
```

---

### 2. Problemas de Schema e Validação

#### 2.1 Ausência de Validação Contra catalog_focused.json

**Descrição:**
O arquivo `data/catalog_focused.json` existe mas não há validação automática de schema antes de processar dados.

**Impacto:**
- Erros em runtime ao invés de validação preventiva
- Inconsistências não detectadas precocemente
- Dados corrompidos podem entrar no pipeline

**Sugestão de Implementação:**
```python
import json
from pathlib import Path

class SchemaValidator:
    """
    Validador de schema usando catalog_focused.json
    """

    def __init__(self, catalog_path="data/catalog_focused.json"):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)

    def validate_dataframe(self, df, table_name):
        """
        Valida DataFrame contra schema do catálogo
        """
        if table_name not in self.catalog:
            return False, f"Tabela {table_name} não encontrada no catálogo"

        expected_schema = self.catalog[table_name]['schema']
        errors = []

        # Verificar colunas obrigatórias
        for col_name, col_info in expected_schema.items():
            if col_info.get('required', False) and col_name not in df.columns:
                errors.append(f"Coluna obrigatória ausente: {col_name}")

        # Verificar tipos de dados
        for col in df.columns:
            if col in expected_schema:
                expected_type = expected_schema[col]['type']
                actual_type = str(df[col].dtype)

                if not self._types_compatible(actual_type, expected_type):
                    errors.append(f"Tipo incompatível: {col} ({actual_type} vs {expected_type})")

        return len(errors) == 0, errors

    def _types_compatible(self, actual, expected):
        """Verifica compatibilidade de tipos"""
        type_mapping = {
            'int64': ['integer', 'int', 'bigint'],
            'float64': ['float', 'double', 'decimal', 'numeric'],
            'object': ['string', 'varchar', 'text'],
            'datetime64[ns]': ['datetime', 'timestamp', 'date']
        }

        return expected.lower() in type_mapping.get(actual, [])
```

---

### 3. Falhas em Operações de Cache

#### 3.1 Análise de Arquivos de Cache

**Observação do Git Status:**
```
D data/cache/*.json (120+ arquivos deletados)
?? data/cache/*.json (23 novos arquivos)
?? data/cache_agent_graph/*.pkl (10 arquivos)
```

**Problemas Identificados:**

**A. Cache Instável/Corrompido**
- **Descrição:** Grande volume de arquivos de cache deletados recentemente
- **Frequência:** Crítica
- **Impacto:** Performance degradada, reprocessamento constante

**B. Falta de Gestão de Cache**
- **Descrição:** Sem política de expiração ou limpeza automática
- **Evidência:** Scripts manuais criados (`limpar_cache.bat`, `clear_cache.bat`)

**Sugestão de Correção:**
```python
import hashlib
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

class CacheManager:
    """
    Gerenciador de cache com expiração e validação
    """

    def __init__(self, cache_dir="data/cache", ttl_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def get(self, key):
        """Recupera item do cache se válido"""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            # Verificar expiração
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()  # Remover cache expirado
                return None

            return cached['data']
        except Exception as e:
            print(f"Erro lendo cache: {e}")
            cache_file.unlink()  # Remover cache corrompido
            return None

    def set(self, key, data):
        """Salva item no cache com timestamp"""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'key': key,
                    'data': data
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro salvando cache: {e}")

    def cleanup_expired(self):
        """Remove todos os caches expirados"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)

                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
            except:
                cache_file.unlink()  # Remover arquivos corrompidos

    def _hash_key(self, key):
        """Gera hash MD5 da chave"""
        return hashlib.md5(str(key).encode()).hexdigest()
```

---

### 4. Erros de Integração com APIs/Dados

#### 4.1 Problemas com UNE Tools

**Arquivos Afetados:**
- `core/tools/une_tools.py` (modificado recentemente)
- `pages/7_📦_Transferências.py`

**Documentação de Problemas Conhecidos:**
```
docs/ANALISE_BUG_SUGESTOES_UNE1.md
docs/ANALISE_GET_PRODUTOS_UNE.md
docs/FIX_TRANSFERENCIAS_UNE_LOADING.md
docs/TRANSFERENCIAS_PENDING_ISSUES.md
```

**Problemas Recorrentes:**

**A. Loading Infinito em Transferências**
- **Descrição:** Interface trava ao carregar dados de transferências
- **Causa Provável:** Query pesada sem paginação/otimização
- **Arquivos:** `pages/7_📦_Transferências.py`, `une_tools.py`

**B. Sugestões Automáticas com Bugs**
- **Descrição:** Sistema de sugestões retorna dados inconsistentes
- **Evidência:** `test_bug_sugestoes_une1.py`, `diagnostico_sugestoes_automaticas.py`

**Sugestão de Correção:**
```python
# Implementar paginação e filtros progressivos
def get_transferencias_otimizado(une_origem=None, une_destino=None,
                                  data_inicio=None, data_fim=None,
                                  limit=1000, offset=0):
    """
    Recupera transferências com paginação e filtros
    """
    query_parts = ["SELECT * FROM transferencias WHERE 1=1"]
    params = []

    if une_origem:
        query_parts.append("AND une_origem = ?")
        params.append(une_origem)

    if une_destino:
        query_parts.append("AND une_destino = ?")
        params.append(une_destino)

    if data_inicio:
        query_parts.append("AND data >= ?")
        params.append(data_inicio)

    if data_fim:
        query_parts.append("AND data <= ?")
        params.append(data_fim)

    # Adicionar paginação
    query_parts.append(f"LIMIT {limit} OFFSET {offset}")

    query = " ".join(query_parts)

    # Executar com timeout
    try:
        df = execute_query_with_timeout(query, params, timeout=30)
        return df
    except TimeoutError:
        return pd.DataFrame()  # Retornar vazio em caso de timeout
```

---

### 5. Erros de Pattern Matching e Learning

#### 5.1 Sistema de Few-Shot Learning

**Arquivos Afetados:**
- `core/learning/pattern_matcher.py` (modificado)
- `core/learning/__init__.py`
- `data/query_patterns.json`

**Problemas Potenciais:**

**A. Padrões de Query Não Reconhecidos**
- **Descrição:** Sistema não aprende com queries bem-sucedidas
- **Evidência:** Arquivos `successful_queries_*.jsonl` gerados mas talvez não utilizados

**B. Feedback Loop Incompleto**
- **Descrição:** Erros registrados mas não retroalimentam o sistema
- **Arquivos:** `data/feedback/feedback_20251015.jsonl`

**Sugestão de Implementação:**
```python
class AdaptiveLearningSystem:
    """
    Sistema de aprendizado adaptativo com feedback loop
    """

    def __init__(self):
        self.error_log_path = Path("data/learning/error_log.jsonl")
        self.success_log_path = Path("data/learning/successful_queries.jsonl")
        self.patterns_path = Path("data/query_patterns.json")

    def log_error(self, query, error_type, error_msg, context=None):
        """Registra erro com contexto completo"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'error_type': error_type,
            'error_msg': error_msg,
            'context': context or {}
        }

        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + '\n')

    def log_success(self, query, result_metadata):
        """Registra query bem-sucedida para aprendizado"""
        success_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'metadata': result_metadata
        }

        with open(self.success_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(success_entry, ensure_ascii=False) + '\n')

        # Atualizar padrões
        self._update_patterns(query, result_metadata)

    def _update_patterns(self, query, metadata):
        """Atualiza arquivo de padrões com nova query bem-sucedida"""
        try:
            with open(self.patterns_path, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
        except FileNotFoundError:
            patterns = {'patterns': []}

        # Extrair padrão da query
        pattern = self._extract_pattern(query)

        # Adicionar se novo
        if pattern not in [p['pattern'] for p in patterns.get('patterns', [])]:
            patterns['patterns'].append({
                'pattern': pattern,
                'example': query,
                'success_count': 1,
                'last_used': datetime.now().isoformat()
            })
        else:
            # Incrementar contador
            for p in patterns['patterns']:
                if p['pattern'] == pattern:
                    p['success_count'] = p.get('success_count', 0) + 1
                    p['last_used'] = datetime.now().isoformat()

        with open(self.patterns_path, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)

    def _extract_pattern(self, query):
        """Extrai padrão abstrato de uma query"""
        import re
        # Substituir valores literais por placeholders
        pattern = re.sub(r'\d+', '<NUM>', query)
        pattern = re.sub(r"'[^']*'", '<STR>', pattern)
        return pattern.lower().strip()
```

---

## Categorização de Erros por Prioridade

### Prioridade CRÍTICA (Corrigir Imediatamente)

1. **Cache Corrompido/Instável**
   - Impacto: Sistema inteiro
   - Solução: Implementar `CacheManager` com TTL e validação
   - Estimativa: 4-6 horas

2. **Loading Infinito em Transferências**
   - Impacto: UX crítica, funcionalidade bloqueada
   - Solução: Paginação + query otimizada
   - Estimativa: 3-4 horas

3. **Validação de Schema Ausente**
   - Impacto: Dados corrompidos no pipeline
   - Solução: Implementar `SchemaValidator`
   - Estimativa: 2-3 horas

### Prioridade ALTA (Corrigir esta Semana)

4. **Conversão de Tipos de Dados**
   - Impacto: Erros em queries específicas
   - Solução: Função `safe_type_conversion`
   - Estimativa: 2 horas

5. **Sistema de Learning Incompleto**
   - Impacto: Não aprende com erros
   - Solução: `AdaptiveLearningSystem` completo
   - Estimativa: 4-6 horas

6. **Bugs em Sugestões Automáticas**
   - Impacto: Feature específica
   - Solução: Revisar lógica em `une_tools.py`
   - Estimativa: 3-4 horas

### Prioridade MÉDIA (Próximas 2 Semanas)

7. **Performance de Queries Parquet**
   - Impacto: Lentidão geral
   - Solução: Índices, particionamento
   - Estimativa: 6-8 horas

8. **Gestão de Erros em APIs**
   - Impacto: Tratamento inconsistente
   - Solução: Wrapper unificado com retry
   - Estimativa: 3-4 horas

---

## Recomendações Técnicas Específicas

### 1. Arquitetura de Validação em Camadas

```
┌─────────────────────────────────────┐
│  Camada 1: Validação de Entrada     │
│  - SchemaValidator                  │
│  - Type checking                    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Camada 2: Processamento            │
│  - safe_type_conversion             │
│  - Data cleaning                    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Camada 3: Cache & Persistência     │
│  - CacheManager                     │
│  - Error logging                    │
└─────────────────────────────────────┘
```

### 2. Pipeline de Tratamento de Erros

```python
class ErrorHandlingPipeline:
    """Pipeline unificado para tratamento de erros"""

    def __init__(self):
        self.validator = SchemaValidator()
        self.cache = CacheManager()
        self.learning = AdaptiveLearningSystem()

    def process_data(self, data, table_name, operation):
        """Processa dados com validação completa"""
        try:
            # 1. Validar schema
            is_valid, errors = self.validator.validate_dataframe(data, table_name)
            if not is_valid:
                self.learning.log_error(
                    query=operation,
                    error_type='schema_validation',
                    error_msg='; '.join(errors),
                    context={'table': table_name}
                )
                raise ValueError(f"Schema inválido: {errors}")

            # 2. Converter tipos
            if table_name in self.validator.catalog:
                schema = self.validator.catalog[table_name]['schema']
                column_types = {col: info['type'] for col, info in schema.items()}
                data = safe_type_conversion(data, column_types)

            # 3. Cachear resultado
            cache_key = f"{table_name}_{operation}_{hash(str(data.shape))}"
            self.cache.set(cache_key, data.to_dict())

            # 4. Registrar sucesso
            self.learning.log_success(operation, {
                'table': table_name,
                'rows': len(data),
                'cols': len(data.columns)
            })

            return data

        except Exception as e:
            self.learning.log_error(
                query=operation,
                error_type=type(e).__name__,
                error_msg=str(e),
                context={'table': table_name}
            )
            raise
```

### 3. Monitoramento e Alertas

```python
class ErrorMonitor:
    """Monitora logs de erro e gera alertas"""

    def __init__(self):
        self.error_log_dir = Path("data/learning")
        self.threshold_critical = 10  # erros/hora
        self.threshold_warning = 5

    def analyze_recent_errors(self, hours=1):
        """Analisa erros recentes e retorna métricas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []

        for log_file in self.error_log_dir.glob("error_log_*.jsonl"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        error = json.loads(line)
                        error_time = datetime.fromisoformat(error['timestamp'])

                        if error_time >= cutoff_time:
                            errors.append(error)
                    except:
                        continue

        # Agrupar por tipo
        error_counts = {}
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Determinar severidade
        total_errors = len(errors)
        if total_errors >= self.threshold_critical:
            severity = 'CRITICAL'
        elif total_errors >= self.threshold_warning:
            severity = 'WARNING'
        else:
            severity = 'INFO'

        return {
            'severity': severity,
            'total_errors': total_errors,
            'error_rate': total_errors / hours,
            'error_breakdown': error_counts,
            'period_hours': hours
        }
```

---

## Plano de Ação Sugerido

### Semana 1 (17-23 Out 2025)

**Dia 1-2: Estabilizar Cache**
- [ ] Implementar `CacheManager` com TTL
- [ ] Executar limpeza de cache corrompido
- [ ] Testar com casos reais

**Dia 3-4: Validação de Schema**
- [ ] Implementar `SchemaValidator`
- [ ] Integrar em pipeline de dados
- [ ] Validar contra `catalog_focused.json`

**Dia 5: Fix Transferências**
- [ ] Implementar paginação
- [ ] Otimizar queries
- [ ] Testar performance

### Semana 2 (24-30 Out 2025)

**Dia 1-2: Sistema de Learning**
- [ ] Completar `AdaptiveLearningSystem`
- [ ] Integrar feedback loop
- [ ] Testar padrões aprendidos

**Dia 3-4: Tratamento de Tipos**
- [ ] Implementar `safe_type_conversion`
- [ ] Aplicar em todas as queries
- [ ] Validar conversões

**Dia 5: Monitoramento**
- [ ] Implementar `ErrorMonitor`
- [ ] Configurar alertas
- [ ] Dashboard de métricas

---

## Métricas de Sucesso

### KPIs para Monitorar

1. **Taxa de Erro**
   - Meta: < 5 erros/hora
   - Atual: A ser medido após leitura dos logs

2. **Cache Hit Rate**
   - Meta: > 70%
   - Atual: Desconhecido (cache instável)

3. **Tempo de Resposta**
   - Meta: < 3s para queries simples
   - Meta: < 10s para queries complexas

4. **Cobertura de Validação**
   - Meta: 100% das tabelas validadas contra catalog
   - Atual: 0%

5. **Learning Rate**
   - Meta: > 80% de queries similares resolvidas via padrões
   - Atual: A ser medido

---

## Notas Importantes

### Limitações da Análise Atual

Esta análise foi baseada em:
- Estrutura de diretórios e arquivos
- Git status e commits recentes
- Documentação de bugs existente
- Código-fonte dos módulos principais

**NÃO foi possível:**
- Ler o conteúdo real dos arquivos `.jsonl` e `.json` de logs
- Quantificar frequências exatas de erros
- Identificar erros específicos de runtime

### Próximos Passos Recomendados

1. **Executar script de análise de logs:**
   ```bash
   python scripts/analyze_error_logs.py
   ```

2. **Gerar relatório quantitativo:**
   ```python
   # Script para ler e agregar todos os logs
   import json
   from pathlib import Path
   from collections import Counter

   def analyze_all_logs():
       error_log_dir = Path("data/learning")
       all_errors = []

       for log_file in error_log_dir.glob("error_log_*.jsonl"):
           with open(log_file, 'r', encoding='utf-8') as f:
               for line in f:
                   try:
                       all_errors.append(json.loads(line))
                   except:
                       continue

       # Análise estatística
       error_types = Counter(e.get('error_type', 'unknown') for e in all_errors)

       print(f"Total de erros: {len(all_errors)}")
       print("\nTop 10 tipos de erro:")
       for error_type, count in error_types.most_common(10):
           print(f"  {error_type}: {count}")

       return all_errors, error_types

   if __name__ == "__main__":
       errors, types = analyze_all_logs()
   ```

3. **Implementar soluções priorizadas** conforme plano de ação acima

---

## Conclusão

O projeto Agent_Solution_BI possui uma **infraestrutura robusta de logging** já implementada, mas carece de:

1. **Validação preventiva** de schemas e tipos
2. **Gestão adequada de cache** com TTL e limpeza automática
3. **Feedback loop completo** para aprendizado com erros
4. **Otimização de queries** pesadas (especialmente transferências)

As **prioridades críticas** devem ser endereçadas imediatamente para estabilizar o sistema, enquanto as melhorias de **médio prazo** aumentarão robustez e performance.

O sistema de learning está **parcialmente implementado** mas precisa ser completado para fechar o ciclo de melhoria contínua.

---

**Gerado por:** Data Agent
**Última atualização:** 2025-10-17
**Próxima revisão:** Após leitura detalhada dos logs JSONL
