# Validators Package

**Versão:** 1.0
**Data:** 2025-10-17
**Autor:** Code Agent

---

## 📋 Visão Geral

Este pacote contém validadores para garantir a integridade de dados e schemas no Agent Solution BI.

### Componentes

- **SchemaValidator**: Valida schemas Parquet contra o catálogo corporativo

---

## 🚀 Instalação

```python
from core.validators import SchemaValidator
```

---

## 📖 Uso Básico

### Exemplo 1: Validar Arquivo Parquet

```python
from core.validators import SchemaValidator

validator = SchemaValidator()

# Validar arquivo
is_valid, errors = validator.validate_parquet_file(
    "data/parquet/produtos_une1.parquet",
    table_name="produtos"
)

if not is_valid:
    print(f"Erros encontrados: {errors}")
else:
    print("Schema válido!")
```

### Exemplo 2: Validar Colunas de Query

```python
validator = SchemaValidator()

# Colunas que você vai usar na query
query_columns = ['produto_id', 'preco', 'estoque']

# Validar antes de executar
is_valid, invalid_cols = validator.validate_query_columns(
    table_name='produtos',
    query_columns=query_columns
)

if not is_valid:
    raise ValueError(f"Colunas inválidas: {invalid_cols}")
```

### Exemplo 3: Listar Colunas Obrigatórias

```python
validator = SchemaValidator()

# Obter lista de colunas esperadas
required_cols = validator.list_required_columns('produtos')

print(f"Colunas obrigatórias: {required_cols}")
```

---

## 🔧 API Reference

### SchemaValidator

#### Métodos Principais

##### `__init__(catalog_path: Optional[str] = None)`

Inicializa o validador.

**Parâmetros:**
- `catalog_path`: Caminho para catalog_focused.json (opcional)

**Exemplo:**
```python
# Usar catálogo padrão
validator = SchemaValidator()

# Usar catálogo customizado
validator = SchemaValidator("path/to/custom_catalog.json")
```

##### `validate_parquet_file(parquet_path: str, table_name: Optional[str] = None) -> Tuple[bool, List[str]]`

Valida um arquivo Parquet contra o catálogo.

**Parâmetros:**
- `parquet_path`: Caminho para o arquivo Parquet
- `table_name`: Nome da tabela no catálogo (inferido se None)

**Retorna:**
- Tupla `(is_valid, errors)` onde:
  - `is_valid`: True se schema válido
  - `errors`: Lista de mensagens de erro

**Exemplo:**
```python
is_valid, errors = validator.validate_parquet_file(
    "data/parquet/produtos.parquet",
    table_name="produtos"
)
```

##### `validate_query_columns(table_name: str, query_columns: List[str]) -> Tuple[bool, List[str]]`

Valida se as colunas de uma query existem no schema.

**Parâmetros:**
- `table_name`: Nome da tabela
- `query_columns`: Lista de colunas usadas na query

**Retorna:**
- Tupla `(is_valid, invalid_columns)`

**Exemplo:**
```python
is_valid, invalid = validator.validate_query_columns(
    'produtos',
    ['produto_id', 'preco', 'estoque']
)
```

##### `list_required_columns(table_name: str) -> List[str]`

Lista as colunas obrigatórias de uma tabela.

**Parâmetros:**
- `table_name`: Nome da tabela

**Retorna:**
- Lista de nomes de colunas obrigatórias

**Exemplo:**
```python
cols = validator.list_required_columns('produtos')
print(f"Colunas obrigatórias: {cols}")
```

##### `get_table_schema(table_name: str) -> Optional[Dict]`

Retorna o schema esperado para uma tabela do catálogo.

**Parâmetros:**
- `table_name`: Nome da tabela

**Retorna:**
- Dict com schema da tabela ou None se não encontrada

**Exemplo:**
```python
schema = validator.get_table_schema('produtos')
if schema:
    print(f"Colunas: {list(schema['columns'].keys())}")
```

---

## 🔍 Mapeamento de Tipos

O SchemaValidator suporta os seguintes mapeamentos de tipos:

| Tipo Base | Tipos Compatíveis |
|-----------|-------------------|
| `int64` | int64, int32, int16, int8 |
| `float64` | float64, float32, double |
| `string` | string, large_string, utf8 |
| `date` | date32, date64 |
| `datetime` | timestamp[ns], timestamp[us], timestamp[ms] |
| `bool` | bool |

**Exemplo:**
```python
# Um arquivo com tipo int32 é compatível com schema esperando int64
# Um arquivo com tipo float32 é compatível com schema esperando float64
```

---

## ⚠️ Tratamento de Erros

### Erros Comuns

#### 1. Arquivo Não Encontrado

```python
# FileNotFoundError se arquivo não existir
is_valid, errors = validator.validate_parquet_file("arquivo_inexistente.parquet")
# errors: ["Erro ao validar arquivo Parquet 'arquivo_inexistente.parquet': ..."]
```

#### 2. Colunas Faltantes

```python
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")
# Se colunas faltando:
# errors: ["Tabela 'produtos': Colunas faltantes: ['coluna1', 'coluna2']"]
```

#### 3. Tipos Incompatíveis

```python
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")
# Se tipos incompatíveis:
# errors: ["Tabela 'produtos', coluna 'preco': Tipo incompatível. Esperado: float64, Encontrado: string"]
```

#### 4. Tabela Não Catalogada

```python
is_valid, errors = validator.validate_parquet_file("arquivo.parquet", "tabela_desconhecida")
# errors: ["Tabela 'tabela_desconhecida' não encontrada no catálogo"]
```

---

## 💡 Boas Práticas

### 1. Validar Antes de Carregar

```python
# ✅ Bom: Validar antes de carregar
validator = SchemaValidator()
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")

if is_valid:
    df = pd.read_parquet("arquivo.parquet")
else:
    print(f"Schema inválido: {errors}")
```

### 2. Validar Colunas de Query

```python
# ✅ Bom: Validar colunas antes de usar
is_valid, invalid = validator.validate_query_columns('produtos', ['col1', 'col2'])

if is_valid:
    df = df[['col1', 'col2']]
else:
    print(f"Colunas inválidas: {invalid}")
```

### 3. Reutilizar Validador

```python
# ✅ Bom: Criar uma instância e reutilizar
validator = SchemaValidator()

for file in files:
    is_valid, errors = validator.validate_parquet_file(file)
    # processar
```

### 4. Tratar Erros Adequadamente

```python
# ✅ Bom: Tratar erros de validação
is_valid, errors = validator.validate_parquet_file("arquivo.parquet")

if not is_valid:
    for error in errors:
        logger.error(error)
    raise ValueError(f"Validação falhou: {len(errors)} erros")
```

---

## 🧪 Testes

### Executar Testes

```bash
python -m pytest tests/test_validators_and_handlers.py::TestSchemaValidator -v
```

### Exemplo de Teste

```python
def test_schema_validator():
    validator = SchemaValidator()

    # Mock de catálogo
    validator.catalog['test_table'] = {
        'columns': {
            'id': {'type': 'int64'},
            'name': {'type': 'string'}
        }
    }

    # Testar validação de colunas
    required = validator.list_required_columns('test_table')
    assert 'id' in required
    assert 'name' in required
```

---

## 📚 Documentação Adicional

- **Guia Completo:** `docs/GUIA_USO_VALIDADORES.md`
- **Quick Reference:** `docs/QUICK_REFERENCE_VALIDADORES.md`
- **Documentação Técnica:** `docs/CORRECOES_QUERIES_IMPLEMENTADAS.md`

---

## 🤝 Contribuindo

Ao adicionar novos validadores:

1. Criar classe em arquivo separado
2. Adicionar imports em `__init__.py`
3. Documentar com docstrings
4. Adicionar testes
5. Atualizar documentação

---

## 📄 Licença

Este código é parte do projeto Agent Solution BI.

---

**Versão:** 1.0
**Última Atualização:** 2025-10-17
**Autor:** Code Agent
