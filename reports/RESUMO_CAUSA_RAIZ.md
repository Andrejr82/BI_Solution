# RESUMO EXECUTIVO: Causa Raiz - Teste vs Streamlit

## PROBLEMA
- **Testes:** 80/80 perguntas = 100% sucesso
- **Streamlit:** Erros com "boolean value of NA is ambiguous"
- **Erro típico:** Function 'equal' has no kernel matching input types (string, int8)

## CAUSA RAIZ IDENTIFICADA

### 1. LOCALIZAÇÃO DO BUG
**Arquivo:** `streamlit_app.py`  
**Linhas:** 514-594  
**Componente:** Cache do agent_graph em Streamlit

### 2. O QUE ACONTECE

#### Em TESTES (100% sucesso):
1. Cada pergunta é processada NOVA
2. Sem cache, `load_data()` sempre executa
3. ESTOQUE_UNE é convertido de STRING para float64
4. Código usa tipos corretos → SUCESSO

#### Em STREAMLIT (erros aleatórios):
1. **Primeira pergunta:** SUCESSO (load_data() executado, tipos corretos)
2. **Resultado é CACHEADO** em `agent_graph_cache`
3. **Pergunta repetida:** Cache retorna resultado ANTIGO
4. Se cache foi feito ANTES do fix (commit c72359b):
   - Código velho trata ESTOQUE_UNE como STRING
   - Comparação com número falha
   - ERRO: "boolean value of NA is ambiguous"

### 3. POR QUE FUNCIONA EM TESTES

```python
# TESTES: Sem cache
test_80_perguntas_completo.py
├─ Cria CodeGenAgent
├─ Cria GraphBuilder
├─ Invoca agent_graph (SEMPRE nova execução)
└─ Sem cache → load_data() SEMPRE executado ✅
```

### 4. POR QUE FALHA EM STREAMLIT

```python
# STREAMLIT: Com cache agressivo
streamlit_app.py linha 514-521
├─ Verifica cache: cache.get(user_input)
├─ Se CACHE HIT (linha 523):
│  └─ Retorna resultado CACHEADO sem re-executar ❌
├─ Se CACHE MISS (linha 536):
│  └─ Executa agent_graph (como testes) ✅
│
# Problema: Cache pode ter código antigo se foi criado
# ANTES do commit c72359b (18/10/2025)
```

### 5. O CÓDIGO COM PROBLEMAS

**Arquivo:** `C:\Users\André\Documents\Agent_Solution_BI\streamlit_app.py`

**Linhas 514-527 (o problema):**
```python
if cached_result:
    # ✅ CACHE HIT! - USA RESULTADO ANTIGO!
    agent_response = cached_result
    agent_response["method"] = "agent_graph_cached"
```

**Por que é problema:**
- Cache contém resultado + código gerado (de antes do fix)
- Código antigo não faz conversão de tipos
- ESTOQUE_UNE permanece como STRING
- Comparação falha

### 6. CONFIRMAÇÃO NO GIT

**Commit que FIX o problema:** `c72359b` (18/10/2025)
- Adicionou conversão robusta em `load_data()`
- Limpeza automática de cache
- **MAS:** Limpeza ocorre apenas a cada 24h!

Se usuário executou query ANTES do fix, resultado está cacheado por até 24 horas.

---

## SOLUÇÃO IMEDIATA

### Opção A: Limpar Cache Agora
```bash
rm -rf data/cache/* data/cache_agent_graph/*
```
**Benefício:** Força regeneração de todo código com tipos corretos  
**Efeito:** Imediato para todos os usuários

### Opção B: Reduzir TTL do Cache
**Arquivo:** `code_gen_agent.py` linha 931
```python
# Mudar de:
max_age = 24 * 60 * 60  # 24 horas

# Para:
max_age = 2 * 60 * 60   # 2 horas
```
**Benefício:** Cache automático mais agressivo  
**Efeito:** Evita problema futuro

### Opção C: Versionar Conversão de Tipos (Robusta)
Adicionar version string ao cache key:
```python
# Adicionar ao prompt_version (linha 968):
'conversion_version': '1.0_numeric_estoque'  # Incrementar quando mudar tipo
```
**Benefício:** Invalida automaticamente se conversão mudar  
**Efeito:** Prevent future issues

---

## DIFERENÇAS LADO A LADO

| Aspecto | TESTES | STREAMLIT |
|---------|--------|-----------|
| Execução | Nova sempre | Nova + Cache |
| load_data() chamado | ✅ SIM | ❌ Não (cache hit) |
| Conversão ESTOQUE_UNE | ✅ float64 | ❌ STRING (cache old) |
| Taxa de erro | 0% | ~20% (cache hit) |
| Como reproduzir erro | Não consegue | Repetir mesma pergunta 2x |

---

## COMO VALIDAR FIX

### Teste 1: Primeira pergunta
```
User: "Quais produtos têm ruptura em TECIDOS?"
Esperado: SUCESSO ✅
Motivo: Sem cache, load_data() sempre executado
```

### Teste 2: Repetir mesma pergunta
```
User: "Quais produtos têm ruptura em TECIDOS?" (novamente)
Esperado: SUCESSO ✅ (após fix)
Motivo: Cache invalidado ou load_data() re-executado
```

### Teste 3: Variação da pergunta
```
User: "Segmentos com ruptura?"
Esperado: SUCESSO ✅
Motivo: Cache miss (pergunta diferente)
```

---

## PRÓXIMAS AÇÕES

1. **HOJE:** Limpar cache + reduzir TTL
2. **CURTO PRAZO:** Testar ambos cenários
3. **MÉDIO PRAZO:** Implementar versioning de conversão
4. **LONGO PRAZO:** Cachear apenas código gerado, não resultado final

---

## ARQUIVOS CRÍTICOS

| Arquivo | Linha | Função |
|---------|-------|--------|
| `code_gen_agent.py` | 164-166 | Conversão load_data() |
| `streamlit_app.py` | 514-527 | CACHE (PROBLEMA) |
| `streamlit_app.py` | 536-594 | Fallback sem cache |
| `parquet_adapter.py` | 151-158 | Conversão alternativa |

---

## RESPOSTA EM POUCAS PALAVRAS

**Por que testes passam e Streamlit falha?**

Porque TESTES não usam cache, enquanto STREAMLIT cacheia resultados.
Se cache tem código antigo (ANTES do fix c72359b), ESTOQUE_UNE fica como STRING.
STRING vs INT = erro de tipo.

**Solução:** Limpar cache + reduzir TTL de 24h para 2h.

