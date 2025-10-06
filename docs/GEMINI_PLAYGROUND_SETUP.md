# 🤖 Gemini Playground - Guia de Configuração

## ✅ Status do Playground

O **Gemini Playground** foi criado com sucesso e está funcionando corretamente!

### Testes Realizados

| Teste | Status | Descrição |
|-------|--------|-----------|
| ✅ Imports | PASSOU | Todos os módulos importados com sucesso |
| ✅ Settings | PASSOU | Configurações carregadas corretamente |
| ✅ Sintaxe | PASSOU | Página sem erros de sintaxe |
| ✅ Adapter | PASSOU | GeminiLLMAdapter inicializado com sucesso |
| ⚠️ API Call | PENDENTE | Aguardando API Key válida |

## 🔑 Configuração da API Key

Para usar o playground, você precisa configurar uma **API Key válida do Google Gemini**.

### Passo 1: Obter a API Key

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### Passo 2: Configurar a API Key

Edite o arquivo `.env` na raiz do projeto:

```env
# API Key do Gemini (substitua pelo valor real)
GEMINI_API_KEY=sua-api-key-aqui

# Modelo (já configurado)
LLM_MODEL_NAME=gemini-2.5-flash-lite
```

### Passo 3: Reiniciar a Aplicação

```bash
streamlit run streamlit_app.py
```

## 🎯 Funcionalidades do Playground

### Interface de Chat
- ✅ Histórico de conversação
- ✅ Suporte a streaming (respostas em tempo real)
- ✅ Modo JSON para respostas estruturadas

### Controles Avançados
- **Temperature**: Controla a criatividade (0.0 - 2.0)
- **Max Tokens**: Limite de tokens na resposta (128 - 8192)
- **JSON Mode**: Força respostas em formato JSON
- **Stream Mode**: Exibe respostas em tempo real

### Estatísticas e Cache
- Visualização de cache hits/misses
- Taxa de acerto do cache
- Economia de créditos API

### Exemplos Prontos
- 📝 Análise de Dados
- 🔍 SQL Queries
- 📊 Código Python

## 🔒 Segurança

O playground possui **acesso restrito apenas para administradores**:

- ✅ Verificação de autenticação
- ✅ Verificação de role (admin)
- ✅ Mensagem de erro para usuários não autorizados

## 📍 Localização da Página

```
pages/10_🤖_Gemini_Playground.py
```

A página aparecerá automaticamente no menu lateral do Streamlit como:
**"🤖 Gemini Playground"**

## 🧪 Testar Novamente

Após configurar a API Key válida, execute:

```bash
cd "C:\Users\André\Documents\Agent_Solution_BI"
echo s | python scripts/test_gemini_playground.py
```

## 🎨 Personalização

### Adicionar Novos Exemplos

Edite a seção de exemplos em `pages/10_🤖_Gemini_Playground.py`:

```python
# Adicione novos botões de exemplo
with col_ex4:
    if st.button("🆕 Seu Exemplo", use_container_width=True):
        example = "Seu prompt aqui"
        st.session_state.example_prompt = example
        st.rerun()
```

### Modificar Parâmetros Padrão

```python
temperature = st.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,  # ← Modifique o valor padrão aqui
    step=0.1
)
```

## 📊 Monitoramento

O playground registra todas as chamadas à API:

```python
logger.info(f"💰 Chamada API Gemini: {model_to_use} - tokens: {max_tokens}")
```

Verifique os logs para acompanhar o uso da API.

## ⚡ Otimizações

### Cache de Respostas
- ✅ TTL de 48 horas
- ✅ Reduz custos com API
- ✅ Respostas mais rápidas para queries repetidas

### Lazy Loading
- ✅ Módulos carregados sob demanda
- ✅ Melhor performance de inicialização

## 🆘 Troubleshooting

### Erro: "API key not valid"
- Verifique se a API key está correta no `.env`
- Confirme que a key não está com prefixo/sufixo errado
- Teste a key diretamente em https://aistudio.google.com

### Erro: "Acesso negado"
- Confirme que está logado como admin
- Verifique `st.session_state.role == "admin"`

### Página não aparece no menu
- Verifique o nome do arquivo: `10_🤖_Gemini_Playground.py`
- Reinicie o Streamlit
- Limpe o cache do navegador

## 📝 Próximos Passos

1. ✅ Obter API Key válida do Gemini
2. ✅ Configurar no `.env`
3. ✅ Testar o playground
4. ✅ Explorar as funcionalidades
5. ✅ Adicionar exemplos personalizados

---

**Desenvolvido para Agent Solution BI** 🚀
