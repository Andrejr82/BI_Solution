# 🚀 PROMPT PARA IMPLEMENTAÇÃO COMPLETA DO PROTÓTIPO UI CHATGPT

**Data:** 20/10/2025
**Versão:** 1.0
**Status:** Pronto para execução

---

## 📋 CONTEXTO

Temos um sistema **Agent BI** em Streamlit funcionando perfeitamente com 12 páginas. Criamos protótipos HTML demonstrando uma interface moderna estilo ChatGPT que preserva 100% das funcionalidades atuais.

**Protótipo de referência:**
`prototipo_multipaginas_completo.html` (1284 linhas)

**Objetivo:**
Implementar a nova interface no Streamlit mantendo toda a lógica Python existente.

---

## 🎯 PROMPT PARA IA/DESENVOLVEDOR

```
# TAREFA: Implementar Interface Estilo ChatGPT no Streamlit

## CONTEXTO
Tenho um sistema Agent BI funcionando em Streamlit com 12 páginas.
Criei um protótipo HTML (`prototipo_multipaginas_completo.html`) mostrando
como quero que a interface fique - estilo ChatGPT com tema escuro.

## OBJETIVO
Aplicar o design do protótipo HTML no Streamlit MANTENDO 100% da lógica Python atual.

## ARQUIVOS IMPORTANTES

### 1. Protótipo HTML (REFERÊNCIA VISUAL)
- Arquivo: `prototipo_multipaginas_completo.html`
- Contém: Design completo, cores, estilos, layout
- USAR COMO: Referência visual e de cores

### 2. Sistema Atual (NÃO MODIFICAR LÓGICA)
- Arquivo principal: `streamlit_app.py`
- 12 páginas em: `pages/*.py`
- Config atual: `.streamlit/config.toml`

### 3. Documentação Técnica
- Implementação: `docs/implementacoes/IMPLEMENTACAO_PROTOTIPOS_UI_CHATGPT_20251020.md`
- Índice: `INDICE_PROTOTIPOS_UI_20251020.md`
- Resumo: `RESUMO_EXECUTIVO_PROTOTIPOS_20251020.md`

## REQUISITOS CRÍTICOS

### ✅ DEVE FAZER
1. Aplicar tema escuro (cores do protótipo)
2. Estilizar mensagens de chat (user vs assistant)
3. Customizar sidebar (cores, espaçamento)
4. Aplicar CSS nos gráficos Plotly
5. Estilizar tabelas e inputs
6. Manter todas as 12 páginas funcionando
7. Preservar 100% da lógica Python

### ❌ NÃO DEVE FAZER
1. Modificar lógica de negócio Python
2. Mudar estrutura de dados
3. Alterar APIs ou integrações
4. Remover funcionalidades
5. Quebrar funcionalidades existentes

## ABORDAGEM RECOMENDADA

### Opção 1: CSS Customizado (RECOMENDADA - 2-4 horas)

**Passo 1: Atualizar `.streamlit/config.toml`**

```toml
[theme]
primaryColor = "#10a37f"
backgroundColor = "#343541"
secondaryBackgroundColor = "#444654"
textColor = "#ececf1"
font = "sans serif"

[ui]
hideTopBar = false
hideSidebarNav = false
```

**Passo 2: Adicionar CSS em `streamlit_app.py` (APÓS os imports)**

```python
import streamlit as st

# ============================================================================
# CSS CUSTOMIZADO - TEMA CHATGPT
# Baseado em: prototipo_multipaginas_completo.html
# ============================================================================

st.markdown("""
<style>
/* ==================== GLOBAL ==================== */
:root {
    --bg-primary: #343541;
    --bg-secondary: #444654;
    --bg-sidebar: #202123;
    --bg-card: #2a2b32;
    --bg-input: #40414f;
    --border-color: #444654;
    --text-primary: #ececf1;
    --text-secondary: #8e8ea0;
    --color-primary: #10a37f;
    --color-secondary: #5436DA;
    --color-danger: #ef4444;
}

/* ==================== SIDEBAR ==================== */
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
}

section[data-testid="stSidebar"] > div {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}

/* User Info no Sidebar */
section[data-testid="stSidebar"] .element-container {
    color: var(--text-primary) !important;
}

/* Botões no Sidebar */
section[data-testid="stSidebar"] button {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}

section[data-testid="stSidebar"] button:hover {
    background-color: var(--bg-secondary) !important;
    border-color: var(--color-primary) !important;
}

/* ==================== CHAT MESSAGES ==================== */
/* Mensagem do Usuário */
.stChatMessage[data-testid="user-message"] {
    background-color: transparent !important;
}

/* Mensagem do Assistente */
.stChatMessage[data-testid="assistant-message"] {
    background-color: var(--bg-secondary) !important;
}

/* Avatares */
.stChatMessage .stAvatar {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
}

/* Avatar do Usuário */
[data-testid="user-message"] .stAvatar {
    background-color: var(--color-primary) !important;
}

/* Avatar do Assistente */
[data-testid="assistant-message"] .stAvatar {
    background-color: var(--color-secondary) !important;
}

/* ==================== INPUT AREA ==================== */
.stChatInput textarea {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 16px !important;
}

.stChatInput textarea:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
}

/* ==================== BOTÕES ==================== */
.stButton button {
    background-color: var(--color-primary) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    background-color: #0d8a6a !important;
}

/* Botão Secundário */
.stButton[data-baseweb="button"][kind="secondary"] button {
    background-color: transparent !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* ==================== CARDS E CONTAINERS ==================== */
div[data-testid="stVerticalBlock"] > div {
    background-color: transparent !important;
}

.element-container {
    color: var(--text-primary) !important;
}

/* Info boxes */
div[data-testid="stNotification"] {
    background-color: var(--bg-card) !important;
    border-left: 3px solid var(--color-primary) !important;
    border-radius: 6px !important;
}

/* ==================== GRÁFICOS PLOTLY ==================== */
.js-plotly-plot {
    background-color: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* ==================== TABELAS ==================== */
.stDataFrame {
    background-color: var(--bg-card) !important;
    border-radius: 8px !important;
}

.stDataFrame table {
    color: var(--text-primary) !important;
}

.stDataFrame thead tr {
    background-color: var(--bg-sidebar) !important;
    border-bottom: 2px solid var(--color-primary) !important;
}

.stDataFrame tbody tr {
    border-bottom: 1px solid var(--border-color) !important;
}

.stDataFrame tbody tr:hover {
    background-color: rgba(16, 163, 127, 0.05) !important;
}

/* ==================== INPUTS ==================== */
input, textarea, select {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
}

/* ==================== MÉTRICAS ==================== */
div[data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 14px !important;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 8px !important;
    height: 8px !important;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary) !important;
}

::-webkit-scrollbar-thumb {
    background: #565869 !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: #6e6e80 !important;
}

/* ==================== TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 6px 6px 0 0 !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--color-primary) !important;
    border-color: var(--color-primary) !important;
}

/* ==================== EXPANDER ==================== */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
}

.streamlit-expanderContent {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
}

/* ==================== HEADER ==================== */
header[data-testid="stHeader"] {
    background-color: var(--bg-primary) !important;
}

/* ==================== RESPONSIVO ==================== */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }

    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0);
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FIM DO CSS CUSTOMIZADO
# ============================================================================

# ... resto do código streamlit_app.py continua igual ...
```

**Passo 3: Atualizar Gráficos Plotly (em TODAS as funções que criam gráficos)**

Onde você tem:
```python
fig = px.bar(df, x='segmento', y='vendas')
st.plotly_chart(fig)
```

Substituir por:
```python
fig = px.bar(df, x='segmento', y='vendas')

# Aplicar tema escuro
fig.update_layout(
    plot_bgcolor='#2a2b32',
    paper_bgcolor='#2a2b32',
    font=dict(color='#ececf1'),
    xaxis=dict(
        gridcolor='#444654',
        tickfont=dict(color='#ececf1')
    ),
    yaxis=dict(
        gridcolor='#444654',
        tickfont=dict(color='#ececf1')
    ),
    margin=dict(l=60, r=40, t=40, b=80),
    hoverlabel=dict(
        bgcolor='#2a2b32',
        bordercolor='#10a37f',
        font=dict(color='#ececf1')
    )
)

st.plotly_chart(fig, use_container_width=True)
```

**Passo 4: Testar em TODAS as 12 páginas**

Execute e teste:
```bash
streamlit run streamlit_app.py
```

Navegue por todas as páginas:
- ✅ Chat BI
- ✅ Métricas
- ✅ Gráficos Salvos
- ✅ Monitoramento
- ✅ Transferências
- ✅ Relatório Transferências
- ✅ Exemplos
- ✅ Ajuda
- ✅ Alterar Senha
- ✅ Gemini Playground
- ✅ Sistema Aprendizado
- ✅ Painel Administração
- ✅ Diagnóstico DB

**Passo 5: Ajustes Finos (se necessário)**

Se algum elemento não estiver com a cor correta, inspecione no navegador:
1. Abra DevTools (F12)
2. Inspecione o elemento
3. Veja qual classe CSS ele tem
4. Adicione CSS customizado para essa classe

## VALIDAÇÃO

### Checklist de Sucesso
- [ ] Tema escuro aplicado em todas as páginas
- [ ] Sidebar com cor #202123
- [ ] Mensagens do chat com backgrounds alternados
- [ ] Avatares estilizados (verde usuário, roxo assistente)
- [ ] Gráficos Plotly com tema escuro
- [ ] Tabelas com hover effect
- [ ] Inputs com borda verde no focus
- [ ] Scrollbar customizada
- [ ] Botões com cor #10a37f
- [ ] ZERO funcionalidades quebradas
- [ ] ZERO erros no console

### Testes de Regressão
Execute e verifique que funcionam:
```bash
# Teste 1: Query simples
"qual o produto mais vendido?"

# Teste 2: Query com gráfico
"gere gráfico de vendas por segmento"

# Teste 3: Navegação
Visite todas as 12 páginas

# Teste 4: Sidebar
Teste logout, perguntas rápidas, painel admin

# Teste 5: Responsividade
Redimensione a janela (mobile, tablet, desktop)
```

## ROLLBACK (Se algo der errado)

```bash
# 1. Parar Streamlit
Ctrl+C

# 2. Reverter arquivos
git checkout HEAD~1 .streamlit/config.toml
git checkout HEAD~1 streamlit_app.py

# 3. Restart
streamlit run streamlit_app.py
```

## TEMPO ESTIMADO

- ✅ Passo 1 (config.toml): 5 minutos
- ✅ Passo 2 (CSS): 30 minutos
- ✅ Passo 3 (Plotly): 1 hora (todos os gráficos)
- ✅ Passo 4 (Testes): 1 hora
- ✅ Passo 5 (Ajustes): 30 minutos

**TOTAL: 2-4 horas**

## ENTREGÁVEIS

Ao final, você deve ter:
1. `.streamlit/config.toml` atualizado
2. `streamlit_app.py` com CSS customizado
3. Todos os gráficos com tema escuro
4. Todas as 12 páginas funcionando
5. Screenshots antes/depois
6. Documentação de mudanças

## REFERÊNCIAS

- Protótipo: `prototipo_multipaginas_completo.html`
- Doc técnica: `docs/implementacoes/IMPLEMENTACAO_PROTOTIPOS_UI_CHATGPT_20251020.md`
- Cores: Seção "ESPECIFICAÇÕES DE DESIGN" na doc técnica

## PERGUNTAS FREQUENTES

**P: Preciso instalar algo novo?**
R: Não. Apenas CSS customizado.

**P: Vai quebrar algo?**
R: Não, se seguir exatamente o prompt. CSS não afeta lógica Python.

**P: E se não funcionar?**
R: Use o rollback acima para voltar ao estado anterior.

**P: Posso modificar as cores?**
R: Sim! Altere as variáveis CSS no `:root`.

**P: Funciona no Streamlit Cloud?**
R: Sim! O `.streamlit/config.toml` funciona no cloud também.

## SUCESSO ESPERADO

Antes:
- Interface Streamlit padrão (cinza claro)
- Tema básico

Depois:
- Interface ChatGPT (tema escuro)
- Moderna e profissional
- 100% funcionalidades preservadas

---

**IMPORTANTE:** Não modifique NENHUMA lógica Python. Apenas CSS e config.toml.
```

---

## 📝 COMO USAR ESTE PROMPT

### Opção 1: Copiar e Colar para IA
1. Copie todo o conteúdo da seção "PROMPT PARA IA/DESENVOLVEDOR" acima
2. Cole em ChatGPT, Claude, ou outra IA
3. A IA terá todas as instruções para implementar

### Opção 2: Entregar para Desenvolvedor
1. Envie este arquivo completo para o desenvolvedor
2. Ele seguirá os passos detalhados
3. Tempo estimado: 2-4 horas

### Opção 3: Implementar Você Mesmo
1. Siga os 5 passos na seção "ABORDAGEM RECOMENDADA"
2. Use o checklist de validação
3. Execute os testes de regressão

---

## ⚡ INÍCIO RÁPIDO (COMANDOS DIRETOS)

```bash
# 1. Fazer backup
cd C:\Users\André\Documents\Agent_Solution_BI
mkdir backup_before_ui_implementation
copy .streamlit\config.toml backup_before_ui_implementation\
copy streamlit_app.py backup_before_ui_implementation\

# 2. Editar arquivos
# - Edite .streamlit/config.toml (veja Passo 1)
# - Edite streamlit_app.py (veja Passo 2)

# 3. Testar
streamlit run streamlit_app.py

# 4. Se algo der errado, reverter
copy backup_before_ui_implementation\config.toml .streamlit\
copy backup_before_ui_implementation\streamlit_app.py .
```

---

## 🎯 MÉTRICAS DE SUCESSO

Após implementação, verifique:

| Métrica | Como Verificar | Status |
|---------|----------------|--------|
| **Tema escuro aplicado** | Abrir app, ver cores | [ ] |
| **12 páginas funcionando** | Navegar por todas | [ ] |
| **Gráficos com tema** | Ver gráficos Plotly | [ ] |
| **Zero erros console** | F12 → Console vazio | [ ] |
| **Responsivo** | Testar mobile/tablet | [ ] |
| **Sidebar estilizado** | Ver cor #202123 | [ ] |
| **Chat alternado** | Ver msgs user/assistant | [ ] |

**Critério de aprovação:** Todas as métricas ✅

---

**Data de criação:** 20/10/2025
**Versão:** 1.0
**Status:** ✅ PRONTO PARA USO
**Tempo estimado de implementação:** 2-4 horas
**Complexidade:** Baixa
**Risco:** Muito Baixo (apenas CSS)
