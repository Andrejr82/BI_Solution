# 🧹 Scripts de Limpeza de Cache

Este diretório contém scripts automáticos para limpar o cache do Streamlit.

---

## 📦 Arquivos Disponíveis

### 1. `limpar_cache.bat` (Windows)
Script batch para Windows com limpeza completa.

**Como usar:**
```cmd
limpar_cache.bat
```

**O que faz:**
- ✓ Limpa cache via `streamlit cache clear`
- ✓ Remove pasta `%USERPROFILE%\.streamlit\cache`
- ✓ Remove arquivos `.pyc` e `__pycache__`
- ✓ Remove session state do Streamlit

---

### 2. `limpar_cache.py` (Multiplataforma)
Script Python que funciona em Windows, Linux e macOS.

**Como usar:**
```bash
python limpar_cache.py
```

**O que faz:**
- ✓ Limpa cache via `streamlit cache clear`
- ✓ Remove pasta `~/.streamlit/cache`
- ✓ Remove arquivos `.pyc` e `__pycache__`
- ✓ Remove session state
- ✓ Prepara limpeza do HybridAdapter

---

## 🚀 Uso Recomendado

### Quando usar?

Execute a limpeza sempre que:

1. **Página de Transferências** não mostrar produtos
2. Mudanças no código **não aparecerem** após reload
3. Erros estranhos relacionados a **dados antigos**
4. Após **atualizar** o arquivo Parquet
5. Após **modificar** o `HybridAdapter`

---

## 📋 Passo a Passo Completo

### Windows (Recomendado)

```cmd
# 1. Executar script de limpeza
limpar_cache.bat

# 2. Reiniciar Streamlit
streamlit run streamlit_app.py
```

### Linux/Mac

```bash
# 1. Executar script de limpeza
python limpar_cache.py

# 2. Reiniciar Streamlit
streamlit run streamlit_app.py
```

---

## ⚙️ Limpeza Manual (Alternativa)

Se preferir limpar manualmente:

### Via CLI
```bash
streamlit cache clear
```

### Via Interface
1. Iniciar Streamlit
2. Pressionar **C** no terminal
3. Selecionar "Clear cache"

### Via Sistema de Arquivos

**Windows:**
```cmd
rmdir /s /q %USERPROFILE%\.streamlit\cache
```

**Linux/Mac:**
```bash
rm -rf ~/.streamlit/cache
```

---

## 🐛 Troubleshooting

### Problema: "streamlit: command not found"

**Solução:**
```bash
# Instalar Streamlit
pip install streamlit

# Ou usar Python diretamente
python -m streamlit cache clear
```

### Problema: "Permission denied"

**Windows (executar como Administrador):**
```cmd
# Clicar com botão direito em limpar_cache.bat
# Selecionar "Executar como Administrador"
```

**Linux/Mac:**
```bash
sudo python limpar_cache.py
```

### Problema: Cache não é limpo

**Verificar localização:**
```python
import streamlit as st
print(st.config.get_option("server.cacheFolderPath"))
```

---

## 📊 O Que Cada Script Limpa

| Item | .bat (Win) | .py (Multi) | Manual |
|------|------------|-------------|--------|
| Cache Streamlit CLI | ✓ | ✓ | ✓ |
| Pasta cache | ✓ | ✓ | ✓ |
| Arquivos .pyc | ✓ | ✓ | ✗ |
| __pycache__ | ✓ | ✓ | ✗ |
| Session state | ✓ | ✓ | ✗ |

---

## ✅ Verificação Pós-Limpeza

Após executar o script:

1. ✓ Cache foi limpo
2. ✓ Streamlit foi reiniciado
3. ✓ Login funcionou
4. ✓ Página Transferências carregou
5. ✓ Produtos aparecem na lista
6. ✓ Problema resolvido!

---

## 📝 Notas Técnicas

### Cache do Streamlit

O Streamlit armazena cache em:
- **Windows:** `C:\Users\<user>\.streamlit\cache`
- **Linux:** `~/.streamlit/cache`
- **macOS:** `~/.streamlit/cache`

### Cache de Funções

Funções com `@st.cache_data` armazenam resultados em memória.

Para forçar recalculo, passe `ttl` (time-to-live):

```python
@st.cache_data(ttl=300)  # 5 minutos
def get_unes_disponiveis():
    ...
```

### Session State

O `st.session_state` persiste durante a sessão do usuário.

Para resetar manualmente:

```python
# Limpar todo o state
st.session_state.clear()

# Limpar item específico
if 'transfer_adapter' in st.session_state:
    del st.session_state['transfer_adapter']
```

---

## 🔗 Referências

- [Streamlit Caching](https://docs.streamlit.io/library/advanced-features/caching)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)

---

**Versão:** 1.0
**Data:** 2025-01-15
**Autor:** Agent_Solution_BI Team
