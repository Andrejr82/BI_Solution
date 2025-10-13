# Sugestões de Melhorias nas Respostas do LLM

## Análise do Sistema Atual

O sistema usa uma arquitetura em camadas:
1. **Classificação de Intenção** (`classify_intent`) → Decide o tipo de análise
2. **Geração de Código** (`CodeGenAgent`) → Cria script Python
3. **Formatação Final** (`format_final_response`) → Estrutura a resposta
4. **Renderização Streamlit** → Exibe ao usuário

### Problemas Identificados

#### 1. **Respostas Muito Técnicas e Sem Contexto**
- **Problema**: Retorna apenas dados brutos sem explicação
- **Exemplo atual**: Tabela com 10 produtos sem contexto do que foi pedido
- **Impacto**: Usuário não sabe interpretar os dados

#### 2. **Falta de Narrativa Analítica**
- **Problema**: Não há insights ou análise dos dados
- **Exemplo**: Top 10 produtos → apenas lista, sem destacar tendências
- **Impacto**: Usuário precisa interpretar tudo sozinho

#### 3. **Ausência de Metadata Contextual**
- **Problema**: Não mostra qual segmento, período, ou filtros aplicados
- **Exemplo**: Ranking de vendas → não menciona "Segmento Tecidos"
- **Impacto**: Usuário esquece o contexto da pergunta

#### 4. **Gráficos Sem Títulos Descritivos**
- **Problema**: Títulos genéricos como "Vendas"
- **Exemplo**: "Vendas" vs "Top 10 Produtos - Segmento Tecidos (Últimos 30 Dias)"
- **Impacto**: Gráfico perde significado quando compartilhado

#### 5. **Erro Messages Pouco Actionáveis**
- **Problema**: Mensagens técnicas sem sugestão de ação
- **Exemplo**: "KeyError: 'NOMESEGMENTO'" vs "Segmento 'X' não existe. Tente: TECIDOS, PAPELARIA, FESTAS"
- **Impacto**: Usuário não sabe como corrigir

---

## 🎯 Plano de Melhorias - Roadmap

### **FASE 1: Quick Wins (1-2 dias)** ⚡

#### 1.1. Adicionar Response Enrichment Layer

**Arquivo**: Criar `core/utils/response_enricher.py`

```python
class ResponseEnricher:
    """Enriquece respostas com contexto, insights e narrativa."""

    def enrich_data_response(self, data: List[Dict], user_query: str, metadata: Dict) -> Dict:
        """
        Enriquece resposta de dados com contexto e insights.

        Args:
            data: Lista de registros
            user_query: Pergunta original do usuário
            metadata: Metadados (filtros, segmento, etc.)

        Returns:
            {
                "summary": "Resumo executivo",
                "data": data,
                "insights": ["Insight 1", "Insight 2"],
                "metadata": {"segment": "TECIDOS", "total_rows": 10}
            }
        """
        summary = self._generate_summary(data, user_query, metadata)
        insights = self._extract_insights(data, metadata)

        return {
            "summary": summary,
            "data": data,
            "insights": insights,
            "metadata": metadata
        }

    def _generate_summary(self, data, query, metadata):
        """Gera resumo executivo em linguagem natural."""
        total_rows = len(data)
        segment = metadata.get("segment", "todos os segmentos")

        # Template baseado no tipo de análise
        if "ranking" in query.lower() or "top" in query.lower():
            return f"📊 Encontrei {total_rows} produtos no segmento {segment}. " \
                   f"O produto mais vendido teve {data[0].get('VENDA_30DD', 0)} vendas nos últimos 30 dias."
        else:
            return f"📊 Sua consulta retornou {total_rows} registros para: {segment}"

    def _extract_insights(self, data, metadata):
        """Extrai insights automáticos dos dados."""
        insights = []

        if not data:
            return ["Nenhum dado encontrado para os critérios especificados."]

        # Insight 1: Concentração de vendas
        if "VENDA_30DD" in data[0]:
            total_sales = sum(row.get("VENDA_30DD", 0) for row in data)
            top_3_sales = sum(row.get("VENDA_30DD", 0) for row in data[:3])
            concentration = (top_3_sales / total_sales * 100) if total_sales > 0 else 0

            if concentration > 50:
                insights.append(f"⚠️ Os top 3 produtos concentram {concentration:.1f}% das vendas totais")

        # Insight 2: Produtos com estoque zero
        zero_stock = sum(1 for row in data if row.get("ESTOQUE_UNE", 0) == 0)
        if zero_stock > 0:
            insights.append(f"🚨 {zero_stock} produtos ({zero_stock/len(data)*100:.1f}%) estão com estoque zerado")

        # Insight 3: Faixa de preço
        if "LIQUIDO_38" in data[0]:
            prices = [row.get("LIQUIDO_38", 0) for row in data if row.get("LIQUIDO_38")]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                insights.append(f"💰 Faixa de preço: R$ {min_price:.2f} a R$ {max_price:.2f}")

        return insights or ["Análise concluída com sucesso."]

    def enrich_chart_response(self, chart_json: Dict, user_query: str, data_summary: Dict) -> Dict:
        """Enriquece resposta de gráfico com contexto."""
        return {
            "chart": chart_json,
            "summary": self._generate_chart_summary(user_query, data_summary),
            "interpretation_tips": self._get_interpretation_tips(user_query)
        }

    def _generate_chart_summary(self, query, summary):
        """Gera descrição do gráfico."""
        return f"📈 Gráfico gerado para: '{query}'. " \
               f"Mostrando {summary.get('total_items', 'N/A')} itens."

    def _get_interpretation_tips(self, query):
        """Fornece dicas de interpretação."""
        tips = []

        if "ranking" in query.lower():
            tips.append("💡 Produtos no topo indicam maior volume de vendas")
            tips.append("💡 Compare a diferença entre o 1º e o último para ver a dispersão")

        if "estoque" in query.lower():
            tips.append("💡 Produtos com estoque zero podem estar em ruptura")
            tips.append("💡 Considere a sazonalidade ao analisar estoque")

        return tips or ["💡 Analise os dados considerando o contexto do seu negócio"]
```

**Integração**: Modificar `format_final_response` em `bi_agent_nodes.py:378`

```python
def format_final_response(state: AgentState) -> Dict[str, Any]:
    """Formata a resposta final para o utilizador."""
    from core.utils.response_enricher import ResponseEnricher

    enricher = ResponseEnricher()
    user_query = state['messages'][-1]['content']

    # ... código existente ...

    if state.get("retrieved_data"):
        # ✨ ENRIQUECER resposta de dados
        raw_data = state.get("retrieved_data")
        metadata = {
            "segment": state.get("parquet_filters", {}).get("NOMESEGMENTO", "Todos"),
            "total_rows": len(raw_data),
            "filters_applied": state.get("parquet_filters", {})
        }

        enriched_response = enricher.enrich_data_response(
            data=raw_data,
            user_query=user_query,
            metadata=metadata
        )

        response = {"type": "data_enriched", "content": enriched_response}
        logger.info(f"📊 ENRICHED DATA RESPONSE with {len(enriched_response.get('insights', []))} insights")

    elif state.get("plotly_spec"):
        # ✨ ENRIQUECER resposta de gráfico
        chart_json = state.get("plotly_spec")
        data_summary = {
            "total_items": len(state.get("retrieved_data", [])),
            "chart_type": chart_json.get("data", [{}])[0].get("type", "unknown")
        }

        enriched_chart = enricher.enrich_chart_response(
            chart_json=chart_json,
            user_query=user_query,
            data_summary=data_summary
        )

        response = {"type": "chart_enriched", "content": enriched_chart}
        logger.info(f"📈 ENRICHED CHART RESPONSE")

    # ... resto do código ...
```

**Benefícios**:
- ✅ Respostas com contexto automático
- ✅ Insights gerados sem chamadas LLM extras
- ✅ Usuário entende melhor os dados
- ⏱️ **Tempo de implementação**: 3-4 horas

---

#### 1.2. Melhorar Títulos de Gráficos Dinamicamente

**Arquivo**: Modificar `core/agents/code_gen_agent.py:234-252`

```python
# Adicionar seção ao prompt:

**📊 REGRAS PARA TÍTULOS DE GRÁFICOS:**

1. **Sempre inclua contexto completo no título**:
   - Segmento analisado
   - Período (se aplicável)
   - Métrica (vendas, estoque, etc.)

2. **Exemplos de títulos RUINS vs BONS**:
   - ❌ RUIM: "Vendas"
   - ✅ BOM: "Top 10 Produtos por Vendas - Segmento Tecidos (Últimos 30 Dias)"

   - ❌ RUIM: "Ranking"
   - ✅ BOM: "Ranking de Vendas - Papelaria (Últimos 30 Dias)"

   - ❌ RUIM: "Produtos"
   - ✅ BOM: "Produtos com Estoque Zero - Segmento Festas"

3. **Template de título**:
   ```
   [Tipo de Análise] - [Segmento/Filtro] ([Período/Contexto])
   ```

**OBRIGATÓRIO**: Todo gráfico DEVE ter um título completo seguindo essas regras!
```

**Benefícios**:
- ✅ Gráficos auto-explicativos
- ✅ Melhor para compartilhamento
- ✅ Usuário não precisa lembrar o contexto
- ⏱️ **Tempo de implementação**: 30 minutos

---

#### 1.3. Adicionar Post-Processing de Respostas

**Arquivo**: Criar `core/utils/response_validator.py`

```python
class ResponseValidator:
    """Valida e corrige respostas antes de exibir ao usuário."""

    def validate_and_fix(self, response: Dict, user_query: str) -> Dict:
        """Valida resposta e aplica correções automáticas."""
        response_type = response.get("type")

        if response_type == "data":
            response = self._fix_data_response(response, user_query)
        elif response_type == "chart":
            response = self._fix_chart_response(response, user_query)
        elif response_type == "error":
            response = self._make_error_actionable(response, user_query)

        return response

    def _fix_data_response(self, response, query):
        """Adiciona contexto se estiver faltando."""
        content = response.get("content", [])

        # Se a resposta não tem resumo, adicionar
        if isinstance(content, list) and not response.get("summary"):
            response["summary"] = f"Resultados para: '{query}' ({len(content)} registros)"

        return response

    def _fix_chart_response(self, response, query):
        """Verifica se o gráfico tem título adequado."""
        chart = response.get("content", {})
        layout = chart.get("layout", {})
        title = layout.get("title", {})

        # Se título está vazio ou muito genérico
        if not title or title.get("text", "").lower() in ["gráfico", "chart", "vendas", ""]:
            # Gerar título automático
            title_text = self._generate_default_title(query)
            if "layout" not in chart:
                chart["layout"] = {}
            chart["layout"]["title"] = {"text": title_text}
            response["content"] = chart
            response["title_auto_generated"] = True

        return response

    def _generate_default_title(self, query):
        """Gera título padrão baseado na query."""
        query_lower = query.lower()

        # Detectar segmento
        segments = ["tecidos", "papelaria", "festas", "artes", "casa", "decoração"]
        segment_found = next((s for s in segments if s in query_lower), "")

        # Detectar tipo de análise
        if "ranking" in query_lower or "top" in query_lower:
            return f"Ranking de Vendas{' - ' + segment_found.title() if segment_found else ''}"
        elif "gráfico" in query_lower:
            return f"Análise{' - ' + segment_found.title() if segment_found else ''}"
        else:
            return f"Resultado da Consulta{' - ' + segment_found.title() if segment_found else ''}"

    def _make_error_actionable(self, response, query):
        """Torna mensagens de erro mais úteis."""
        error_msg = response.get("content", "")

        # Mapear erros comuns → sugestões
        error_suggestions = {
            "KeyError": "❓ **O que fazer:** Verifique se o nome do segmento/categoria está correto. Use 'listar segmentos' para ver opções válidas.",
            "MemoryError": "⚠️ **O que fazer:** Sua consulta retornou muitos dados. Tente adicionar filtros (ex: 'top 10', 'segmento X').",
            "TypeError": "🔧 **O que fazer:** Houve um erro no processamento. Tente reformular sua pergunta de forma mais simples.",
            "FileNotFoundError": "📁 **O que fazer:** Dados não encontrados. Verifique se o sistema está configurado corretamente.",
        }

        # Detectar tipo de erro e adicionar sugestão
        for error_type, suggestion in error_suggestions.items():
            if error_type in error_msg:
                response["content"] = f"{error_msg}\n\n{suggestion}"
                break

        return response
```

**Integração**: Adicionar no final de `format_final_response`:

```python
def format_final_response(state: AgentState) -> Dict[str, Any]:
    # ... código existente ...

    # ✅ VALIDAR E CORRIGIR resposta antes de retornar
    from core.utils.response_validator import ResponseValidator
    validator = ResponseValidator()
    response = validator.validate_and_fix(response, user_query)

    return {"messages": final_messages, "final_response": response}
```

**Benefícios**:
- ✅ Erros mais claros e acionáveis
- ✅ Correções automáticas de títulos faltantes
- ✅ Melhor UX sem aumentar latência
- ⏱️ **Tempo de implementação**: 2-3 horas

---

### **FASE 2: Melhorias Estruturais (3-5 dias)** 🏗️

#### 2.1. Adicionar Camada de Summarization com LLM

**Conceito**: Usar LLM para gerar resumo executivo dos dados APÓS a consulta.

**Arquivo**: Criar `core/utils/llm_summarizer.py`

```python
class LLMSummarizer:
    """Usa LLM para gerar resumos executivos de dados."""

    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.llm = llm_adapter

    def summarize_data_response(self, data: List[Dict], user_query: str, max_tokens=150) -> str:
        """
        Gera resumo executivo dos dados usando LLM.

        Args:
            data: Dados retornados (top 10 para não exceder tokens)
            user_query: Pergunta original
            max_tokens: Limite de tokens para o resumo

        Returns:
            Resumo em linguagem natural
        """
        # Limitar dados para não exceder context window
        sample_data = data[:10] if len(data) > 10 else data

        prompt = f"""Você é um analista de dados. Gere um resumo executivo CONCISO (máximo 3 frases) dos dados abaixo.

**Pergunta do Usuário:** "{user_query}"

**Dados (top {len(sample_data)}):**
```json
{json.dumps(sample_data, indent=2, ensure_ascii=False)}
```

**Instruções:**
1. Mencione quantos registros foram encontrados
2. Destaque o principal insight (produto mais vendido, maior diferença, etc.)
3. Seja objetivo e use linguagem de negócio (não técnica)
4. Use emojis relevantes (📊, 💰, 🚨, ⚡)

**Resumo Executivo:**"""

        response = self.llm.get_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3  # Baixa temperatura para respostas mais consistentes
        )

        return response.get("content", "Análise concluída com sucesso.")

    def suggest_next_questions(self, data: List[Dict], user_query: str) -> List[str]:
        """
        Sugere próximas perguntas baseadas nos dados retornados.

        Returns:
            Lista de 3 sugestões de perguntas
        """
        sample_data = data[:5]

        prompt = f"""Baseado na pergunta do usuário e nos dados retornados, sugira 3 perguntas de DRILL-DOWN que o usuário pode fazer para aprofundar a análise.

**Pergunta Original:** "{user_query}"

**Dados (amostra):**
```json
{json.dumps(sample_data, indent=2, ensure_ascii=False)}
```

**Instruções:**
1. As perguntas devem ser ESPECÍFICAS aos dados retornados
2. Sugira drill-downs em diferentes dimensões (tempo, categoria, UNE, etc.)
3. Use linguagem natural (como o usuário falaria)

**Retorne APENAS um JSON array com 3 perguntas:**
```json
["pergunta 1", "pergunta 2", "pergunta 3"]
```"""

        response = self.llm.get_completion(
            messages=[{"role": "user", "content": prompt}],
            json_mode=True,
            max_tokens=200
        )

        try:
            suggestions = json.loads(response.get("content", "[]"))
            return suggestions[:3]  # Garantir máximo 3
        except:
            return [
                "Mostre o estoque desses produtos",
                "Compare com outro segmento",
                "Gere um gráfico desses dados"
            ]
```

**Integração**:

```python
# Em format_final_response:
if state.get("retrieved_data") and len(state.get("retrieved_data", [])) > 0:
    from core.utils.llm_summarizer import LLMSummarizer

    summarizer = LLMSummarizer(llm_adapter)  # Precisa injetar llm_adapter

    # Gerar resumo executivo
    summary = summarizer.summarize_data_response(
        data=state.get("retrieved_data"),
        user_query=user_query
    )

    # Sugerir próximas perguntas
    suggestions = summarizer.suggest_next_questions(
        data=state.get("retrieved_data"),
        user_query=user_query
    )

    response = {
        "type": "data_with_summary",
        "content": state.get("retrieved_data"),
        "executive_summary": summary,
        "next_questions": suggestions
    }
```

**Benefícios**:
- ✅ Resumo executivo gerado automaticamente
- ✅ Sugestões de drill-down contextuais
- ✅ Melhor experiência conversacional
- ⚠️ **Trade-off**: +1-2s de latência por chamada LLM extra
- ⏱️ **Tempo de implementação**: 4-6 horas

---

#### 2.2. Implementar Response Templates por Tipo de Análise

**Conceito**: Criar templates específicos para cada tipo de análise (ranking, comparação, trend, etc.)

**Arquivo**: Criar `core/templates/response_templates.py`

```python
class ResponseTemplates:
    """Templates de resposta por tipo de análise."""

    TEMPLATES = {
        "ranking": {
            "summary_template": "📊 **Ranking de {metric}** no segmento **{segment}**\n\n"
                              "• **Total de itens**: {total}\n"
                              "• **Líder**: {top_item} ({top_value})\n"
                              "• **Último**: {bottom_item} ({bottom_value})\n"
                              "• **Diferença**: {difference}x entre o 1º e o último",
            "insights": [
                "Os top 3 concentram {concentration}% do total",
                "Há uma diferença de {gap}x entre o 1º e o 10º colocado"
            ]
        },
        "comparison": {
            "summary_template": "⚖️ **Comparação**: {item_a} vs {item_b}\n\n"
                              "• **{item_a}**: {value_a}\n"
                              "• **{item_b}**: {value_b}\n"
                              "• **Diferença**: {difference}% ({winner} está à frente)",
            "insights": [
                "{winner} tem desempenho {difference}% superior"
            ]
        },
        "filter_simple": {
            "summary_template": "🔍 **Resultados da busca**: {filter_description}\n\n"
                              "• **Total encontrado**: {total}\n"
                              "• **Principais critérios**: {filters}",
            "insights": []
        }
    }

    @classmethod
    def generate_response(cls, analysis_type: str, data: List[Dict], metadata: Dict) -> Dict:
        """Gera resposta formatada baseada no template."""
        template = cls.TEMPLATES.get(analysis_type, cls.TEMPLATES["filter_simple"])

        if analysis_type == "ranking":
            return cls._generate_ranking_response(data, metadata, template)
        elif analysis_type == "comparison":
            return cls._generate_comparison_response(data, metadata, template)
        else:
            return cls._generate_simple_response(data, metadata, template)

    @classmethod
    def _generate_ranking_response(cls, data, metadata, template):
        """Gera resposta para análise de ranking."""
        if not data or len(data) < 2:
            return {"summary": "Dados insuficientes para ranking", "insights": []}

        metric = metadata.get("metric", "vendas")
        segment = metadata.get("segment", "todos")

        top_item = data[0]
        bottom_item = data[-1]

        top_value = top_item.get("VENDA_30DD", 0)
        bottom_value = bottom_item.get("VENDA_30DD", 1)  # Evitar divisão por zero

        difference = top_value / bottom_value if bottom_value > 0 else 0

        summary = template["summary_template"].format(
            metric=metric,
            segment=segment,
            total=len(data),
            top_item=top_item.get("NOME", "N/A"),
            top_value=f"{top_value:,.0f}",
            bottom_item=bottom_item.get("NOME", "N/A"),
            bottom_value=f"{bottom_value:,.0f}",
            difference=f"{difference:.1f}"
        )

        # Calcular insights
        total_sales = sum(row.get("VENDA_30DD", 0) for row in data)
        top3_sales = sum(row.get("VENDA_30DD", 0) for row in data[:3])
        concentration = (top3_sales / total_sales * 100) if total_sales > 0 else 0

        insights = [
            f"📊 Os top 3 concentram {concentration:.1f}% do total de vendas",
            f"⚡ Há uma diferença de {difference:.1f}x entre o 1º e o último colocado"
        ]

        return {"summary": summary, "insights": insights}

    # ... implementar outros métodos ...
```

**Benefícios**:
- ✅ Respostas padronizadas e profissionais
- ✅ Fácil manutenção e atualização de templates
- ✅ Consistência nas respostas
- ⏱️ **Tempo de implementação**: 6-8 horas

---

### **FASE 3: Melhorias Avançadas (1-2 semanas)** 🚀

#### 3.1. Sistema de Explicação de Respostas (Explainability)

**Conceito**: Adicionar botão "Como cheguei a essa resposta?" que mostra o raciocínio do agente.

**Componentes**:
1. **Tracking de Decisões**: Logar cada decisão do agent_graph
2. **Explanation Generator**: Traduzir logs técnicos em linguagem natural
3. **UI Component**: Expander no Streamlit com a explicação

**Exemplo de Explicação**:
```
🤖 Como cheguei a essa resposta:

1. ✅ Identifiquei sua intenção: "Ranking de vendas"
2. ✅ Detectei o segmento: "TECIDOS"
3. ✅ Gerei código Python para:
   • Filtrar produtos do segmento TECIDOS
   • Ordenar por VENDA_30DD (vendas últimos 30 dias)
   • Selecionar os top 10
4. ✅ Executei o código e retornei 10 produtos
5. ✅ Gerei um gráfico de barras para visualização
```

**Benefícios**:
- ✅ Transparência e confiança
- ✅ Usuário entende o raciocínio do agente
- ✅ Útil para debugging e aprendizado
- ⏱️ **Tempo de implementação**: 2-3 dias

---

#### 3.2. Adaptive Response Format (Personalização por Usuário)

**Conceito**: Aprender preferências do usuário (verboso vs conciso, tabelas vs gráficos).

**Implementação**:
1. **User Profile Storage**: Armazenar preferências em `data/user_profiles/{username}.json`
2. **Feedback Loop**: Capturar feedback (👍/👎) e ajustar estilo
3. **Response Adapter**: Modificar formato baseado no perfil

**Exemplo**:
```json
{
  "username": "usuario_x",
  "preferences": {
    "response_style": "concise",  // ou "detailed"
    "prefer_charts": true,
    "show_insights": true,
    "show_metadata": false
  },
  "feedback_history": [
    {"query": "ranking tecidos", "liked": true, "response_type": "chart"}
  ]
}
```

**Benefícios**:
- ✅ Experiência personalizada
- ✅ Maior satisfação do usuário
- ✅ Sistema aprende com uso
- ⏱️ **Tempo de implementação**: 1 semana

---

#### 3.3. Multi-Modal Responses (Texto + Gráfico + Dados)

**Conceito**: Retornar múltiplas representações da mesma resposta.

**Exemplo de Resposta Multi-Modal**:
```json
{
  "type": "multi_modal",
  "content": {
    "summary": "Resumo executivo em texto",
    "chart": {...},  // Gráfico Plotly
    "data": [...],   // Dados tabulares
    "insights": ["Insight 1", "Insight 2"],
    "export_options": ["CSV", "Excel", "PDF"]
  }
}
```

**UI no Streamlit**:
```python
# Tabs para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["📊 Resumo", "📈 Gráfico", "📋 Dados"])

with tab1:
    st.markdown(response["summary"])
    for insight in response["insights"]:
        st.info(insight)

with tab2:
    st.plotly_chart(response["chart"])

with tab3:
    st.dataframe(response["data"])
    st.download_button("Baixar CSV", ...)
```

**Benefícios**:
- ✅ Usuário escolhe formato preferido
- ✅ Melhor para diferentes casos de uso
- ✅ Exportação facilitada
- ⏱️ **Tempo de implementação**: 1 semana

---

## 📊 Impacto Esperado das Melhorias

| Melhoria | Impacto UX | Esforço | Prioridade |
|----------|-----------|---------|------------|
| Response Enrichment | 🔥🔥🔥 Alto | 3-4h | **P0** |
| Títulos Dinâmicos | 🔥🔥 Médio | 30min | **P0** |
| Response Validator | 🔥🔥🔥 Alto | 2-3h | **P0** |
| LLM Summarizer | 🔥🔥 Médio | 4-6h | **P1** |
| Response Templates | 🔥🔥 Médio | 6-8h | **P1** |
| Explainability | 🔥 Baixo | 2-3d | **P2** |
| Adaptive Format | 🔥 Baixo | 1sem | **P3** |
| Multi-Modal | 🔥🔥 Médio | 1sem | **P2** |

---

## 🎯 Recomendação: Implementar FASE 1 (Quick Wins)

**Justificativa**:
- ✅ **Alto impacto**: Melhora significativa nas respostas
- ✅ **Baixo esforço**: 6-8 horas no total
- ✅ **Sem quebrar nada**: Adiciona camadas sem alterar lógica core
- ✅ **ROI imediato**: Usuário percebe diferença na primeira interação

**Próximos Passos**:
1. Implementar `ResponseEnricher` (3-4h)
2. Adicionar regras de títulos no prompt (30min)
3. Criar `ResponseValidator` (2-3h)
4. Testar com queries reais e iterar

**Quer que eu implemente alguma dessas melhorias agora?**
