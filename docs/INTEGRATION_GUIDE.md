# Guia de Integração Rápida - Agent_BI Refactoring

## 🚀 Como Usar os Novos Componentes

### 1. Governança de Prompts (CO-STAR)

```python
from core.agents.prompt_loader import PromptLoader

# Inicializar loader
loader = PromptLoader()

# Carregar template
template = loader.load_prompt_template("prompt_analise")

# Injetar contexto
context = {
    "CONTEXTO_DADOS": schema_banco_dados,
    "PERGUNTA_USUARIO": pergunta_usuario
}

prompt_final = loader.inject_context_into_template(template, context)
```

### 2. Segurança de Dados (PII Masking)

```python
from core.security import mask_pii, mask_pii_dict

# Mascarar texto
texto_mascarado = mask_pii(input_usuario)

# Mascarar dicionário
dados_mascarados = mask_pii_dict(dados_sensiveis)
```

### 3. Serviço LLM com Streaming

```python
from core.llm_service import create_llm_service

# Criar serviço
llm_service = create_llm_service(llm_adapter)

# Modo não-streaming
response = llm_service.get_response(prompt, context, mask_pii_data=True)

# Modo streaming
for chunk in llm_service.get_response_stream(prompt, context):
    print(chunk, end='', flush=True)
```

## 📋 Checklist de Integração no Streamlit

### Passo 1: Adicionar Imports
```python
# No início do streamlit_app.py
from core.llm_service import create_llm_service
from core.security import mask_pii
```

### Passo 2: Inicializar LLMService
```python
# Na função initialize_backend()
llm_service = create_llm_service(llm_adapter)

return {
    "llm_adapter": llm_adapter,
    "llm_service": llm_service,  # NOVO
    # ... outros componentes
}
```

### Passo 3: Mascarar Input do Usuário
```python
# Onde o input é recebido
if user_input:
    # Mascarar PII antes de processar
    masked_input = mask_pii(user_input)
    logger.info("PII mascarado no input")
```

### Passo 4: Usar LLMService com Streaming
```python
# Substituir chamada direta ao LLM
llm_service = backend["llm_service"]

# Carregar e preparar prompt
context = {
    "CONTEXTO_DADOS": schema,
    "PERGUNTA_USUARIO": masked_input
}

prompt = llm_service.load_and_inject_prompt("prompt_analise", context)

# Streaming de resposta
with st.chat_message("assistant"):
    response_placeholder = st.empty()
    full_response = ""
    
    for chunk in llm_service.get_response_stream(prompt, context):
        full_response += chunk
        response_placeholder.markdown(full_response + "▌")
    
    response_placeholder.markdown(full_response)
```

## ✅ Validação

Execute os testes:
```bash
python tests/test_implementation_pillars.py
```

Resultado esperado:
- ✅ Todos os testes do Pilar 1 passam
- ✅ Todos os testes do Pilar 2 passam
- ✅ Todos os testes do Pilar 3 passam

## 🎯 Benefícios Imediatos

1. **Prompts Estruturados:** Respostas mais precisas e consistentes
2. **Segurança:** PII automaticamente mascarado
3. **UX Melhorada:** Respostas em streaming (mais fluido)

## 📚 Documentação Completa

Veja [walkthrough.md](file:///C:/Users/André/.gemini/antigravity/brain/c02c0b9b-e2c8-480b-859b-75010a67b6ba/walkthrough.md) para detalhes completos da implementação.
