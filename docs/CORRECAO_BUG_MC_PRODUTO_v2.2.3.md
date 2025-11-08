# Correção Bug: Produto não encontrado ao calcular MC

**Versão**: v2.2.3
**Data**: 2025-11-07
**Severity**: CRÍTICO - Bloqueava consultas de MC

---

## Resumo Executivo

Bug crítico corrigido na função `calcular_mc_produto()` que causava erro "Produto não encontrado" mesmo quando o produto existia na base de dados.

**Causa raiz**: Tentativa de carregar colunas inexistentes do Parquet (`ESTOQUE_GONDOLA`, `estoque_gondola`)

**Impacto**: 100% das consultas de MC falhavam com erro falso-positivo

**Solução**: Mapeamento correto de colunas do Parquet e normalização de nomes

---

## Problema Identificado

### Sintoma
```
Erro: Produto 369947 não encontrado na UNE 2720
```

Quando executado:
```python
calcular_mc_produto(produto_id=369947, une_id=2720)
```

### Causa Raiz

A função `calcular_mc_produto()` solicitava colunas que **não existem** no arquivo Parquet:

```python
# ANTES (INCORRETO)
produto_df = _load_data(
    filters={'codigo': produto_id, 'une': une_id},
    columns=['codigo', 'nome_produto', 'une', 'mc', 'estoque_atual',
            'linha_verde', 'nomesegmento', 'ESTOQUE_GONDOLA', 'estoque_gondola']
)
```

**Problema**: Colunas `ESTOQUE_GONDOLA` e `estoque_gondola` não existem no Parquet.

**Efeito**: `pd.read_parquet()` falhava ao tentar ler colunas inexistentes, retornando erro e fazendo a função retornar DataFrame vazio.

---

## Análise Detalhada

### 1. Estrutura Real do Parquet

**Colunas existentes**:
- `media_considerada_lv` (MC = Média Considerada Linha Verde)
- `estoque_lv` (Linha Verde / Estoque Máximo)
- `estoque_gondola_lv` (Estoque em Gôndola)
- `estoque_atual` (Estoque Atual)

**Colunas NÃO existentes** (causavam falha):
- ❌ `ESTOQUE_GONDOLA`
- ❌ `estoque_gondola`
- ❌ `mc` (precisa ser mapeada para `media_considerada_lv`)
- ❌ `linha_verde` (precisa ser mapeada para `estoque_lv`)

### 2. Mapeamento Necessário

| Coluna Solicitada | Coluna Real no Parquet | Tipo |
|-------------------|------------------------|------|
| `mc` | `media_considerada_lv` | float |
| `linha_verde` | `estoque_lv` | float |
| `estoque_gondola` | `estoque_gondola_lv` | float |
| `estoque_atual` | `estoque_atual` | float |

---

## Correções Implementadas

### 1. Corrigir função `calcular_mc_produto()`

**Arquivo**: `core/tools/une_tools.py:376-384`

```python
# ANTES (INCORRETO)
produto_df = _load_data(
    filters={'codigo': produto_id, 'une': une_id},
    columns=['codigo', 'nome_produto', 'une', 'mc', 'estoque_atual',
            'linha_verde', 'nomesegmento', 'ESTOQUE_GONDOLA', 'estoque_gondola']
)

# DEPOIS (CORRETO)
produto_df = _load_data(
    filters={'codigo': produto_id, 'une': une_id},
    columns=['codigo', 'nome_produto', 'une', 'mc', 'estoque_atual',
            'linha_verde', 'nomesegmento', 'estoque_gondola_lv']
)
```

### 2. Atualizar leitura de `estoque_gondola`

**Arquivo**: `core/tools/une_tools.py:401-408`

```python
# ANTES (INCORRETO)
if 'ESTOQUE_GONDOLA' in row:
    estoque_gondola = float(row['ESTOQUE_GONDOLA'])
elif 'estoque_gondola' in row:
    estoque_gondola = float(row['estoque_gondola'])

# DEPOIS (CORRETO)
if 'estoque_gondola_lv' in row:
    estoque_gondola = float(row['estoque_gondola_lv'])
elif 'ESTOQUE_GONDOLA' in row:
    estoque_gondola = float(row['ESTOQUE_GONDOLA'])
elif 'estoque_gondola' in row:
    estoque_gondola = float(row['estoque_gondola'])
```

### 3. Adicionar mapeamento em `_load_data()`

**Arquivo**: `core/tools/une_tools.py:112-126` e `157-171`

```python
# Mapeamento de colunas no _load_data
for col in columns:
    if col == 'linha_verde':
        parquet_cols.append('estoque_lv')
    elif col == 'mc':
        parquet_cols.append('media_considerada_lv')
    elif col == 'estoque_gondola_lv':
        parquet_cols.append(col)  # Já é correto
    elif col in ['ESTOQUE_GONDOLA', 'estoque_gondola']:
        parquet_cols.append('estoque_gondola_lv')  # Mapear para correto
    else:
        parquet_cols.append(col)
```

### 4. Normalização reversa em `_normalize_dataframe()`

**Arquivo**: `core/tools/une_tools.py:84-94`

```python
# Mapear colunas do Parquet para nomes padronizados
if 'media_considerada_lv' in df.columns and 'mc' not in df.columns:
    df['mc'] = df['media_considerada_lv']

if 'estoque_lv' in df.columns and 'linha_verde' not in df.columns:
    df['linha_verde'] = df['estoque_lv']

if 'estoque_gondola_lv' in df.columns and 'estoque_gondola' not in df.columns:
    df['estoque_gondola'] = df['estoque_gondola_lv']
```

---

## Validação

### Teste Realizado

```python
from core.tools.une_tools import calcular_mc_produto

resultado = calcular_mc_produto.invoke({
    "produto_id": 369947,
    "une_id": 2720
})
```

### Resultado Antes da Correção
```
{
    "error": "Produto 369947 não encontrado na UNE 2720",
    "produto_id": 369947,
    "une_id": 2720
}
```

### Resultado Após a Correção ✅
```
{
    "produto_id": 369947,
    "une_id": 2720,
    "nome": "TNT 40GRS 100%O LG 1.40 035 BRANCO",
    "segmento": "TECIDOS",
    "mc_calculada": 444.0,
    "estoque_atual": 100.0,
    "linha_verde": 444.0,
    "percentual_linha_verde": 22.52,
    "estoque_gondola": 0.0,
    "recomendacao": "Aumentar ESTOQUE em gôndola - MC superior ao estoque atual"
}
```

---

## Dados do Produto 369947 na UNE 2720 (MAD)

**Informações Básicas**:
- **Código**: 369947
- **Nome**: TNT 40GRS 100%O LG 1.40 035 BRANCO
- **Segmento**: TECIDOS
- **UNE**: 2720 (MAD)

**Métricas**:
- **MC (Média Considerada LV)**: 444.0 unidades
- **Estoque Atual**: 100.0 unidades (22.52% da linha verde)
- **Linha Verde**: 444.0 unidades
- **Estoque Gôndola**: 0.0 unidades
- **Venda 30 dias**: 700.0 unidades

**Valores**:
- **Preço**: R$ 1.99
- **Custo**: R$ 0.72
- **Margem**: R$ 1.27 (63.82%)

---

## Impacto

### Antes
- ❌ 100% das consultas de MC falhavam
- ❌ Mensagem de erro enganosa ("Produto não encontrado")
- ❌ Impossível consultar MC via LLM

### Depois
- ✅ Consultas de MC funcionam corretamente
- ✅ Retorna dados completos do produto
- ✅ Recomendações de abastecimento geradas

---

## Lições Aprendidas

1. **Schema Validation**: Sempre validar schema do Parquet antes de solicitar colunas
2. **Mapeamento de Colunas**: Documentar mapeamento entre nomes lógicos e físicos
3. **Error Handling**: Melhorar mensagens de erro para distinguir "coluna não existe" vs "produto não encontrado"
4. **Testes**: Adicionar testes unitários para validar mapeamento de colunas

---

## Próximos Passos

### Recomendações Técnicas

1. **Criar schema validator** que alerte sobre colunas inexistentes antes de tentar carregar
2. **Adicionar testes automatizados** para todas as funções de tools UNE
3. **Documentar schema** completo do Parquet com tipos de dados
4. **Criar dicionário de dados** com mapeamento de todas as colunas

### Melhorias de UX

1. Mensagens de erro mais específicas distinguindo:
   - Produto não existe
   - Produto existe mas não na UNE especificada
   - Erro de schema/colunas

2. Adicionar validação de entrada:
   - Verificar se UNE_ID é válido
   - Verificar se PRODUTO_ID tem formato correto

---

## Arquivos Modificados

1. `core/tools/une_tools.py`
   - `calcular_mc_produto()` (linha 376-408)
   - `_load_data()` (linhas 112-126, 157-171)
   - `_normalize_dataframe()` (linhas 84-94)

## Scripts de Diagnóstico Criados

1. `diagnostic_produto_369947.py` - Diagnóstico completo
2. `analise_produto_369947.py` - Análise detalhada de colunas
3. `teste_filtro_produto.py` - Reprodução do bug
4. `teste_correcao_mc.py` - Validação da correção

---

## Conclusão

Bug crítico **100% resolvido**. A função `calcular_mc_produto()` agora:
- ✅ Encontra produtos corretamente
- ✅ Mapeia colunas do Parquet corretamente
- ✅ Retorna dados completos e precisos
- ✅ Gera recomendações de abastecimento

**Resposta à query do usuário**: O MC do produto 369947 na UNE MAD é **444.0** (Média Considerada Linha Verde).
