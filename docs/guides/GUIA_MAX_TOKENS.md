# 📊 Guia de Configuração de Max Tokens

## Visão Geral

O parâmetro `max_tokens` controla o **número máximo de tokens** que o modelo pode gerar na resposta. Um token é aproximadamente 3-4 caracteres em português, ou cerca de 0.75 palavras.

## Limites por Modelo

### Gemini 2.5 Flash
- **Limite de Saída**: 8,192 tokens
- **Contexto Total**: 1,048,576 tokens (prompt + resposta)
- **Custo**: ~0.15 USD por 1M tokens de entrada / 0.60 USD por 1M tokens de saída

### DeepSeek V3
- **Limite de Saída**: 8,192 tokens
- **Contexto Total**: 64,000 tokens
- **Custo**: ~0.27 USD por 1M tokens de entrada / 1.10 USD por 1M tokens de saída

## Valores Recomendados por Caso de Uso

### 🎯 **Produção (Agent_BI)**

| Caso de Uso | max_tokens | Justificativa |
|-------------|-----------|---------------|
| **Intent Classification** | 512-1024 | Resposta curta (apenas classificação) |
| **Code Generation** | 2048-4096 | Código Python + comentários + explicação |
| **Data Analysis** | 4096-6144 | Análise detalhada + insights + gráficos |
| **Conversação Geral** | 1024-2048 | Respostas diretas ao usuário |
| **Error Messages** | 512 | Mensagens de erro concisas |

### 🧪 **Desenvolvimento e Testes**

| Caso de Uso | max_tokens | Justificativa |
|-------------|-----------|---------------|
| **Playground** | **4096** (padrão) | Experimentação sem cortes |
| **Testes Unitários** | 50-100 | Validação rápida |
| **Health Checks** | 10 | Apenas verificação de conectividade |
| **Debugging** | 2048-4096 | Análise detalhada de erros |

## Configurações Atuais do Sistema

### Core LLM Adapter
```python
# core/llm_adapter.py
def get_completion(self, messages, model=None, temperature=0, max_tokens=1024, ...):
```
**Status**: ✅ **1024 tokens** (adequado para uso geral)

### Playground
```python
# pages/10_🤖_Gemini_Playground.py
max_tokens = st.slider(
    "Max Tokens",
    min_value=512,
    max_value=8192,
    value=4096,  # ✅ ATUALIZADO de 2048 → 4096
    step=512
)
```
**Status**: ✅ **4096 tokens** (ideal para experimentação)

### Intent Classifier
```python
# core/business_intelligence/intent_classifier.py
max_output_tokens=1024
```
**Status**: ✅ **1024 tokens** (suficiente para classificação)

## Como Identificar Respostas Cortadas

### Sinais de Corte
1. **Código incompleto**: Falta `]`, `}`, ou quebra no meio de uma função
2. **Texto interrompido**: Frase termina abruptamente sem pontuação
3. **Aviso no log**: `finish_reason='length'`

### Como Verificar no Código
```python
response = llm.get_completion(messages, max_tokens=1024)

# Verificar se foi cortada
if response.get('finish_reason') == 'length':
    print("⚠️ Resposta cortada! Aumente max_tokens")
```

### Solução
1. **Aumentar max_tokens** gradualmente: 1024 → 2048 → 4096
2. **Otimizar o prompt**: Tornar mais conciso e direto
3. **Quebrar em múltiplas chamadas**: Para análises muito longas

## Impacto no Custo

### Estimativa de Custo (Gemini 2.5 Flash)
| max_tokens | Tokens Reais | Custo/Chamada | Custo/1000 Chamadas |
|------------|--------------|---------------|---------------------|
| 1024 | ~800 | $0.00048 | $0.48 |
| 2048 | ~1600 | $0.00096 | $0.96 |
| 4096 | ~3200 | $0.00192 | $1.92 |
| 8192 | ~6400 | $0.00384 | $3.84 |

**Nota**: Custo real depende do tamanho da resposta gerada, não do limite configurado.

## Melhores Práticas

### ✅ DO (Faça)
- Use valores adequados ao caso de uso
- Monitore `finish_reason` para detectar cortes
- Implemente cache para economizar tokens
- Teste com valores baixos em desenvolvimento
- Use max_tokens alto apenas quando necessário

### ❌ DON'T (Não Faça)
- Usar 8192 tokens por padrão (desperdício)
- Usar < 512 tokens para análise de código
- Ignorar avisos de resposta cortada
- Processar múltiplas análises em uma única chamada
- Esquecer de documentar configurações customizadas

## Troubleshooting

### Problema: "Resposta Vazia"
**Causa**: `max_tokens` muito baixo, modelo não consegue gerar nada
**Solução**: Aumentar para no mínimo 512 tokens

### Problema: "Resposta Cortada no Meio do Código"
**Causa**: `max_tokens` insuficiente para resposta completa
**Solução**: Aumentar para 2048-4096 tokens

### Problema: "Alto consumo de créditos"
**Causa**: `max_tokens` muito alto em todas as chamadas
**Solução**: Ajustar por caso de uso, usar cache

### Problema: "Timeout na API"
**Causa**: Resposta muito longa + processamento demorado
**Solução**: Reduzir max_tokens ou quebrar em múltiplas chamadas

## Monitoramento

### Métricas a Acompanhar
1. **Taxa de corte**: Quantas respostas foram cortadas (finish_reason='length')
2. **Tokens médios**: Média de tokens usados por resposta
3. **Custo total**: Consumo de tokens × preço por token
4. **Cache hit rate**: Porcentagem de respostas do cache (sem consumir tokens)

### Alertas Recomendados
- Taxa de corte > 5% → Aumentar max_tokens padrão
- Tokens médios < 30% do max_tokens → Reduzir max_tokens
- Custo mensal > $100 → Revisar uso de tokens

## Referências

- [Gemini API - Pricing](https://ai.google.dev/pricing)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)
- [Token Counting Best Practices](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)

---

**Última Atualização**: 13/10/2025
**Versão**: 1.0
**Autor**: Agent_BI Team
