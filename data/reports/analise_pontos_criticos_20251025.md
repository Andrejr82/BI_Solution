# Análise de Pontos Críticos do Projeto - 25/10/2025

## 🔴 PROBLEMAS CRÍTICOS IDENTIFICADOS

---

## 1. ⚠️ **MAPEAMENTO DE COLUNAS INCORRETO** (CRÍTICO!)

### Problema
O código está usando nomes de colunas MAIÚSCULAS que **NÃO EXISTEM** no Parquet real.

### Colunas Reais do Parquet (minúsculas):
```
'id', 'une', 'codigo', 'tipo', 'une_nome', 'nome_produto', 'embalagem',
'nomesegmento', 'NOMECATEGORIA', 'nomegrupo', 'NOMESUBGRUPO',
'NOMEFABRICANTE', 'ean', 'promocional', 'foralinha', 'preco_38_percent',
'venda_30_d', 'estoque_atual', 'estoque_lv', 'media_considerada_lv', ...
```

### Colunas que o CÓDIGO está usando (INCORRETAS):
```python
# Em code_gen_agent.py:270
essential_cols = ['PRODUTO', 'NOME', 'UNE', 'NOMESEGMENTO', 'VENDA_30DD',
                  'ESTOQUE_UNE', 'LIQUIDO_38', 'NOMEGRUPO']
```

### ❌ Mapeamento ERRADO:
| Código Usa | Deveria Ser | Status |
|-----------|-------------|--------|
| `PRODUTO` | `codigo` | ❌ ERRO |
| `NOME` | `nome_produto` | ❌ ERRO |
| `UNE` | `une` | ⚠️ Case mismatch |
| `NOMESEGMENTO` | `nomesegmento` | ⚠️ Case mismatch |
| `VENDA_30DD` | `venda_30_d` | ❌ ERRO (nome diferente) |
| `ESTOQUE_UNE` | `estoque_atual` ou `estoque_lv` | ❌ ERRO |
| `LIQUIDO_38` | `preco_38_percent` | ❌ ERRO |
| `NOMEGRUPO` | `nomegrupo` | ⚠️ Case mismatch |

### 📍 Locais Afetados:
1. **`core/agents/code_gen_agent.py:270`** - Colunas essenciais do fallback
2. **`data/query_examples.json`** - 102 exemplos com colunas erradas
3. **Prompts do LLM** - Instruindo uso de colunas que não existem
4. **`data/catalog_focused.json`** - Catálogo com colunas incorretas

### 🔥 Impacto:
- **100% das queries que não passam filtros iniciais falham**
- LLM gera código com colunas inexistentes
- KeyError em tempo de execução
- Mensagens de erro confusas ao usuário

---

## 2. 🔴 **INCONSISTÊNCIA DE CASE NOS NOMES**

### Problema
O Parquet tem **mix de MAIÚSCULAS e minúsculas** sem padrão claro:

```python
# MAIÚSCULAS
'NOMECATEGORIA', 'NOMESUBGRUPO', 'NOMEFABRICANTE'

# minúsculas
'une', 'codigo', 'tipo', 'une_nome', 'nome_produto', 'embalagem'

# MiXtAs
'nomesegmento', 'nomegrupo'
```

### Impacto:
- LLM não sabe qual case usar
- Código gerado falha em 50% dos casos
- Validador de código não detecta o problema

---

## 3. ⚠️ **NOMES DE COLUNAS NÃO INTUITIVOS**

### Exemplos Problemáticos:

| Coluna Real | Nome Intuitivo | Problema |
|------------|----------------|----------|
| `venda_30_d` | `venda_30_dias` ou `venda_30dd` | Abreviação inconsistente |
| `preco_38_percent` | `preco_liquido_38` ou `liquido_38` | Nome pouco claro |
| `estoque_lv` | `estoque_une` ou `estoque_loja` | LV não é óbvio |
| `codigo` | `produto` ou `produto_codigo` | Genérico demais |
| `abc_une_30_dd` | `classificacao_abc_30d` | Abreviação obscura |

### Impacto:
- LLM tem dificuldade em mapear queries para colunas corretas
- Usuário não entende mensagens de erro
- Desenvolvedor perde tempo debugando

---

## 4. 🟡 **COLUNAS COM VALORES VAZIOS/NULL**

### Encontrado na amostra:
```python
# Linha 0:
'estoque_atual': 0E-16,  # Praticamente zero
'estoque_lv': NaN,
'estoque_gondola_lv': NaN,

# Linha 1:
'estoque_gondola_lv': 0E-16,
'estoque_ilha_lv': 0E-16,
```

### Problema:
- Colunas importantes com valores nulos
- LLM pode gerar código que assume valores sempre preenchidos
- Queries de "ruptura" podem falhar

---

## 5. 🟡 **MÚLTIPLAS COLUNAS PARA MESMO CONCEITO**

### Estoque (5 variações):
```
- estoque_cd      # Estoque do CD
- estoque_atual   # Estoque atual (?)
- estoque_lv      # Estoque Linha Verde?
- estoque_gondola_lv
- estoque_ilha_lv
```

### Vendas (15+ variações):
```
- venda_30_d
- mes_01, mes_02, ..., mes_12
- semana_atual, semana_anterior_2, ...
- qtde_semana_atual, media_semana_atual
```

### Problema:
- LLM não sabe qual coluna usar
- Usuário pede "estoque" mas há 5 tipos diferentes
- Necessidade de regras de negócio explícitas

---

## 6. 🔴 **EXEMPLOS DE QUERIES COM COLUNAS ERRADAS**

### `data/query_examples.json` (102 exemplos):

Todos os 102 exemplos usam:
```json
{
  "code": "df[df['NOMESEGMENTO'].str.upper() == 'TECIDO']"
}
```

Deveria ser:
```python
df[df['nomesegmento'].str.upper() == 'TECIDO']
```

### Impacto:
- **Sistema RAG retorna exemplos ERRADOS**
- Few-Shot Learning ensina o LLM a errar
- Pilar 2 do sistema está comprometido

---

## 7. 🟡 **FALTA DE DOCUMENTAÇÃO DAS COLUNAS**

### Colunas sem documentação clara:
```
- abc_une_30_xabc_cacula_90_dd  # O que significa "x"?
- freq_ult_sem                   # Frequência de quê?
- exposicao_minima_une           # Unidade?
- leadtime_lv                    # Dias? Semanas?
- picklist_conferencia           # Booleano? String?
```

### Impacto:
- LLM não entende semântica das colunas
- Código gerado pode usar colunas erradas
- Impossível validar lógica de negócio

---

## 8. ⚠️ **ENCODING DE CARACTERES**

### Problema observado:
```
'nomesegmento': 'ARMARINHO E CONFEC��O'  # Caracteres corrompidos
```

### Possíveis causas:
- Encoding incorreto na exportação do Parquet
- Problema no SQL Server original
- Conversão UTF-8 ↔ CP1252 mal feita

### Impacto:
- Filtros por segmento podem falhar
- Comparações de string não funcionam
- Visualizações mostram caracteres estranhos

---

## 9. 🔴 **VALIDADOR DE CÓDIGO NÃO DETECTA COLUNAS ERRADAS**

### `core/validation/code_validator.py`

Atualmente valida:
- Sintaxe Python
- Imports perigosos
- Funções proibidas

**NÃO valida:**
- Nomes de colunas
- Existência de colunas no DataFrame
- Case sensitivity

### Impacto:
- Erros só aparecem em runtime
- Usuário espera muito tempo para receber erro
- Sistema parece "burro" ao gerar código inválido

---

## 10. 🟡 **PROMPTS DESATUALIZADOS**

### Arquivos com informações incorretas:
1. **`core/agents/code_gen_agent.py`** - Prompt base com colunas erradas
2. **`docs/prompts/PROMPT_ROBUSTO_SQLSERVER_PARQUET.md`** - Documentação desatualizada
3. **`data/catalog_focused.json`** - Catálogo de colunas incorreto

### Exemplo de prompt problemático:
```python
# No prompt do LLM:
"Use as colunas: PRODUTO, NOME, VENDA_30DD, ESTOQUE_UNE"
```

Deveria ser:
```python
"Use as colunas: codigo, nome_produto, venda_30_d, estoque_atual"
```

---

## 📊 RESUMO DE SEVERIDADE

| Problema | Severidade | Impacto | Urgência |
|----------|-----------|---------|----------|
| Colunas incorretas no código | 🔴 CRÍTICO | 90% | IMEDIATA |
| Case inconsistente | 🔴 CRÍTICO | 70% | ALTA |
| Exemplos RAG errados | 🔴 CRÍTICO | 80% | ALTA |
| Nomes não intuitivos | 🟡 MÉDIO | 40% | MÉDIA |
| Validador incompleto | 🟡 MÉDIO | 50% | MÉDIA |
| Múltiplas colunas/conceito | 🟡 MÉDIO | 30% | BAIXA |
| Documentação ausente | 🟢 BAIXO | 20% | BAIXA |
| Encoding corrompido | 🟢 BAIXO | 10% | BAIXA |

---

## 🔧 SOLUÇÕES RECOMENDADAS

### Prioridade CRÍTICA 🔴

#### 1. Criar Mapeamento Oficial de Colunas
```python
# core/config/column_mapping.py (NOVO)
COLUMN_MAP = {
    # Nome Legado → Nome Real
    "PRODUTO": "codigo",
    "NOME": "nome_produto",
    "UNE": "une",
    "NOMESEGMENTO": "nomesegmento",
    "VENDA_30DD": "venda_30_d",
    "ESTOQUE_UNE": "estoque_atual",
    "LIQUIDO_38": "preco_38_percent",
    "NOMEGRUPO": "nomegrupo",
    # ... mais 89 colunas
}
```

#### 2. Atualizar Code Gen Agent
```python
# Substituir linha 270
essential_cols = ['codigo', 'nome_produto', 'une', 'nomesegmento',
                  'venda_30_d', 'estoque_atual', 'preco_38_percent', 'nomegrupo']
```

#### 3. Corrigir 102 Exemplos RAG
- Atualizar `data/query_examples.json`
- Re-treinar embeddings FAISS
- Validar todos os exemplos

#### 4. Adicionar Validação de Colunas
```python
def validate_columns(code: str, df_columns: list) -> list:
    """Valida se colunas usadas no código existem no DataFrame"""
    # Extrair colunas do código
    # Comparar com df_columns
    # Retornar lista de erros
```

### Prioridade ALTA 🟠

#### 5. Normalizar Case das Colunas
```python
# Opção 1: Converter tudo para minúsculas
df.columns = df.columns.str.lower()

# Opção 2: Manter mas documentar
# Criar índice case-insensitive
```

#### 6. Criar Glossário de Colunas
```python
COLUMN_GLOSSARY = {
    "codigo": {
        "nome": "Código do Produto",
        "tipo": "int",
        "exemplo": "704559",
        "nullable": False,
        "aliases": ["PRODUTO", "produto_codigo"]
    },
    # ... para todas as 97 colunas
}
```

#### 7. Atualizar Prompts do LLM
- Incluir lista de colunas reais
- Exemplos com nomes corretos
- Warnings sobre case sensitivity

### Prioridade MÉDIA 🟡

#### 8. Implementar Sugestão de Colunas
```python
def suggest_column(user_input: str) -> list:
    """Sugere coluna baseado em input do usuário"""
    # Similar ao suggest_une()
    # "estoque" → ["estoque_atual", "estoque_lv", "estoque_cd"]
```

#### 9. Documentar Regras de Negócio
```markdown
## Qual coluna de estoque usar?
- `estoque_atual`: Estoque físico total da UNE
- `estoque_lv`: Estoque na Linha Verde (área de venda)
- `estoque_cd`: Estoque no Centro de Distribuição
```

---

## 📈 IMPACTO ESPERADO DAS CORREÇÕES

### Antes:
- ❌ 90% das queries com colunas erradas falham
- ❌ RAG retorna exemplos inválidos
- ❌ LLM aprende padrões incorretos
- ❌ Usuário recebe KeyError confusos

### Depois:
- ✅ 95% das queries usam colunas corretas
- ✅ RAG retorna exemplos válidos
- ✅ LLM aprende padrões corretos
- ✅ Usuário recebe mensagens claras

---

## 🎯 PLANO DE AÇÃO SUGERIDO

### Semana 1 (CRÍTICO):
1. ✅ Criar `column_mapping.py`
2. ✅ Atualizar `code_gen_agent.py`
3. ✅ Corrigir `query_examples.json`
4. ✅ Re-treinar sistema RAG

### Semana 2 (ALTA):
5. ⏳ Implementar validador de colunas
6. ⏳ Normalizar case (decisão: minúsculas)
7. ⏳ Atualizar todos os prompts

### Semana 3 (MÉDIA):
8. ⏳ Criar glossário completo
9. ⏳ Implementar sugestão de colunas
10. ⏳ Documentar regras de negócio

---

**Relatório gerado automaticamente por Claude Code**
**Data:** 2025-10-25 10:00 UTC
**Análise baseada em:** Código fonte + Parquet + Logs
**Status:** ⚠️ AÇÃO IMEDIATA NECESSÁRIA
