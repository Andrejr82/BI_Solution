# 🚨 PLANO: Fix CodeGenAgent data_adapter Error

**Data:** 12/10/2025
**Tipo:** Bug Fix - Critical
**Status:** 🔴 EM PLANEJAMENTO

---

## 📋 Problema

### Erro Persistente:
```python
TypeError: CodeGenAgent.__init__() got an unexpected keyword argument 'data_adapter'
```

### Causa Raiz:
**INCONSISTÊNCIA** na assinatura do `CodeGenAgent.__init__()`

#### Situação Atual:
1. **Arquivo `code_gen_agent.py` (linhas 34-42):**
   ```python
   def __init__(self, llm_adapter: BaseLLMAdapter, data_adapter: any):
       self.llm = llm_adapter
       self.data_adapter = data_adapter
   ```

2. **Chamadas em outros arquivos:**
   ```python
   # streamlit_app.py:270 ✅ CORRETO
   CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)

   # tests/test_agent_flow.py:47 ❌ ERRADO
   CodeGenAgent(llm_adapter=llm_adapter)

   # tests/test_agent_graph_live.py:48 ❌ ERRADO
   CodeGenAgent(llm_adapter=llm_adapter)

   # main.py:41 ❌ ERRADO
   CodeGenAgent(llm_adapter=llm_adapter)

   # scripts/test_direct_vs_agent_graph.py:27 ✅ CORRETO
   CodeGenAgent(llm_adapter=llm_adapter, data_adapter=adapter)
   ```

### Impacto:
- ❌ **Streamlit Cloud falha** ao inicializar backend
- ❌ **Agent Graph não carrega** (erro na linha 270 do streamlit_app.py)
- ❌ **Testes falham**
- ❌ **Main.py não funciona**

---

## 🎯 Objetivos

1. ✅ **Consistência Total** - Todas as chamadas devem usar a mesma assinatura
2. ✅ **Backward Compatibility** - Não quebrar código existente
3. ✅ **Flexibilidade** - Suportar ambos os cenários (com e sem data_adapter)
4. ✅ **Clareza** - Documentação clara do parâmetro

---

## 🔧 Solução Proposta

### Opção 1: Tornar `data_adapter` OPCIONAL (✅ RECOMENDADO)

```python
def __init__(self, llm_adapter: BaseLLMAdapter, data_adapter: any = None):
    """
    Inicializa o agente com o adaptador LLM e opcionalmente o adaptador de dados.

    Args:
        llm_adapter: Adaptador LLM para geração de código
        data_adapter: (Opcional) Adaptador de dados para injeção de load_data()
                      Se None, load_data() usará path padrão do Parquet
    """
    self.logger = logging.getLogger(__name__)
    self.llm = llm_adapter
    self.data_adapter = data_adapter  # Pode ser None
    self.code_cache = {}
    self.logger.info("CodeGenAgent inicializado.")
```

**Modificar `load_data()` em dois lugares:**

**1. Em `_execute_generated_code()` (linha 51-61):**
```python
def load_data():
    """Carrega o dataframe Dask usando o adaptador, garantindo eficiência."""
    if self.data_adapter:
        # Usar adapter injetado
        if hasattr(self.data_adapter, '_get_base_dask_df'):
            return self.data_adapter._get_base_dask_df()
        else:
            return self.data_adapter.load_dask_dataframe()
    else:
        # Fallback: carregar diretamente do Parquet
        import os
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")
        return pd.read_parquet(parquet_path)
```

**2. Em `generate_and_execute_code()` (linha 229-260) - já tem fallback, basta ajustar:**
```python
def load_data():
    if self.data_adapter:
        # Usar adapter injetado (preferencial)
        if hasattr(self.data_adapter, '_get_base_dask_df'):
            return self.data_adapter._get_base_dask_df()
        elif hasattr(self.data_adapter, 'load_dask_dataframe'):
            return self.data_adapter.load_dask_dataframe()

    # Fallback: usar path do parquet_dir (compatibilidade legacy)
    parquet_file = os.path.join(self.parquet_dir, "admmat.parquet")
    if not os.path.exists(parquet_file):
        raise FileNotFoundError(f"Arquivo Parquet não encontrado em {parquet_file}")
    return pd.read_parquet(parquet_file)
```

**Vantagens:**
- ✅ **Backward compatible** - Código antigo continua funcionando
- ✅ **Flexível** - Suporta ambos os casos
- ✅ **Sem quebrar nada** - Mudança mínima

**Desvantagens:**
- ⚠️ Precisa ajustar `load_data()` para ter fallback

---

### Opção 2: Remover `data_adapter` e usar sempre path (❌ NÃO RECOMENDADO)

```python
def __init__(self, llm_adapter: BaseLLMAdapter):
    self.llm = llm_adapter
    # Sempre usa path direto do Parquet
```

**Vantagens:**
- ✅ Simples
- ✅ Consistente com código legado

**Desvantagens:**
- ❌ **Perde flexibilidade** - Não permite injetar HybridDataAdapter
- ❌ **Quebra streamlit_app.py** que já está correto
- ❌ **Menos eficiente** - Não aproveita cache do adapter

---

## 📝 Plano de Ação (OPÇÃO 1)

### FASE 1: Corrigir `code_gen_agent.py`

**Tarefa 1.1:** Tornar `data_adapter` opcional
- [ ] Modificar linha 34: adicionar `= None`
- [ ] Atualizar docstring (linhas 35-37)

**Tarefa 1.2:** Atualizar `_execute_generated_code()`
- [ ] Modificar função `load_data()` (linhas 51-61)
- [ ] Adicionar verificação `if self.data_adapter:`
- [ ] Adicionar fallback para path direto

**Tarefa 1.3:** Atualizar `generate_and_execute_code()`
- [ ] Modificar função `load_data()` (linhas 229-260)
- [ ] Adicionar verificação `if self.data_adapter:`
- [ ] Garantir fallback funciona

**Tarefa 1.4:** Remover referências quebradas
- [ ] Remover `self.parquet_dir` se não for mais necessário
- [ ] Ou mantê-lo para fallback

---

### FASE 2: Corrigir Chamadas Incorretas

**Tarefa 2.1:** `main.py` (linha 41)
```python
# ANTES
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)

# DEPOIS (opcional, mas recomendado)
data_adapter = SQLServerAdapter(...)  # ou ParquetAdapter
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
```

**Tarefa 2.2:** `tests/test_agent_flow.py` (linha 47)
```python
# ANTES
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)

# DEPOIS
data_adapter = HybridDataAdapter()
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
```

**Tarefa 2.3:** `tests/test_agent_graph_live.py` (linha 48)
```python
# ANTES
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)

# DEPOIS (ou deixar sem, já que é opcional)
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)  # OK agora
```

**Tarefa 2.4:** Documentações (18 arquivos em docs/)
- [ ] Atualizar todos os exemplos em `docs/*.md`
- [ ] Adicionar nota sobre `data_adapter` ser opcional

---

### FASE 3: Testes

**Tarefa 3.1:** Testar com `data_adapter`
```bash
# Deve funcionar
python -c "
from core.agents.code_gen_agent import CodeGenAgent
from core.factory.component_factory import ComponentFactory
from core.connectivity.hybrid_adapter import HybridDataAdapter

llm = ComponentFactory.get_llm_adapter('gemini')
adapter = HybridDataAdapter()
agent = CodeGenAgent(llm_adapter=llm, data_adapter=adapter)
print('✅ OK com data_adapter')
"
```

**Tarefa 3.2:** Testar SEM `data_adapter`
```bash
# Deve funcionar (fallback)
python -c "
from core.agents.code_gen_agent import CodeGenAgent
from core.factory.component_factory import ComponentFactory

llm = ComponentFactory.get_llm_adapter('gemini')
agent = CodeGenAgent(llm_adapter=llm)
print('✅ OK sem data_adapter')
"
```

**Tarefa 3.3:** Testar Streamlit App
```bash
streamlit run streamlit_app.py
# Fazer login
# Selecionar "IA Completa"
# Perguntar: "qual é o ranking do tecido"
# Verificar se funciona
```

---

### FASE 4: Commit e Deploy

**Tarefa 4.1:** Commit das mudanças
```bash
git add core/agents/code_gen_agent.py
git add main.py tests/*.py
git commit -m "fix: Tornar data_adapter opcional em CodeGenAgent

- Adicionar data_adapter=None para backward compatibility
- Atualizar load_data() com fallback para path direto
- Corrigir chamadas em tests e main.py
- Documentação atualizada

Fixes: TypeError 'unexpected keyword argument data_adapter'"
```

**Tarefa 4.2:** Merge para main
```bash
git checkout main
git merge gemini-deepseek-only --no-edit
git checkout gemini-deepseek-only
```

**Tarefa 4.3:** Push para Streamlit Cloud
```bash
git push origin main
git push origin gemini-deepseek-only
```

**Tarefa 4.4:** Monitorar Deploy
- [ ] Verificar logs do Streamlit Cloud
- [ ] Testar aplicação em produção
- [ ] Confirmar que "IA Completa" funciona

---

## 🔍 Checklist de Validação

### Antes do Commit:
- [ ] `code_gen_agent.py` compilat sem erros
- [ ] Todos os testes passam (`pytest`)
- [ ] Streamlit roda localmente sem erros
- [ ] Ambos os cenários funcionam (com e sem data_adapter)

### Depois do Deploy:
- [ ] Streamlit Cloud carrega sem erros
- [ ] Backend inicializa com sucesso
- [ ] "Modo IA Completa" está disponível
- [ ] Consulta de teste funciona
- [ ] Logs não mostram TypeError

---

## 📊 Arquivos Afetados

### Modificações Necessárias:
1. ✅ `core/agents/code_gen_agent.py` - Tornar data_adapter opcional
2. ✅ `main.py` - Adicionar data_adapter (opcional)
3. ✅ `tests/test_agent_flow.py` - Adicionar data_adapter
4. ✅ `tests/test_agent_graph_live.py` - Funciona sem data_adapter
5. ⚠️ `docs/*.md` (18 arquivos) - Atualizar exemplos

### Já Corretos:
- ✅ `streamlit_app.py:270` - Já usa data_adapter
- ✅ `scripts/test_direct_vs_agent_graph.py:27` - Já usa data_adapter

---

## ⏱️ Estimativa de Tempo

- **FASE 1:** Corrigir code_gen_agent.py - **30 min**
- **FASE 2:** Corrigir chamadas - **20 min**
- **FASE 3:** Testes - **30 min**
- **FASE 4:** Commit e Deploy - **20 min**

**TOTAL:** ~2 horas

---

## 🎯 Critério de Sucesso

A correção será considerada bem-sucedida quando:

1. ✅ `streamlit_app.py` inicializa sem erros
2. ✅ Backend components carrega `agent_graph` com sucesso
3. ✅ Modo "IA Completa" está disponível e funciona
4. ✅ Consulta "qual é o ranking do tecido" retorna resultados
5. ✅ Todos os testes passam
6. ✅ Nenhum TypeError de `data_adapter` nos logs

---

## 🚀 Início da Execução

**Status:** Aguardando aprovação do usuário

**Próximo Passo:** Executar FASE 1 - Corrigir code_gen_agent.py

**Comando para iniciar:**
```bash
# Vou modificar code_gen_agent.py para tornar data_adapter opcional
```

---

**Autor:** Claude Code
**Data:** 12/10/2025
**Prioridade:** 🔴 CRÍTICA
**Bloqueio:** Agent Graph não funciona no Streamlit Cloud
