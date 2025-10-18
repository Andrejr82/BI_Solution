# Quick Reference - Validadores e Handlers

**Versão:** 1.0 | **Data:** 2025-10-17 | **Autor:** Code Agent

---

## 🚀 Imports Essenciais

```python
# SchemaValidator
from core.validators import SchemaValidator

# QueryValidator
from core.utils.query_validator import (
    QueryValidator,
    validate_columns,
    handle_nulls,
    safe_filter,
    get_friendly_error
)

# ErrorHandler
from core.utils.error_handler import (
    handle_error,
    error_handler_decorator,
    create_error_response,
    get_error_stats
)
```

---

## 📋 Cheat Sheet

### SchemaValidator

```python
# Inicializar
validator = SchemaValidator()

# Validar arquivo Parquet
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")

# Validar colunas de query
is_valid, invalid = validator.validate_query_columns("tabela", ["col1", "col2"])

# Listar colunas obrigatórias
cols = validator.list_required_columns("tabela")
```

### QueryValidator

```python
# Validar colunas
is_valid, missing = validate_columns(df, ["col1", "col2"], "tabela")

# Tratar nulos
df = handle_nulls(df, "coluna", strategy="fill", fill_value=0)
# Estratégias: "drop", "fill", "keep"

# Filtro seguro
df = safe_filter(df, lambda df: df[df["col"] > 0])

# Converter tipos
validator = QueryValidator()
df = validator.validate_and_convert_types(df, {
    "col_int": "int",
    "col_float": "float",
    "col_str": "str",
    "col_date": "datetime"
})

# Timeout
result = validator.execute_with_timeout(func, timeout=30)

# Mensagem amigável
msg = get_friendly_error(exception)
```

### ErrorHandler

```python
# Tratamento manual
try:
    # código
except Exception as e:
    error_ctx = handle_error(e, context={"key": "value"})
    print(error_ctx.user_message)

# Decorador
@error_handler_decorator(
    context_func=lambda x: {"param": x},
    return_on_error={"success": False}
)
def funcao(param):
    # código
    return {"success": True}

# Resposta padronizada
response = create_error_response(exception, context={})

# Estatísticas
stats = get_error_stats()
```

---

## 📝 Templates Comuns

### Template 1: Função com Validação Completa

```python
from core.validators import SchemaValidator
from core.utils.query_validator import validate_columns, handle_nulls
from core.utils.error_handler import error_handler_decorator
import pandas as pd

@error_handler_decorator(
    context_func=lambda **kwargs: {"params": kwargs},
    return_on_error={"success": False, "data": [], "count": 0}
)
def consultar_dados(tabela: str, filtro: dict = None):
    """Template de consulta com validação."""

    # 1. Validar schema
    validator = SchemaValidator()
    file_path = f"data/parquet/{tabela}.parquet"

    is_valid, errors = validator.validate_parquet_file(file_path)
    if not is_valid:
        raise ValueError(f"Schema inválido: {errors}")

    # 2. Carregar
    df = pd.read_parquet(file_path)

    # 3. Validar colunas
    required = ["id", "nome"]
    is_valid, missing = validate_columns(df, required)
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # 4. Tratar nulos
    df = handle_nulls(df, "valor", strategy="fill", fill_value=0)

    # 5. Aplicar filtros
    if filtro:
        for col, val in filtro.items():
            df = df[df[col] == val]

    return {
        "success": True,
        "data": df.to_dict("records"),
        "count": len(df)
    }
```

### Template 2: Pipeline de Transformação

```python
from core.utils.query_validator import QueryValidator, validate_columns, handle_nulls

def pipeline_transformacao(df: pd.DataFrame):
    """Pipeline de transformação com validação."""

    validator = QueryValidator()

    # 1. Validar colunas
    is_valid, missing = validate_columns(df, ["id", "valor"])
    if not is_valid:
        raise ValueError(f"Colunas faltando: {missing}")

    # 2. Tratar nulos
    df = handle_nulls(df, "valor", strategy="fill", fill_value=0)

    # 3. Converter tipos
    df = validator.validate_and_convert_types(df, {
        "id": "str",
        "valor": "float"
    })

    # 4. Limpar
    df = df.drop_duplicates()

    return df
```

### Template 3: Validação de Múltiplos Arquivos

```python
from core.validators import SchemaValidator
from pathlib import Path

def validar_todos_arquivos(diretorio: str):
    """Valida todos os arquivos Parquet em um diretório."""

    validator = SchemaValidator()
    resultados = []

    for arquivo in Path(diretorio).glob("*.parquet"):
        is_valid, errors = validator.validate_parquet_file(str(arquivo))

        resultados.append({
            "arquivo": arquivo.name,
            "valido": is_valid,
            "erros": errors
        })

    return resultados
```

---

## 🔧 Configurações Comuns

### Configurar Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Configurar Timeout Padrão

```python
from core.utils.query_validator import QueryValidator

# Timeout de 60 segundos
validator = QueryValidator(default_timeout=60)
```

### Habilitar/Desabilitar Cache

```python
from core.tools.une_tools import enable_cache, disable_cache, clear_cache

enable_cache()   # Habilitar
disable_cache()  # Desabilitar
clear_cache()    # Limpar
```

---

## 🐛 Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| `KeyError: 'coluna'` | Use `validate_columns()` antes de acessar |
| `ValueError: could not convert` | Use `validate_and_convert_types()` |
| `QueryTimeout` | Aumente timeout ou otimize query |
| `Schema inválido` | Verifique `validate_parquet_file()` |
| `FileNotFoundError` | Verifique caminho do arquivo |

### Comandos de Debug

```python
# Verificar colunas disponíveis
print(list(df.columns))

# Verificar tipos
print(df.dtypes)

# Verificar nulos
print(df.isna().sum())

# Verificar schema esperado
validator = SchemaValidator()
schema = validator.get_table_schema("tabela")
print(schema["columns"].keys())

# Verificar estatísticas de erro
stats = get_error_stats()
print(stats)
```

---

## 📊 Exemplos por Caso de Uso

### Caso 1: Carregar e Validar Dados

```python
from core.validators import SchemaValidator
import pandas as pd

validator = SchemaValidator()

# Validar antes de carregar
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")

if is_valid:
    df = pd.read_parquet("arquivo.parquet")
else:
    print(f"Erros: {errors}")
```

### Caso 2: Query com Filtros Seguros

```python
from core.utils.query_validator import safe_filter
import pandas as pd

df = pd.read_parquet("arquivo.parquet")

# Aplicar filtros com segurança
df = safe_filter(df, lambda df: df[df["preco"] > 0])
df = safe_filter(df, lambda df: df[df["estoque"] >= 0])
```

### Caso 3: Converter Tipos com Segurança

```python
from core.utils.query_validator import QueryValidator

validator = QueryValidator()

df = validator.validate_and_convert_types(df, {
    "id": "str",
    "preco": "float",
    "quantidade": "int",
    "data": "datetime"
})
```

### Caso 4: Tratamento de Erros

```python
from core.utils.error_handler import create_error_response

try:
    # operação
    result = processar()
except Exception as e:
    return create_error_response(e, context={"op": "processar"})
```

---

## ⚡ Dicas de Performance

### 1. Use Cache

```python
# Une_tools já tem cache implementado
from core.tools.une_tools import get_produtos_une

# Primeira chamada: carrega do Parquet
result1 = get_produtos_une(une=1)

# Segunda chamada: usa cache
result2 = get_produtos_une(une=1)  # Mais rápido!
```

### 2. Valide Schemas Uma Vez

```python
# ❌ Ruim: Validar toda vez
for i in range(100):
    validator.validate_parquet_file("arquivo.parquet")

# ✅ Bom: Validar uma vez
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")
if is_valid:
    for i in range(100):
        # processar
```

### 3. Use Chunks para Arquivos Grandes

```python
# Para arquivos muito grandes
for chunk in pd.read_parquet("arquivo_grande.parquet", chunksize=10000):
    processar(chunk)
```

### 4. Limite Resultados

```python
# Sempre use limit para queries exploratórias
df = pd.read_parquet("arquivo.parquet")
df_sample = df.head(1000)  # Apenas 1000 linhas
```

---

## 📖 Referências Rápidas

### Documentação Completa
- `docs/CORRECOES_QUERIES_IMPLEMENTADAS.md` - Referência técnica
- `docs/GUIA_USO_VALIDADORES.md` - Guia completo de uso
- `docs/RESUMO_CORRECOES_QUERIES.md` - Resumo executivo

### Executar Testes

```bash
# Testes
python -m pytest tests/test_validators_and_handlers.py -v

# Demo
python scripts/demo_validators.py
```

### Estrutura de Arquivos

```
core/
├── validators/
│   ├── __init__.py
│   └── schema_validator.py
└── utils/
    ├── query_validator.py
    └── error_handler.py
```

---

## 🎯 Checklist de Uso

Ao implementar uma nova query/função, use este checklist:

- [ ] Importar validadores necessários
- [ ] Validar schema do arquivo Parquet
- [ ] Validar colunas obrigatórias no DataFrame
- [ ] Tratar valores nulos
- [ ] Converter tipos com segurança
- [ ] Aplicar filtros com `safe_filter()`
- [ ] Usar decorador `@error_handler_decorator`
- [ ] Retornar resposta padronizada
- [ ] Adicionar testes

---

## 💡 Padrões Recomendados

### Nomenclatura

```python
# ✅ Bom
def get_produtos_une(une: int) -> Dict[str, Any]:
    """Descrição clara."""
    pass

# ❌ Ruim
def gpune(u):
    pass
```

### Tipos de Retorno

```python
# ✅ Bom: Sempre retornar dict padronizado
return {
    "success": True,
    "data": [...],
    "count": 10,
    "message": "Sucesso"
}

# ❌ Ruim: Retornar tipos inconsistentes
return lista_dados  # Às vezes lista, às vezes dict
```

### Validação

```python
# ✅ Bom: Validar no início
def funcao(param):
    if not validar(param):
        raise ValueError("Parâmetro inválido")
    # processar

# ❌ Ruim: Validar no meio do processamento
def funcao(param):
    # processar
    if not validar(param):  # Muito tarde!
        raise ValueError("Erro")
```

---

**Fim da Referência Rápida**

Para mais detalhes, consulte a documentação completa em `docs/`.
