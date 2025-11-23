# Mapeamento: Próximos Passos ↔ PIC (Plano de Implementação Cirúrgica)

**Data:** 22 de Novembro de 2025  
**Documento de Referência:** `prompt_pic_agent_bi_implementation.md`

---

## ✅ Resposta Direta

**SIM!** Os próximos passos opcionais correspondem **EXATAMENTE** às seções do PIC que ainda não foram implementadas.

---

## 📊 Mapeamento Detalhado

### Próximos Passos Opcionais → Seções do PIC

| Próximo Passo | Seção do PIC | Linhas | Status |
|---------------|--------------|--------|--------|
| Integrar mascaramento no `streamlit_app.py` (input) | **2.3.2** - Mascarar Input do Usuário | 623-645 | ⏳ Pendente |
| Integrar mascaramento no `streamlit_app.py` (output) | **2.3.3** - Mascarar Output do LLM | 647-671 | ⏳ Pendente |
| Integrar streaming no `streamlit_app.py` | **3.2** - Modificação: streamlit_app.py (Streaming) | 872-950 | ⏳ Pendente |
| Remover spinners bloqueantes | **3.2.2** - Implementar Streaming na Exibição | 891-930 | ⏳ Pendente |
| Implementar resposta progressiva | **3.2.2** - Streaming com placeholder | 901-930 | ⏳ Pendente |

---

## 📝 Detalhamento das Seções Pendentes

### 1. Seção 2.3.2 do PIC: Mascarar Input do Usuário

**Localização no PIC:** Linhas 623-645  
**Objetivo:** Integrar mascaramento de PII no input do usuário

**Código Especificado no PIC:**
```python
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    # Mascarar PII antes de processar
    masked_input = mask_pii(user_input)
    logger.info(f"Input mascarado: PII removido")
    
    # Usar masked_input para o resto do processamento
    user_input_for_llm = masked_input
else:
    user_input_for_llm = None
```

**Status:** ✅ Módulo criado, ⏳ Integração pendente

---

### 2. Seção 2.3.3 do PIC: Mascarar Output do LLM

**Localização no PIC:** Linhas 647-671  
**Objetivo:** Mascarar PII na resposta do LLM

**Código Especificado no PIC:**
```python
llm_response = call_llm(user_input_for_llm)

# Mascarar PII na resposta do LLM (camada extra de proteção)
masked_response = mask_pii(llm_response)

# Exibir resposta mascarada
st.write(masked_response)

# Log de segurança
pii_summary = get_pii_summary()
if pii_summary:
    logger.warning(f"PII detectado e mascarado: {pii_summary}")
```

**Status:** ✅ Módulo criado, ⏳ Integração pendente

---

### 3. Seção 3.2 do PIC: Streaming no streamlit_app.py

**Localização no PIC:** Linhas 872-950  
**Objetivo:** Implementar streaming de respostas

**Código Especificado no PIC:**
```python
# 3.2.1. Adicionar Import
from core.llm_service import get_llm_response_stream, get_llm_service

# 3.2.2. Implementar Streaming
if user_input:
    # SEM spinner bloqueante
    response_placeholder = st.empty()
    full_response = ""
    
    for chunk in get_llm_response_stream(prompt, context):
        full_response += chunk
        response_placeholder.markdown(full_response + "▌")
    
    response_placeholder.markdown(full_response)
```

**Status:** ✅ Serviço criado, ⏳ Integração pendente

---

## 🎯 Resumo da Correspondência

### O que JÁ foi implementado (Pilares Core):

✅ **Pilar 1: Governança de Prompts**
- ✅ Seção 1.1: `prompt_loader.py` estendido
- ✅ Seção 1.2: `prompt_desambiguacao.md` criado
- ✅ Seção 1.3: `prompt_analise.md` atualizado

✅ **Pilar 2: Segurança de Dados (Módulos)**
- ✅ Seção 2.1: `data_masking.py` criado
- ✅ Seção 2.2: `security/__init__.py` atualizado

✅ **Pilar 3: Streaming (Serviço)**
- ✅ Seção 3.1: `llm_service.py` criado

### O que FALTA implementar (Integração no Streamlit):

⏳ **Integração no streamlit_app.py:**
- ⏳ Seção 2.3.1: Import do módulo de segurança
- ⏳ Seção 2.3.2: Mascarar input do usuário
- ⏳ Seção 2.3.3: Mascarar output do LLM
- ⏳ Seção 3.2.1: Import do serviço LLM
- ⏳ Seção 3.2.2: Implementar streaming na UI

---

## 📋 Próximos Passos Detalhados (Seguindo o PIC)

### Passo 1: Adicionar Imports no streamlit_app.py

**Localização:** Após linha ~20 (seção de imports)

```python
# Importar módulo de segurança (Seção 2.3.1 do PIC)
from core.security import mask_pii, mask_pii_dict, get_pii_summary

# Importar serviço LLM (Seção 3.2.1 do PIC)
from core.llm_service import get_llm_response_stream, get_llm_service
```

### Passo 2: Mascarar Input do Usuário

**Localização:** Onde `user_input` é recebido (buscar por processamento de input)

```python
if user_input:
    # Mascarar PII antes de processar
    masked_input = mask_pii(user_input)
    logger.info("PII mascarado no input")
    
    # Usar masked_input para processamento
    user_input_for_llm = masked_input
```

### Passo 3: Implementar Streaming com Mascaramento

**Localização:** Onde a resposta é exibida

```python
# Obter resposta com streaming
response_placeholder = st.empty()
full_response = ""

for chunk in get_llm_response_stream(prompt, context):
    full_response += chunk
    response_placeholder.markdown(full_response + "▌")

# Mascarar PII na resposta final
masked_response = mask_pii(full_response)
response_placeholder.markdown(masked_response)

# Log de segurança
pii_summary = get_pii_summary()
if pii_summary:
    logger.warning(f"PII detectado: {pii_summary}")
```

---

## ✅ Conclusão

**Os próximos passos opcionais são EXATAMENTE as seções 2.3 e 3.2 do PIC.**

**Implementação Core:** ✅ 100% Concluída  
**Integração no Streamlit:** ⏳ 0% (Próxima fase)

**Referências:**
- PIC Completo: [prompt_pic_agent_bi_implementation.md](file:///c:/Users/André/Documents/Agent_Solution_BI/prompt_pic_agent_bi_implementation.md)
- Seção 2.3: Linhas 604-671
- Seção 3.2: Linhas 872-950
