# 🔍 Relatório de Investigação: Query "10 produtos mais vendidos na UNE NIG"

**Data:** 2025-10-01
**Investigador:** Claude Code
**Solicitante:** André

---

## 📋 Sumário Executivo

A query "quais são os 10 produtos mais vendidos na UNE NIG?" **deveria retornar um erro informativo**, pois a UNE "NIG" **não existe** no dataset. O sistema possui tratamento adequado para este cenário, mas o comportamento pode depender de qual resposta você recebeu.

---

## 🗂️ Estrutura dos Dados Reais

### Arquivo: `data/parquet/admmat.parquet`
- **Tamanho:** 20 MB
- **Total de linhas:** 252,077 produtos
- **Total de colunas:** 95 colunas
- **Colunas de vendas:** `mes_01` até `mes_12` (vendas mensais)
- **Coluna de UNE:** `une` (código numérico) e `une_nome` (nome da unidade)

### UNEs Disponíveis no Dataset

| Código UNE | Nome  | Total de Produtos |
|-----------|-------|-------------------|
| 1         | SCR   | 57,496           |
| 1685      | 261   | 60,452           |
| 2365      | BAR   | 56,826           |
| 2720      | MAD   | 52,588           |
| 3116      | TIJ   | 24,715           |

**Total:** 5 UNEs apenas

### ❌ UNE "NIG" NÃO EXISTE

A busca por "NIG" no campo `une_nome` retornou **0 resultados**.

---

## 🔍 Dados Mockados Encontrados

### Local: `streamlit_app.py` (linhas 188-198)

```python
if not os.path.exists(parquet_path):
    # Criar dados mock para cloud se arquivo não existir
    import pandas as pd
    mock_data = pd.DataFrame({
        'codigo': [59294, 12345, 67890],
        'descricao': ['Produto Exemplo 1', 'Produto Exemplo 2', 'Produto Exemplo 3'],
        'preco': [99.90, 149.50, 79.30],
        'categoria': ['Categoria A', 'Categoria B', 'Categoria A']
    })
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    mock_data.to_parquet(parquet_path)
    debug_info.append("⚠️ Arquivo parquet não encontrado - criado dados mock")
```

**Status:** Dados mock **NÃO são usados** no seu ambiente local, pois o arquivo `admmat.parquet` existe.

**Problema:** No Streamlit Cloud, se o arquivo não for carregado corretamente, o sistema cria apenas 3 produtos mock que **não possuem colunas de UNE**, o que causaria falhas nas queries.

---

## ⚙️ Como o Sistema Processa a Query

### 1. Classificação (DirectQueryEngine linha 202-208)

```python
top_produtos_une_match = re.search(r'(\d+)\s*produtos\s*mais\s*vendidos\s+na\s+une\s+([A-Za-z0-9]+)\b', query_lower)
if top_produtos_une_match:
    limite = int(top_produtos_une_match.group(1))
    une_nome = top_produtos_une_match.group(2).upper()
    result = ("top_produtos_une_especifica", {"limite": limite, "une_nome": une_nome})
```

**Resultado esperado:**
- `query_type`: "top_produtos_une_especifica"
- `params`: `{"limite": 10, "une_nome": "NIG"}`

### 2. Execução (DirectQueryEngine linha 609-625)

```python
def _query_top_produtos_une_especifica(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    limite = params.get('limite', 10)
    une_nome = params.get('une_nome')

    # Verificar se UNE existe
    une_data = df[df['une_nome'] == une_nome]
    if une_data.empty:
        unes_disponiveis = df['une_nome'].unique()
        return {
            "error": f"UNE {une_nome} não encontrada",
            "type": "error",
            "suggestion": f"UNEs disponíveis: {', '.join(unes_disponiveis[:10])}"
        }
```

**Comportamento Esperado:** ✅ Sistema deveria retornar:
```json
{
    "error": "UNE NIG não encontrada",
    "type": "error",
    "suggestion": "UNEs disponíveis: SCR, 261, BAR, MAD, TIJ"
}
```

---

## 🎯 Teste Real com UNE Válida

### Query: "10 produtos mais vendidos na UNE MAD"

Resultado esperado (baseado em análise dos dados):

| Código | Nome do Produto                                      | Vendas Totais |
|--------|-----------------------------------------------------|---------------|
| 639705 | PAPEL 40KG 96X66 120G/M BRANCO                     | 18,857       |
| 59294  | PAPEL CHAMEX A4 75GRS 500FLS                       | 11,784       |
| 672540 | BOMBOM LACTA OURO BRANCO REF.17012                 | 8,684        |
| 369947 | TNT 40GRS 100%O LG 1.40 035 BRANCO                 | 7,000        |
| 5184   | REFIL P/PISTOLA QUENTE FINA PCT 7 5MMX300MM       | 6,982        |
| 672541 | BOMBOM LACTA SONHO DE VALSA REF.17013             | 6,961        |
| 59334  | PAPEL CHAMEQUINHO A4 BRANCO 75G 100FLS            | 6,923        |
| 270066 | TEC PANO PRATO TARQUINADO 100%A LG 0.69 01 BRANCO | 5,892        |
| 740626 | AGUA CRYSTAL 500ML S/ GAS PT                       | 5,797        |
| 703328 | LINHA COSTURA POLIESTER X1500JDS ST-1500W 301...  | 5,770        |

---

## 🐛 Possíveis Problemas

### 1. Dados Mock no Streamlit Cloud
**Risco:** Se o arquivo `admmat.parquet` não for enviado para o Streamlit Cloud, apenas 3 produtos mock serão criados, **sem colunas de UNE**, causando falhas em todas as queries relacionadas a UNE.

**Solução:** Garantir que `data/parquet/admmat.parquet` esteja no repositório Git ou seja carregado via secrets/external storage.

### 2. Case Sensitivity
**Problema:** O código compara `une_nome == "NIG"` (case-sensitive).
**Status:** Correto, pois os nomes de UNE no dataset são maiúsculos (SCR, BAR, MAD, TIJ) e o código converte para `.upper()`.

### 3. Fallback para Agent Graph
Se o DirectQueryEngine retornar erro, o sistema pode fazer fallback para o Agent Graph (LangGraph), que pode:
- Gerar código Python que tenta filtrar por UNE NIG
- Retornar um DataFrame vazio
- Criar uma mensagem genérica

---

## 📊 Recomendações

### 1. **Remover Dados Mock do streamlit_app.py**
Os dados mock são inadequados e podem causar mais problemas. Substituir por uma mensagem de erro clara:

```python
if not os.path.exists(parquet_path):
    st.error("❌ Arquivo de dados não encontrado. Configure o arquivo admmat.parquet corretamente.")
    return None
```

### 2. **Melhorar Mensagem de Erro no DirectQueryEngine**
Incluir sugestões de UNEs similares (fuzzy matching):

```python
if une_data.empty:
    # Buscar UNEs similares
    from difflib import get_close_matches
    similar = get_close_matches(une_nome, unes_disponiveis, n=3, cutoff=0.6)

    suggestion = f"UNEs disponíveis: {', '.join(unes_disponiveis[:10])}"
    if similar:
        suggestion = f"Você quis dizer: {', '.join(similar)}? " + suggestion

    return {
        "error": f"UNE '{une_nome}' não encontrada",
        "type": "error",
        "suggestion": suggestion
    }
```

### 3. **Validar Dados no Streamlit Cloud**
Adicionar validação na inicialização:

```python
if os.path.exists(parquet_path):
    df = pd.read_parquet(parquet_path)
    if 'une_nome' not in df.columns:
        st.error("❌ Arquivo de dados inválido: coluna 'une_nome' não encontrada")
    elif len(df) < 1000:
        st.warning(f"⚠️ Arquivo de dados muito pequeno: {len(df)} linhas (esperado: >250k)")
```

---

## ✅ Conclusão

1. **Dados reais existem** localmente: 252,077 produtos em 5 UNEs
2. **UNE "NIG" não existe** no dataset
3. **Sistema possui tratamento de erro adequado** no DirectQueryEngine
4. **Dados mock são problemáticos** e devem ser removidos
5. **A resposta que você recebeu depende** de:
   - Se o DirectQueryEngine foi usado (deveria retornar erro)
   - Se houve fallback para Agent Graph (pode ter tentado gerar código)
   - Se dados mock foram usados no Cloud (resultados inválidos)

**Ação recomendada:** Compartilhe a resposta exata que recebeu para eu identificar qual caminho o sistema tomou.
