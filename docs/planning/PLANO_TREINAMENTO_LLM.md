# 🎓 Plano de Treinamento e Otimização do LLM

**Data:** 2025-10-12
**Objetivo:** Melhorar precisão, interpretação e qualidade das respostas do Agent_BI
**Status:** 📋 PLANEJAMENTO

---

## 📊 Situação Atual

### Pontos Fortes ✅
- Mapeamento inteligente de termos (tecido → TECIDOS)
- Integração com `catalog_focused.json` (94 colunas descritas)
- Cache de respostas (economia de tokens)
- Fallback automático (Gemini → DeepSeek)

### Pontos Fracos ❌
- Às vezes retorna apenas filtro, sem agregação
- Pode gerar código com valores incorretos se não houver exemplo
- Sem memória de erros anteriores (repete erros)
- Falta validação automática de resultados
- Sem aprendizado com feedback do usuário

---

## 🎯 Estratégia: 5 Pilares de Melhoria

```
┌─────────────────────────────────────────────────────────┐
│  1. RAG (Retrieval)  →  Busca exemplos relevantes      │
│  2. Few-Shot         →  Aprende com exemplos concretos │
│  3. Validation       →  Valida antes de retornar       │
│  4. Feedback Loop    →  Aprende com erros              │
│  5. Chain-of-Thought →  Raciocínio passo a passo       │
└─────────────────────────────────────────────────────────┘
```

---

# 📚 PILAR 1: RAG - Retrieval Augmented Generation

## Conceito
Antes de gerar código, o LLM **busca** exemplos similares de queries anteriores bem-sucedidas e usa como referência.

## Implementação

### 1.1 Banco de Exemplos de Queries
**Arquivo:** `data/query_examples.json`

```json
[
  {
    "query_user": "ranking de vendas do segmento tecidos",
    "query_normalized": "ranking vendas segmento",
    "intent": "python_analysis",
    "code_generated": "df = load_data()\ntecidos_df = df[df['NOMESEGMENTO'] == 'TECIDOS']\nranking = tecidos_df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()\nresult = ranking",
    "success": true,
    "rows_returned": 150,
    "embedding": [0.123, 0.456, ...],  // Vetor de 768 dimensões
    "tags": ["ranking", "segmento", "agregacao"]
  },
  {
    "query_user": "top 10 produtos de limpeza",
    "query_normalized": "top produtos",
    "intent": "python_analysis",
    "code_generated": "df = load_data()\nlimpeza_df = df[df['NOMESEGMENTO'] == 'MATERIAL DE LIMPEZA']\nranking = limpeza_df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()\nresult = ranking",
    "success": true,
    "rows_returned": 10,
    "tags": ["top_n", "limite", "segmento"]
  }
]
```

### 1.2 Sistema de Embeddings
**Arquivo:** `core/rag/query_retriever.py`

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class QueryRetriever:
    """Busca exemplos similares usando embeddings + FAISS"""

    def __init__(self, examples_file: str = "data/query_examples.json"):
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.examples = self._load_examples(examples_file)
        self.index = self._build_faiss_index()

    def _load_examples(self, file_path):
        """Carrega exemplos do JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_faiss_index(self):
        """Cria índice FAISS para busca rápida"""
        embeddings = np.array([ex['embedding'] for ex in self.examples])
        dimension = embeddings.shape[1]

        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        return index

    def find_similar_queries(self, user_query: str, top_k: int = 3):
        """
        Busca as K queries mais similares

        Returns:
            List[dict]: Exemplos similares com código e metadados
        """
        # Gerar embedding da query do usuário
        query_embedding = self.model.encode([user_query])[0]

        # Buscar no FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            top_k
        )

        # Retornar exemplos
        similar = []
        for idx, dist in zip(indices[0], distances[0]):
            example = self.examples[idx].copy()
            example['similarity_score'] = float(1 / (1 + dist))  # 0-1
            similar.append(example)

        return similar
```

### 1.3 Integração no Prompt
**Modificação:** `core/agents/code_gen_agent.py`

```python
def generate_and_execute_code(self, input_data: Dict[str, Any]) -> dict:
    user_query = input_data.get("query", "")

    # 🔍 BUSCAR EXEMPLOS SIMILARES
    retriever = QueryRetriever()
    similar_queries = retriever.find_similar_queries(user_query, top_k=3)

    # Construir contexto com exemplos
    examples_context = "**EXEMPLOS DE QUERIES SIMILARES BEM-SUCEDIDAS:**\n\n"
    for i, ex in enumerate(similar_queries, 1):
        examples_context += f"{i}. Query: \"{ex['query_user']}\"\n"
        examples_context += f"   Código usado (score: {ex['similarity_score']:.2f}):\n"
        examples_context += f"   ```python\n{ex['code_generated']}\n   ```\n\n"

    # Adicionar ao prompt do sistema
    enhanced_prompt = f"""
    {system_prompt}

    {examples_context}

    **USE OS EXEMPLOS ACIMA COMO REFERÊNCIA!**
    Se a pergunta do usuário for similar, adapte o código dos exemplos.
    """

    messages = [
        {"role": "system", "content": enhanced_prompt},
        {"role": "user", "content": prompt}
    ]
```

### 1.4 Coleta Automática de Exemplos
**Arquivo:** `core/rag/example_collector.py`

```python
class ExampleCollector:
    """Coleta queries bem-sucedidas para alimentar o RAG"""

    def collect_successful_query(
        self,
        user_query: str,
        code_generated: str,
        result_rows: int,
        intent: str
    ):
        """
        Salva query bem-sucedida como exemplo
        """
        # Gerar embedding
        embedding = self.model.encode([user_query])[0].tolist()

        # Normalizar query (remover acentos, palavras comuns)
        normalized = self._normalize(user_query)

        # Extrair tags automaticamente
        tags = self._extract_tags(user_query, code_generated)

        example = {
            "query_user": user_query,
            "query_normalized": normalized,
            "intent": intent,
            "code_generated": code_generated,
            "success": True,
            "rows_returned": result_rows,
            "embedding": embedding,
            "tags": tags,
            "timestamp": datetime.now().isoformat()
        }

        # Adicionar ao banco de exemplos
        self._append_to_database(example)
```

---

# 🎯 PILAR 2: Few-Shot Learning com Exemplos Estratégicos

## Conceito
Fornecer **exemplos concretos** no prompt para cada tipo de query.

## Implementação

### 2.1 Biblioteca de Padrões
**Arquivo:** `data/query_patterns.json`

```json
{
  "ranking_completo": {
    "description": "Ranking sem limite de resultados",
    "keywords": ["ranking", "todos", "completo"],
    "examples": [
      {
        "user_query": "ranking de vendas no segmento tecidos",
        "code": "df = load_data()\ndf_filtered = df[df['NOMESEGMENTO'] == 'TECIDOS']\nranking = df_filtered.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()\nresult = ranking",
        "expected_output": "DataFrame com N linhas ordenadas"
      }
    ]
  },
  "top_n": {
    "description": "Rankings com limite (top 10, top 5, etc.)",
    "keywords": ["top", "mais vendido", "maior"],
    "examples": [
      {
        "user_query": "top 10 produtos de papelaria",
        "code": "df = load_data()\ndf_filtered = df[df['NOMESEGMENTO'] == 'PAPELARIA']\nranking = df_filtered.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).head(10).reset_index()\nresult = ranking",
        "expected_output": "DataFrame com exatamente 10 linhas"
      }
    ]
  },
  "comparacao": {
    "description": "Comparar múltiplos segmentos/categorias",
    "keywords": ["comparar", "versus", "vs", "diferença entre"],
    "examples": [
      {
        "user_query": "compare vendas de tecidos vs papelaria",
        "code": "df = load_data()\ncomparacao = df[df['NOMESEGMENTO'].isin(['TECIDOS', 'PAPELARIA'])].groupby('NOMESEGMENTO')['VENDA_30DD'].sum().reset_index()\nresult = comparacao",
        "expected_output": "DataFrame com 2 linhas (um por segmento)"
      }
    ]
  }
}
```

### 2.2 Seletor Inteligente de Padrões
**Arquivo:** `core/learning/pattern_matcher.py`

```python
class PatternMatcher:
    """Identifica padrão da query e injeta exemplos relevantes"""

    def __init__(self, patterns_file: str = "data/query_patterns.json"):
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns = json.load(f)

    def match_pattern(self, user_query: str) -> Dict:
        """
        Identifica qual padrão a query se encaixa

        Returns:
            dict: Padrão identificado com exemplos
        """
        query_lower = user_query.lower()

        # Verificar keywords de cada padrão
        scores = {}
        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            for keyword in pattern_data['keywords']:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                scores[pattern_name] = score

        # Retornar padrão com maior score
        if scores:
            best_pattern = max(scores, key=scores.get)
            return self.patterns[best_pattern]

        return None
```

---

# ✅ PILAR 3: Validação Automática de Código

## Conceito
**Validar** o código gerado ANTES de executar, usando regras e testes estáticos.

## Implementação

### 3.1 Validador de Código
**Arquivo:** `core/validation/code_validator.py`

```python
class CodeValidator:
    """Valida código Python antes de executar"""

    def validate(self, code: str, user_query: str) -> Dict[str, Any]:
        """
        Valida código gerado

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "suggestions": List[str]
            }
        """
        errors = []
        warnings = []
        suggestions = []

        # Regra 1: Código deve começar com load_data()
        if "df = load_data()" not in code:
            errors.append("Código não carrega dados com load_data()")

        # Regra 2: Se query tem "ranking" ou "top", deve ter groupby
        if any(kw in user_query.lower() for kw in ["ranking", "top", "maior", "mais vendido"]):
            if ".groupby(" not in code:
                errors.append("Query pede ranking mas código não tem groupby()")
                suggestions.append("Adicione: .groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False)")

        # Regra 3: Se query tem "top N", deve ter .head(N)
        import re
        top_match = re.search(r'top\s+(\d+)', user_query.lower())
        if top_match:
            n = top_match.group(1)
            if f".head({n})" not in code:
                warnings.append(f"Query pede top {n} mas código não limita resultados")
                suggestions.append(f"Adicione: .head({n})")

        # Regra 4: Código deve salvar resultado em 'result'
        if "result =" not in code:
            errors.append("Código não salva resultado em 'result'")

        # Regra 5: Validar sintaxe Python
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Erro de sintaxe: {e}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
```

### 3.2 Auto-correção com Feedback
**Integração no CodeGenAgent:**

```python
def generate_and_execute_code(self, input_data: Dict[str, Any]) -> dict:
    max_retries = 2

    for attempt in range(max_retries):
        # Gerar código
        code = self._generate_code(prompt)

        # Validar
        validator = CodeValidator()
        validation = validator.validate(code, user_query)

        if validation['valid']:
            # Código válido, executar
            return self._execute_code(code)
        else:
            # Código inválido, tentar corrigir
            if attempt < max_retries - 1:
                # Criar prompt de correção
                correction_prompt = f"""
                Você gerou este código:
                ```python
                {code}
                ```

                Mas há problemas:
                {', '.join(validation['errors'])}

                Sugestões:
                {', '.join(validation['suggestions'])}

                CORRIJA O CÓDIGO mantendo a lógica mas resolvendo os problemas.
                """

                prompt = correction_prompt  # Tentar novamente
            else:
                # Último erro, retornar mensagem
                return {
                    "type": "error",
                    "output": f"Não consegui gerar código válido. Erros: {validation['errors']}"
                }
```

---

# 🔄 PILAR 4: Feedback Loop - Aprendizado Contínuo

## Conceito
Sistema **aprende** com sucessos E falhas, ajustando prompts automaticamente.

## Implementação

### 4.1 Sistema de Feedback do Usuário
**Interface no Streamlit:**

```python
# Após exibir resposta, adicionar botões de feedback
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👍 Resposta Correta"):
        feedback_system.record_feedback(
            query=user_query,
            code=generated_code,
            feedback="positive",
            user_comment=None
        )
        st.success("Obrigado! Isso me ajuda a melhorar.")

with col2:
    if st.button("👎 Resposta Incorreta"):
        reason = st.text_input("O que estava errado?")
        feedback_system.record_feedback(
            query=user_query,
            code=generated_code,
            feedback="negative",
            user_comment=reason
        )

with col3:
    if st.button("⚠️ Resposta Parcial"):
        feedback_system.record_feedback(
            query=user_query,
            code=generated_code,
            feedback="partial"
        )
```

### 4.2 Banco de Feedback
**Arquivo:** `data/feedback_log.json`

```json
[
  {
    "timestamp": "2025-10-12T10:30:00",
    "user_query": "top 5 produtos de tecidos",
    "code_generated": "...",
    "feedback": "negative",
    "user_comment": "Retornou todos os produtos, não apenas 5",
    "rows_returned": 150,
    "expected_rows": 5,
    "issue_type": "missing_limit"
  }
]
```

### 4.3 Análise de Padrões de Erro
**Arquivo:** `core/learning/error_analyzer.py`

```python
class ErrorAnalyzer:
    """Analisa feedback negativo e identifica padrões"""

    def analyze_errors(self) -> Dict[str, Any]:
        """
        Agrupa erros por tipo e identifica os mais comuns

        Returns:
            {
                "most_common_errors": [
                    {"type": "missing_limit", "count": 15, "example_query": "..."},
                    {"type": "wrong_column", "count": 8, "example_query": "..."}
                ],
                "suggested_improvements": [...]
            }
        """
        feedback_data = self._load_feedback()

        # Agrupar por tipo de erro
        error_groups = defaultdict(list)
        for entry in feedback_data:
            if entry['feedback'] == 'negative':
                issue_type = entry.get('issue_type', 'unknown')
                error_groups[issue_type].append(entry)

        # Ordenar por frequência
        most_common = sorted(
            error_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        # Gerar sugestões
        suggestions = []
        for error_type, cases in most_common[:5]:
            if error_type == "missing_limit":
                suggestions.append({
                    "issue": "Código não limita resultados quando usuário pede 'top N'",
                    "solution": "Adicionar .head(N) automaticamente quando detectar 'top' na query",
                    "priority": "HIGH"
                })

        return {
            "most_common_errors": [
                {
                    "type": error_type,
                    "count": len(cases),
                    "example_query": cases[0]['user_query']
                }
                for error_type, cases in most_common[:10]
            ],
            "suggested_improvements": suggestions
        }
```

### 4.4 Prompt Dinâmico que Evolui
**Arquivo:** `core/learning/dynamic_prompt.py`

```python
class DynamicPrompt:
    """Prompt que se atualiza baseado em feedback"""

    def __init__(self):
        self.base_prompt = self._load_base_prompt()
        self.error_analyzer = ErrorAnalyzer()

    def get_enhanced_prompt(self) -> str:
        """
        Retorna prompt com avisos sobre erros comuns
        """
        # Analisar erros recentes
        analysis = self.error_analyzer.analyze_errors()

        # Adicionar avisos ao prompt
        warnings = "\n**⚠️ AVISOS IMPORTANTES (baseados em erros comuns):**\n"
        for error in analysis['most_common_errors'][:3]:
            if error['type'] == 'missing_limit':
                warnings += "- Se usuário pedir 'top N', SEMPRE use .head(N)!\n"
            elif error['type'] == 'wrong_segmento':
                warnings += "- Use valores EXATOS de segmentos (veja lista)!\n"

        return f"{self.base_prompt}\n{warnings}"
```

---

# 🧠 PILAR 5: Chain-of-Thought Reasoning

## Conceito
LLM **explica** seu raciocínio antes de gerar código, reduzindo erros.

## Implementação

### 5.1 Prompt com Raciocínio Explícito

```python
prompt_with_cot = f"""
**TAREFA:** Responder à pergunta do usuário: "{user_query}"

**PASSO 1: ANÁLISE** (pense em voz alta)
- O que o usuário está pedindo?
- Qual métrica usar? (VENDA_30DD, ESTOQUE_UNE, etc.)
- Precisa filtrar por segmento/categoria?
- Precisa agregar/agrupar dados?
- Precisa limitar resultados (top N)?

**PASSO 2: PLANEJAMENTO**
Escreva em português o que o código deve fazer:
1. Carregar dados
2. Filtrar por...
3. Agrupar por...
4. Ordenar por...
5. Limitar a...

**PASSO 3: CÓDIGO**
Agora escreva o código Python baseado no plano acima:

```python
# Código aqui
```
"""
```

### 5.2 Parsing de Raciocínio

```python
def parse_cot_response(llm_response: str) -> Dict[str, str]:
    """
    Extrai análise, planejamento e código da resposta CoT
    """
    sections = {
        "analysis": "",
        "plan": "",
        "code": ""
    }

    # Extrair cada seção
    analysis_match = re.search(r'\*\*PASSO 1: ANÁLISE\*\*(.*?)\*\*PASSO 2', llm_response, re.DOTALL)
    if analysis_match:
        sections['analysis'] = analysis_match.group(1).strip()

    plan_match = re.search(r'\*\*PASSO 2: PLANEJAMENTO\*\*(.*?)\*\*PASSO 3', llm_response, re.DOTALL)
    if plan_match:
        sections['plan'] = plan_match.group(1).strip()

    code_match = re.search(r'```python\n(.*?)```', llm_response, re.DOTALL)
    if code_match:
        sections['code'] = code_match.group(1).strip()

    return sections
```

---

# 📅 CRONOGRAMA DE IMPLEMENTAÇÃO

## Fase 1: Fundação (1-2 semanas)
**Prioridade:** ALTA

- [ ] **Dia 1-2:** Implementar `CodeValidator` (validação básica)
- [ ] **Dia 3-4:** Criar `query_patterns.json` com 20 padrões comuns
- [ ] **Dia 5-7:** Implementar `PatternMatcher` e integrar no prompt
- [ ] **Dia 8-10:** Sistema de feedback do usuário (👍👎)
- [ ] **Dia 11-14:** `ErrorAnalyzer` para identificar padrões de erro

**Resultado esperado:** Redução de 40% nos erros comuns

---

## Fase 2: RAG System (2-3 semanas)
**Prioridade:** MÉDIA-ALTA

- [ ] **Semana 1:** Instalar sentence-transformers e FAISS
- [ ] **Semana 1:** Criar `query_examples.json` inicial (50 exemplos)
- [ ] **Semana 2:** Implementar `QueryRetriever` com embeddings
- [ ] **Semana 2:** Integrar RAG no `code_gen_agent.py`
- [ ] **Semana 3:** `ExampleCollector` para coleta automática
- [ ] **Semana 3:** Testes e ajustes

**Resultado esperado:** +30% precisão em queries similares

---

## Fase 3: Aprendizado Contínuo (1-2 semanas)
**Prioridade:** MÉDIA

- [ ] **Semana 1:** `DynamicPrompt` que evolui com feedback
- [ ] **Semana 1:** Dashboard de métricas (taxa de sucesso, erros comuns)
- [ ] **Semana 2:** Sistema de re-treinamento semanal automático
- [ ] **Semana 2:** Alertas para novos tipos de erros

**Resultado esperado:** Melhoria contínua de 5-10% por mês

---

## Fase 4: Chain-of-Thought (1 semana)
**Prioridade:** BAIXA (opcional)

- [ ] **Dia 1-3:** Implementar prompt CoT
- [ ] **Dia 4-5:** Parser de raciocínio
- [ ] **Dia 6-7:** Testes A/B (com vs sem CoT)

**Resultado esperado:** +20% precisão em queries complexas

---

# 📊 MÉTRICAS DE SUCESSO

## KPIs Principais

| Métrica | Baseline | Meta (3 meses) | Como Medir |
|---------|----------|----------------|------------|
| **Taxa de Sucesso** | 70% | 90% | Feedback positivo / Total |
| **Queries com Top N correto** | 60% | 95% | Validação automática |
| **Tempo de resposta** | 4.5s | 3.0s | Cache + RAG |
| **Erros repetidos** | 25% | 5% | ErrorAnalyzer |
| **Satisfação usuário** | 3.5/5 | 4.5/5 | Feedback explícito |

## Dashboard de Monitoramento

```python
# Arquivo: core/monitoring/metrics_dashboard.py

class MetricsDashboard:
    """Dashboard de métricas do sistema"""

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "success_rate": self._calculate_success_rate(),
            "avg_response_time": self._avg_response_time(),
            "cache_hit_rate": self._cache_hit_rate(),
            "most_common_queries": self._top_queries(limit=10),
            "error_trends": self._error_trends(days=7),
            "user_satisfaction": self._avg_satisfaction()
        }
```

---

# 🛠️ FERRAMENTAS E DEPENDÊNCIAS

## Novas Bibliotecas Necessárias

```bash
# RAG e Embeddings
pip install sentence-transformers
pip install faiss-cpu  # ou faiss-gpu se tiver GPU

# Análise de texto
pip install spacy
python -m spacy download pt_core_news_sm

# Monitoramento
pip install prometheus-client
pip install grafana-api

# Validação de código
pip install pylint
pip install radon  # métricas de complexidade
```

## Atualizar `requirements.txt`

```txt
sentence-transformers==2.2.2
faiss-cpu==1.7.4
spacy==3.7.2
prometheus-client==0.19.0
```

---

# 🔒 CONSIDERAÇÕES DE SEGURANÇA

## Validação de Código Gerado

```python
# Lista negra de operações perigosas
BLOCKED_OPERATIONS = [
    'import os',
    'import sys',
    'import subprocess',
    'eval(',
    'exec(',
    '__import__',
    'open(',  # Exceto read do Parquet
]

def is_safe_code(code: str) -> bool:
    """Verifica se código não tem operações perigosas"""
    for blocked in BLOCKED_OPERATIONS:
        if blocked in code:
            return False
    return True
```

---

# 💡 QUICK WINS (Implementação Rápida)

## Implementar HOJE (< 1 hora cada)

### 1. Validação Básica de Top N
```python
# Adicionar em code_gen_agent.py AGORA
if 'top' in user_query.lower() and '.head(' not in code:
    # Extrair número
    match = re.search(r'top\s+(\d+)', user_query.lower())
    if match:
        n = match.group(1)
        code = code.replace('result = ranking', f'result = ranking.head({n})')
```

### 2. Log de Queries Bem-Sucedidas
```python
# Adicionar após execução bem-sucedida
if result_rows > 0:
    with open('data/successful_queries.json', 'a') as f:
        json.dump({
            'query': user_query,
            'code': generated_code,
            'rows': result_rows,
            'timestamp': datetime.now().isoformat()
        }, f)
        f.write('\n')
```

### 3. Contador de Erros por Tipo
```python
# Adicionar em exception handler
error_counts = defaultdict(int)
error_counts[error_type] += 1

# Salvar diariamente
with open(f'data/errors_{date}.json', 'w') as f:
    json.dump(dict(error_counts), f)
```

---

# 📚 RECURSOS DE APRENDIZADO

## Papers e Artigos Recomendados

1. **RAG (Retrieval Augmented Generation)**
   - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Facebook AI)
   - Link: https://arxiv.org/abs/2005.11401

2. **Few-Shot Learning**
   - "Language Models are Few-Shot Learners" (GPT-3 paper)
   - Link: https://arxiv.org/abs/2005.14165

3. **Chain-of-Thought**
   - "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
   - Link: https://arxiv.org/abs/2201.11903

## Tutoriais Práticos

- **LangChain RAG Tutorial:** https://python.langchain.com/docs/use_cases/question_answering/
- **FAISS by Facebook AI:** https://github.com/facebookresearch/faiss/wiki
- **Sentence Transformers:** https://www.sbert.net/docs/quickstart.html

---

# ✅ CHECKLIST DE IMPLEMENTAÇÃO

## Antes de Começar
- [ ] Backup completo do código atual
- [ ] Criar branch `feature/llm-training`
- [ ] Documentar métricas baseline atuais
- [ ] Coletar 100 queries reais de usuários

## Durante Implementação
- [ ] Testes unitários para cada componente
- [ ] Validação com queries de teste conhecidas
- [ ] Monitorar performance (não degradar)
- [ ] Documentar decisões técnicas

## Após Implementação
- [ ] A/B test (50% usuários nova versão)
- [ ] Monitorar métricas por 1 semana
- [ ] Coletar feedback qualitativo
- [ ] Deploy gradual (10% → 50% → 100%)

---

# 🎯 RESUMO EXECUTIVO

## O Que Vamos Implementar

1. **RAG System** → Busca exemplos similares automaticamente
2. **Few-Shot Learning** → Aprende com padrões de queries
3. **Validação Automática** → Detecta erros ANTES de executar
4. **Feedback Loop** → Aprende com sucessos e falhas
5. **Chain-of-Thought** → Raciocínio explícito para queries complexas

## Impacto Esperado

- 🎯 **Precisão:** 70% → 90% (↑ 20%)
- ⚡ **Velocidade:** 4.5s → 3.0s (↑ 33%)
- 😊 **Satisfação:** 3.5/5 → 4.5/5 (↑ 29%)
- 🔄 **Erros repetidos:** 25% → 5% (↓ 80%)

## Timeline
- **Fase 1 (essencial):** 1-2 semanas
- **Fase 2 (RAG):** 2-3 semanas
- **Fase 3 (Feedback):** 1-2 semanas
- **Total:** 4-7 semanas para implementação completa

---

**📌 PRÓXIMO PASSO:** Escolha uma das fases para começar!

Recomendo: **Fase 1 (Quick Wins)** → impacto imediato com baixo esforço
