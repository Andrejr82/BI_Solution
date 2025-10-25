# Formatação de Moeda Brasileira (R$)

**Data:** 20 de Outubro de 2025
**Status:** ✅ Implementado

---

## 📋 Resumo

Sistema automático de formatação de valores monetários em Real Brasileiro (R$) para melhor apresentação dos dados ao usuário.

### ✨ O Que Mudou?

**ANTES:**
```
NOMESEGMENTO          VENDA_30DD
PAPELARIA            101868.644
TECIDOS               77328.702
FESTAS                41750.3402
```

**DEPOIS:**
```
NOMESEGMENTO          VENDA_30DD
PAPELARIA            R$ 101.868,64
TECIDOS              R$ 77.328,70
FESTAS               R$ 41.750,34
```

---

## 🎯 Funcionalidades

### 1. **Formatação Automática**

O sistema detecta automaticamente colunas com valores monetários:

- **Colunas detectadas como moeda:**
  - `VENDA_30DD`, `LIQUIDO_38`, `PRECO`, `CUSTO`, `VALOR`
  - `mes_01` a `mes_12` (vendas mensais)
  - Qualquer coluna com palavras-chave: "venda", "preço", "custo", "total"

- **Formatação aplicada:**
  - Símbolo: `R$`
  - Separador de milhar: `.` (ponto)
  - Separador decimal: `,` (vírgula)
  - 2 casas decimais

### 2. **Formatação de Números Gerais**

Colunas numéricas não-monetárias também são formatadas:

- **Exemplo:** `ESTOQUE_UNE`
  - ANTES: `1500`
  - DEPOIS: `1.500,00`

### 3. **Download CSV Formatado**

Ao baixar dados, o CSV já vem formatado:

```csv
NOMESEGMENTO,VENDA_30DD
PAPELARIA,"R$ 101.868,64"
TECIDOS,"R$ 77.328,70"
FESTAS,"R$ 41.750,34"
```

---

## 🔧 Como Usar

### No Streamlit (Automático)

A formatação é aplicada **automaticamente** quando você consulta dados:

1. Digite sua pergunta (ex: "ranking de vendas por segmento")
2. O sistema retorna dados formatados em R$
3. Botão "📥 Baixar CSV (formatado)" disponível

### Programaticamente

```python
from core.utils.dataframe_formatter import format_dataframe_for_display

# Criar DataFrame
df = pd.DataFrame({
    'produto': ['Produto A', 'Produto B'],
    'preco': [150.50, 299.99],
    'quantidade': [10, 25]
})

# Formatar automaticamente (detecta colunas de moeda)
df_formatado = format_dataframe_for_display(df, auto_detect=True)

# OU especificar colunas manualmente
df_formatado = format_dataframe_for_display(
    df,
    auto_detect=False,
    currency_cols=['preco'],
    number_cols=['quantidade']
)
```

### Criar CSV para Download

```python
from core.utils.dataframe_formatter import create_download_csv

csv_data, filename = create_download_csv(df, filename_prefix="vendas")
# Retorna: ("NOMESEGMENTO,VENDA...", "2025-10-20T09-12_vendas.csv")
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Ranking de Vendas

**Query:** "ranking de vendas por segmento"

**Resultado:**
| NOMESEGMENTO | VENDA_30DD |
|--------------|------------|
| PAPELARIA | R$ 101.868,64 |
| ARMARINHO E CONFECÇÃO | R$ 101.700,80 |
| TECIDOS | R$ 77.328,70 |

---

### Exemplo 2: Produtos com Preço

**Query:** "produtos do segmento tecidos com preço"

**Resultado:**
| NOME | LIQUIDO_38 | ESTOQUE_UNE |
|------|------------|-------------|
| Tecido Algodão | R$ 25,90 | 150,00 |
| Tecido Poliéster | R$ 18,50 | 200,00 |

---

### Exemplo 3: Evolução de Vendas

**Query:** "evolução de vendas últimos 3 meses"

**Resultado:**
| PRODUTO | mes_01 | mes_02 | mes_03 |
|---------|--------|--------|--------|
| Produto A | R$ 1.250,00 | R$ 1.180,50 | R$ 1.420,80 |
| Produto B | R$ 890,30 | R$ 920,10 | R$ 850,00 |

---

## 🎨 Detecção Automática

### Palavras-chave para Moeda

O sistema reconhece estas palavras nas colunas:
- `preco`, `preço`, `valor`, `custo`
- `venda`, `vendas`, `liquido`, `bruto`
- `receita`, `faturamento`, `total`
- `LIQUIDO`, `VENDA`, `PRECO` (maiúsculas)

### Palavras-chave para Números

Colunas numéricas não-monetárias:
- `estoque`, `quantidade`, `qtd`
- `ESTOQUE_UNE`, `estoque_atual`

### Colunas Excluídas

Não são formatadas (mantêm valor original):
- IDs: `id`, `codigo`, `produto`, `une_id`
- Códigos de barras: `ean`, `ean13`

---

## 🔧 Configuração Avançada

### Personalizar Formatação

```python
from core.utils.dataframe_formatter import format_currency_value, format_number_value

# Formatar valor individual
valor = format_currency_value(1234.56)
# Retorna: "R$ 1.234,56"

# Formatar número com precisão customizada
numero = format_number_value(1234.567, decimals=3)
# Retorna: "1.234,567"
```

### Desabilitar Auto-Detecção

```python
# Desabilitar detecção automática
df_formatado = format_dataframe_for_display(
    df,
    auto_detect=False,
    currency_cols=['coluna_especifica'],
    number_cols=[]
)
```

---

## 📁 Arquivos Relacionados

### Código Principal

```
core/utils/dataframe_formatter.py  - Formatador principal
core/utils/text_utils.py          - Utilitários de texto (legado)
streamlit_app.py (linhas 1080-1107) - Integração Streamlit
```

### Testes

```python
# Testar formatador
python core/utils/dataframe_formatter.py

# Ver exemplo antes/depois
python -c "from core.utils.dataframe_formatter import *; ..."
```

---

## ✅ Benefícios

1. **Profissionalismo** 🎯
   - Dados apresentados no padrão brasileiro
   - Melhor legibilidade

2. **Automação** 🚀
   - Detecta colunas automaticamente
   - Sem configuração necessária

3. **Consistência** ✨
   - Formato uniforme em todo o sistema
   - CSV baixado já formatado

4. **UX Melhorada** 💡
   - Usuário entende valores imediatamente
   - Não precisa interpretar números brutos

---

## 🐛 Tratamento de Erros

O sistema possui fallback automático:

```python
try:
    df_formatado = format_dataframe_for_display(df)
    st.dataframe(df_formatado)
except Exception as e:
    # Fallback: exibe sem formatação
    logger.warning(f"Erro ao formatar: {e}")
    st.dataframe(df)  # DataFrame original
```

---

## 🔄 Compatibilidade

- ✅ Pandas DataFrames
- ✅ Listas de dicionários (convertidas para DataFrame)
- ✅ Valores None/NaN (exibidos como "R$ 0,00" ou "0")
- ✅ Valores negativos (formatados como "-R$ X.XXX,XX")

---

## 📞 Suporte

### Problemas Comuns

**1. Coluna não formatada automaticamente**
- Verificar se nome da coluna contém palavras-chave
- Especificar manualmente: `currency_cols=['nome_coluna']`

**2. Formatação incorreta**
- Verificar se coluna é numérica (`pd.api.types.is_numeric_dtype`)
- Valores string não são formatados

**3. CSV sem formatação**
- Usar `create_download_csv()` em vez de `df.to_csv()`

---

## 🚀 Próximas Melhorias

1. **Formatação de Porcentagem**
   - Detectar colunas com "%"
   - Formatar como "XX,XX%"

2. **Formatação de Data**
   - Detectar colunas de data
   - Formatar como "DD/MM/YYYY"

3. **Configuração por Usuário**
   - Permitir usuário escolher formato
   - Salvar preferências

4. **Suporte a Múltiplas Moedas**
   - US$, EUR, etc.
   - Detectar por contexto

---

**Última atualização:** 2025-10-20
**Status:** ✅ Produção
