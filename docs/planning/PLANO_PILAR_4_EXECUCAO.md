# Plano de Execução - Pilar 4: Análise de Logs e Métricas

**Data:** 2025-10-18
**Estimativa:** 2-3 horas
**Estratégia:** Subagentes com tarefas atômicas

---

## 🎯 Objetivo

Implementar sistema de análise de logs e métricas que:
1. Agrupa erros por tipo
2. Gera sugestões automáticas
3. Atualiza prompt dinamicamente
4. Dashboard de métricas em tempo real

---

## 📋 Tarefas (Ordem de Execução)

### TAREFA 1: ErrorAnalyzer
**Subagente:** code-agent
**Arquivo:** `core/learning/error_analyzer.py`
**Linhas:** ~200
**Tempo:** 45 min

**Especificação:**
```python
class ErrorAnalyzer:
    """Analisa feedback negativo e identifica padrões"""

    def __init__(self, feedback_dir: str = "data/learning"):
        # Carrega feedback de data/learning/feedback_*.jsonl
        pass

    def analyze_errors(self, days: int = 7) -> Dict[str, Any]:
        """
        Retorna:
        {
            "most_common_errors": [
                {"type": "missing_limit", "count": 15, "example": "..."},
                {"type": "wrong_column", "count": 8, "example": "..."}
            ],
            "suggested_improvements": [...]
        }
        """
        pass

    def get_error_types(self) -> List[str]:
        """Lista tipos de erro conhecidos"""
        pass
```

**Validação:**
- Carregar feedback dos últimos 7 dias
- Agrupar por tipo de erro
- Retornar top 5 erros mais comuns

---

### TAREFA 2: DynamicPrompt
**Subagente:** code-agent
**Arquivo:** `core/learning/dynamic_prompt.py`
**Linhas:** ~150
**Tempo:** 45 min

**Especificação:**
```python
class DynamicPrompt:
    """Prompt que evolui baseado em feedback"""

    def __init__(self):
        self.base_prompt = self._load_base_prompt()
        self.error_analyzer = ErrorAnalyzer()

    def get_enhanced_prompt(self) -> str:
        """
        Retorna prompt com avisos sobre erros comuns:

        {base_prompt}

        ⚠️ AVISOS (baseados em erros recentes):
        - Se usuário pedir 'top N', SEMPRE use .head(N)
        - Use valores EXATOS de segmentos
        """
        pass

    def update_prompt(self) -> bool:
        """Atualiza prompt baseado em análise de erros"""
        pass
```

**Validação:**
- Carregar prompt base
- Adicionar avisos de erros comuns
- Atualizar dinamicamente

---

### TAREFA 3: MetricsDashboard
**Subagente:** code-agent
**Arquivo:** `core/monitoring/metrics_dashboard.py`
**Linhas:** ~250
**Tempo:** 1 hora

**Especificação:**
```python
class MetricsDashboard:
    """Dashboard de métricas em tempo real"""

    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Retorna:
        {
            "success_rate": 0.85,
            "avg_response_time": 3.2,
            "cache_hit_rate": 0.45,
            "total_queries": 150,
            "top_queries": [...],
            "error_trend": {...}
        }
        """
        pass

    def get_success_rate(self) -> float:
        """Taxa de sucesso (feedback positivo / total)"""
        pass

    def get_top_queries(self, limit: int = 10) -> List[Dict]:
        """Top N queries mais executadas"""
        pass
```

**Validação:**
- Calcular métricas de data/learning/
- Taxa de sucesso
- Top 10 queries

---

### TAREFA 4: Página Streamlit
**Subagente:** code-agent
**Arquivo:** `pages/05_📊_Metricas.py`
**Linhas:** ~150
**Tempo:** 30 min

**Especificação:**
```python
import streamlit as st
from core.monitoring.metrics_dashboard import MetricsDashboard

st.set_page_config(page_title="Métricas", page_icon="📊")

st.title("📊 Métricas do Sistema")

dashboard = MetricsDashboard()
metrics = dashboard.get_metrics(days=7)

# Layout em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Taxa de Sucesso", f"{metrics['success_rate']:.1%}")

with col2:
    st.metric("Tempo Médio", f"{metrics['avg_response_time']:.1f}s")

# ... resto dos widgets
```

**Validação:**
- Exibir métricas em cards
- Gráficos de tendências
- Top queries

---

### TAREFA 5: Integração
**Subagente:** code-agent
**Arquivo:** `core/agents/code_gen_agent.py`
**Modificação:** Adicionar DynamicPrompt
**Linhas:** ~30
**Tempo:** 30 min

**Especificação:**
```python
# No __init__:
from core.learning.dynamic_prompt import DynamicPrompt
self.dynamic_prompt = DynamicPrompt()

# No generate_and_execute_code:
enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt()
# Usar enhanced_prompt no lugar do prompt estático
```

**Validação:**
- Importar sem erros
- Prompt dinâmico funcionando

---

### TAREFA 6: Testes
**Subagente:** code-agent
**Arquivo:** `tests/test_pilar_4.py`
**Linhas:** ~100
**Tempo:** 30 min

**Especificação:**
```python
def test_error_analyzer():
    analyzer = ErrorAnalyzer()
    analysis = analyzer.analyze_errors(days=7)
    assert "most_common_errors" in analysis
    assert len(analysis["most_common_errors"]) > 0

def test_dynamic_prompt():
    dp = DynamicPrompt()
    prompt = dp.get_enhanced_prompt()
    assert len(prompt) > 0
    assert "AVISOS" in prompt or "base" in prompt

def test_metrics_dashboard():
    dashboard = MetricsDashboard()
    metrics = dashboard.get_metrics(days=7)
    assert "success_rate" in metrics
    assert 0 <= metrics["success_rate"] <= 1
```

---

## 🤖 Estratégia de Subagentes

### Execução em Sequência (SEM paralelismo)
1. **code-agent** → ErrorAnalyzer (isolado)
2. **code-agent** → DynamicPrompt (depende de ErrorAnalyzer)
3. **code-agent** → MetricsDashboard (isolado)
4. **code-agent** → Página Streamlit (depende de MetricsDashboard)
5. **code-agent** → Integração (depende de DynamicPrompt)
6. **code-agent** → Testes (depende de todos)

### Prompt para Cada Subagente

**Template:**
```
Implementar [COMPONENTE] conforme especificação em
docs/planning/PLANO_PILAR_4_EXECUCAO.md TAREFA [N].

Requisitos:
- Seguir EXATAMENTE a estrutura da classe
- Implementar TODOS os métodos especificados
- Adicionar docstrings
- Código completo e funcional
- NÃO adicionar funcionalidades extras

Arquivo: [CAMINHO]
Linhas estimadas: [N]

Use TodoWrite para marcar tarefa como in_progress no início
e completed ao finalizar.
```

---

## 📊 Controle de Tokens

### Tokens Atuais: ~80k / 200k
### Tokens Disponíveis: ~120k

**Estimativa por tarefa:**
- ErrorAnalyzer: ~15k tokens
- DynamicPrompt: ~12k tokens
- MetricsDashboard: ~20k tokens
- Página Streamlit: ~10k tokens
- Integração: ~8k tokens
- Testes: ~10k tokens

**Total estimado:** ~75k tokens
**Margem de segurança:** 45k tokens (37%)

### Estratégia de Compactação
Se tokens > 150k durante execução:
1. Limpar histórico de respostas antigas
2. Focar apenas na tarefa atual
3. Reduzir contexto de arquivos lidos

---

## ✅ Checklist de Validação

Por tarefa:
- [ ] Arquivo criado no caminho correto
- [ ] Classe implementada com todos os métodos
- [ ] Docstrings completas
- [ ] Código sem erros de sintaxe
- [ ] Imports corretos

Final:
- [ ] Todos os arquivos criados
- [ ] Imports funcionando
- [ ] Testes passando
- [ ] Integração funcionando
- [ ] Commit realizado

---

## 🎯 Resultado Esperado

### Arquivos Criados (6)
1. `core/learning/error_analyzer.py`
2. `core/learning/dynamic_prompt.py`
3. `core/monitoring/metrics_dashboard.py`
4. `pages/05_📊_Metricas.py`
5. `tests/test_pilar_4.py`
6. Modificação: `core/agents/code_gen_agent.py`

### Funcionalidades
- ✅ Análise automática de erros
- ✅ Prompt que evolui
- ✅ Dashboard de métricas
- ✅ Sistema integrado

---

**Versão:** 1.0
**Status:** PRONTO PARA EXECUÇÃO
