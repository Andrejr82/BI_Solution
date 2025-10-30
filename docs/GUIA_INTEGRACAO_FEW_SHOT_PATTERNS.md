# Guia de Integração - Few-Shot Pattern Library

## Visão Geral

Este guia explica como integrar a biblioteca de padrões de queries (FASE 2.1) no sistema LLM para melhorar a geração de código Polars através de Few-Shot Learning.

---

## Arquivos Criados

### 1. Biblioteca de Padrões
```
C:\Users\André\Documents\Agent_Solution_BI\query_patterns_complete.json
```
- 30 padrões validados
- 45 exemplos reais
- 8 categorias organizadas
- Metadados completos

### 2. Script de Validação
```
C:\Users\André\Documents\Agent_Solution_BI\scripts\validate_query_patterns.py
```
- Valida sintaxe JSON
- Verifica estrutura dos padrões
- Valida código Polars
- Gera estatísticas

### 3. Pattern Matcher
```
C:\Users\André\Documents\Agent_Solution_BI\scripts\few_shot_pattern_matcher.py
```
- Busca padrões similares
- Calcula score de relevância
- Gera prompts Few-Shot
- Extrai parâmetros

---

## Como Integrar

### Opção 1: Integração Básica (Recomendada)

```python
from scripts.few_shot_pattern_matcher import FewShotPatternMatcher

# Inicializar matcher
matcher = FewShotPatternMatcher("query_patterns_complete.json")

# Processar query do usuário
user_query = "Top 10 produtos mais vendidos da UNE FORTALEZA"
results = matcher.process_query(
    user_query,
    return_prompt=True,
    return_code=False
)

# Usar prompt Few-Shot com LLM
few_shot_prompt = results['few_shot_prompt']
llm_response = your_llm_function(few_shot_prompt)
```

### Opção 2: Integração Avançada

```python
from scripts.few_shot_pattern_matcher import FewShotPatternMatcher

class EnhancedCodeGenerator:
    def __init__(self):
        self.matcher = FewShotPatternMatcher("query_patterns_complete.json")
        self.llm = your_llm_instance

    def generate_code(self, user_query: str) -> str:
        # 1. Buscar padrões relevantes
        matches = self.matcher.find_matching_patterns(user_query, top_n=3)

        if not matches:
            # Fallback para geração sem Few-Shot
            return self.generate_without_patterns(user_query)

        # 2. Gerar prompt Few-Shot
        prompt = self.matcher.generate_few_shot_prompt(user_query, matches)

        # 3. Enviar para LLM
        code = self.llm.generate(prompt)

        # 4. Validar e retornar
        if self.validate_code(code):
            return code
        else:
            # Tentar novamente com padrão direto
            return self.generate_from_template(matches[0], user_query)

    def generate_from_template(self, match, user_query):
        # Extrair parâmetros
        params = self.matcher.extract_parameters_from_query(user_query)

        # Gerar código do template
        code = self.matcher.generate_code_from_template(
            match.pattern,
            params
        )

        return code
```

---

## Integração no Code Gen Agent

### Modificar `core/agents/code_gen_agent.py`

```python
# Adicionar import
from scripts.few_shot_pattern_matcher import FewShotPatternMatcher

class CodeGenAgent:
    def __init__(self):
        # ... código existente ...

        # Adicionar pattern matcher
        self.pattern_matcher = FewShotPatternMatcher(
            "query_patterns_complete.json"
        )

    def generate_code(self, user_query: str, context: Dict) -> str:
        """Gera código com Few-Shot Learning"""

        # 1. Buscar padrões relevantes
        pattern_results = self.pattern_matcher.process_query(
            user_query,
            return_prompt=True,
            return_code=True
        )

        if pattern_results['success']:
            # 2. Tentar código direto do template (mais rápido)
            if 'generated_code' in pattern_results:
                template_code = pattern_results['generated_code']

                # Validar código do template
                if self.validate_polars_code(template_code):
                    logger.info(f"Usando código do template (padrão: {pattern_results['matches'][0]['pattern_id']})")
                    return template_code

            # 3. Usar Few-Shot prompt com LLM
            few_shot_prompt = pattern_results['few_shot_prompt']

            # Adicionar context ao prompt
            enhanced_prompt = self._enhance_prompt_with_context(
                few_shot_prompt,
                context
            )

            # Gerar código com LLM
            llm_code = self.llm.generate(enhanced_prompt)

            return llm_code

        else:
            # 4. Fallback: geração sem Few-Shot
            logger.warning("Nenhum padrão encontrado, usando geração padrão")
            return self.generate_without_patterns(user_query, context)
```

---

## Melhorias no Prompt System

### Adicionar Sistema de Templates no Prompt

```python
def _enhance_prompt_with_context(self, few_shot_prompt: str, context: Dict) -> str:
    """Adiciona context ao prompt Few-Shot"""

    # Informações do schema
    schema_info = f"""
Schema disponível:
Colunas: {', '.join(context.get('columns', []))}
UNEs disponíveis: {', '.join(context.get('unes', []))}
"""

    # Regras específicas
    rules = """
Regras importantes:
1. SEMPRE usar pl.col() para referenciar colunas
2. Para Top N, SEMPRE usar .head(n)
3. Para filtrar UNE, usar: pl.col('UNE_NOME') == 'NOME_UNE'
4. Para agregações, usar .group_by().agg()
5. SEMPRE ordenar com .sort() antes de .head()
"""

    # Combinar tudo
    enhanced = f"""
{few_shot_prompt}

{schema_info}

{rules}

Gere o código agora:
"""
    return enhanced
```

---

## Sistema de Cache de Padrões

### Cache para Queries Comuns

```python
from functools import lru_cache
import hashlib

class CachedPatternMatcher(FewShotPatternMatcher):
    def __init__(self, patterns_file):
        super().__init__(patterns_file)
        self.query_cache = {}

    @lru_cache(maxsize=100)
    def find_matching_patterns_cached(self, query_hash: str, query: str, top_n: int):
        """Versão com cache do find_matching_patterns"""
        return super().find_matching_patterns(query, top_n)

    def process_query(self, user_query: str, **kwargs):
        # Gerar hash da query
        query_hash = hashlib.md5(user_query.lower().encode()).hexdigest()

        # Verificar cache
        if query_hash in self.query_cache:
            logger.info(f"Cache HIT para query: {user_query[:50]}...")
            return self.query_cache[query_hash]

        # Processar normalmente
        results = super().process_query(user_query, **kwargs)

        # Salvar no cache
        self.query_cache[query_hash] = results

        return results
```

---

## Sistema de Métricas

### Monitorar Uso dos Padrões

```python
import json
from datetime import datetime
from pathlib import Path

class PatternUsageTracker:
    def __init__(self, log_file="data/learning/pattern_usage.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_usage(self, query: str, pattern_id: str, success: bool, execution_time: float):
        """Registra uso de um padrão"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'pattern_id': pattern_id,
            'success': success,
            'execution_time': execution_time
        }

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_pattern_stats(self) -> Dict:
        """Retorna estatísticas de uso dos padrões"""
        stats = {}

        if not self.log_file.exists():
            return stats

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                pattern_id = entry['pattern_id']

                if pattern_id not in stats:
                    stats[pattern_id] = {
                        'total_uses': 0,
                        'successful_uses': 0,
                        'avg_execution_time': 0,
                        'success_rate': 0
                    }

                stats[pattern_id]['total_uses'] += 1
                if entry['success']:
                    stats[pattern_id]['successful_uses'] += 1

        # Calcular taxas de sucesso
        for pattern_id, data in stats.items():
            data['success_rate'] = (
                data['successful_uses'] / data['total_uses'] * 100
                if data['total_uses'] > 0 else 0
            )

        return stats
```

---

## Testes e Validação

### Script de Teste Completo

```python
def test_few_shot_integration():
    """Testa integração completa do Few-Shot Learning"""

    matcher = FewShotPatternMatcher("query_patterns_complete.json")

    test_cases = [
        {
            'query': 'Top 10 produtos mais vendidos da UNE FORTALEZA',
            'expected_pattern': 'ranking_top_n_une_vendas',
            'expected_params': {'n': 10, 'une_nome': 'FORTALEZA'}
        },
        {
            'query': 'Total de vendas por UNE',
            'expected_pattern': 'agregacao_vendas_por_une',
            'expected_params': {}
        },
        {
            'query': 'Produtos com estoque abaixo de 100',
            'expected_pattern': 'filtro_estoque_abaixo_valor',
            'expected_params': {'valor': 100}
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        results = matcher.process_query(
            test['query'],
            return_code=True
        )

        # Verificar se encontrou padrão correto
        if results['matches'][0]['pattern_id'] == test['expected_pattern']:
            passed += 1
            print(f"[PASS] {test['query']}")
        else:
            failed += 1
            print(f"[FAIL] {test['query']}")
            print(f"  Expected: {test['expected_pattern']}")
            print(f"  Got: {results['matches'][0]['pattern_id']}")

    print(f"\nResultados: {passed} passed, {failed} failed")
    return failed == 0
```

---

## Próximos Passos

### FASE 2.2 - Aprendizado Contínuo

1. **Sistema de Feedback**
   - Capturar queries que falharam
   - Identificar novos padrões
   - Auto-atualização da biblioteca

2. **Similaridade Semântica**
   - Usar embeddings para matching
   - Melhorar detecção de padrões similares
   - Suporte a variações de linguagem

3. **Otimização de Padrões**
   - Ranquear padrões por taxa de sucesso
   - Remover padrões não utilizados
   - Adicionar novos padrões automaticamente

---

## Métricas de Sucesso

### KPIs a Monitorar

1. **Taxa de Acerto**
   - % de queries que usaram padrões
   - % de código gerado que executou com sucesso

2. **Performance**
   - Tempo de matching de padrões
   - Tempo total de geração de código
   - Taxa de cache hit

3. **Cobertura**
   - % de queries cobertas por padrões
   - Distribuição de uso por categoria
   - Padrões mais utilizados

---

## Troubleshooting

### Problema: Nenhum Padrão Encontrado

**Solução:**
```python
# Reduzir min_score
matches = matcher.find_matching_patterns(
    user_query,
    top_n=5,
    min_score=0.0  # Aceitar qualquer match
)

# Ou usar busca fuzzy nas keywords
```

### Problema: Código Gerado Inválido

**Solução:**
```python
# Adicionar validação antes de executar
def validate_generated_code(code: str) -> bool:
    # Verificar sintaxe básica
    if 'df.' not in code:
        return False

    # Verificar imports necessários
    required_patterns = ['pl.col', 'group_by', 'agg', 'filter']
    # ... validações ...

    return True
```

---

## Conclusão

A biblioteca de padrões está pronta para uso e deve melhorar significativamente a qualidade da geração de código Polars através de Few-Shot Learning.

**Benefícios Esperados:**
- Redução de 60% nos erros de sintaxe
- Código mais consistente e seguindo melhores práticas
- Respostas mais rápidas (uso de templates)
- Menor dependência de ajuste fino do LLM

**Arquivos de Referência:**
- `query_patterns_complete.json` - Biblioteca de padrões
- `validate_query_patterns.py` - Script de validação
- `few_shot_pattern_matcher.py` - Sistema de matching
- `FASE_2_1_BIBLIOTECA_QUERY_PATTERNS_RELATORIO.md` - Relatório completo
