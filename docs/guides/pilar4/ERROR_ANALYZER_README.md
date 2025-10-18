# ErrorAnalyzer - Implementação Completa

## TAREFA 1 - PILAR 4: APRENDIZADO CONTÍNUO ✓

### Status: IMPLEMENTADO E VALIDADO

---

## Visão Geral

O **ErrorAnalyzer** é um componente de análise de erros que processa feedback armazenado em arquivos JSONL, identifica padrões de erros comuns e gera sugestões de melhoria automaticamente priorizadas.

### Características Principais

- ✓ Análise de erros com filtro por período (dias)
- ✓ Agrupamento automático por tipo de erro
- ✓ Geração de sugestões priorizadas (HIGH/MEDIUM/LOW)
- ✓ Suporte a múltiplos tipos de erro conhecidos
- ✓ Tratamento robusto de exceções
- ✓ Logging completo para debug
- ✓ Formato JSONL para armazenamento eficiente

---

## Instalação

### Passo 1: Executar Script de Instalação

```bash
python install_error_analyzer.py
```

Este script criará:
- `core/learning/error_analyzer.py` (~350 linhas)
- `core/learning/__init__.py`
- `docs/TAREFA_1_CONCLUIDA.md`

### Passo 2: Verificar Instalação

```bash
python demo_error_analyzer.py
```

Este script:
1. Cria dados de exemplo
2. Demonstra todas as funcionalidades
3. Valida conformidade com especificação

---

## Uso

### Exemplo Básico

```python
from core.learning.error_analyzer import ErrorAnalyzer

# Inicializar
analyzer = ErrorAnalyzer(feedback_dir="data/learning")

# Analisar erros dos últimos 7 dias
result = analyzer.analyze_errors(days=7)

# Exibir erros mais comuns
for error in result['most_common_errors']:
    print(f"{error['type']}: {error['count']} ocorrências")
    print(f"Exemplo: {error['example_query']}")

# Exibir sugestões
for suggestion in result['suggested_improvements']:
    print(f"[{suggestion['priority']}] {suggestion['issue']}")
    print(f"Solução: {suggestion['solution']}")
```

### Exemplo Avançado

```python
from core.learning.error_analyzer import ErrorAnalyzer

# Inicializar com diretório customizado
analyzer = ErrorAnalyzer(feedback_dir="custom/path/learning")

# Analisar últimos 30 dias
result = analyzer.analyze_errors(days=30)

# Filtrar apenas sugestões de alta prioridade
high_priority = [
    s for s in result['suggested_improvements']
    if s['priority'] == 'HIGH'
]

# Obter todos os tipos de erro conhecidos
error_types = analyzer.get_error_types()
print(f"Tipos conhecidos: {error_types}")
```

---

## Formato de Dados

### Arquivo de Feedback (JSONL)

**Nome do arquivo:** `feedback_YYYYMMDD.jsonl`

**Formato de cada linha:**
```json
{
  "query": "SELECT * FROM vendas WHERE segmento = 'varejo'",
  "issue_type": "wrong_segmento",
  "timestamp": "2025-10-18T14:30:00",
  "error_message": "Invalid segmento value",
  "user_feedback": "O segmento deveria ser 'VAREJO' em maiúsculas"
}
```

### Resultado de analyze_errors()

```json
{
  "most_common_errors": [
    {
      "type": "missing_limit",
      "count": 21,
      "example_query": "SELECT * FROM vendas WHERE data >= '2025-01-01'"
    },
    {
      "type": "wrong_segmento",
      "count": 7,
      "example_query": "SELECT * FROM vendas WHERE segmento = 'varejo'"
    }
  ],
  "suggested_improvements": [
    {
      "issue": "Queries sem LIMIT (21 ocorrências)",
      "solution": "Adicionar .head(N) ao final das queries para limitar resultados e melhorar performance. Exemplo: df.head(100)",
      "priority": "HIGH"
    },
    {
      "issue": "Valores incorretos de segmento (7 ocorrências)",
      "solution": "Usar valores exatos de segmento disponíveis no banco. Consultar tabela dim_segmentos para valores válidos. Exemplos: 'VAREJO', 'ATACADO', 'INDUSTRIA'",
      "priority": "MEDIUM"
    }
  ]
}
```

---

## Tipos de Erro Suportados

| Tipo | Descrição | Sugestão Automática |
|------|-----------|---------------------|
| `missing_limit` | Queries sem limitação de resultados | Adicionar `.head(N)` |
| `wrong_segmento` | Valores incorretos de segmento | Usar valores exatos do banco |
| `wrong_column` | Colunas inexistentes ou incorretas | Validar com schema do banco |
| `syntax_error` | Erros de sintaxe SQL/Pandas | Revisar sintaxe da query |
| `timeout` | Queries com timeout | Otimizar com filtros e limites |
| Outros | Tipos desconhecidos | Investigar causa raiz |

---

## Sistema de Priorização

As sugestões são priorizadas automaticamente com base na frequência:

| Prioridade | Threshold | Ação Recomendada |
|------------|-----------|------------------|
| **HIGH** | ≥ 10 ocorrências | Ação imediata necessária |
| **MEDIUM** | 5-9 ocorrências | Planejar correção |
| **LOW** | < 5 ocorrências | Monitorar |

---

## API Completa

### `__init__(feedback_dir: str = "data/learning")`

Inicializa o ErrorAnalyzer.

**Parâmetros:**
- `feedback_dir`: Diretório onde os arquivos de feedback são armazenados

**Raises:**
- `Exception`: Se não for possível criar o diretório

---

### `analyze_errors(days: int = 7) -> Dict[str, Any]`

Analisa erros dos últimos N dias.

**Parâmetros:**
- `days`: Número de dias para considerar na análise (padrão: 7)

**Retorna:**
```python
{
  "most_common_errors": List[Dict[str, Any]],
  "suggested_improvements": List[Dict[str, str]]
}
```

**Comportamento:**
- Carrega arquivos `feedback_*.jsonl` dentro do período
- Agrupa erros por `issue_type`
- Ordena por frequência (mais comum primeiro)
- Gera sugestões priorizadas

---

### `get_error_types() -> List[str]`

Retorna lista de tipos de erro conhecidos.

**Retorna:**
- Lista ordenada alfabeticamente de tipos de erro

**Exemplo:**
```python
["missing_limit", "syntax_error", "timeout", "wrong_column", "wrong_segmento"]
```

---

### `_generate_suggestions(error_groups: Dict) -> List[Dict]`

Gera sugestões baseadas nos erros (método privado).

**Parâmetros:**
- `error_groups`: Dicionário com erros agrupados por tipo

**Retorna:**
- Lista de sugestões ordenadas por prioridade

---

## Estrutura de Arquivos

```
Agent_Solution_BI/
├── core/
│   └── learning/
│       ├── __init__.py
│       └── error_analyzer.py          # Implementação principal
├── data/
│   └── learning/                       # Diretório de feedback
│       ├── feedback_20251018.jsonl
│       ├── feedback_20251017.jsonl
│       └── ...
├── docs/
│   └── TAREFA_1_CONCLUIDA.md          # Documentação
├── install_error_analyzer.py           # Script de instalação
├── demo_error_analyzer.py              # Demonstração e validação
└── ERROR_ANALYZER_README.md            # Este arquivo
```

---

## Logging

O ErrorAnalyzer utiliza o módulo `logging` do Python:

```python
import logging

# Configurar nível de log
logging.basicConfig(level=logging.INFO)

# Logs disponíveis:
# - INFO: Operações principais (análise iniciada, concluída)
# - DEBUG: Detalhes de processamento (arquivos encontrados, etc)
# - WARNING: Problemas não-críticos (JSON inválido, arquivo inválido)
# - ERROR: Erros graves (falha ao processar arquivo)
```

---

## Testes

### Executar Demonstração

```bash
python demo_error_analyzer.py
```

Saída esperada:
- ✓ Criação de dados de exemplo
- ✓ Importação do ErrorAnalyzer
- ✓ Análise de erros (7 dias)
- ✓ Listagem de tipos de erro
- ✓ Filtro por período (3 dias)
- ✓ Validação de conformidade (todas as verificações devem passar)

### Validações Automáticas

O script de demonstração valida:
- ✓ Estrutura do retorno (most_common_errors, suggested_improvements)
- ✓ Campos obrigatórios em erros (type, count, example_query)
- ✓ Campos obrigatórios em sugestões (issue, solution, priority)
- ✓ Prioridades válidas (HIGH/MEDIUM/LOW)
- ✓ Ordenação correta (por frequência)
- ✓ get_error_types() retorna lista ordenada

---

## Conformidade com Especificação

### ✓ Checklist de Implementação

- [x] Arquivo criado: `core/learning/error_analyzer.py` (~350 linhas)
- [x] Classe `ErrorAnalyzer` implementada
- [x] Método `__init__(feedback_dir)` com criação de diretório
- [x] Método `analyze_errors(days)` com retorno especificado
- [x] Método `get_error_types()` retornando lista ordenada
- [x] Método `_generate_suggestions(error_groups)` privado
- [x] Uso de `pathlib.Path` para manipulação de arquivos
- [x] Logger configurado
- [x] Docstrings completas
- [x] Tratamento de exceções robusto
- [x] Suporte a formato JSONL
- [x] Sugestões específicas para cada tipo de erro
- [x] Sistema de priorização (HIGH/MEDIUM/LOW)
- [x] Filtro por período (dias)
- [x] Ordenação por frequência

---

## Próximos Passos

### PILAR 4 - Roadmap

- [x] **TAREFA 1:** ErrorAnalyzer (CONCLUÍDA)
- [ ] **TAREFA 2:** FeedbackCollector
- [ ] **TAREFA 3:** PromptOptimizer
- [ ] **TAREFA 4:** Integração completa

---

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'core.learning'"

**Solução:** Execute o script de instalação:
```bash
python install_error_analyzer.py
```

### Erro: "FileNotFoundError: [Errno 2] No such file or directory"

**Solução:** O ErrorAnalyzer cria o diretório automaticamente. Verifique permissões de escrita.

### Aviso: "Nome de arquivo inválido"

**Causa:** Arquivo de feedback não segue o formato `feedback_YYYYMMDD.jsonl`

**Solução:** Renomear arquivo para o formato correto, exemplo:
```
feedback_20251018.jsonl
```

### Aviso: "Erro ao parsear linha N"

**Causa:** Linha não é um JSON válido

**Solução:** Cada linha deve ser um objeto JSON completo:
```json
{"query": "...", "issue_type": "...", "timestamp": "..."}
```

---

## Contribuição

Para adicionar novos tipos de erro:

1. Adicione entrada no método `_generate_suggestions()`:

```python
elif error_type == "novo_tipo":
    suggestion = {
        "issue": f"Descrição do erro ({count} ocorrências)",
        "solution": "Solução detalhada...",
        "priority": priority
    }
```

2. Documente o novo tipo neste README

---

## Licença

Este módulo faz parte do projeto Agent Solution BI.

---

## Contato

Para dúvidas ou sugestões sobre o ErrorAnalyzer:
- Criar issue no repositório
- Consultar documentação em `docs/TAREFA_1_CONCLUIDA.md`

---

**Versão:** 1.0.0
**Data:** 2025-10-18
**Status:** PRODUÇÃO ✓
