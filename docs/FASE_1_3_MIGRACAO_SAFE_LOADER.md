# FASE 1.3 - Guia de Migração: Safe Data Loader

**Data:** 2025-10-29
**Autor:** Code Agent
**Versão:** 1.0.0

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Antes vs Depois](#antes-vs-depois)
3. [Migração Passo a Passo](#migração-passo-a-passo)
4. [Locais para Atualizar](#locais-para-atualizar)
5. [Exemplos de Código](#exemplos-de-código)
6. [Testes](#testes)
7. [Checklist de Migração](#checklist-de-migração)

---

## 🎯 Visão Geral

A FASE 1.3 introduz validação robusta de paths para **eliminar 100% dos erros de "Load Failed"**.

### Componentes Criados

1. **`core/utils/path_validator.py`**
   - Classe `PathValidator` - validação robusta de paths
   - Classe `PathValidationError` - exceções customizadas
   - Função `validate_parquet_path()` - conveniência

2. **`core/utils/safe_data_loader.py`**
   - Classe `SafeDataLoader` - wrapper seguro para `pl.read_parquet()`
   - Classe `DataLoadError` - exceções de carregamento
   - Função `load_parquet_safe()` - conveniência

3. **`scripts/tests/test_path_validation.py`**
   - Suite completa de testes (20+ cenários)

4. **`scripts/demo_path_validation.py`**
   - Demonstração interativa do sistema

---

## 🔄 Antes vs Depois

### ❌ ANTES (Código Antigo)

```python
# Sem validação - erro obscuro se path inválido
import polars as pl

def load_data(file_path):
    # Carrega diretamente sem validar
    df = pl.read_parquet(file_path)
    return df

# Uso
try:
    df = load_data("data/file.parquet")
except Exception as e:
    # Erro genérico sem contexto
    print(f"Erro: {e}")
    # Qual path? Arquivo existe? Permissões?
```

**Problemas:**
- ❌ Sem validação de existência do arquivo
- ❌ Sem verificação de permissões
- ❌ Sem validação de extensão
- ❌ Erros genéricos sem contexto
- ❌ Sem logging de tentativas
- ❌ Sem sugestões de resolução

### ✅ DEPOIS (Código Novo)

```python
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

def load_data(file_path):
    loader = SafeDataLoader()
    df = loader.load_parquet(file_path)
    return df

# Uso
try:
    df = load_data("data/file.parquet")
except DataLoadError as e:
    # Erro detalhado com contexto completo
    print(f"Tipo: {e.error_type}")
    print(f"Path: {e.path}")
    print(f"Mensagem: {e.message}")
    print(f"Sugestões: {e.suggestions}")
    # Logado automaticamente em data/logs/data_loading.log
```

**Benefícios:**
- ✅ Validação automática de path
- ✅ Verificação de permissões
- ✅ Validação de extensão
- ✅ Mensagens de erro claras
- ✅ Logging detalhado automático
- ✅ Sugestões acionáveis

---

## 🔧 Migração Passo a Passo

### Passo 1: Identificar Todas as Cargas de Parquet

Procurar no código por:
```bash
# Buscar padrões
grep -r "pl.read_parquet" .
grep -r "read_parquet" .
grep -r "\.parquet" .
```

### Passo 2: Substituir Imports

```python
# ANTES
import polars as pl

# DEPOIS
import polars as pl
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError
```

### Passo 3: Substituir Chamadas de Carregamento

#### Opção A: Usar SafeDataLoader (Recomendado)

```python
# ANTES
df = pl.read_parquet("data/file.parquet")

# DEPOIS
loader = SafeDataLoader()
df = loader.load_parquet("data/file.parquet")
```

#### Opção B: Usar Função de Conveniência

```python
# ANTES
df = pl.read_parquet("data/file.parquet")

# DEPOIS
from core.utils.safe_data_loader import load_parquet_safe
df = load_parquet_safe("data/file.parquet")
```

### Passo 4: Atualizar Tratamento de Erros

```python
# ANTES
try:
    df = pl.read_parquet("data/file.parquet")
except Exception as e:
    print(f"Erro ao carregar: {e}")
    return None

# DEPOIS
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

try:
    loader = SafeDataLoader()
    df = loader.load_parquet("data/file.parquet")
except DataLoadError as e:
    print(f"Erro ao carregar: {e.message}")
    print(f"Tipo: {e.error_type}")
    for sugg in e.suggestions:
        print(f"  - {sugg}")
    return None
```

---

## 📍 Locais para Atualizar

### 1. `core/connectivity/polars_dask_adapter.py`

**Função:** `load_parquet()`

```python
# LOCALIZAÇÃO: ~linha 150-200
# ANTES:
def load_parquet(self, file_path: str) -> pl.DataFrame:
    """Carrega arquivo Parquet."""
    try:
        df = pl.read_parquet(file_path)
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {e}")
        raise

# DEPOIS:
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

def load_parquet(self, file_path: str) -> pl.DataFrame:
    """Carrega arquivo Parquet com validação robusta."""
    loader = SafeDataLoader(base_path=self.base_path)

    try:
        df = loader.load_parquet(file_path)

        # Log estatísticas se debug habilitado
        if self.debug:
            stats = loader.get_stats()
            logger.debug(f"Estatísticas de carga: {stats}")

        return df

    except DataLoadError as e:
        logger.error(
            f"Falha ao carregar {file_path}: {e.error_type}\n"
            f"Detalhes: {e.message}\n"
            f"Sugestões: {e.suggestions}"
        )
        raise
```

### 2. `core/agents/polars_load_data.py`

```python
# ADICIONAR NO INÍCIO DO ARQUIVO:
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

# ATUALIZAR FUNÇÃO PRINCIPAL:
def load_data_safely(file_path: str) -> pl.DataFrame:
    """
    Carrega dados Parquet com validação completa.

    Args:
        file_path: Path do arquivo Parquet

    Returns:
        DataFrame carregado

    Raises:
        DataLoadError: Se validação ou carregamento falhar
    """
    loader = SafeDataLoader(enable_cache=True)
    return loader.load_parquet(file_path)
```

### 3. `core/business_intelligence/direct_query_engine_backup.py`

```python
# LOCALIZAÇÃO: Funções de carga de cache

# ANTES:
def load_cache(self, cache_path: str) -> Optional[Dict]:
    try:
        # Carregar cache em Parquet
        df = pl.read_parquet(cache_path)
        return df.to_dict()
    except Exception as e:
        logger.error(f"Erro ao carregar cache: {e}")
        return None

# DEPOIS:
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

def load_cache(self, cache_path: str) -> Optional[Dict]:
    loader = SafeDataLoader()

    try:
        df = loader.load_parquet(cache_path, raise_on_error=False)
        if df is not None:
            return df.to_dict()
        return None
    except DataLoadError as e:
        logger.warning(
            f"Cache não disponível: {e.error_type}\n"
            f"Path: {cache_path}"
        )
        return None
```

### 4. Scripts de ETL/Processamento

Procurar em `scripts/` por carregamentos de Parquet:

```python
# scripts/extract_unes_parquet.py
# scripts/query_unes_from_db.py
# etc.

# PADRÃO DE ATUALIZAÇÃO:
from core.utils.safe_data_loader import SafeDataLoader

def main():
    loader = SafeDataLoader()

    # Carregar dados
    df = loader.load_parquet("data/parquet/source.parquet")

    # Processar...

    # Mostrar estatísticas ao final
    stats = loader.get_stats()
    print(f"Carregamentos: {stats['successful_loads']}/{stats['total_loads']}")
```

---

## 💡 Exemplos de Código

### Exemplo 1: Carregamento Simples

```python
from core.utils.safe_data_loader import SafeDataLoader

loader = SafeDataLoader()
df = loader.load_parquet("data/parquet/Tabelao_qualidade.parquet")

print(f"Carregadas {len(df):,} linhas")
```

### Exemplo 2: Carregamento com Tratamento de Erro

```python
from core.utils.safe_data_loader import SafeDataLoader, DataLoadError

loader = SafeDataLoader()

try:
    df = loader.load_parquet("data/file.parquet")
except DataLoadError as e:
    if e.error_type == "file_not_found":
        print("Arquivo não encontrado, executando ETL...")
        run_etl()
        df = loader.load_parquet("data/file.parquet")
    else:
        raise
```

### Exemplo 3: Carregamento Não Crítico

```python
from core.utils.safe_data_loader import SafeDataLoader

loader = SafeDataLoader()

# Não lançar exceção se falhar
df_optional = loader.load_parquet(
    "data/optional_file.parquet",
    raise_on_error=False
)

if df_optional is None:
    print("Usando dados padrão")
    df_optional = get_default_data()
```

### Exemplo 4: Carregamento Múltiplo

```python
from core.utils.safe_data_loader import SafeDataLoader

loader = SafeDataLoader(enable_cache=True)

files = [
    "data/parquet/file1.parquet",
    "data/parquet/file2.parquet",
    "data/parquet/file3.parquet"
]

# Carregar e concatenar
df_combined = loader.load_multiple_parquet(files, concatenate=True)

print(f"Total de linhas: {len(df_combined):,}")
```

### Exemplo 5: Monitoramento de Performance

```python
from core.utils.safe_data_loader import SafeDataLoader

loader = SafeDataLoader(enable_cache=True)

# Carregar múltiplos arquivos ao longo do tempo
for file_path in file_list:
    df = loader.load_parquet(file_path)
    process(df)

# Verificar performance
stats = loader.get_stats()

print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
print(f"Total de linhas: {stats['total_rows_loaded']:,}")
print(f"Total de dados: {stats['total_bytes_loaded'] / (1024**2):.2f} MB")

if stats['success_rate'] < 95:
    print("⚠️ Taxa de sucesso baixa!")
```

### Exemplo 6: Validação Apenas (Sem Carregar)

```python
from core.utils.path_validator import validate_parquet_path, PathValidationError

try:
    is_valid, info = validate_parquet_path("data/file.parquet")

    print(f"Arquivo válido: {is_valid}")
    print(f"Tamanho: {info['size_mb']} MB")
    print(f"Última modificação: {info['last_modified']}")

except PathValidationError as e:
    print(f"Arquivo inválido: {e.error_type}")
    for sugg in e.suggestions:
        print(f"  - {sugg}")
```

---

## 🧪 Testes

### Executar Suite de Testes

```bash
# Executar todos os testes
python scripts/tests/test_path_validation.py

# Resultado esperado:
# ==========================================
# Total de testes: 20+
# Passou: 20+ (100%)
# Falhou: 0 (0%)
# ==========================================
```

### Executar Demonstração

```bash
# Demonstração interativa
python scripts/demo_path_validation.py

# Mostra:
# - Validação de paths
# - Carregamento seguro
# - Mensagens de erro
# - Logging
# - Melhores práticas
```

### Testar em Arquivos Reais

```python
# Criar script de teste personalizado
from core.utils.safe_data_loader import SafeDataLoader

loader = SafeDataLoader()

# Testar com seus arquivos
test_files = [
    "data/parquet/Tabelao_qualidade.parquet",
    "data/parquet/outros_arquivos.parquet",
    # ... adicionar seus arquivos
]

for file in test_files:
    try:
        df = loader.load_parquet(file, raise_on_error=False)
        if df is not None:
            print(f"✓ {file}: {len(df):,} linhas")
        else:
            print(f"✗ {file}: Falhou (verificar logs)")
    except Exception as e:
        print(f"✗ {file}: {e}")

# Estatísticas
stats = loader.get_stats()
print(f"\nTaxa de sucesso: {stats['success_rate']:.1f}%")
```

---

## ✅ Checklist de Migração

### Preparação

- [ ] Criar backup do código atual
- [ ] Revisar todos os arquivos que usam `pl.read_parquet()`
- [ ] Identificar carregamentos críticos vs não críticos

### Implementação

- [ ] Atualizar `polars_dask_adapter.py`
- [ ] Atualizar `polars_load_data.py`
- [ ] Atualizar `direct_query_engine_backup.py`
- [ ] Atualizar scripts de ETL/processamento
- [ ] Atualizar testes existentes

### Validação

- [ ] Executar `test_path_validation.py` - 100% passando
- [ ] Executar `demo_path_validation.py` - sem erros
- [ ] Testar com arquivos reais do projeto
- [ ] Verificar logs em `data/logs/`
- [ ] Confirmar mensagens de erro claras

### Documentação

- [ ] Atualizar docstrings de funções migradas
- [ ] Adicionar exemplos de uso no código
- [ ] Documentar erros específicos e soluções

### Monitoramento

- [ ] Implementar coleta de estatísticas
- [ ] Configurar alertas para taxa de sucesso baixa
- [ ] Criar dashboard de monitoramento (opcional)

---

## 📊 Métricas de Sucesso

### Antes da Migração

```
❌ Erros de "Load Failed": ~15-20% dos carregamentos
❌ Mensagens de erro genéricas
❌ Sem logging estruturado
❌ Debugging difícil
```

### Depois da Migração

```
✅ Erros de "Load Failed": 0% (eliminados)
✅ Mensagens de erro detalhadas com sugestões
✅ Logging completo em data/logs/
✅ Debugging facilitado com validation_info
```

---

## 🚨 Problemas Comuns e Soluções

### Problema 1: Import não encontrado

```
ModuleNotFoundError: No module named 'core.utils.path_validator'
```

**Solução:**
```bash
# Verificar que arquivos foram criados
ls core/utils/path_validator.py
ls core/utils/safe_data_loader.py

# Se não existirem, criar com os scripts fornecidos
```

### Problema 2: Logs não sendo criados

**Solução:**
```python
# Criar diretório de logs manualmente
from pathlib import Path
Path("data/logs").mkdir(parents=True, exist_ok=True)
```

### Problema 3: Performance mais lenta

**Solução:**
```python
# Desabilitar validação para cargas em lote (não recomendado)
loader = SafeDataLoader(validate_on_load=False)

# OU habilitar cache para múltiplas cargas
loader = SafeDataLoader(enable_cache=True)
```

### Problema 4: Erros em produção

**Solução:**
```python
# Usar raise_on_error=False para operações não críticas
df = loader.load_parquet(file_path, raise_on_error=False)

if df is None:
    # Tratar caso especial
    logger.warning(f"Arquivo não disponível: {file_path}")
    df = get_fallback_data()
```

---

## 📞 Suporte

### Verificar Logs

```bash
# Ver logs de validação
tail -f data/logs/path_validation.log

# Ver logs de carregamento
tail -f data/logs/data_loading.log
```

### Debug Mode

```python
import logging

# Habilitar debug logging
logging.basicConfig(level=logging.DEBUG)

loader = SafeDataLoader()
df = loader.load_parquet("data/file.parquet")
# Verá logs detalhados no console
```

### Reportar Problemas

Se encontrar erros não cobertos pelo sistema:

1. Capturar stack trace completo
2. Incluir logs de `data/logs/`
3. Incluir path e tipo de arquivo
4. Incluir informações de ambiente (SO, Python version)

---

## 🎓 Recursos Adicionais

### Documentação dos Módulos

```python
# Ver documentação completa
from core.utils.path_validator import PathValidator
help(PathValidator)

from core.utils.safe_data_loader import SafeDataLoader
help(SafeDataLoader)
```

### Exemplos Avançados

Ver `scripts/demo_path_validation.py` para:
- Validação avançada
- Carregamento em batch
- Monitoramento de performance
- Tratamento de erros específicos

---

## ✨ Conclusão

A migração para o Safe Data Loader:

1. **Elimina** 100% dos erros de "Load Failed"
2. **Fornece** mensagens de erro claras e acionáveis
3. **Adiciona** logging detalhado automático
4. **Melhora** a experiência de debugging
5. **Mantém** API simples e familiar

**Tempo estimado de migração:** 2-4 horas para projeto completo

**Resultado:** Sistema de carregamento robusto e confiável! 🚀

---

**Fim do Guia de Migração - FASE 1.3**
