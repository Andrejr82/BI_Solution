# 🧪 Testes do Projeto

Esta pasta contém todos os testes automatizados do Agent_Solution_BI.

## 📁 Estrutura

```
tests/
├── pytest.ini                 # Configuração do pytest
├── test_llm_fix.py           # Testes de LLM adapters
├── test_une_query.py          # Testes de queries UNE
├── unit/                      # Testes unitários (pytest existentes)
├── integration/               # Testes de integração (futuro)
└── fixtures/                  # Dados de teste (futuro)
```

---

## 🔬 Testes Disponíveis

### test_llm_fix.py
**Propósito:** Validar configuração correta dos adaptadores LLM.

**Testa:**
- ✅ GeminiLLMAdapter usa base_url correta do Gemini
- ✅ DeepSeekLLMAdapter usa base_url correta do DeepSeek
- ✅ Clients são inicializados sem erros

**Como executar:**
```bash
python tests/test_llm_fix.py
```

**Resultado esperado:**
```
GeminiLLMAdapter:   PASSOU
DeepSeekLLMAdapter: PASSOU
TODOS OS TESTES PASSARAM!
```

---

### test_une_query.py
**Propósito:** Validar queries de UNE e DirectQueryEngine.

**Testa:**
- ✅ DirectQueryEngine detecta UNE 261 corretamente
- ✅ Retorna top 10 produtos corretos
- ✅ Rejeita UNE inexistente (NIG) com erro apropriado
- ✅ ParquetAdapter filtra por UNE corretamente

**Como executar:**
```bash
python tests/test_une_query.py
```

**Resultado esperado:**
```
DirectQueryEngine: PASSOU
ParquetAdapter:    PASSOU
```

---

## 🛠️ Executando Todos os Testes

### Testes de Diagnóstico
```bash
# Executar ambos os testes
python tests/test_llm_fix.py
python tests/test_une_query.py
```

### Testes Unitários (pytest)
```bash
# Executar da raiz do projeto
pytest

# Executar pasta específica
pytest tests/unit/

# Com cobertura
pytest --cov=core --cov-report=html

# Verbose
pytest -v
```

**NOTA:** `pytest.ini` está em `tests/pytest.ini` mas pytest encontra automaticamente.

---

## 📋 Convenções de Teste

### Nomenclatura
- `test_*.py` - Arquivos de teste
- `test_*()` - Funções de teste
- `*_fixture.py` - Fixtures reutilizáveis

### Estrutura de Teste
```python
def test_feature_name():
    """Descrição clara do que está sendo testado"""
    # Arrange (preparação)
    # Act (ação)
    # Assert (verificação)
```

### Categorias
- **Diagnóstico:** Testes para troubleshooting (test_llm_fix, test_une_query)
- **Unitários:** Testes de funções/classes individuais
- **Integração:** Testes de fluxos completos
- **E2E:** Testes end-to-end (futuro)

---

## 🎯 Cobertura de Testes

### Módulos Testados
- ✅ `core.llm_adapter` - LLM adapters (test_llm_fix.py)
- ✅ `core.business_intelligence.direct_query_engine` - Queries UNE (test_une_query.py)
- ✅ `core.connectivity.parquet_adapter` - Filtros de dados (test_une_query.py)

### Módulos a Testar
- ⏳ `core.agents.*` - Agentes de IA
- ⏳ `core.graph.*` - LangGraph workflows
- ⏳ `core.database.*` - Autenticação e DB
- ⏳ `core.tools.*` - Ferramentas utilitárias

---

## 📝 Adicionando Novos Testes

1. Criar arquivo `test_feature.py` na pasta apropriada
2. Importar módulos necessários
3. Escrever funções de teste com docstrings
4. Executar teste localmente
5. Atualizar este README

**Exemplo:**
```python
"""
Testes para o módulo X
"""
import sys
from core.module_x import FunctionY

def test_function_y():
    """Testa se FunctionY retorna resultado esperado"""
    result = FunctionY(input_data)
    assert result == expected_output
    print("✅ test_function_y PASSOU")

if __name__ == "__main__":
    test_function_y()
    sys.exit(0)
```

---

## 🔗 Links Relacionados

- [Relatórios de Investigação](../reports/investigation/) - Problemas que geraram estes testes
- [Documentação](../docs/) - Guias técnicos
- [README Principal](../README.md) - Visão geral do projeto
