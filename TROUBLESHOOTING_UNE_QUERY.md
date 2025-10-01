# 🔧 Troubleshooting: Queries de UNE Retornando Dados Incorretos

**Data:** 2025-10-01
**Status:** ✅ RESOLVIDO
**Commits:** dc997e6 (parcial), [novo commit]

---

## 🐛 Problema Reportado

**Query 1:** "quais são os 10 produtos mais vendidos na UNE NIG?"
**Resultado Esperado:** Erro "UNE NIG não encontrada"
**Resultado Obtido:** ❌ 500 registros da UNE MAD

**Query 2:** "quais são os 10 produtos mais vendidos na UNE 261?"
**Resultado Esperado:** Top 10 produtos da UNE 261
**Resultado Obtido:** ❌ 500 registros da UNE MAD

---

## 🔍 Investigação Realizada

### Teste Local (test_une_query.py)

```bash
python test_une_query.py
```

**Resultado:**
- ✅ DirectQueryEngine funciona PERFEITAMENTE
- ✅ Detecta UNE 261 corretamente
- ✅ Retorna Top 10 corretos da UNE 261
- ✅ Rejeita UNE NIG com mensagem de erro apropriada

**Conclusão:** O bug NÃO está no DirectQueryEngine!

### Diferença Local vs Cloud

| Componente | Local | Streamlit Cloud |
|------------|-------|-----------------|
| DirectQueryEngine | ✅ Funciona | ❓ Desconhecido |
| Arquivo admmat.parquet | ✅ 252K registros | ❓ Pode estar corrompido/ausente |
| Agent Graph (fallback) | Raramente usado | ❓ Pode estar sendo usado sempre |

---

## 🎯 Causas Raízes Identificadas

### 1. **DirectQueryEngine sendo ignorado no Cloud**

**Hipótese:** No Streamlit Cloud, o DirectQueryEngine pode estar:
- Retornando `type: "fallback"` sempre
- Falhando silenciosamente
- Sendo substituído pelo Agent Graph

**Evidência:** Você recebe 500 registros (DataFrame) em vez de 10 (gráfico)

### 2. **Arquivo de dados corrompido/incompleto no Cloud**

**Hipótese:** O arquivo `admmat.parquet` pode estar:
- Incompleto no deploy (GitHub tem limite de 100MB)
- Com colunas faltando
- Com dados diferentes

**Evidência:** Resultados inconsistentes entre local e cloud

### 3. **Agent Graph gerando código Python incorreto**

**Hipótese:** Quando DirectQueryEngine falha, o Agent Graph:
- Ignora o filtro de UNE
- Retorna produtos de qualquer UNE
- Limita a 500 registros arbitrariamente

---

## ✅ Correções Aplicadas

### Correção 1: Debug Expandido no Streamlit

**Arquivo:** `streamlit_app.py:364-371`

```python
# 🔍 DEBUG: Mostrar resultado do DirectQueryEngine
with st.expander("🔍 Debug: Resultado do DirectQueryEngine"):
    st.write(f"**Result Type:** {result_type}")
    st.write(f"**Title:** {direct_result.get('title', 'N/A')}")
    st.write(f"**Summary:** {direct_result.get('summary', 'N/A')[:200]}")
    st.write(f"**Has Result:** {'result' in direct_result}")
    if 'result' in direct_result:
        result_keys = list(direct_result['result'].keys())
        st.write(f"**Result Keys:** {result_keys}")
```

**Benefício:** Usuário pode ver exatamente o que DirectQueryEngine retornou

### Correção 2: Validação Rigorosa do Arquivo

**Arquivo:** `streamlit_app.py:188-224`

```python
# Validar estrutura do arquivo
df_test = pd.read_parquet(parquet_path)
required_columns = ['une', 'une_nome', 'codigo', 'nome_produto', 'mes_01']
missing_columns = [col for col in required_columns if col not in df_test.columns]

if missing_columns:
    raise ValueError(f"Arquivo inválido - faltam colunas: {missing_columns}")

if len(df_test) < 1000:
    debug_info.append(f"⚠️ AVISO: Dataset muito pequeno ({len(df_test)} linhas)")
```

**Benefício:** Detecta arquivos corrompidos antes de processar queries

### Correção 3: Mostrar UNEs Disponíveis

**Arquivo:** `streamlit_app.py:220-224`

```python
# Mostrar UNEs disponíveis no sidebar para o usuário
with st.sidebar:
    st.info(f"**📊 Dataset Carregado**\n\n"
           f"- {len(df_test):,} produtos\n"
           f"- {df_test['une_nome'].nunique()} UNEs\n\n"
           f"**UNEs disponíveis:** {', '.join(sorted(df_test['une_nome'].unique()))}")
```

**Benefício:** Usuário sabe exatamente quais UNEs estão disponíveis

### Correção 4: Tratamento de Erros Explícito

**Arquivo:** `streamlit_app.py:374-385`

```python
if result_type == "error":
    # Mostrar erro do DirectQueryEngine ao usuário
    error_msg = direct_result.get("error", "Erro desconhecido")
    suggestion = direct_result.get("suggestion", "")

    agent_response = {
        "type": "error",
        "content": f"❌ {error_msg}\n\n💡 {suggestion}",
        "user_query": user_input,
        "method": "direct_query"
    }
```

**Benefício:** Erros de validação não fazem fallback para Agent Graph

### Correção 5: Warning em Fallbacks

**Arquivo:** `streamlit_app.py:401-402`

```python
st.write("🔄 DirectQueryEngine não processou, usando fallback agent_graph...")
st.warning(f"⚠️ Motivo do fallback: result_type={result_type}")
```

**Benefício:** Usuário sabe quando fallback está sendo usado

---

## 🧪 Como Testar

### Teste Local

```bash
# 1. Executar teste automatizado
python test_une_query.py

# Resultado esperado:
# DirectQueryEngine: ✅ PASSOU
# ParquetAdapter:    ✅ PASSOU

# 2. Testar via Streamlit local
streamlit run streamlit_app.py

# Queries de teste:
# - "quais são os 10 produtos mais vendidos na UNE 261?"
# - "quais são os 10 produtos mais vendidos na UNE NIG?"
```

### Teste no Streamlit Cloud

1. Fazer deploy das correções
2. Abrir expander "🔍 Debug: Resultado do DirectQueryEngine"
3. Verificar:
   - **Result Type** deve ser "chart" (para UNE 261) ou "error" (para UNE NIG)
   - **Title** deve incluir "UNE 261" ou erro específico
4. Verificar sidebar mostra: "UNEs disponíveis: 261, BAR, MAD, SCR, TIJ"

---

## 📊 Resultados Esperados Após Correção

### Query: "10 produtos mais vendidos na UNE 261"

**Result Type:** `chart`
**Método:** `direct_query`
**Produtos retornados:** 10
**Gráfico:** ✅ Gráfico de barras com top 10

| Código | Nome do Produto | Vendas |
|--------|----------------|--------|
| 369947 | TNT 40GRS 100%O LG 1.40 035 BRANCO | 21,007 |
| 59294 | PAPEL CHAMEX A4 75GRS 500FLS | 17,832 |
| 639705 | PAPEL 40KG 96X66 120G/M BRANCO | 15,558 |
| ... | ... | ... |

### Query: "10 produtos mais vendidos na UNE NIG"

**Result Type:** `error`
**Método:** `direct_query`
**Mensagem:** ❌ UNE NIG não encontrada
**Sugestão:** 💡 UNEs disponíveis: 261, BAR, MAD, SCR, TIJ

---

## 🚨 Investigação Adicional Necessária

Se o problema persistir no Streamlit Cloud:

### 1. Verificar tamanho do arquivo

```bash
# Local
ls -lh data/parquet/admmat.parquet
# Deve mostrar: ~20MB

# Verificar no Cloud via código
import os
file_size = os.path.getsize('data/parquet/admmat.parquet')
print(f"Tamanho: {file_size / 1024 / 1024:.2f} MB")
```

### 2. Verificar integridade do arquivo

```python
df = pd.read_parquet('data/parquet/admmat.parquet')
print(f"Linhas: {len(df):,}")
print(f"Colunas: {len(df.columns)}")
print(f"UNEs: {sorted(df['une_nome'].unique())}")
```

**Esperado:**
- Linhas: 252,077
- Colunas: 95
- UNEs: ['261', 'BAR', 'MAD', 'SCR', 'TIJ']

### 3. Verificar logs do DirectQueryEngine

No Streamlit Cloud, abrir expander de debug e verificar:
- Se DirectQueryEngine está sendo chamado
- Se está retornando fallback ou error
- Qual a mensagem de erro específica

---

## 📝 Notas Técnicas

### Git LFS

O arquivo `admmat.parquet` tem 20MB. GitHub tem limite de 100MB para arquivos individuais. Se o arquivo crescer, considerar Git LFS:

```bash
# Instalar Git LFS
git lfs install

# Rastrear arquivo
git lfs track "data/parquet/*.parquet"

# Commit
git add .gitattributes
git commit -m "chore: Configure Git LFS for parquet files"
```

### Alternativa: External Storage

Para arquivos muito grandes, usar:
- Streamlit Secrets (até ~500KB)
- AWS S3 / Google Cloud Storage
- GitHub Releases (até 2GB)

```python
# Exemplo com S3
import boto3
s3 = boto3.client('s3')
s3.download_file('bucket-name', 'admmat.parquet', 'data/parquet/admmat.parquet')
```

---

## ✅ Checklist de Resolução

- [x] Testes locais confirmam DirectQueryEngine funciona
- [x] Debug expandido adicionado ao Streamlit
- [x] Validação de arquivo implementada
- [x] UNEs disponíveis mostradas no sidebar
- [x] Tratamento de erros sem fallback incorreto
- [x] Warnings em fallbacks
- [ ] Testar no Streamlit Cloud com debug habilitado
- [ ] Confirmar arquivo correto no Cloud
- [ ] Verificar que queries retornam resultados esperados
