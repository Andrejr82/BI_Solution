# Plano de Implementação - Queries DirectQueryEngine

**Objetivo:** Aumentar cobertura do DirectQueryEngine de 1.3% para 50%+ nas 80 perguntas de negócio

**Status:** Planejamento
**Data:** 03/10/2025

---

## 📊 Análise de Impacto

### Queries por Frequência (do teste)
| Query | Ocorrências | Impacto | Complexidade |
|-------|-------------|---------|--------------|
| `analise_geral` | 47 | 🔴 ALTO | 🟡 MÉDIA |
| `ranking_geral` | ~8 | 🟠 MÉDIO | 🟢 BAIXA |
| `comparacao_segmentos` | ~3 | 🟠 MÉDIO | 🟡 MÉDIA |
| `analise_abc` | ~4 | 🟠 MÉDIO | 🟡 MÉDIA |
| `sazonalidade` | ~3 | 🟡 BAIXO | 🔴 ALTA |
| `consulta_une_especifica` | ~4 | 🟠 MÉDIO | 🟢 BAIXA |
| `estoque_alto` | 1 | 🟡 BAIXO | 🟢 BAIXA |
| `rotacao_estoque` | 1 | 🟡 BAIXO | 🟡 MÉDIA |
| `ranking_fabricantes` | ~3 | 🟡 BAIXO | 🟢 BAIXA |

---

## 🎯 Estratégia de Implementação

### Fase 1: Quick Wins (Semana 1) - Meta: 20% cobertura
**Objetivo:** Implementar queries simples com alto impacto

#### 1.1 Ranking Geral (`ranking_geral`)
- **Esforço:** 2-3 horas
- **Impacto:** ~8 perguntas
- **Implementação:**
  ```python
  def _query_ranking_geral(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
      """Rankings genéricos (produtos, UNEs, segmentos)"""
      # Detectar tipo de ranking pela query original
      # Retornar top N com gráfico de barras
  ```

#### 1.2 Consulta UNE Específica (`consulta_une_especifica`)
- **Esforço:** 1-2 horas
- **Impacto:** ~4 perguntas
- **Status:** Método existe mas está com fallback
- **Ação:** Revisar e corrigir implementação existente

#### 1.3 Ranking Fabricantes (`ranking_fabricantes`)
- **Esforço:** 2 horas
- **Impacto:** ~3 perguntas
- **Implementação:**
  ```python
  def _query_ranking_fabricantes(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
      """Top N fabricantes por volume de vendas"""
      # Agrupar por nome_fabricante
      # Somar vendas_total
      # Retornar chart_data
  ```

**📊 Resultado Fase 1:** +15 perguntas cobertas = ~20% total

---

### Fase 2: Análises Essenciais (Semana 2) - Meta: 35% cobertura

#### 2.1 Comparação de Segmentos (`comparacao_segmentos`)
- **Esforço:** 3-4 horas
- **Impacto:** ~3 perguntas
- **Implementação:**
  ```python
  def _query_comparacao_segmentos(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
      """Compara vendas entre 2+ segmentos"""
      segmentos = params.get('segmentos', [])
      # Filtrar por segmentos
      # Agrupar e comparar
      # Retornar comparison chart
  ```

#### 2.2 Análise ABC (`analise_abc`)
- **Esforço:** 4-5 horas
- **Impacto:** ~4 perguntas
- **Implementação:**
  ```python
  def _query_analise_abc(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
      """Classificação ABC de produtos"""
      # Usar coluna abc_une_mes_01 (ou calcular)
      # Filtrar por classe se especificado
      # Retornar distribuição ou produtos por classe
  ```

#### 2.3 Estoque Básico (`estoque_alto`, `produtos_reposicao`)
- **Esforço:** 3 horas
- **Impacto:** ~2 perguntas
- **Implementação:**
  ```python
  def _query_estoque_alto(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
      """Produtos com excesso de estoque"""
      # Comparar estoque_atual vs vendas médias
      # Retornar produtos com ratio > threshold
  ```

**📊 Resultado Fase 2:** +9 perguntas = ~35% total

---

### Fase 3: Análise Geral Inteligente (Semana 3) - Meta: 65%+ cobertura

#### 3.1 Sistema de Roteamento `analise_geral`
- **Esforço:** 6-8 horas
- **Impacto:** 🔴 **47 perguntas** (maior impacto!)
- **Estratégia:**
  - `analise_geral` é um "catch-all" muito genérico
  - Implementar sistema de sub-classificação inteligente
  - Rotear para queries específicas baseado em keywords

**Implementação:**
```python
def _query_analise_geral(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Router inteligente para análises genéricas"""

    # Pegar query original do usuário
    user_query = params.get('user_query', '').lower()

    # Sub-classificação por keywords
    if 'abc' in user_query:
        return self._query_analise_abc(df, params)

    elif 'sazonalidade' in user_query or 'sazonal' in user_query:
        return self._query_sazonalidade(df, params)

    elif 'crescimento' in user_query:
        return self._query_crescimento_segmento(df, params)

    elif 'concentração' in user_query or 'dependência' in user_query:
        return self._query_concentracao(df, params)

    elif 'penetração' in user_query:
        return self._query_penetracao(df, params)

    elif 'diversidade' in user_query:
        return self._query_diversidade_produtos(df, params)

    # Se não conseguir classificar, fallback
    else:
        return self._query_fallback(user_query)
```

**📊 Resultado Fase 3:** +47 perguntas = ~65% total

---

### Fase 4: Análises Avançadas (Semana 4) - Meta: 80%+ cobertura

#### 4.1 Análises Temporais
- `sazonalidade` - Detectar padrões sazonais
- `tendencia_vendas` - Calcular tendências
- `pico_vendas` - Identificar picos
- **Esforço:** 8-10 horas total
- **Impacto:** ~8 perguntas

#### 4.2 Análises de Estoque Avançadas
- `rotacao_estoque` - Calcular giro de estoque
- `vendas_produto_une` - Vendas produto+UNE específicos
- **Esforço:** 4-5 horas
- **Impacto:** ~3 perguntas

#### 4.3 Evolução e Crescimento
- `evolucao_mes_a_mes` - Evolução temporal
- `crescimento_segmento` - Taxa de crescimento
- **Esforço:** 5 horas
- **Impacto:** ~4 perguntas

**📊 Resultado Fase 4:** +15 perguntas = ~80% total

---

## 📅 Cronograma Resumido

| Fase | Semana | Queries | Cobertura | Esforço |
|------|--------|---------|-----------|---------|
| **Fase 1** | Semana 1 | 3 queries | ~20% | 6h |
| **Fase 2** | Semana 2 | 3 queries | ~35% | 11h |
| **Fase 3** | Semana 3 | 1 query (router) | ~65% | 8h |
| **Fase 4** | Semana 4 | 7 queries | ~80% | 17h |
| **TOTAL** | 4 semanas | 14 queries | **80%** | **42h** |

---

## 🔧 Estrutura Técnica

### Arquivo Principal
- `core/business_intelligence/direct_query_engine.py`

### Padrão de Implementação
```python
def _query_[nome_query](self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Descrição da query

    Args:
        df: DataFrame com dados
        params: Parâmetros extraídos do classify_intent_direct

    Returns:
        Dict com structure:
        {
            "type": "chart|table|text",
            "title": "Título",
            "result": {...},
            "summary": "Resumo",
            "tokens_used": 0
        }
    """
    # 1. Validar dados
    # 2. Processar/filtrar
    # 3. Calcular métricas
    # 4. Preparar visualização
    # 5. Retornar resultado estruturado
```

### Registro de Queries no Mapa
```python
# No __init__ ou método de setup
self.query_methods = {
    "ranking_geral": self._query_ranking_geral,
    "ranking_fabricantes": self._query_ranking_fabricantes,
    "comparacao_segmentos": self._query_comparacao_segmentos,
    # ... adicionar novas queries
}
```

---

## ✅ Checklist de Implementação

### Para Cada Query:
- [ ] Implementar método `_query_[nome]()`
- [ ] Adicionar ao mapeamento de métodos
- [ ] Criar/atualizar regex pattern em `query_patterns_training.json`
- [ ] Testar com exemplos reais
- [ ] Adicionar logging adequado
- [ ] Documentar no código
- [ ] Atualizar testes

---

## 🎯 Métricas de Sucesso

### Objetivos Mensuráveis
1. **Cobertura:** De 1.3% → 80%+ nas 80 perguntas
2. **Performance:** < 1s para queries diretas (sem LLM)
3. **Tokens:** Redução de 97% no uso de LLM
4. **Precisão:** 95%+ das queries retornam resultado correto

### KPIs por Fase
- **Fase 1:** 20% cobertura, 15 queries funcionando
- **Fase 2:** 35% cobertura, 24 queries funcionando
- **Fase 3:** 65% cobertura, 52 queries funcionando
- **Fase 4:** 80% cobertura, 64+ queries funcionando

---

## 🚀 Próxima Ação Imediata

### FASE 1 - Query 1: `ranking_geral`
**Começar agora:**
1. Criar método `_query_ranking_geral()`
2. Detectar tipo de ranking (produtos/UNEs/segmentos)
3. Implementar top N genérico
4. Testar com perguntas do teste

**Comando para iniciar:**
```bash
# Abrir arquivo
code core/business_intelligence/direct_query_engine.py

# Procurar linha para adicionar método
# Adicionar após outros métodos _query_*
```

---

## 📝 Notas Importantes

1. **Priorizar Fase 3:** O router `analise_geral` tem maior impacto (47 perguntas)
2. **Reusar Código:** Muitas queries compartilham lógica (ranking, agregação)
3. **Testar Incrementalmente:** Executar teste após cada implementação
4. **Documentar:** Adicionar exemplos de perguntas suportadas

---

**Status:** ⏸️ Aguardando aprovação para iniciar Fase 1
**Próximo Milestone:** Implementar 3 queries da Fase 1 (ETA: Semana 1)
