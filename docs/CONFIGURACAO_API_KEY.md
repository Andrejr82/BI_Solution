# 🔑 Configuração de API Key - Onde Configurar?

## ✅ Resposta Rápida: NÃO PRECISA configurar no .env

Se você já configurou em `.streamlit/secrets.toml`, **está completo!**

---

## 🔍 Como o Sistema Carrega a Chave

O sistema tem uma **ordem de prioridade**:

### Ordem de Carregamento (do código em `safe_settings.py`):

```python
def _get_gemini_key(self):
    # 1️⃣ PRIORIDADE 1: Streamlit Secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]  # ← USA ESTE!
    except:
        pass

    # 2️⃣ PRIORIDADE 2: Arquivo .env (FALLBACK)
    key = os.getenv("GEMINI_API_KEY", "")
    return key
```

### O Que Isso Significa:

1. **PRIMEIRO** tenta carregar de `.streamlit/secrets.toml`
2. **SE NÃO ENCONTRAR**, aí tenta carregar do `.env`

---

## ✅ Você Configurou em `secrets.toml`? Então Está OK!

Se você tem isso em `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "AIzaSyC..."
```

**Está completo!** Não precisa fazer mais nada.

---

## 📁 Quando Usar Cada Arquivo?

### Use `.streamlit/secrets.toml` quando:
- ✅ Rodando aplicativo Streamlit localmente
- ✅ Deploy no Streamlit Cloud
- ✅ Quer simplicidade (recomendado!)

### Use `.env` quando:
- Rodando scripts Python sem Streamlit
- Rodando testes automatizados
- Quer usar variáveis de ambiente do sistema

---

## 🧪 Como Verificar Se Está Funcionando?

Execute o teste que criei:

```bash
python test_api_connection.py
```

**Se aparecer:**
```
[OK] API Key encontrada: AIza...3Afc
```

Significa que o sistema **encontrou e carregou** a chave corretamente!

---

## 📝 Arquivos de Configuração - Resumo

### `.streamlit/secrets.toml` (Você JÁ configurou ✅)
```toml
GEMINI_API_KEY = "sua_chave_aqui"
DEEPSEEK_API_KEY = "sua_chave_deepseek"  # opcional
```

**Vantagens:**
- ✅ Mais seguro (não commita no Git)
- ✅ Funciona com Streamlit Cloud
- ✅ Prioridade máxima

### `.env` (NÃO precisa configurar)
```bash
GEMINI_API_KEY=sua_chave_aqui
DEEPSEEK_API_KEY=sua_chave_deepseek
```

**Quando usar:**
- Apenas se NÃO estiver usando Streamlit
- Scripts standalone
- Testes sem Streamlit

---

## ⚠️ IMPORTANTE: Segurança

Ambos os arquivos estão no `.gitignore`:

```gitignore
.env
.streamlit/secrets.toml
```

Isso garante que suas chaves **NUNCA** sejam commitadas no Git.

---

## 🎯 Conclusão

### Você configurou em `.streamlit/secrets.toml`?

✅ **SIM** → Está perfeito! Não precisa fazer mais nada.

❌ **NÃO** → Configure APENAS no `secrets.toml`, não precisa do `.env`

---

## 🚀 Próximo Passo

Agora que você configurou a chave:

```bash
python test_api_connection.py
```

Se o teste passar, você está pronto para usar o sistema! 🎉

---

**Resumindo:**
- ✅ `secrets.toml` configurado = SUFICIENTE
- ❌ `.env` = NÃO necessário (só se não usar Streamlit)
- 🎯 Prioridade: `secrets.toml` > `.env`
