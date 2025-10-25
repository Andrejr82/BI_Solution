# 🤖 Sistema 100% LLM - Testes e Execução

## ✅ O que Mudou?

### ANTES (DirectQueryEngine):
- ❌ Usava queries diretas (sem LLM)
- ❌ Limitado a padrões pré-definidos
- ❌ Fallback para LLM apenas quando não entendia

### AGORA (100% LLM - GraphBuilder):
- ✅ **TUDO** usa LLM (GraphBuilder + Agent Graph)
- ✅ CodeGenAgent gera código Python dinamicamente
- ✅ Respostas mais inteligentes e adaptáveis
- ✅ Few-Shot Learning ativo
- ✅ Dynamic Prompts com aprendizado

---

## 🚀 Como Executar os Testes

### 1️⃣ Teste Rápido (5 perguntas)

**Recomendado para validação inicial**

```bash
cd "C:\Users\André\Documents\Agent_Solution_BI"
python tests/test_rapido_100_llm.py
```

**Tempo estimado:** 2-3 minutos

**O que testa:**
- ✅ 5 perguntas representativas
- ✅ Valida que sistema está funcionando
- ✅ Mostra taxa de sucesso imediata

---

### 2️⃣ Teste Completo (80 perguntas)

**Para análise detalhada**

```bash
cd "C:\Users\André\Documents\Agent_Solution_BI"
python tests/test_80_perguntas_completo.py
```

**Tempo estimado:** 15-20 minutos

**O que gera:**
- 📄 `relatorio_teste_80_perguntas_YYYYMMDD_HHMMSS.json` (dados brutos)
- 📊 `relatorio_teste_80_perguntas_YYYYMMDD_HHMMSS.md` (relatório visual)

---

## 📊 Interpretando os Resultados

### Status Possíveis:

| Status | Significado | Ação |
|--------|-------------|------|
| ✅ **SUCCESS** | Query processada com sucesso pela LLM | Nada a fazer |
| ❌ **ERROR** | Erro durante processamento | Verificar logs |
| ❓ **UNKNOWN** | Tipo de resposta desconhecido | Atualizar validação |

### Tipos de Resposta:

| Tipo | Descrição |
|------|-----------|
| `data` | DataFrame/Tabela de dados |
| `chart` | Gráfico Plotly |
| `text` | Resposta textual |
| `clarification` | Sistema pedindo esclarecimento |

---

## 🔧 Arquitetura 100% LLM

### Fluxo de Processamento:

```
Pergunta do Usuário
    ↓
GraphBuilder (LangGraph)
    ↓
classify_intent (LLM)
    ↓
generate_plotly_spec (CodeGenAgent)
    ↓
    → LLM gera código Python
    → Código é executado
    → Resultado retornado
    ↓
format_final_response
    ↓
Resposta ao Usuário
```

### Componentes:

1. **GraphBuilder** - Orquestra o fluxo
2. **LLM Adapter (Gemini)** - Interface com API
3. **CodeGenAgent** - Gera código Python dinamicamente
4. **HybridDataAdapter** - Acesso aos dados
5. **PatternMatcher** - Few-Shot Learning
6. **DynamicPrompt** - Aprendizado de erros

---

## 💡 Vantagens do Sistema 100% LLM

### 1. **Flexibilidade Total**
- Entende perguntas em linguagem natural
- Não limitado a padrões pré-definidos
- Adapta-se a novas questões

### 2. **Aprendizado Contínuo**
- Few-Shot Learning identifica padrões
- Dynamic Prompts aprende com erros
- Melhora ao longo do tempo

### 3. **Código Otimizado**
- LLM gera código Pandas/Dask otimizado
- Usa melhores práticas
- Adiciona validações automaticamente

### 4. **Respostas Inteligentes**
- Detecta intenção corretamente
- Gera gráficos apropriados
- Formata dados adequadamente

---

## 🎯 Exemplos de Perguntas que Funcionam

### Análises por Produto:
```
"Quais são os 5 produtos mais vendidos na UNE SCR?"
"Compare vendas do produto 369947 entre todas as UNEs"
"Top 10 produtos por margem de crescimento"
```

### Análises por Segmento:
```
"Quais são os 10 produtos que mais vendem no segmento TECIDOS?"
"Compare vendas entre ARMARINHO E CONFECÇÃO vs TECIDOS"
"Ranking dos segmentos por volume de vendas"
```

### Análises por UNE:
```
"Ranking de performance de vendas por UNE no segmento TECIDOS"
"Qual UNE vende mais produtos do segmento PAPELARIA?"
"Identifique UNEs com maior potencial de crescimento"
```

### Análises Complexas:
```
"Produtos com vendas acima da média no segmento"
"Análise de sazonalidade no segmento FESTAS"
"UNEs com maior diversidade de produtos vendidos"
```

---

## 📈 Performance e Custos

### Tempo de Resposta:
- **Média:** 3-6 segundos por query
- **Primeiro acesso:** ~10s (compilação do grafo)
- **Queries subsequentes:** 3-5s

### Uso de LLM:
- **Chamadas por query:** 2-3 chamadas
  1. Classificação de intenção (~500 tokens)
  2. Geração de código (~1000 tokens)
  3. (Opcional) Formatação de resposta

### Cache:
- ✅ Cache de respostas LLM (48h TTL)
- ✅ Economia de tokens em queries repetidas
- ✅ Cache de código gerado

---

## 🔍 Troubleshooting

### Problema: "max_tokens muito baixo"

**Solução:** Verificar configuração em `.env`:
```env
GEMINI_MAX_TOKENS=2048  # Aumentar se necessário
```

### Problema: "Timeout na execução"

**Solução:** Queries complexas podem demorar. Aumentar timeout:
```python
grafo.invoke({...}, config={"timeout": 120})
```

### Problema: "Dados vazios retornados"

**Possíveis causas:**
1. Filtro muito restritivo
2. Dados não existem no dataset
3. Erro no código gerado

**Verificar logs:** Procurar por `WARNING` ou `ERROR`

---

## 📝 Logs Importantes

### Durante Execução, Procure Por:

```
[OK] GraphBuilder inicializado (100% LLM ativo)
✅ PatternMatcher inicializado (Few-Shot Learning ativo)
✅ DynamicPrompt inicializado (Pilar 4 ativo)
[OK] Cache HIT - Economia de tokens
```

### Indicadores de Problemas:

```
[ERRO] max_tokens muito baixo
WARNING: Código com problemas
ERROR: Falha ao executar código
```

---

## 🎓 Próximos Passos

### Para Usuários:
1. Execute o teste rápido
2. Verifique taxa de sucesso
3. Teste suas próprias perguntas

### Para Desenvolvedores:
1. Analise relatório completo (.md)
2. Identifique padrões de erro
3. Ajuste prompts se necessário
4. Adicione novos exemplos ao Few-Shot Learning

---

## 📞 Suporte

### Documentação:
- `README_RELATORIOS.md` - Formato dos relatórios
- `EXEMPLO_RELATORIO.md` - Exemplo visual
- Este arquivo - Sistema 100% LLM

### Arquivos de Teste:
- `test_rapido_100_llm.py` - Teste rápido
- `test_80_perguntas_completo.py` - Teste completo

---

**Sistema 100% LLM ativo e funcionando!** ✅

*Última atualização: 19/10/2025*
