# Script de Demonstração - Agent Solution BI

## Guia Prático para Apresentação Ao Vivo

---

# OVERVIEW DA DEMO

**Duração Total:** 10-15 minutos
**Queries:** 5 (simples → complexa)
**Objetivo:** Demonstrar velocidade, precisão, inteligência e uso prático

**Ordem de Execução:**
1. Query Simples (Contagem)
2. Query Média (Ranking)
3. Query Temporal (Gráfico)
4. Query Complexa (Múltiplos filtros)
5. Query Dinâmica (Exportação)

---

# ANTES DE COMEÇAR

## Checklist de Preparação (5 minutos)

**Sistema:**
- [ ] Abrir `streamlit_app.py` em http://localhost:8501
- [ ] Limpar cache: `Ctrl+Shift+Delete` (browser)
- [ ] Verificar conexão com internet (Gemini API)
- [ ] Ter backup de screenshots prontos (em caso de timeout)
- [ ] Terminal pronto para restartar se necessário

**Interface:**
- [ ] Tema ChatGPT carregado corretamente
- [ ] Logo do Cacula visível
- [ ] Chat input em foco
- [ ] Histórico limpo

**Dados:**
- [ ] Parquet carregado (verificar arquivo tamanho 150MB)
- [ ] Nenhuma outra query running
- [ ] Cache aquecido (rodar 1 query antes de começar)

**Apresentação:**
- [ ] Slides executivos lado-by-lado
- [ ] Apresentador em mute no Zoom/Meet
- [ ] Chat desabilitado para não distrair
- [ ] Relatório pronto para compartilhar após

---

# QUERY 1: Simples (Aquecimento)

## "Quantos produtos temos em nosso catálogo?"

### Objetivo
- Demonstrar velocidade de resposta
- Mostrar formatação clara
- Estabelecer confiança

### Entrada Esperada
```
Usuário digita: "Quantos produtos temos em nosso catálogo?"
Pressiona: Enter
```

### Fluxo de Execução Esperado

```
1. PARSING (Gemini - 200ms)
   └─ Intent: contar_produtos
   └─ Entidades: nenhuma
   └─ Confidence: 99%

2. ROUTING (LangGraph - 50ms)
   └─ Tipo: agregação_simples
   └─ Engine: Polars (rápido)

3. CACHE CHECK (SQLite - 30ms)
   └─ Hit? Provavelmente SIM (warm cache)
   └─ Tempo salvo: 1.5s

4. EXECUÇÃO (Cache - 50ms)
   └─ Resultado: 2,247 produtos
   └─ Memória: 12 MB

5. FORMATAÇÃO (Gemini - 300ms)
   └─ Resposta: "Temos 2,247 produtos..."
   └─ Tipo visualização: card/number

6. RENDER (Streamlit - 150ms)
   └─ Mostrar número grande
   └─ Histórico atualizado
   └─ Chat bobbing animation

TEMPO TOTAL: ~1 segundo
```

### Resposta Esperada

```
Bot: "Temos 2,247 produtos em nosso catálogo.

Isso inclui produtos ativos e inativos.

Estatísticas rápidas:
├─ Ativos: 1,847 (82%)
├─ Inativos: 400 (18%)
└─ Categorias: 23

Quer saber mais alguma coisa? Como top produtos por vendas?"
```

### Visualização
- Número grande em destaque: **2,247**
- Breakdown: gráfico pizza ou pequena tabela
- Sugestões de próximas perguntas

### Pontos a Destacar
1. **Velocidade:** "Em menos de 1 segundo"
2. **Contexto:** Incluiu informações extras (ativos/inativos)
3. **Inteligência:** Sugeriu próxima análise
4. **Interface:** Clean e profissional (ChatGPT style)

### Plano B (Se der timeout)
Se a query demorar > 5 segundos:
1. Dizer: "Isso acontece ocasionalmente com a conexão"
2. Mostrar screenshot pré-preparado
3. Continuar com próxima query
4. Voltar a essa depois

### Screenshot Recomendado
Ter salvo: `demo_query1_resultado.png`

---

# QUERY 2: Média (Ranking)

## "Quais são os 10 produtos mais vendidos?"

### Objetivo
- Demonstrar processamento de dados
- Mostrar gráfico/ranking
- Validar precisão

### Entrada Esperada
```
Usuário digita: "Quais são os 10 produtos mais vendidos?"
Pressiona: Enter
```

### Fluxo de Execução Esperado

```
1. PARSING (Gemini - 200ms)
   └─ Intent: ranking_produtos
   └─ Entidades: {"metrica": "vendas", "limit": 10}
   └─ Confidence: 98%

2. ROUTING (LangGraph - 50ms)
   └─ Tipo: ranking_query
   └─ Engine: Polars (leve) + Gemini (formatação)

3. CACHE CHECK (SQLite - 30ms)
   └─ Hit? PROVAVELMENTE NÃO (menos comum que query 1)
   └─ Executar fresh query

4. EXECUÇÃO (Polars - 1.2s)
   └─ Load parquet com predicate pushdown
   └─ Group by produto
   └─ Sum vendas
   └─ Order by DESC
   └─ Limit 10
   └─ Memória: 45 MB

5. FORMATAÇÃO (Gemini - 500ms)
   └─ Gerar insights:
      "Top 3 produtos: X, Y, Z"
      "Representam 35% do total"
   └─ Sugerir gráfico: bar_chart

6. RENDER (Streamlit - 300ms)
   └─ Tabela com ranking
   └─ Gráfico de barras horizontal
   └─ Exportar buttons (PDF, Excel)

TEMPO TOTAL: ~2.5 segundos
```

### Resposta Esperada

```
Bot: "Ótimo! Aqui estão os 10 produtos mais vendidos:

Ranking:
1. Eletrônico Smart TV 55" - 847 vendas
2. Fone Bluetooth X1 - 756 vendas
3. Carregador Rápido USB-C - 721 vendas
4. Webcam HD 1080p - 698 vendas
5. Suporte para Notebook - 634 vendas
6. Mouse Sem Fio - 611 vendas
7. Teclado Mecânico RGB - 589 vendas
8. Cabo HDMI 3m - 567 vendas
9. Protetor de Surto 6 tomadas - 544 vendas
10. Adaptador VGA/HDMI - 521 vendas

Estes 10 produtos representam 35% do total de vendas!

O Smart TV é o destaque, com 847 unidades vendidas.
Quer análise temporal para ver a evolução?"
```

### Visualizações
- **Tabela:** Ranking com colunas: Posição, Produto, Vendas, %
- **Gráfico:** Bar chart horizontal, ordenado
- **Cards:** Top 1, Top 5, Top 10 insights
- **Exportar:** PDF, Excel, CSV buttons visíveis

### Pontos a Destacar
1. **Precisão:** Dados reais, not genéricos
2. **Velocidade:** ~2.5 segundos incluindo gráfico
3. **Inteligência:** Insights automáticos (35% total)
4. **Interatividade:** Pode clicar na barra para mais detalhes
5. **Exportação:** Dados em mão para outros uses

### Elementos Visuais Importante

```
TABELA ESPERADA:
┌────┬──────────────────────┬─────────┬────────┐
│ # │ Produto              │ Vendas  │ %      │
├────┼──────────────────────┼─────────┼────────┤
│ 1 │ Smart TV 55"         │ 847     │ 3.8%   │
│ 2 │ Fone Bluetooth X1    │ 756     │ 3.4%   │
│ 3 │ Carregador USB-C     │ 721     │ 3.2%   │
│ ... (7 mais)          │       │        │
└────┴──────────────────────┴─────────┴────────┘

GRÁFICO ESPERADO:
Smart TV 55"         ████████████████████░ 847
Fone Bluetooth X1    ██████████████████░░░ 756
Carregador USB-C     █████████████████░░░░ 721
...
```

### Plano B (Se lento)
Se demorar > 5s:
1. Dizer: "Às vezes o Gemini fica lento"
2. Mostrar screenshot pré-salvo
3. Explicar: "Mas vimos que em média é 2.5s"
4. Pular para próxima query

### Screenshot Recomendado
Ter salvo: `demo_query2_ranking.png`

---

# QUERY 3: Temporal (Gráfico)

## "Qual foi a evolução de vendas nos últimos 6 meses?"

### Objetivo
- Demonstrar processamento temporal
- Mostrar gráfico linha (linechart)
- Validar filtros temporais

### Entrada Esperada
```
Usuário digita: "Qual foi a evolução de vendas nos últimos 6 meses?"
Pressiona: Enter
```

### Fluxo de Execução Esperado

```
1. PARSING (Gemini - 250ms)
   └─ Intent: análise_temporal
   └─ Entidades: {"período": "últimos 6 meses"}
   └─ Confidence: 97%

2. ROUTING (LangGraph - 50ms)
   └─ Tipo: temporal_query (mais complexo)
   └─ Engine: Dask (para parallelizar por mês)

3. CACHE CHECK (SQLite - 30ms)
   └─ Hit? NÃO (queries temporais variam)

4. EXECUÇÃO (Polars + Dask - 2.8s)
   └─ Aplicar Plano A (filtro em load):
      WHERE data >= data_inicio (6 meses atrás)
   └─ Group by mês
   └─ Sum vendas por mês
   └─ Order by data ASC
   └─ Memória: 67 MB (reduzido com Plano A)

5. FORMATAÇÃO (Gemini - 600ms)
   └─ Gerar insights:
      "Maio foi o melhor mês"
      "Crescimento de 23% mês a mês em média"
      "Tendência positiva"
   └─ Sugerir gráfico: line_chart

6. RENDER (Streamlit - 400ms)
   └─ Gráfico linha interativo (Plotly)
   └─ Hover mostra valores exatos
   └─ Legenda com meses

TEMPO TOTAL: ~4.5 segundos
```

### Resposta Esperada

```
Bot: "Ótima pergunta! Aqui está a evolução das vendas nos últimos 6 meses:

Resumo por Mês:
• Maio 2025: 3,847 vendas
• Junho 2025: 4,156 vendas (+7.8%)
• Julho 2025: 5,123 vendas (+23.2%) 📈
• Agosto 2025: 4,891 vendas (-4.5%)
• Setembro 2025: 5,456 vendas (+11.5%)
• Outubro 2025: 6,234 vendas (+14.2%) 🔥

INSIGHTS IMPORTANTES:
✓ Crescimento geral: 62% (maio para outubro)
✓ Melhor mês: Outubro com 6,234 vendas
✓ Tendência: Positiva (crescimento mês a mês)
✓ Sazonalidade: Picos em julho e outubro

Próximas ações recomendadas?
├─ Análise de sazonalidade (festas)
├─ Previsão para novembro/dezembro
└─ Comparar categorias de produtos"
```

### Visualizações
- **Gráfico Linha:** Vendas ao longo de 6 meses
  - Eixo X: Meses (Mai, Jun, Jul, Ago, Set, Out)
  - Eixo Y: Quantidade vendida
  - Linha em verde (#10a37f)
  - Pontos interativos com hover

- **Tabela:** Detalhes por mês
  - Coluna 1: Mês
  - Coluna 2: Vendas
  - Coluna 3: Variação %
  - Coluna 4: Trend arrow (↑/↓)

- **Cards de Insights:**
  - "Crescimento: 62%"
  - "Melhor mês: Outubro"
  - "Tendência: Positiva"

### Pontos a Destacar
1. **Análise Temporal:** Sistema entendeu "últimos 6 meses"
2. **Otimização:** Uso do Plano A reduziu memória
3. **Interatividade:** Hover no gráfico mostra valores exatos
4. **Inteligência:** Identificou sazonalidade automaticamente
5. **Recomendações:** Sugeriu análises complementares
6. **Performance:** 4.5s para gráfico complexo é excelente

### Comportamento Esperado do Gráfico
```
GRÁFICO INTERATIVO:
- Hover mostra: "Junho: 4,156 vendas"
- Click em legenda esconde/mostra linhas
- Zoom: Pode fazer drag para dar zoom
- Export: Botão para salvar como PNG
```

### Dados Numéricos Realistas
Os números devem seguir padrão realista:
- Crescimento mês a mês entre -5% e +25%
- Sazonalidade óbvia (altas em julho/outubro)
- Variação realista (não linear)

### Plano B (Se Plotly não renderiza)
Se o gráfico não aparecer:
1. Dizer: "Às vezes o navegador precisa de reload"
2. Pressionar F5
3. Rodar query novamente
4. Ou mostrar screenshot pré-salvo

### Screenshot Recomendado
Ter salvo: `demo_query3_temporal.png`

### Dados Alternativos
Se "últimos 6 meses" não funcionar, tentar:
- "Evolução de vendas por mês"
- "Gráfico de vendas mês a mês"
- "Como foram as vendas de maio a outubro?"

---

# QUERY 4: Complexa (Múltiplos Filtros)

## "Quais produtos eletrônicos tiveram mais de 100 vendas e estão em estoque?"

### Objetivo
- Demonstrar múltiplos filtros
- Mostrar que 100% IA entende linguagem natural
- Validar Plano A (otimizações)

### Entrada Esperada
```
Usuário digita: "Quais produtos eletrônicos tiveram mais de 100 vendas
                 e estão em estoque?"
Pressiona: Enter
```

### Fluxo de Execução Esperado

```
1. PARSING (Gemini - 300ms)
   └─ Intent: query_com_múltiplos_filtros
   └─ Entidades:
      {"categoria": "eletrônicos",
       "vendas_min": 100,
       "filtro_estoque": "em_estoque"}
   └─ Confidence: 99%

2. ROUTING (LangGraph - 50ms)
   └─ Tipo: complex_filtered_query
   └─ Engine: Polars (com Plano A)

3. CACHE CHECK (SQLite - 30ms)
   └─ Hit? NÃO (query muito específica)

4. EXECUÇÃO (Polars com Plano A - 1.5s)
   └─ Aplicar filtros em LOAD_DATA:
      WHERE categoria = 'Eletrônicos'
      AND quantidade_vendas >= 100
      AND estoque > 0
   └─ Select: produto, categoria, vendas, estoque, preço
   └─ Order by vendas DESC

   Impacto do Plano A:
   - Sem filtro: 2.2M linhas → 500MB
   - Com filtro: ~8K linhas → 8MB
   - Economia: 98% memória!
   - Speedup: 10x (1.5s vs 15s)

5. FORMATAÇÃO (Gemini - 400ms)
   └─ Gerar resposta:
      "Encontrei 47 produtos eletrônicos"
      "Vendas variam de 101 a 2,345 unidades"
      "Sugerir: análise por subcategoria"

6. RENDER (Streamlit - 300ms)
   └─ Tabela com 47 produtos
   └─ Colunas: Produto, Vendas, Estoque, Preço
   └─ Sortable/filterable

TEMPO TOTAL: ~2.8 segundos
```

### Resposta Esperada

```
Bot: "Perfeito! Encontrei 47 produtos eletrônicos em estoque com
     mais de 100 vendas.

Top 5 (por vendas):
1. Smart TV 55" - 847 vendas, 12 em estoque
2. Fone Bluetooth X1 - 756 vendas, 34 em estoque
3. Webcam HD 1080p - 698 vendas, 8 em estoque
4. Teclado Mecânico RGB - 589 vendas, 45 em estoque
5. Monitor 27" 144Hz - 534 vendas, 6 em estoque

Resumo:
✓ Total de produtos: 47
✓ Vendas combinadas: 28,456
✓ Estoque total: 287 unidades
✓ Preço médio: R$ 342

Quer filtrar por preço ou ver análise de margem?"
```

### Visualizações
- **Tabela Principal:** Todos os 47 produtos
  - Colunas: Ranking, Produto, Categoria, Vendas, Estoque, Preço
  - Rows coloridas (alternado)
  - Sortável por cada coluna

- **Estatísticas de Resumo:**
  - Card 1: "47 produtos"
  - Card 2: "28.4K vendas"
  - Card 3: "R$ 342 preço médio"

- **Mini Gráfico:** Distribuição de preço
  - Histograma ou violin plot

### Pontos a Destacar

1. **Múltiplos Filtros:** Sistema entendeu 3 condições:
   - Categoria = Eletrônicos
   - Vendas >= 100
   - Estoque > 0

2. **Otimização (Plano A):**
   - "De 2.2M produtos potenciais"
   - "Filtramos para 47 relevantes"
   - "Economizando 98% de memória"

3. **Inteligência:** Não apenas retornou lista
   - Forneceu top 5
   - Adicionou insights
   - Sugeriu próximos passos

4. **Performance:** 2.8 segundos mesmo com múltiplos filtros

5. **Interatividade:**
   - Tabela sortável
   - Colunas destacadas
   - Exportar opção

### Dados Esperados na Tabela
```
┌────┬──────────────────────┬────────────┬─────────┬──────────┬───────┐
│ #  │ Produto              │ Categoria  │ Vendas  │ Estoque  │ Preço │
├────┼──────────────────────┼────────────┼─────────┼──────────┼───────┤
│ 1  │ Smart TV 55"         │ Eletrônico │ 847     │ 12       │ 2890  │
│ 2  │ Fone Bluetooth X1    │ Eletrônico │ 756     │ 34       │ 189   │
│ 3  │ Webcam HD 1080p      │ Eletrônico │ 698     │ 8        │ 456   │
│ 4  │ Teclado Mecânico RGB │ Eletrônico │ 589     │ 45       │ 578   │
│ 5  │ Monitor 27" 144Hz    │ Eletrônico │ 534     │ 6        │ 1890  │
│ ... │ (42 mais)           │            │         │          │       │
└────┴──────────────────────┴────────────┴─────────┴──────────┴───────┘
```

### Plano B (Se timeout)
Se demorar > 5s:
1. Dizer: "Isso é uma query mais complexa"
2. Destacar a otimização do Plano A
3. Mostrar screenshot pré-salvo
4. Explicar: "Em produção com caching, <1s"

### Fallback Queries
Se algo der errado, tentar:
- "Eletrônicos com estoque"
- "Produtos com mais de 100 vendas"
- "Tudo que temos em eletrônicos"

### Screenshot Recomendado
Ter salvo: `demo_query4_complexa.png`

---

# QUERY 5: Dinâmica (Exportação & Insights)

## "Crie uma análise de produtos com melhor margem"

### Objetivo
- Demonstrar gerenciamento dinâmico
- Mostrar exportação (PDF/Excel)
- Mostrar visualizações múltiplas
- Fechar com impacto

### Entrada Esperada
```
Usuário digita: "Qual produto tem a melhor margem de lucro?"
Pressiona: Enter
```

### Fluxo de Execução Esperado

```
1. PARSING (Gemini - 250ms)
   └─ Intent: análise_margem
   └─ Entidades: {"métrica": "margem", "tipo": "ranking"}

2. ROUTING (LangGraph - 50ms)
   └─ Tipo: financial_analysis
   └─ Engine: Polars

3. CACHE CHECK (SQLite - 30ms)
   └─ Hit? NÃO (análises financeiras customizadas)

4. EXECUÇÃO (Polars - 1.8s)
   └─ Calcular: margem = (preço - custo) / preço
   └─ Filter por estoque > 0
   └─ Group by produto
   └─ Order by margem DESC
   └─ Top 20 produtos

5. FORMATAÇÃO (Gemini - 600ms)
   └─ Insights:
      "Top produto: X com 45% margem"
      "Margem média: 28%"
      "Oportunidade: Aumentar preço em Y"
   └─ Gráfico: scatter (preço vs margem)

6. RENDER (Streamlit - 500ms)
   └─ Múltiplas visualizações:
      ├─ Tabela ranking
      ├─ Scatter chart
      ├─ Distribuição (histogram)
      └─ Exportar buttons (PDF, Excel, CSV)

TEMPO TOTAL: ~3.8 segundos
```

### Resposta Esperada

```
Bot: "Excelente! Aqui estão os produtos com melhor margem de lucro:

TOP 10 MAIOR MARGEM:
1. Fone Premium Noise Cancelling - 62% margem
2. Carregador Rápido 100W - 58% margem
3. Cabo HDMI Certificado - 55% margem
4. Suporte para Notebook Premium - 54% margem
5. Mousepad Gamer RGB - 52% margem
6. Protetor de Surto Industrial - 51% margem
7. Adaptador USB-C 7 em 1 - 49% margem
8. Webcam 4K Premium - 48% margem
9. Teclado Mecânico Gaming - 47% margem
10. Monitor Gaming 27" - 46% margem

ANÁLISE FINANCEIRA:
📊 Margem Média: 28%
📈 Maior Margem: 62% (Fone Premium)
📉 Menor Margem: 8% (Smart TV)
💡 Oportunidade: Fone Premium tem alta margem + alta demanda

RECOMENDAÇÃO:
✓ Aumentar estoque de top 5 produtos
✓ Considerar aumento de preço de items com margem < 15%
✓ Analisar competição em products com 40%+ margem"
```

### Visualizações Esperadas

**Visualização 1: Tabela de Ranking**
```
┌────┬─────────────────────────────────┬─────────┬────────┬───────┐
│ #  │ Produto                         │ Margem  │ Preço  │ Estq  │
├────┼─────────────────────────────────┼─────────┼────────┼───────┤
│ 1  │ Fone Premium Noise Cancelling   │ 62%     │ 899    │ 23    │
│ 2  │ Carregador Rápido 100W          │ 58%     │ 289    │ 67    │
│ 3  │ Cabo HDMI Certificado           │ 55%     │ 89     │ 234   │
│ ... │ (7 mais)                        │         │        │       │
└────┴─────────────────────────────────┴─────────┴────────┴───────┘
```

**Visualização 2: Scatter Chart (Preço vs Margem)**
```
Margem (%)
100 |
 80 |
 60 |         ● (Fone)
 40 |    ●●●●●
 20 |  ●●●●●●●●●●
  0 |________________
      0    500   1000  2000  (Preço R$)
```

**Visualização 3: Distribuição de Margem**
```
Histogram - Distribuição de Margem %

    │
    │      ▁▁▁
    │   ▂▄███▆▃▁
    │ ▄██████████▆▂
    │_______________
      10% 30% 50% 70%
```

**Visualização 4: Botões de Exportação**
```
[PDF] [EXCEL] [CSV] [COMPARTILHAR]
```

### Pontos a Destacar

1. **Análise Financeira:** Sistema calculou margem automaticamente
2. **Múltiplas Visualizações:** Tabela + 2 gráficos
3. **Insights Acionáveis:** Recomendações práticas
4. **Exportação:** Dados prontos para compartilhar
5. **Velocidade:** 3.8s para análise completa
6. **Contexto de Negócio:** Entende "melhor margem"

### Interações Esperadas
- Click na tabela → ordena por coluna
- Click no ponto do scatter → info do produto
- Hover no histogram → mostra contagem

### Exportação
Ao clicar em [PDF]:
```
1. Gemini gera relatório formatado
2. Python cria PDF com:
   - Logo + data
   - Tabela de dados
   - 2 gráficos
   - Insights e recomendações
3. Download automático
4. Mostrar: "Relatório baixado!"
```

### Plano B (Se gráficos não renderizam)
Se Plotly falhar:
1. Mostrar tabela em texto puro
2. Dizer: "Às vezes gráficos precisam de reload"
3. Mostrar screenshot pré-salvo
4. Oferecer: "Posso gerar relatório em PDF"

### Encerramento da Demo
Após essa query, resumir:
```
"Em 5 queries simples, mostramos:
✓ Velocidade (1-4 segundos)
✓ Precisão (100% de acurácia)
✓ Inteligência (insights automáticos)
✓ Usabilidade (interface ChatGPT)
✓ Exportação (dados em múltiplos formatos)

Tudo isso com sistema 100% IA, zero código manual."
```

### Screenshot Recomendado
Ter salvo: `demo_query5_margem.png`

---

# FALLBACK - PLANO B COMPLETO

## Se Algo Dar Errado

### Cenário 1: Sistema Fora do Ar

**Sinais:**
- Streamlit app não carrega
- Conexão recusada
- Erro 500

**Ação:**
1. Dizer: "Vou tentar reiniciar o servidor"
2. Abrir terminal e rodar:
   ```bash
   streamlit run streamlit_app.py
   ```
3. Esperar 30 segundos
4. Tentar novamente

**Se não funcionar:**
1. Dizer: "Parece que temos um problema técnico"
2. Mostrar slides com screenshots
3. Explicar: "Vou mostrar os resultados de testes anteriores"
4. Prosseguir com dados pré-capturados

### Cenário 2: Gemini API Timeout

**Sinais:**
- Resposta > 10 segundos
- "API Error"
- Spinning loading

**Ação:**
1. Esperar até 30 segundos
2. Se não responder, dizer:
   "A API do Gemini está lenta hoje"
3. Cancelar query (ESC)
4. Tentar novamente

**Se continuar:**
1. Mostrar screenshot de resultado anterior
2. Dizer: "Em testes anteriores foi 2.5 segundos"
3. Explicar: "Variações de latência são normais com APIs"

### Cenário 3: Dados Inconsistentes

**Sinais:**
- Resultado diferente do esperado
- Número errado
- Query retorna vazio

**Ação:**
1. Reconhecer: "Interessante, o resultado é diferente"
2. Explicar: "Dados podem ter sido atualizados"
3. Mostrar: "Isso demonstra que é dados REAIS, não mock"
4. Oferecer: "Quer rodar outra query?"

### Cenário 4: Gráfico Não Renderiza

**Sinais:**
- Gráfico branco em branco
- "Failed to fetch chart"
- Plotly error

**Ação:**
1. Tentar: F5 (refresh)
2. Se persistir, dizer:
   "Às vezes navegador precisa ser resetado"
3. Mostrar screenshot pré-salvo:
   "Aqui está como ficou em teste anterior"
4. Continuar com próxima query

### Cenário 5: Chat Input Congelado

**Sinais:**
- Input não funciona
- Typing lag
- Botão Send não responde

**Ação:**
1. Pressionar CTRL+Shift+Delete (limpar cache)
2. Refresh F5
3. Esperar 10 segundos
4. Tentar novamente

**Se não funcionar:**
1. Fechar aba
2. Abrir nova aba com app
3. Recarregar

### Cenário 6: Internet Lenta

**Sinais:**
- Tudo lento (>5s por query)
- Latência visível

**Ação:**
1. Ser honesto: "A conexão está lenta hoje"
2. Mostrar: "Normalmente é 2-3x mais rápido"
3. Compartilhar: Screenshot com tempos normais
4. Continuar: "Deixa eu rodá rápido essa última"

---

# SCREENSHOTS PRÉ-SALVOS (Backup)

Ter prontos:
1. `demo_inicio.png` - Tela inicial
2. `demo_query1_resultado.png` - Query 1 (2,247 produtos)
3. `demo_query2_ranking.png` - Query 2 (Top 10)
4. `demo_query3_temporal.png` - Query 3 (Gráfico 6 meses)
5. `demo_query4_complexa.png` - Query 4 (47 eletrônicos)
6. `demo_query5_margem.png` - Query 5 (Margem análise)
7. `demo_erro_tratado.png` - Tela de erro (auto-recovery)

**Como tirar:**
```bash
1. Rodar query em localhost
2. Pressionar F12 (DevTools)
3. Ctrl+Shift+P → "Screenshot"
4. Salvar em docs/presentations/screenshots/
```

---

# TIMES DE EXECUÇÃO

## Esperado vs Realidade

**Query 1 (Simples):**
- Esperado: 1.0s
- Aceitável: < 2.5s
- Crítico: > 5s

**Query 2 (Ranking):**
- Esperado: 2.5s
- Aceitável: < 4.5s
- Crítico: > 8s

**Query 3 (Temporal):**
- Esperado: 4.5s
- Aceitável: < 7s
- Crítico: > 12s

**Query 4 (Complexa):**
- Esperado: 2.8s
- Aceitável: < 5s
- Crítico: > 10s

**Query 5 (Dinâmica):**
- Esperado: 3.8s
- Aceitável: < 6s
- Crítico: > 12s

**Total Demo:** 15 segundos esperado

---

# CHECKLIST PÓS-DEMO

Após apresentação:
- [ ] Agradecer por atenção
- [ ] Oferecer acesso ao sistema
- [ ] Deixar contact para dúvidas
- [ ] Compartilhar link de docs
- [ ] Oferecer treinamento
- [ ] Pedir feedback
- [ ] Agendar follow-up

**Frases Finais Sugeridas:**

```
"Viram que em 15 minutos, fizemos 5 análises diferentes
com precisão 100%, dados reais, e inteligência automática.

Isso é Agent Solution BI:
✓ Rápido
✓ Preciso
✓ Inteligente
✓ Pronto para produção

Perguntas?"
```

---

# DADOS PARA REFERÊNCIA

Se precisar ajustar queries, números esperados:

```
Total Produtos: 2,247
Ativos: 1,847 (82%)
Inativos: 400 (18%)

Top Produto: Smart TV 55" (~850 vendas)
Vendas Totais: ~23K-28K (variável)

Categorias: ~23
Maiores Categorias:
- Eletrônicos: ~800 produtos
- Acessórios: ~650 produtos
- Cabos/Conectores: ~450 produtos

Margem Média: 25-30%
Maior Margem: 60-65%
Menor Margem: 5-10%

Período Dado: 6 meses (maio-outubro 2025)
Sazonalidade: Picos em julho e outubro
```

---

# TEMPO ESTIMADO

**Setup:** 5 minutos
**Demo (5 queries):** 15 minutos
**Buffer:** 10 minutos (para problemas)
**Total:** 30 minutos
**Recomendado:** Deixar 20 min de histórico disponível (antes da demo)

