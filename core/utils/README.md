# Utils Package

**Versão:** 1.0
**Data:** 2025-10-17
**Autor:** Code Agent

---

## 📋 Visão Geral

Este pacote contém utilitários para validação de queries e tratamento de erros no Agent Solution BI.

### Componentes

- **QueryValidator**: Validação e tratamento de queries
- **ErrorHandler**: Tratamento centralizado de erros

---

## 🚀 Instalação

```python
from core.utils.query_validator import QueryValidator, validate_columns, handle_nulls
from core.utils.error_handler import handle_error, error_handler_decorator
```

---

## 📖 QueryValidator

### Uso Básico

#### Validar Colunas

```python
from core.utils.query_validator import validate_columns
import pandas as pd

df = pd.read_parquet("arquivo.parquet")

is_valid, missing = validate_columns(
    df,
    required_columns=['produto_id', 'preco', 'estoque'],
    table_name='produtos'
)

if not is_valid:
    raise ValueError(f"Colunas faltando: {missing}")
```

#### Tratar Valores Nulos

```python
from core.utils.query_validator import handle_nulls

# Remover linhas com nulos
df = handle_nulls(df, 'preco', strategy='drop')

# Preencher com valor
df = handle_nulls(df, 'estoque', strategy='fill', fill_value=0)

# Manter nulos (apenas log)
df = handle_nulls(df, 'observacao', strategy='keep')
```

#### Converter Tipos

```python
from core.utils.query_validator import QueryValidator

validator = QueryValidator()

df = validator.validate_and_convert_types(df, {
    'produto_id': 'str',
    'preco': 'float',
    'estoque': 'int',
    'data_cadastro': 'datetime'
})
```

#### Filtro Seguro

```python
from core.utils.query_validator import safe_filter

# Aplicar filtro com tratamento de erro
df_filtered = safe_filter(
    df,
    filter_func=lambda df: df[df['preco'] > 0],
    error_msg="Erro ao filtrar por preço"
)
```

#### Timeout

```python
from core.utils.query_validator import QueryValidator, QueryTimeout

validator = QueryValidator(default_timeout=30)

def query_pesada():
    # processamento pesado
    return resultado

try:
    result = validator.execute_with_timeout(query_pesada, timeout=15)
except QueryTimeout:
    print("Query muito lenta!")
```

### API Reference - QueryValidator

#### Classe QueryValidator

##### `__init__(default_timeout: int = 30)`

Inicializa o validador.

**Parâmetros:**
- `default_timeout`: Timeout padrão em segundos

##### `validate_columns_in_dataframe(df, required_columns, table_name) -> Tuple[bool, List[str]]`

Valida se colunas existem no DataFrame.

**Retorna:** `(is_valid, missing_columns)`

##### `handle_null_values(df, column_name, strategy='drop', fill_value=None) -> DataFrame`

Trata valores nulos.

**Estratégias:**
- `'drop'`: Remove linhas com nulos
- `'fill'`: Preenche com fill_value
- `'keep'`: Mantém nulos

##### `validate_and_convert_types(df, column_types) -> DataFrame`

Converte tipos de colunas.

**Tipos suportados:** `'int'`, `'float'`, `'str'`, `'datetime'`

##### `safe_filter(df, filter_func, error_message) -> DataFrame`

Aplica filtro com tratamento de erro.

##### `execute_with_timeout(func, timeout, *args, **kwargs) -> Any`

Executa função com timeout.

#### Funções Auxiliares

```python
# Validar colunas
is_valid, missing = validate_columns(df, ['col1', 'col2'])

# Tratar nulos
df = handle_nulls(df, 'coluna', strategy='fill', fill_value=0)

# Filtro seguro
df = safe_filter(df, lambda df: df[df['col'] > 0])

# Mensagem amigável
msg = get_friendly_error(exception)
```

---

## 📖 ErrorHandler

### Uso Básico

#### Tratamento Manual

```python
from core.utils.error_handler import handle_error

try:
    # operação que pode falhar
    df = pd.read_parquet("arquivo.parquet")
except Exception as e:
    error_ctx = handle_error(
        error=e,
        context={'operation': 'load_data', 'file': 'arquivo.parquet'},
        user_message="Não foi possível carregar os dados"
    )

    print(error_ctx.user_message)
    # Erro é automaticamente logado e salvo
```

#### Decorador

```python
from core.utils.error_handler import error_handler_decorator

@error_handler_decorator(
    context_func=lambda une: {'une': une},
    return_on_error={'success': False, 'data': [], 'count': 0}
)
def buscar_produtos(une: int):
    if une < 1 or une > 9:
        raise ValueError(f"UNE inválida: {une}")

    return {'success': True, 'data': [...], 'count': 10}

# Uso: se houver erro, retorna return_on_error automaticamente
result = buscar_produtos(une=1)
```

#### Resposta Padronizada

```python
from core.utils.error_handler import create_error_response

try:
    # operação
    result = processar_dados()
except Exception as e:
    response = create_error_response(
        error=e,
        context={'operation': 'processar_dados'},
        include_details=False
    )

    # response = {
    #     'success': False,
    #     'data': [],
    #     'count': 0,
    #     'message': 'Mensagem amigável',
    #     'error_type': 'ValueError',
    #     'timestamp': '2025-10-17T10:30:00'
    # }
```

#### Estatísticas

```python
from core.utils.error_handler import get_error_stats

stats = get_error_stats()

print(f"Total de erros: {stats['total_errors']}")
print(f"Erro mais comum: {stats['most_common_error']}")
print(f"Contadores: {stats['error_counts']}")
```

### API Reference - ErrorHandler

#### Classe ErrorContext

Contexto rico de erro com:
- `error`: Exceção original
- `error_type`: Nome da classe de exceção
- `error_message`: Mensagem técnica
- `user_message`: Mensagem amigável
- `context`: Dict com contexto
- `timestamp`: Momento do erro
- `traceback`: Stack trace completo

**Métodos:**
- `to_dict()`: Converte para dicionário
- `log(level)`: Registra no log
- `save_to_file()`: Salva em arquivo JSONL

#### Classe ErrorHandler

##### `handle_error(error, context, user_message=None, log_level=ERROR, save_to_file=True) -> ErrorContext`

Trata erro de forma centralizada.

##### `get_error_stats() -> Dict`

Retorna estatísticas de erros.

##### `clear_stats()`

Limpa estatísticas de erro.

#### Funções Auxiliares

```python
# Tratamento de erro
error_ctx = handle_error(exception, context={})

# Estatísticas
stats = get_error_stats()

# Decorador
@error_handler_decorator(...)
def funcao():
    pass

# Resposta padronizada
response = create_error_response(exception, context={})
```

#### ParquetErrorHandler

Handler específico para erros de Parquet:

```python
from core.utils.error_handler import ParquetErrorHandler

try:
    df = pd.read_parquet("arquivo.parquet")
except Exception as e:
    response = ParquetErrorHandler.handle_parquet_error(
        error=e,
        file_path="arquivo.parquet"
    )
```

---

## 🔍 Mensagens User-Friendly

O ErrorHandler mapeia erros técnicos para mensagens amigáveis:

| Erro Técnico | Mensagem User-Friendly |
|--------------|----------------------|
| `FileNotFoundError` | Arquivo de dados não encontrado. Verifique se os dados foram carregados. |
| `KeyError` | Campo não encontrado nos dados. Verifique os parâmetros da consulta. |
| `ValueError` | Valor inválido encontrado. Verifique os dados de entrada. |
| `TypeError` | Tipo de dado incompatível na operação. |
| `ParserError` | Erro ao ler arquivo de dados. O arquivo pode estar corrompido. |
| `MemoryError` | Memória insuficiente. Tente reduzir o volume de dados consultado. |
| `TimeoutError` | A operação demorou muito tempo. Tente usar filtros mais específicos. |

---

## 💡 Exemplos Práticos

### Exemplo 1: Pipeline de Validação Completo

```python
from core.utils.query_validator import QueryValidator, validate_columns, handle_nulls
from core.utils.error_handler import error_handler_decorator

@error_handler_decorator(
    context_func=lambda **kwargs: kwargs,
    return_on_error={'success': False, 'data': []}
)
def processar_dados(file_path: str):
    # 1. Carregar
    df = pd.read_parquet(file_path)

    # 2. Validar colunas
    is_valid, missing = validate_columns(df, ['id', 'valor'])
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # 3. Tratar nulos
    df = handle_nulls(df, 'valor', strategy='fill', fill_value=0)

    # 4. Converter tipos
    validator = QueryValidator()
    df = validator.validate_and_convert_types(df, {
        'id': 'str',
        'valor': 'float'
    })

    # 5. Retornar
    return {
        'success': True,
        'data': df.to_dict('records')
    }
```

### Exemplo 2: Query com Timeout

```python
from core.utils.query_validator import QueryValidator, QueryTimeout

validator = QueryValidator(default_timeout=30)

def query_pesada():
    # processamento pesado
    return resultado

try:
    result = validator.execute_with_timeout(query_pesada, timeout=15)
except QueryTimeout:
    print("Query muito lenta! Use filtros mais específicos.")
```

### Exemplo 3: Análise de Erros

```python
from core.utils.error_handler import get_error_stats

# Após executar várias operações
stats = get_error_stats()

if stats['total_errors'] > 0:
    print(f"Erros detectados: {stats['total_errors']}")
    print(f"Mais comum: {stats['most_common_error']}")

    for error_type, count in stats['error_counts'].items():
        print(f"  {error_type}: {count}")
```

---

## 🧪 Testes

### Executar Testes

```bash
# Testes de QueryValidator
python -m pytest tests/test_validators_and_handlers.py::TestQueryValidator -v

# Testes de ErrorHandler
python -m pytest tests/test_validators_and_handlers.py::TestErrorHandler -v
```

---

## 📚 Documentação Adicional

- **Guia Completo:** `docs/GUIA_USO_VALIDADORES.md`
- **Quick Reference:** `docs/QUICK_REFERENCE_VALIDADORES.md`
- **Documentação Técnica:** `docs/CORRECOES_QUERIES_IMPLEMENTADAS.md`

---

## 🤝 Contribuindo

Ao adicionar novos utilitários:

1. Criar função/classe em arquivo apropriado
2. Documentar com docstrings
3. Adicionar testes
4. Atualizar documentação
5. Adicionar exemplos de uso

---

## 📄 Licença

Este código é parte do projeto Agent Solution BI.

---

**Versão:** 1.0
**Última Atualização:** 2025-10-17
**Autor:** Code Agent
