# ANÁLISE DETALHADA: get_produtos_une()

## Arquivo Analisado
`C:\Users\André\Documents\Agent_Solution_BI\pages\7_📦_Transferências.py`

---

## 1. IMPLEMENTAÇÃO ATUAL

```python
def get_produtos_une():
    """Obtém lista de produtos com estoque > 0 na UNE via API"""
    try:
        with st.spinner("🔍 Buscando produtos na UNE..."):
            # Usa a ferramenta UNE para buscar produtos com estoque
            result = une_estoque_tool._run(
                consulta="mostre produtos com estoque maior que zero",
                loja="UNE"
            )

            if not result or "erro" in result.lower():
                st.error("❌ Erro ao buscar produtos da UNE")
                return []

            # Parse do resultado
            produtos = []
            lines = result.split('\n')
            for line in lines:
                if '|' in line and not line.startswith('|--'):
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 3 and parts[0].isdigit():
                        produtos.append({
                            'codigo': parts[0],
                            'descricao': parts[1],
                            'estoque': parts[2]
                        })

            return produtos
    except Exception as e:
        st.error(f"❌ Erro ao carregar produtos: {str(e)}")
        return []
```

---

## 2. BUGS IDENTIFICADOS

### 🐛 BUG #1: Filtro de Estoque Ineficaz
**Linha:** `consulta="mostre produtos com estoque maior que zero"`

**Problema:**
- A consulta em linguagem natural NÃO garante filtro SQL correto
- A UNE tool pode retornar todos os produtos e apenas formatar a resposta
- Não há validação numérica do campo `estoque` após o parse

**Impacto:**
- Produtos com estoque = 0 ou NULL podem aparecer na lista
- Performance ruim (busca tudo e filtra na apresentação)

---

### 🐛 BUG #2: Parse de Texto sem Validação Numérica
**Linhas:**
```python
if len(parts) >= 3 and parts[0].isdigit():
    produtos.append({
        'codigo': parts[0],
        'descricao': parts[1],
        'estoque': parts[2]  # ⚠️ STRING, não numérico!
    })
```

**Problema:**
- `parts[2]` é **STRING** (ex: "10.5", "0", "NULL")
- Sem conversão para `float` ou `int`
- Sem validação se estoque > 0 após parse
- Campo `estoque` fica inconsistente para comparações

**Impacto:**
- Comparações numéricas falham silenciosamente
- Produtos com estoque "0" (string) passam no filtro
- Ordenação alfabética ao invés de numérica

---

### 🐛 BUG #3: Falta Validação de Tipo na UNE Tool
**Arquivo relacionado:** `core/tools/une_tools.py`

**Problema:**
- A função `_consultar_parquet()` retorna `estoque_atual` como STRING
- Não há conversão `pd.to_numeric()` no processamento Parquet
- Schema incorreto ou casting ausente

---

### 🐛 BUG #4: Lógica de Parse Frágil
**Linha:** `if '|' in line and not line.startswith('|--'):`

**Problema:**
- Assume formato de tabela markdown
- Pode quebrar se a UNE tool mudar formato de resposta
- Não trata casos de colunas vazias ou NULL

---

## 3. MAPEAMENTO DE COLUNAS

### SQL → Parquet → Streamlit

| Origem SQL | Parquet Cache | Parse Streamlit | Tipo Esperado |
|------------|---------------|-----------------|---------------|
| `codigo` | `codigo` | `codigo` (str) | ✅ STRING |
| `descricao` | `descricao` | `descricao` (str) | ✅ STRING |
| `estoque_atual` | `estoque_atual` | `estoque` (str) | ❌ **DEVERIA SER NUMERIC** |

**Problema:**
- No Parquet, `estoque_atual` está como **object/string**
- Deveria ser **float64** ou **int64**

---

## 4. SOLUÇÃO PROPOSTA

### FIX #1: Corrigir Conversão de Tipos no une_tools.py

**Arquivo:** `C:\Users\André\Documents\Agent_Solution_BI\core\tools\une_tools.py`

**Localização:** Função `_consultar_parquet()` ou `_processar_resultado()`

```python
# ANTES (incorreto)
df = pd.read_parquet(cache_file)

# DEPOIS (correto)
df = pd.read_parquet(cache_file)
# Garantir conversão numérica
if 'estoque_atual' in df.columns:
    df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
```

---

### FIX #2: Filtro SQL Direto (Melhor Abordagem)

**Arquivo:** `C:\Users\André\Documents\Agent_Solution_BI\pages\7_📦_Transferências.py`

```python
def get_produtos_une():
    """Obtém lista de produtos com estoque > 0 na UNE via consulta SQL otimizada"""
    try:
        with st.spinner("🔍 Buscando produtos na UNE..."):
            # OPÇÃO A: Consulta SQL direta (mais eficiente)
            result = une_estoque_tool._run(
                consulta="SELECT codigo, descricao, estoque_atual FROM produtos WHERE loja = 'UNE' AND estoque_atual > 0",
                loja="UNE",
                formato="sql"  # Se suportado
            )

            # OPÇÃO B: Parse com validação numérica
            produtos = []
            lines = result.split('\n')
            for line in lines:
                if '|' in line and not line.startswith('|--'):
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            estoque = float(parts[2].replace(',', '.'))
                            if estoque > 0:  # ✅ Filtro numérico explícito
                                produtos.append({
                                    'codigo': parts[0],
                                    'descricao': parts[1],
                                    'estoque': estoque  # ✅ Agora é float
                                })
                        except (ValueError, IndexError):
                            continue  # Ignora linhas inválidas

            return produtos
    except Exception as e:
        st.error(f"❌ Erro ao carregar produtos: {str(e)}")
        return []
```

---

### FIX #3: Validação de Tipo no Cache Parquet

**Arquivo:** `C:\Users\André\Documents\Agent_Solution_BI\core\tools\une_tools.py`

**Função:** `_salvar_cache()` ou similar

```python
def _processar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
    """Garante tipos corretos antes de salvar cache"""

    # Converter colunas numéricas
    numeric_cols = ['estoque_atual', 'preco', 'custo']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Converter colunas de texto
    text_cols = ['codigo', 'descricao', 'loja']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df
```

---

## 5. CÓDIGO FINAL RECOMENDADO

### get_produtos_une() - VERSÃO CORRIGIDA

```python
def get_produtos_une():
    """
    Obtém lista de produtos com estoque > 0 na UNE via API.

    Returns:
        list[dict]: Lista de dicionários com:
            - codigo (str): Código do produto
            - descricao (str): Descrição do produto
            - estoque (float): Quantidade em estoque

    Validações:
        - Converte estoque para numérico
        - Filtra apenas estoque > 0
        - Ignora linhas inválidas
    """
    try:
        with st.spinner("🔍 Buscando produtos na UNE..."):
            # Consulta produtos na UNE
            result = une_estoque_tool._run(
                consulta="mostre todos os produtos da loja UNE com código, descrição e estoque",
                loja="UNE"
            )

            if not result or "erro" in result.lower():
                st.error("❌ Erro ao buscar produtos da UNE")
                return []

            # Parse do resultado com validação numérica
            produtos = []
            lines = result.split('\n')

            for line in lines:
                # Ignora cabeçalhos e separadores
                if '|' in line and not line.startswith('|--') and not line.startswith('| Código'):
                    parts = [p.strip() for p in line.split('|') if p.strip()]

                    if len(parts) >= 3:
                        try:
                            codigo = parts[0]
                            descricao = parts[1]

                            # ✅ CONVERSÃO NUMÉRICA EXPLÍCITA
                            estoque_str = parts[2].replace(',', '.')
                            estoque = float(estoque_str)

                            # ✅ FILTRO NUMÉRICO EXPLÍCITO
                            if estoque > 0 and codigo.isdigit():
                                produtos.append({
                                    'codigo': codigo,
                                    'descricao': descricao,
                                    'estoque': estoque
                                })

                        except (ValueError, IndexError, AttributeError) as e:
                            # Ignora linhas com dados inválidos
                            continue

            # Log para debug
            st.info(f"✅ {len(produtos)} produtos encontrados com estoque > 0")

            return produtos

    except Exception as e:
        st.error(f"❌ Erro ao carregar produtos: {str(e)}")
        return []
```

---

## 6. TESTES RECOMENDADOS

### Teste de Conversão de Tipo

```python
def test_estoque_conversion():
    """Testa conversão de estoque string → float"""
    test_cases = [
        ("10.5", 10.5),
        ("10,5", 10.5),
        ("0", 0.0),
        ("100", 100.0),
        ("", None),  # Deve falhar
        ("NULL", None),  # Deve falhar
    ]

    for input_val, expected in test_cases:
        try:
            result = float(input_val.replace(',', '.'))
            assert result == expected, f"Expected {expected}, got {result}"
        except ValueError:
            assert expected is None
```

---

## 7. CHECKLIST DE CORREÇÃO

- [ ] Corrigir conversão de tipos em `une_tools.py` (linhas ~150-200)
- [ ] Adicionar validação numérica em `get_produtos_une()` (linha ~45)
- [ ] Implementar filtro `estoque > 0` após conversão (linha ~60)
- [ ] Adicionar tratamento de exceção para valores inválidos
- [ ] Testar com dados reais do cache Parquet
- [ ] Validar schema do Parquet (tipos corretos)
- [ ] Adicionar logs de debug para diagnóstico

---

## 8. IMPACTO ESPERADO

### Antes da Correção
- Produtos com estoque = 0 aparecem
- Comparações numéricas falham
- Ordenação alfabética incorreta

### Depois da Correção
- Apenas produtos com estoque > 0
- Comparações numéricas precisas
- Ordenação numérica correta
- Performance melhorada (filtro early)

---

## 9. ARQUIVOS RELACIONADOS

1. `pages/7_📦_Transferências.py` - Função principal
2. `core/tools/une_tools.py` - Conversão de tipos
3. `data/cache/*.json` - Cache Parquet (verificar schema)
4. `tests/test_transferencias_streamlit.py` - Testes automatizados

---

**Gerado por:** Code Agent
**Data:** 2025-10-15
**Commit sugerido:** `fix(transferencias): Corrigir filtro de estoque e conversão de tipos em get_produtos_une()`
