# Guia de Logging

## Padrão de Mensagens Estruturadas

Para manter consistência e facilitar a análise de logs, use o seguinte formato:

```python
logger.info("🎯 Descrição curta " +
    "[chave1: valor1] " +
    "[chave2: valor2] " +
    "[razao: explicacao]"
)
```

### Elementos do Log

1. **Emoji Indicador**
   - 🎯 Objetivo/Meta atingido
   - ⚠️ Aviso/Atenção necessária
   - ❌ Erro/Falha
   - 🔄 Processo em andamento
   - ✅ Sucesso/Conclusão
   - 📊 Visualização/Gráfico
   - 📝 Texto/Formatação
   - ➡️ Roteamento/Fluxo

2. **Descrição**
   - Mensagem curta e clara
   - Verbo no gerúndio para ações em progresso
   - Verbo no passado para ações concluídas

3. **Metadados**
   - Use `[chave: valor]` para informações estruturadas
   - Chaves comuns:
     - `[intent: xyz]` - Intenção detectada
     - `[route: xyz]` - Próximo nó do grafo
     - `[reason: xyz]` - Razão da decisão
     - `[error_type: xyz]` - Tipo de erro
     - `[performance: xyz]` - Métricas de performance

### Exemplos

```python
# Roteamento
logger.info("➡️ Roteamento decidido [intent: analise] [route: plotly] [reason: graph_needed]")

# Erro com contexto
logger.error(
    "❌ Falha na inicialização " +
    "[error_type: ConnectionError] " +
    "[component: database] " +
    "[retry: true]",
    exc_info=True
)

# Sucesso com métricas
logger.info(
    "✅ Cache otimizado " +
    "[items_removed: 150] " +
    "[space_saved: 25MB] " +
    "[performance: 95ms]"
)
```

### Compatibilidade

O formato é compatível com:
- structlog (quando disponível)
- logging padrão do Python (via StructlogLikeAdapter)
- Ferramentas de análise de log
- Dashboards de monitoramento

### Quando Não Usar Kwargs

Evite passar kwargs diretos para o logger:
```python
# ❌ NÃO FAÇA ISSO
logger.info("mensagem", type="erro", code=500)  # Pode falhar!

# ✅ USE ISSO
logger.info("mensagem [type: erro] [code: 500]")  # Sempre funciona
```

O único kwarg permitido é `exc_info` para logs de erro:
```python
logger.error("mensagem [type: erro]", exc_info=True)  # OK
```