# Investigação e Correção de Problemas do Agente BI

**Data**: 2025-10-03
**Problema Reportado**: Agente retornando fallback para perguntas básicas como "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?"

## Problemas Identificados

### 1. **Mapeamento Incorreto de Query Type**
- **Arquivo**: `data/query_patterns_training.json`
- **Problema**: Pattern `top_produtos_une` retornava `id: "top_produtos_une"` mas o método no DirectQueryEngine chama-se `_query_top_produtos_une_especifica`
- **Correção**: Alterado `id` de `"top_produtos_une"` para `"top_produtos_une_especifica"`

### 2. **Regex não Capturava Variações de Pergunta**
- **Arquivo**: `data/query_patterns_training.json` (linha 41)
- **Problema**: Regex `(top\\s+)?(\\d+)\\s*produtos...` não capturava "Quais são os 5 produtos..."
- **Correção**: Regex expandido para `(quais?\\s+(?:são|s[ãa]o)?\\s+(?:os?\\s+)?)?(top\\s+)?(\\d+)\\s*produtos...`

### 3. **Conversão de Tipo - Limite como String**
- **Arquivo**: `core/business_intelligence/direct_query_engine.py` (linha 644)
- **Problema**: `limite` extraído do regex era string `'5'`, mas `nlargest()` exige int
- **Correção**: `limite = int(params.get('limite', 10))`

### 4. **Extração de Parâmetros Incorreta**
- **Arquivo**: `data/query_patterns_training.json`
- **Problema**: Com regex expandido, `group(2)` virou `group(3)` para limite
- **Correção**: Ajustado `"extract": {"limite": "group(3)", "une_nome": "group(6)"}`

## Resultados dos Testes

Testado com as perguntas:
1. ✅ "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?"
2. ✅ "Gere um gráfico de vendas do produto 369947 na UNE SCR"
3. ✅ "Produto mais vendido"
4. ✅ "Top 10 produtos mais vendidos no segmento TECIDOS"
5. ✅ "Vendas totais de cada UNE"

**Status**: Todas respondidas corretamente SEM fallback, com ZERO tokens LLM.

## Arquivos Modificados

1. `data/query_patterns_training.json`:
   - ID alterado: `top_produtos_une` → `top_produtos_une_especifica`
   - Regex expandido para capturar mais variações
   - Exemplo adicionado à lista
   - Groups ajustados: `group(2)` → `group(3)` e `group(5)` → `group(6)`

2. `core/business_intelligence/direct_query_engine.py`:
   - Linha 644: Conversão explícita `int(params.get('limite', 10))`

## Recomendações

1. **Adicionar mais padrões** ao `query_patterns_training.json` para cobrir variações comuns
2. **Validação de tipos** nos métodos `_query_*` para evitar erros similares
3. **Testes automatizados** com perguntas de `docs/exemplos_perguntas_negocio.md`
4. **Logging**: Remover emojis incompatíveis com encoding do Windows (cp1252)
