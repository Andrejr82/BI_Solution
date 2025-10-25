# Teste de 80 Perguntas - 100% LLM

## 📋 Visão Geral

Este teste avalia a capacidade do sistema de processar 80 perguntas de negócio usando **100% LLM** (Gemini ou DeepSeek), sem cache ou padrões pré-definidos.

## 🎯 Objetivo

Validar que a LLM consegue:
- Entender perguntas complexas de negócio
- Processar consultas em linguagem natural
- Gerar respostas completas e relevantes
- **Consumir tokens da API para cada pergunta**

## ⚠️ ATENÇÃO - CONSUMO DE TOKENS

Este teste **consome tokens da API**!

- **Estimativa**: 5.000 - 10.000 tokens para 80 perguntas
- **Custo aproximado**:
  - Gemini: ~$0.005 - $0.010
  - DeepSeek: ~$0.0005 - $0.001

## 🔑 Pré-requisitos

### 1. Configurar API Key

Você precisa de pelo menos uma das seguintes chaves de API:

**Opção A: Gemini (Google)**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "sua-chave-aqui"

# Windows (CMD)
set GEMINI_API_KEY=sua-chave-aqui

# Linux/Mac
export GEMINI_API_KEY="sua-chave-aqui"
```

**Opção B: DeepSeek**
```bash
# Windows (PowerShell)
$env:DEEPSEEK_API_KEY = "sua-chave-aqui"

# Windows (CMD)
set DEEPSEEK_API_KEY=sua-chave-aqui

# Linux/Mac
export DEEPSEEK_API_KEY="sua-chave-aqui"
```

### 2. Verificar .env (Opcional)

Ou adicione no arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua-chave-aqui
DEEPSEEK_API_KEY=sua-chave-aqui
```

## 🚀 Como Executar

### Opção 1: Script Auxiliar (Recomendado)

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python tests/run_test_llm.py
```

### Opção 2: Diretamente

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python tests/test_80_perguntas_llm.py
```

## 📊 O que é Testado

O teste cobre as mesmas 10 categorias do teste DirectQueryEngine:

1. 🎯 Vendas por Produto (8 perguntas)
2. 🏪 Análises por Segmento (8 perguntas)
3. 🏬 Análises por UNE/Loja (8 perguntas)
4. 📈 Análises Temporais (8 perguntas)
5. 💰 Performance e ABC (8 perguntas)
6. 📦 Estoque e Logística (8 perguntas)
7. 🏭 Análises por Fabricante (8 perguntas)
8. 🎨 Categoria/Grupo (8 perguntas)
9. 📊 Dashboards Executivos (8 perguntas)
10. 🔍 Análises Específicas (8 perguntas)

**Total: 80 perguntas**

## 📈 Métricas Avaliadas

- ✅ **SUCCESS**: LLM processou com sucesso
- ❌ **ERROR**: Erro durante processamento
- ⏱️ **TIMEOUT**: Excedeu 60 segundos

Adicionalmente:
- **Tokens consumidos** (estimativa)
- **Tempo de processamento** por pergunta
- **Preview da resposta** gerada

## 📄 Relatório Gerado

```
tests/relatorio_teste_80_perguntas_llm_YYYYMMDD_HHMMSS.json
```

### Estrutura do Relatório

```json
{
  "metadata": {
    "timestamp": "2025-10-19T...",
    "total_perguntas": 80,
    "total_categorias": 10,
    "llm_usado": "Gemini",
    "modo": "100% LLM"
  },
  "estatisticas": {
    "SUCCESS": 75,
    "ERROR": 3,
    "TIMEOUT": 2,
    "total_tokens_estimados": 8450,
    "media_tokens_pergunta": 105.6
  },
  "resultados": [
    {
      "id": 1,
      "categoria": "🎯 Vendas por Produto",
      "pergunta": "Gere um gráfico...",
      "status": "SUCCESS",
      "mensagem": "Resposta gerada (542 chars)",
      "tokens_estimados": 135,
      "tempo_processamento": 2.45,
      "timestamp": "2025-10-19T...",
      "resposta_preview": "Para gerar o gráfico..."
    }
  ]
}
```

## 🔍 Interpretação dos Resultados

### Meta de Sucesso
- **Excelente**: SUCCESS > 90% (72+ perguntas)
- **Ótimo**: SUCCESS > 80% (64+ perguntas)
- **Bom**: SUCCESS > 70% (56+ perguntas)
- **Aceitável**: SUCCESS > 60% (48+ perguntas)

### Análise de Performance
- **Tempo médio**: Ideal < 3 segundos/pergunta
- **Tokens médios**: ~80-150 tokens/resposta
- **Taxa de timeout**: Ideal < 5%

### Comparação com DirectQueryEngine

Use este teste para comparar:
- **Performance**: DirectQuery = ~0.5s, LLM = ~2-5s
- **Custo**: DirectQuery = $0, LLM = $0.005-0.01
- **Flexibilidade**: LLM tem maior capacidade de entender variações

## 🎮 Controle de Execução

### Cancelar o Teste

Pressione `Ctrl+C` para cancelar:
- Nos primeiros 5 segundos: cancela antes de iniciar
- Durante execução: interrompe e salva resultados parciais

### Timeout por Pergunta

Cada pergunta tem timeout de 60 segundos. Se exceder:
- Status = TIMEOUT
- Pergunta é pulada
- Teste continua com a próxima

## 💡 Dicas de Uso

### 1. Teste Pequeno Primeiro

Antes de rodar todas as 80 perguntas, teste com poucas:

```python
# Edite test_80_perguntas_llm.py
# Comente categorias que não quer testar
PERGUNTAS = {
    "🎯 Vendas por Produto": [
        "Gere um gráfico de vendas do produto 369947 na UNE SCR",
        # ... apenas 2-3 perguntas para teste
    ]
}
```

### 2. Monitor de Custos

Acompanhe o consumo de tokens no dashboard da API:
- **Gemini**: https://makersuite.google.com/
- **DeepSeek**: https://platform.deepseek.com/

### 3. Escolha da LLM

- **Gemini**: Melhor qualidade, mais caro
- **DeepSeek**: Mais barato, boa qualidade

O script tenta Gemini primeiro, depois DeepSeek como fallback.

## 🐛 Troubleshooting

### Erro: "API key not found"

```bash
# Verifique se configurou a variável
echo $env:GEMINI_API_KEY  # PowerShell
echo %GEMINI_API_KEY%     # CMD
```

### Erro: "Rate limit exceeded"

Aguarde alguns minutos. As APIs têm limites de requisições/minuto.

### Erro: "Module not found"

```bash
pip install -r requirements.txt
```

### Muitos Timeouts

- Verifique sua conexão de internet
- Tente usar DeepSeek (geralmente mais rápido)
- Aumente o timeout no código (linha ~180)

## 📊 Comparação: DirectQuery vs LLM

| Métrica | DirectQuery | 100% LLM |
|---------|-------------|----------|
| Velocidade | ~0.5s/pergunta | ~2-5s/pergunta |
| Custo | $0 | $0.005-0.01 |
| Flexibilidade | Padrões fixos | Alta |
| Novos tipos de pergunta | Precisa implementar | Entende naturalmente |
| Consumo de recursos | Baixo (CPU) | Médio (API) |
| Offline | ✅ Sim | ❌ Não |

## 🎯 Quando Usar Cada Abordagem

### Use DirectQuery quando:
- Perguntas são repetitivas e conhecidas
- Velocidade é crítica
- Quer economizar custos de API
- Sistema precisa funcionar offline

### Use 100% LLM quando:
- Perguntas são variadas e imprevisíveis
- Flexibilidade é mais importante que velocidade
- Custo de API é aceitável
- Quer capacidade de entender nuances

### Use Híbrido quando:
- Quer o melhor dos dois mundos
- DirectQuery para padrões comuns
- LLM para casos complexos/novos

## 📝 Exemplo de Saída

```
================================================================================
TESTE COMPLETO DAS 80 PERGUNTAS DE NEGÓCIO - 100% LLM
================================================================================
Início: 2025-10-19 10:30:00

Inicializando GraphAgent com LLM...
[OK] GraphAgent inicializado com Gemini

================================================================================
[CATEGORIA] 🎯 Vendas por Produto
================================================================================

[1/80] Testando: Gere um gráfico de vendas do produto 369947 na UNE SCR...
[OK] SUCCESS: Resposta gerada (542 chars) (2.45s, ~135 tokens)

[2/80] Testando: Mostre a evolução de vendas mensais do produto 369947...
[OK] SUCCESS: Resposta gerada (678 chars) (3.12s, ~169 tokens)

...

================================================================================
ESTATÍSTICAS FINAIS
================================================================================
LLM usado: Gemini
Total de perguntas testadas: 80
[OK] Sucesso (SUCCESS):        75 (93.8%)
[XX] Erros (ERROR):            3 (3.8%)
[TO] Timeout:                  2 (2.5%)

[$$] Total de tokens estimados: 8,450
[$$] Média de tokens por pergunta: 105.6
```

## 📞 Suporte

Em caso de problemas:
1. Verifique as API keys
2. Consulte o relatório JSON gerado
3. Revise os logs de erro
4. Teste com uma pergunta simples primeiro

---

**Última atualização**: 2025-10-19
**Versão**: 1.0
