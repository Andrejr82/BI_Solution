# Guia de Uso - Validadores e Error Handlers

**Versão:** 1.0
**Data:** 2025-10-17
**Autor:** Code Agent

---

## Índice

1. [Introdução](#introdução)
2. [SchemaValidator](#schemavalidator)
3. [QueryValidator](#queryvalidator)
4. [ErrorHandler](#errorhandler)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Boas Práticas](#boas-práticas)
7. [Troubleshooting](#troubleshooting)

---

## Introdução

Este guia apresenta os novos componentes de validação e tratamento de erros implementados no Agent Solution BI v2.2.

### Componentes Implementados

- **SchemaValidator**: Validação de schemas Parquet contra catálogo
- **QueryValidator**: Validação e tratamento de queries
- **ErrorHandler**: Tratamento centralizado de erros

### Quando Usar

✅ **Use estes componentes quando:**
- Carregar dados de arquivos Parquet
- Executar queries complexas
- Processar entrada de usuário
- Realizar conversões de tipo
- Aplicar filtros em DataFrames

---

## SchemaValidator

### Instalação

```python
from core.validators import SchemaValidator
```

### Uso Básico

#### 1. Validar Arquivo Parquet

```python
validator = SchemaValidator()

# Validar arquivo
is_valid, errors = validator.validate_parquet_file(
    "data/parquet/produtos_une1.parquet",
    table_name="produtos"
)

if not is_valid:
    print(f"Erros encontrados: {errors}")
    # Tratar erros...
else:
    # Prosseguir com query
    df = pd.read_parquet("data/parquet/produtos_une1.parquet")
```

#### 2. Validar Colunas de Query

```python
validator = SchemaValidator()

# Colunas que você pretende usar na query
query_columns = ['produto_id', 'preco', 'estoque']

# Validar antes de executar
is_valid, invalid_cols = validator.validate_query_columns(
    table_name='produtos',
    query_columns=query_columns
)

if not is_valid:
    raise ValueError(f"Colunas inválidas: {invalid_cols}")
```

#### 3. Listar Colunas Obrigatórias

```python
validator = SchemaValidator()

# Obter lista de colunas esperadas
required_cols = validator.list_required_columns('produtos')

print(f"Colunas obrigatórias: {required_cols}")
# Output: ['produto_id', 'descricao', 'preco', 'estoque', ...]
```

### Uso Avançado

#### Validar Múltiplos Arquivos

```python
from pathlib import Path

validator = SchemaValidator()
parquet_dir = Path("data/parquet")

# Validar todos os arquivos de produtos
for une in range(1, 10):
    file_path = parquet_dir / f"produtos_une{une}.parquet"

    if file_path.exists():
        is_valid, errors = validator.validate_parquet_file(str(file_path))

        if not is_valid:
            print(f"UNE {une}: ❌ {len(errors)} erros")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"UNE {une}: ✅ Schema válido")
```

#### Validar Schema Customizado

```python
validator = SchemaValidator()

# Obter schema esperado
schema = validator.get_table_schema('produtos')

if schema:
    print(f"Colunas: {list(schema['columns'].keys())}")
    print(f"Tipos: {[col['type'] for col in schema['columns'].values()]}")
```

---

## QueryValidator

### Instalação

```python
from core.utils.query_validator import (
    QueryValidator,
    validate_columns,
    handle_nulls,
    safe_filter,
    get_friendly_error
)
```

### Uso Básico

#### 1. Validar Colunas em DataFrame

```python
import pandas as pd

df = pd.read_parquet("data/parquet/produtos.parquet")

# Validar colunas obrigatórias
is_valid, missing = validate_columns(
    df,
    required_columns=['produto_id', 'preco', 'estoque'],
    table_name='produtos'
)

if not is_valid:
    raise ValueError(f"Colunas faltando: {missing}")
```

#### 2. Tratar Valores Nulos

```python
# Estratégia 1: Remover linhas com nulos
df_clean = handle_nulls(df, 'preco', strategy='drop')

# Estratégia 2: Preencher com valor padrão
df_clean = handle_nulls(df, 'estoque', strategy='fill', fill_value=0)

# Estratégia 3: Manter nulos (apenas log)
df_clean = handle_nulls(df, 'observacao', strategy='keep')
```

#### 3. Converter Tipos com Segurança

```python
validator = QueryValidator()

df = validator.validate_and_convert_types(df, {
    'produto_id': 'str',
    'preco': 'float',
    'estoque': 'int',
    'data_cadastro': 'datetime'
})
```

#### 4. Aplicar Filtro Seguro

```python
# Filtro que pode falhar
df_filtered = safe_filter(
    df,
    filter_func=lambda df: df[df['preco'] > 100],
    error_msg="Erro ao filtrar por preço"
)

# Se o filtro falhar (ex: coluna não existe), retorna DataFrame original
```

#### 5. Timeout para Queries Longas

```python
validator = QueryValidator(default_timeout=30)

def minha_query_pesada():
    df = pd.read_parquet("arquivo_grande.parquet")
    # Processamento pesado...
    return df

try:
    # Executar com timeout de 15 segundos
    result = validator.execute_with_timeout(
        minha_query_pesada,
        timeout=15
    )
except QueryTimeout:
    print("Query muito lenta! Use filtros mais específicos.")
```

#### 6. Mensagens User-Friendly

```python
try:
    df = pd.read_parquet("arquivo_inexistente.parquet")
except Exception as e:
    user_message = get_friendly_error(e)
    print(user_message)
    # Output: "Arquivo de dados não encontrado. Verifique se os dados foram carregados corretamente."
```

### Uso Avançado

#### Pipeline Completo de Validação

```python
from core.utils.query_validator import QueryValidator

validator = QueryValidator()

def processar_produtos(une: int):
    """Pipeline completo de validação."""

    # 1. Carregar dados
    df = pd.read_parquet(f"data/parquet/produtos_une{une}.parquet")

    # 2. Validar colunas
    is_valid, missing = validate_columns(df, ['produto_id', 'preco', 'estoque'])
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # 3. Tratar nulos
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
    df = handle_nulls(df, 'estoque', strategy='fill', fill_value=0)

    # 4. Converter tipos
    df = validator.validate_and_convert_types(df, {
        'preco': 'float',
        'estoque': 'int'
    })

    # 5. Aplicar filtros
    df = safe_filter(df, lambda df: df[df['preco'] > 0])
    df = safe_filter(df, lambda df: df[df['estoque'] > 0])

    return df
```

---

## ErrorHandler

### Instalação

```python
from core.utils.error_handler import (
    handle_error,
    get_error_stats,
    error_handler_decorator,
    create_error_response,
    ParquetErrorHandler
)
```

### Uso Básico

#### 1. Tratamento Manual de Erro

```python
try:
    # Operação que pode falhar
    df = pd.read_parquet("arquivo.parquet")
    resultado = processar(df)

except Exception as e:
    error_ctx = handle_error(
        error=e,
        context={
            'function': 'processar_arquivo',
            'file': 'arquivo.parquet',
            'user_id': 123
        },
        user_message="Não foi possível processar o arquivo"  # opcional
    )

    # Usar mensagem amigável
    print(error_ctx.user_message)

    # Erro é automaticamente:
    # - Logado com logging.ERROR
    # - Salvo em data/learning/error_log_YYYYMMDD.jsonl
```

#### 2. Decorador de Error Handling

```python
@error_handler_decorator(
    context_func=lambda une, limit: {'une': une, 'limit': limit},
    return_on_error={'success': False, 'data': [], 'count': 0}
)
def buscar_produtos(une: int, limit: int = 100):
    """Função que pode falhar."""

    # Validar parâmetros
    if une < 1 or une > 9:
        raise ValueError(f"UNE inválida: {une}")

    # Processar...
    df = pd.read_parquet(f"data/parquet/produtos_une{une}.parquet")

    return {
        'success': True,
        'data': df.head(limit).to_dict('records'),
        'count': len(df)
    }

# Uso: se houver erro, retorna automaticamente return_on_error
result = buscar_produtos(une=1, limit=50)

if result['success']:
    print(f"Encontrados {result['count']} produtos")
else:
    print(f"Erro: {result['error']}")
```

#### 3. Resposta Padronizada de Erro

```python
try:
    # Operação
    result = processar_dados()

except Exception as e:
    response = create_error_response(
        error=e,
        context={'operation': 'processar_dados', 'input': 'arquivo.csv'},
        include_details=False  # True para debugging
    )

    # Resposta padronizada:
    # {
    #     'success': False,
    #     'data': [],
    #     'count': 0,
    #     'message': 'Mensagem amigável para usuário',
    #     'error_type': 'ValueError',
    #     'timestamp': '2025-10-17T10:30:00'
    # }

    return response
```

#### 4. Estatísticas de Erros

```python
# Após executar várias operações
stats = get_error_stats()

print(f"Total de erros: {stats['total_errors']}")
print(f"Erro mais comum: {stats['most_common_error']}")

for error_type, count in stats['error_counts'].items():
    print(f"{error_type}: {count}")
```

#### 5. Handler Específico para Parquet

```python
try:
    df = pd.read_parquet("arquivo_corrompido.parquet")

except Exception as e:
    response = ParquetErrorHandler.handle_parquet_error(
        error=e,
        file_path="arquivo_corrompido.parquet"
    )

    print(response['message'])
    # Mensagem específica para erros de Parquet
```

### Uso Avançado

#### Função com Error Handling Completo

```python
from core.utils.error_handler import error_handler_decorator, handle_error
from core.utils.query_validator import validate_columns, handle_nulls

@error_handler_decorator(
    context_func=lambda **kwargs: {'params': kwargs},
    return_on_error={'success': False, 'data': [], 'errors': []}
)
def get_produtos_une(une: int, categoria: str = None, limit: int = 100):
    """
    Busca produtos de uma UNE com validação completa.
    """

    # Validar parâmetros
    if une < 1 or une > 9:
        raise ValueError(f"UNE deve estar entre 1 e 9, recebido: {une}")

    # Carregar dados
    file_path = f"data/parquet/produtos_une{une}.parquet"
    df = pd.read_parquet(file_path)

    # Validar colunas
    is_valid, missing = validate_columns(df, ['produto_id', 'preco', 'estoque'])
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # Tratar nulos
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)

    # Filtrar por categoria
    if categoria:
        if 'categoria' in df.columns:
            df = df[df['categoria'] == categoria]
        else:
            raise KeyError("Coluna 'categoria' não encontrada")

    # Limitar resultados
    df = df.head(limit)

    return {
        'success': True,
        'data': df.to_dict('records'),
        'count': len(df)
    }

# Uso
result = get_produtos_une(une=1, categoria='Eletrônicos', limit=50)

if result['success']:
    print(f"Produtos encontrados: {result['count']}")
else:
    print(f"Erro: {result.get('error', 'Erro desconhecido')}")
```

---

## Exemplos Práticos

### Exemplo 1: Query de Produtos com Validação Completa

```python
from core.validators import SchemaValidator
from core.utils.query_validator import QueryValidator, validate_columns, handle_nulls
from core.utils.error_handler import error_handler_decorator
import pandas as pd

@error_handler_decorator(
    context_func=lambda une: {'une': une},
    return_on_error={'success': False, 'data': [], 'count': 0}
)
def consultar_produtos_validado(une: int):
    """Consulta produtos com todas as validações."""

    # 1. Validar schema do arquivo
    schema_validator = SchemaValidator()
    file_path = f"data/parquet/produtos_une{une}.parquet"

    is_valid, errors = schema_validator.validate_parquet_file(file_path, 'produtos')
    if not is_valid:
        raise ValueError(f"Schema inválido: {errors}")

    # 2. Carregar dados
    df = pd.read_parquet(file_path)

    # 3. Validar colunas
    is_valid, missing = validate_columns(df, ['produto_id', 'preco', 'estoque'])
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # 4. Tratar nulos
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
    df = handle_nulls(df, 'estoque', strategy='fill', fill_value=0)

    # 5. Converter tipos
    query_validator = QueryValidator()
    df = query_validator.validate_and_convert_types(df, {
        'preco': 'float',
        'estoque': 'int'
    })

    # 6. Filtrar produtos válidos
    df = df[(df['preco'] > 0) & (df['estoque'] >= 0)]

    return {
        'success': True,
        'data': df.to_dict('records'),
        'count': len(df)
    }

# Uso
result = consultar_produtos_validado(une=1)
print(f"Success: {result['success']}, Count: {result['count']}")
```

### Exemplo 2: Validação de Múltiplas UNEs

```python
from core.validators import SchemaValidator

def validar_todas_unes():
    """Valida schemas de todas as UNEs."""

    validator = SchemaValidator()
    relatorio = []

    for une in range(1, 10):
        file_path = f"data/parquet/produtos_une{une}.parquet"

        try:
            is_valid, errors = validator.validate_parquet_file(file_path, 'produtos')

            relatorio.append({
                'une': une,
                'valido': is_valid,
                'erros': errors
            })

        except FileNotFoundError:
            relatorio.append({
                'une': une,
                'valido': False,
                'erros': ['Arquivo não encontrado']
            })

    # Imprimir relatório
    print("\n=== RELATÓRIO DE VALIDAÇÃO ===\n")
    for item in relatorio:
        status = "✅" if item['valido'] else "❌"
        print(f"{status} UNE {item['une']}: {'OK' if item['valido'] else item['erros']}")

    return relatorio

# Executar validação
relatorio = validar_todas_unes()
```

### Exemplo 3: Pipeline de Transformação com Validação

```python
from core.utils.query_validator import QueryValidator, validate_columns, handle_nulls, safe_filter
from core.utils.error_handler import handle_error

def pipeline_transformacao(df: pd.DataFrame):
    """Pipeline de transformação com validação em cada etapa."""

    validator = QueryValidator()

    try:
        # Etapa 1: Validar colunas
        print("1. Validando colunas...")
        is_valid, missing = validate_columns(df, ['produto_id', 'preco', 'estoque'])
        if not is_valid:
            raise ValueError(f"Colunas faltando: {missing}")

        # Etapa 2: Tratar nulos
        print("2. Tratando valores nulos...")
        df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
        df = handle_nulls(df, 'estoque', strategy='fill', fill_value=0)

        # Etapa 3: Converter tipos
        print("3. Convertendo tipos...")
        df = validator.validate_and_convert_types(df, {
            'preco': 'float',
            'estoque': 'int'
        })

        # Etapa 4: Filtros
        print("4. Aplicando filtros...")
        df = safe_filter(df, lambda df: df[df['preco'] > 0], "Filtro de preço")
        df = safe_filter(df, lambda df: df[df['estoque'] >= 0], "Filtro de estoque")

        # Etapa 5: Limpeza
        print("5. Limpeza final...")
        df = df.drop_duplicates(subset=['produto_id'])

        print(f"✅ Pipeline concluído: {len(df)} registros")
        return df

    except Exception as e:
        error_ctx = handle_error(
            e,
            context={'operation': 'pipeline_transformacao'},
            user_message="Erro no pipeline de transformação"
        )
        print(f"❌ Erro: {error_ctx.user_message}")
        raise

# Uso
df_original = pd.read_parquet("data/parquet/produtos.parquet")
df_transformado = pipeline_transformacao(df_original)
```

---

## Boas Práticas

### 1. Sempre Valide Antes de Processar

```python
# ❌ Ruim: Processar sem validar
df = pd.read_parquet("arquivo.parquet")
resultado = df[df['preco'] > 100]  # Pode falhar se coluna não existir

# ✅ Bom: Validar antes
df = pd.read_parquet("arquivo.parquet")
is_valid, missing = validate_columns(df, ['preco'])
if is_valid:
    resultado = df[df['preco'] > 100]
else:
    raise ValueError(f"Colunas faltando: {missing}")
```

### 2. Use Decoradores para Funções Críticas

```python
# ✅ Bom: Usar decorador para error handling automático
@error_handler_decorator(
    context_func=lambda **kwargs: kwargs,
    return_on_error={'success': False, 'data': []}
)
def funcao_critica(param1, param2):
    # código que pode falhar
    return {'success': True, 'data': resultado}
```

### 3. Trate Nulos Explicitamente

```python
# ❌ Ruim: Ignorar nulos
df['preco'].mean()  # Pode dar resultado incorreto

# ✅ Bom: Tratar nulos antes
df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
media = df['preco'].mean()
```

### 4. Forneça Mensagens Claras

```python
# ❌ Ruim: Mensagem genérica
raise ValueError("Erro")

# ✅ Bom: Mensagem específica
raise ValueError(f"UNE {une} inválida. Deve estar entre 1 e 9.")
```

### 5. Use Timeout para Queries Pesadas

```python
# ✅ Bom: Definir timeout
validator = QueryValidator(default_timeout=30)

try:
    resultado = validator.execute_with_timeout(query_pesada, timeout=15)
except QueryTimeout:
    print("Query muito lenta. Otimize ou use filtros.")
```

### 6. Monitore Estatísticas de Erros

```python
# ✅ Bom: Monitorar erros periodicamente
stats = get_error_stats()
if stats['total_errors'] > 100:
    print(f"⚠️ Muitos erros detectados: {stats['total_errors']}")
    print(f"Erro mais comum: {stats['most_common_error']}")
```

---

## Troubleshooting

### Problema 1: "Coluna não encontrada"

**Sintoma:**
```
KeyError: 'nome_coluna'
```

**Solução:**
```python
# Validar colunas antes de usar
is_valid, missing = validate_columns(df, ['nome_coluna'])
if not is_valid:
    print(f"Colunas disponíveis: {list(df.columns)}")
    print(f"Colunas faltando: {missing}")
```

### Problema 2: "Schema inválido"

**Sintoma:**
```
Schema inválido: ['Coluna X: Tipo incompatível']
```

**Solução:**
```python
# Verificar schema do arquivo
validator = SchemaValidator()
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")

if not is_valid:
    print("Erros de schema:")
    for error in errors:
        print(f"  - {error}")

    # Opção 1: Recriar arquivo Parquet com schema correto
    # Opção 2: Atualizar catalog_focused.json
```

### Problema 3: "Conversão de tipo falhou"

**Sintoma:**
```
ValueError: could not convert string to float: 'invalid'
```

**Solução:**
```python
# Usar validador que trata erros de conversão
validator = QueryValidator()
df = validator.validate_and_convert_types(df, {
    'preco': 'float'  # Converte com errors='coerce', NaN vira 0.0
})
```

### Problema 4: "Query muito lenta"

**Sintoma:**
```
QueryTimeout: Query excedeu o tempo limite de 30 segundos
```

**Solução:**
```python
# Opção 1: Aumentar timeout
validator = QueryValidator(default_timeout=60)

# Opção 2: Otimizar query
df_filtrado = df[df['coluna'].isin(valores_especificos)]  # Mais rápido

# Opção 3: Usar chunks
for chunk in pd.read_parquet("arquivo.parquet", chunksize=10000):
    processar(chunk)
```

### Problema 5: "Muitos valores nulos"

**Sintoma:**
```
INFO: Encontrados 500 valores nulos em 'preco'
```

**Solução:**
```python
# Analisar antes de decidir estratégia
null_count = df['preco'].isna().sum()
null_percent = (null_count / len(df)) * 100

if null_percent > 50:
    # Mais de 50% nulos: considerar remover coluna
    df = df.drop(columns=['preco'])
elif null_percent > 10:
    # Entre 10-50%: preencher com mediana
    median = df['preco'].median()
    df = handle_nulls(df, 'preco', strategy='fill', fill_value=median)
else:
    # Menos de 10%: preencher com 0 ou remover linhas
    df = handle_nulls(df, 'preco', strategy='drop')
```

---

## Scripts de Demonstração

### Executar Demo Completa

```bash
# Windows
python scripts\demo_validators.py

# Linux/Mac
python scripts/demo_validators.py
```

### Executar Testes

```bash
# Windows
python -m pytest tests\test_validators_and_handlers.py -v

# Linux/Mac
python -m pytest tests/test_validators_and_handlers.py -v
```

---

## Referências

- **Documentação Completa**: `docs/CORRECOES_QUERIES_IMPLEMENTADAS.md`
- **Código Fonte**:
  - `core/validators/schema_validator.py`
  - `core/utils/query_validator.py`
  - `core/utils/error_handler.py`
- **Testes**: `tests/test_validators_and_handlers.py`
- **Demo**: `scripts/demo_validators.py`

---

**Versão:** 1.0
**Última Atualização:** 2025-10-17
**Autor:** Code Agent
