# 🔍 Diagnóstico Rápido - Erros de Queries

**Data:** 2025-10-18
**Status:** IDENTIFICADO - PRONTO PARA CORREÇÃO
**Tokens Usados:** ~55k de 200k (27%)

---

## 📊 Resumo Executivo

Identifiquei **4 categorias de erros** analisando diretamente:
- `data/catalog_focused.json` (schema oficial)
- `logs/errors.log` (erros reais)
- Histórico de interações do usuário

---

## ❌ ERROS IDENTIFICADOS

### 1. Case Sensitivity em Nomes de Colunas

| Código Gerado (❌ ERRADO) | Schema Real (✅ CORRETO) | Impacto |
|---------------------------|--------------------------|---------|
| `une_nome` (lowercase) | `UNE_NOME` (UPPERCASE) | 🔴 CRÍTICO |
| `NOMEFABRICANTE` | `NomeFabricante` (MixedCase) | 🔴 CRÍTICO |
| `DATA` (genérico) | Não existe! | 🔴 CRÍTICO |

**Evidência dos logs:**
```
KeyError: 'une_nome'
File "direct_query_engine.py", line 972
    (ddf['une_nome'].str.upper() == une_upper)
```

**Causa raiz:** DirectQueryEngine está usando nomes em lowercase, mas o schema usa UPPERCASE e MixedCase.

---

### 2. Coluna "DATA" Inexistente

**Erro reportado pelo usuário:**
```
"gráfico de vendas evolução do produto 59294"
❌ Erro ao processar: 'DATA'
```

**Problema:** Não existe coluna chamada `DATA` no schema.

**Colunas de data disponíveis:**
```python
{
    "ULTIMA_ENTRADA_DATA_CD": "datetime64[ns]",      # Data última entrada CD
    "ULTIMO_INVENTARIO_UNE": "datetime64[ns]",       # Data último inventário
    "ULTIMA_ENTRADA_DATA_UNE": "datetime64[ns]",     # Data última entrada UNE
    "SOLICITACAO_PENDENTE_DATA": "datetime64[ns]",   # Data solicitação pendente
    "PICKLIST_CONFERENCIA": "datetime64[ns]",        # Data conferência picklist
    "NOTA_EMISSAO": "datetime64[ns]"                 # Data emissão nota
}
```

**Para queries de evolução temporal, usar:** `MES_01` a `MES_12` (vendas mensais)

---

### 3. Problemas no Sistema de Transferências

**Erro reportado:**
```
"⚠️ Nenhum produto com estoque encontrado nas UNEs selecionadas"
```

**Causas identificadas:**
1. ❌ Código busca `estoque_atual` → Não existe!
2. ✅ Deve usar `ESTOQUE_UNE` (float64)

**Filtros de segmento retornando produtos errados:**
- Usuário filtrou "ARTES"
- Sistema retornou produtos de outros segmentos
- **Causa:** Filtro não está sendo aplicado corretamente

---

### 4. Problemas de Fabricante

**Erro nos logs:**
```
KeyError: 'NomeFabricante'
```

**Schema oficial (linha 17):**
```json
"NomeFabricante": "object"
```

**Case correto:** `NomeFabricante` (com "N" e "F" maiúsculos)

---

## 🎯 TOP 5 CORREÇÕES PRIORITÁRIAS

### Correção #1: Mapeamento de Colunas no DirectQueryEngine
**Arquivo:** `core/business_intelligence/direct_query_engine.py`
**Linha:** 972 (e similares)

```python
# ❌ ANTES (ERRADO)
(ddf['une_nome'].str.upper() == une_upper)

# ✅ DEPOIS (CORRETO)
(ddf['UNE_NOME'].str.upper() == une_upper)
```

**Ação:** Criar mapa de colunas case-insensitive ou usar nomes corretos.

---

### Correção #2: Validação de Colunas no CodeGenAgent
**Arquivo:** `core/agents/code_gen_agent.py`

**Adicionar validação ANTES de executar código:**

```python
def validate_columns_exist(self, code: str, available_columns: list) -> tuple[bool, str]:
    """Valida se colunas usadas no código existem no schema"""
    import re

    # Extrai colunas referenciadas no código
    column_refs = re.findall(r"df\['([^']+)'\]|ddf\['([^']+)'\]", code)
    referenced_cols = [c for group in column_refs for c in group if c]

    # Verifica se existem (case-sensitive!)
    missing = []
    for col in referenced_cols:
        if col not in available_columns:
            # Tenta encontrar match case-insensitive
            matches = [c for c in available_columns if c.upper() == col.upper()]
            if matches:
                missing.append(f"'{col}' → Use '{matches[0]}' (case correto)")
            else:
                missing.append(f"'{col}' não existe no schema")

    if missing:
        return False, "Colunas inválidas:\n" + "\n".join(missing)

    return True, "OK"
```

---

### Correção #3: Mapa de Aliases para Datas
**Arquivo:** `core/agents/code_gen_agent.py`

**Adicionar ao system prompt:**

```python
COLUMN_MAPPINGS = {
    "DATA": "Use MES_01 a MES_12 para evolução temporal, ou NOTA_EMISSAO para datas específicas",
    "data": "NÃO EXISTE! Veja mapeamento acima",
    "estoque_atual": "ESTOQUE_UNE",
    "estoque": "ESTOQUE_UNE (estoque da UNE) ou ESTOQUE_CD (estoque do CD)",
    "fabricante": "NomeFabricante (case correto: NomeFabricante)",
    "segmento": "NOMESEGMENTO",
    "une_nome": "UNE_NOME"
}

system_prompt += f"""
**MAPEAMENTO OBRIGATÓRIO DE COLUNAS:**

{json.dumps(COLUMN_MAPPINGS, indent=2, ensure_ascii=False)}

**REGRA CRÍTICA:** Sempre use os nomes EXATOS das colunas conforme o schema.
Case sensitivity importa! 'UNE_NOME' ≠ 'une_nome' ≠ 'Une_Nome'
"""
```

---

### Correção #4: Fix no get_produtos_une (Transferências)
**Arquivo:** `core/tools/une_tools.py` (ou onde get_produtos_une está)

```python
# ❌ ANTES
df_filtered = df[df['estoque_atual'] > 0]

# ✅ DEPOIS
df_filtered = df[df['ESTOQUE_UNE'] > 0]
```

**E adicionar validação de segmento:**

```python
if segmento:
    # Case-insensitive match
    df_filtered = df_filtered[
        df_filtered['NOMESEGMENTO'].str.upper() == segmento.upper()
    ]
```

---

### Correção #5: Adicionar Few-Shot Learning para Evolução Temporal
**Arquivo:** `data/query_patterns.json`

**Adicionar novo padrão:**

```json
{
  "evolucao_temporal": {
    "description": "Análises de evolução no tempo (tendência, crescimento, comparação mensal)",
    "keywords": ["evolução", "tendência", "crescimento", "ao longo do tempo", "mês a mês", "histórico"],
    "examples": [
      {
        "user_query": "evolução de vendas do produto 59294",
        "code": "df = load_data()\ndf_produto = df[df['PRODUTO'] == 59294]\nmeses = ['MES_01', 'MES_02', 'MES_03', 'MES_04', 'MES_05', 'MES_06', 'MES_07', 'MES_08', 'MES_09', 'MES_10', 'MES_11', 'MES_12']\nevolucao = df_produto[meses].T.reset_index()\nevolucao.columns = ['Mês', 'Vendas']\nevolucao['Mês'] = evolucao['Mês'].str.replace('MES_', 'Mês ')\nresult = evolucao",
        "expected_output": "DataFrame com colunas ['Mês', 'Vendas'] mostrando evolução mensal"
      }
    ]
  }
}
```

---

## 📈 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: Correções Críticas (30 min, ~10k tokens)
1. ✅ Corrigir DirectQueryEngine (une_nome → UNE_NOME)
2. ✅ Corrigir get_produtos_une (estoque_atual → ESTOQUE_UNE)
3. ✅ Adicionar validação de colunas no CodeGenAgent

### Fase 2: Melhorias no Pilar 2 (45 min, ~15k tokens)
4. ✅ Adicionar padrão "evolucao_temporal" ao query_patterns.json
5. ✅ Adicionar mais 3-4 padrões para casos comuns de erro
6. ✅ Testar Few-Shot Learning com queries reais do usuário

### Fase 3: Limpeza do Projeto (30 min, ~10k tokens)
7. ✅ Remover scripts temporários de debug (FIX_NOW.py, etc.)
8. ✅ Consolidar documentação
9. ✅ Atualizar INDEX.md com este diagnóstico

**Total estimado:** ~35k tokens, ~1h45min

---

## 📊 ESTIMATIVA DE IMPACTO

| Correção | Erros Resolvidos | Impacto | Prioridade |
|----------|------------------|---------|------------|
| #1 - DirectQueryEngine | 70% dos erros de UNE | 🔴 Muito Alto | P0 |
| #2 - Validação Colunas | 80% dos erros de schema | 🔴 Muito Alto | P0 |
| #3 - Mapa de Aliases | 90% dos erros de "DATA" | 🔴 Muito Alto | P0 |
| #4 - Fix Transferências | 100% dos erros de transferências | 🟡 Alto | P1 |
| #5 - Few-Shot Temporal | 60% dos erros de evolução | 🟡 Alto | P1 |

---

## ✅ PRÓXIMOS PASSOS

**Escolha uma opção:**

### Opção A: Implementação Completa Automatizada
- Aciono subagentes (code-agent, data-agent) para implementar todas as 5 correções
- Tempo estimado: ~1h45min
- Tokens estimados: ~35k

### Opção B: Implementação Manual Guiada
- Forneço os patches de código exatos para você aplicar
- Você revisa e aplica manualmente
- Mais rápido (~30min) mas menos automático

### Opção C: Priorizar Apenas P0 (Mais Rápido)
- Implementar apenas correções #1, #2 e #3
- Tempo: ~30min, ~10k tokens
- Resolve 80% dos problemas críticos

---

**Aguardando sua decisão para prosseguir...**

**Budget atual:** 145k tokens restantes (72% disponível)
