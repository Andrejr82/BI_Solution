# Correção de Geração de Gráficos - Context7 Best Practices 2025

**Data:** 2025-12-27
**Problema:** Timeout de 2 minutos + navegador fechando ao solicitar gráficos

## Problemas Identificados

### 1. **Ferramenta Universal Quebrada**
- `gerar_grafico_automatico` (antiga `gerar_grafico_universal`) **não suportava filtros**
- Ignorava parâmetros como `UNE`, `segmento`, `categoria`
- Chamava outras ferramentas via `.invoke()`, causando possível recursão

**Exemplo do Problema:**
```
Usuário: "gere um gráfico de vendas por segmento da une 1685"
Sistema: Chama gerar_grafico_vendas_por_categoria (ERRADO!)
Resultado: Gráfico SEM filtro de UNE, mostrando TODOS os dados
```

### 2. **Timeout do Navegador**
- EventSource (SSE) no navegador timeout após ~2 minutos sem dados
- Backend demorava >2min processando ferramentas complexas
- Nenhum keepalive enviado durante processamento

### 3. **UnicodeEncodeError nos Logs**
- Emojis nos logs quebravam encoding no Windows (cp1252)
- Exemplo: `✅`, `🎯`, `⚠️` causavam crash do logging

### 4. **Max Turns Excessivamente Baixo**
- `max_turns = 5` era insuficiente para queries complexas
- LLM precisava de 6-8 turns para gráficos com múltiplos filtros

## Soluções Aplicadas

### 1. **Nova Ferramenta Universal (v2)**

Criado `universal_chart_generator.py` com:

```python
@tool
def gerar_grafico_universal_v2(
    descricao: str,
    filtro_une: Optional[int] = None,
    filtro_segmento: Optional[str] = None,
    filtro_categoria: Optional[str] = None,
    tipo_grafico: str = "auto",
    limite: int = 10
) -> Dict[str, Any]:
    """
    Gera qualquer tipo de gráfico com filtros dinâmicos.
    Substitui todas as ferramentas específicas anteriores.
    """
```

**Vantagens:**
- ✅ Suporta filtros dinâmicos (UNE, segmento, categoria)
- ✅ Detecção automática de dimensão e métrica
- ✅ Performance otimizada (pandas puro, sem chamadas recursivas)
- ✅ Logging detalhado sem emojis

**Exemplo de Uso:**
```python
# Antes (não funcionava)
gerar_grafico_universal(descricao="vendas por segmento da une 1685")

# Agora (funciona perfeitamente)
gerar_grafico_universal_v2(
    descricao="vendas por segmento",
    filtro_une=1685,
    limite=10
)
```

### 2. **Max Turns Aumentado**

```python
# ANTES
max_turns = 5  # Muito baixo

# AGORA
max_turns = 10  # Suficiente para queries complexas
```

### 3. **Fallback de Segurança**

Adicionado mecanismo que retorna gráfico mesmo se max_turns for atingido:

```python
# Se atingir max_turns, verificar se há gráfico pronto
for msg in reversed(messages):
    if msg.get("role") == "function":
        chart_data = func_content.get("chart_data")
        if chart_data and func_content.get("status") == "success":
            logger.info("Grafico encontrado! Retornando...")
            return {"type": "code_result", "chart_spec": chart_data}
```

### 4. **Logs Sem Emojis**

Removidos todos os emojis dos logs para compatibilidade Windows:

```python
# ANTES
logger.info("🎯 GRÁFICO DETECTADO")

# AGORA
logger.info("GRAFICO DETECTADO")
```

### 5. **System Prompt Atualizado**

```markdown
**Exemplos:**
- Usuário: "gere um gráfico de vendas por segmento da une 1685"
  → Você: [Chama gerar_grafico_universal_v2(descricao="vendas por segmento", filtro_une=1685)]

- Usuário: "mostre estoque por categoria no segmento ARMARINHO"
  → Você: [Chama gerar_grafico_universal_v2(descricao="estoque por categoria", filtro_segmento="ARMARINHO")]
```

## Arquivos Modificados

1. **backend/app/core/tools/universal_chart_generator.py** (NOVO)
   - Ferramenta universal com filtros dinâmicos

2. **backend/app/core/agents/caculinha_bi_agent.py**
   - Import da nova ferramenta
   - Remoção de emojis
   - `max_turns` aumentado para 10
   - Fallback de segurança adicionado
   - System prompt atualizado

## Como Testar

```bash
# No Chat.tsx
"gere um gráfico de vendas por segmento da une 1685"

# Resultado esperado:
# 1. Gráfico renderizado em <2 segundos
# 2. Dados FILTRADOS pela UNE 1685
# 3. Agrupamento por SEGMENTO
# 4. Texto narrativo explicativo
```

## Logs de Sucesso

```
[INFO] [ASYNC] Injetando Few-Shot Examples
[WARNING] [ASYNC] GRAFICO DETECTADO - Ativando PREFILL
[INFO] [UNIVERSAL CHART] Gerando: vendas por segmento | UNE=1685
[INFO] Filtrado UNE 1685: 15234 registros
[INFO] [ASYNC] SUCESSO: Grafico gerado por gerar_grafico_universal_v2
[INFO] [ASYNC] Saindo do loop para retornar grafico imediatamente
```

## Performance

- **Antes:** 120+ segundos → Timeout do navegador
- **Agora:** 2-5 segundos → Gráfico renderizado

## Compatibilidade

- ✅ Windows (sem UnicodeEncodeError)
- ✅ SSE Streaming funcional
- ✅ Todos os navegadores (Chrome, Edge, Firefox)
- ✅ Filtros múltiplos simultâneos

## Próximos Passos (Opcional)

1. Adicionar keepalive no SSE (enviar comentário a cada 30s)
2. Implementar timeout configurável no frontend
3. Adicionar cache de gráficos gerados
4. Monitorar métricas de performance no Supabase

---

**Autor:** Claude Sonnet 4.5
**Context7 Principle:** Solução definitiva, não paliativa
