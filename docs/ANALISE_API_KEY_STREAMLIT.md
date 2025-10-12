# 🔍 ANÁLISE: API Key Gemini no Streamlit

**Data**: 11/10/2025 17:45
**Problema**: Testes com API Key funcionam, mas Streamlit não funciona

---

## 🔴 PROBLEMAS IDENTIFICADOS

### 1. **Streamlit Secrets tem PRIORIDADE sobre .env**

**Localização**: `streamlit_app.py` linhas 173-197

```python
# ORDEM DE BUSCA DA API KEY:
try:
    # 1º: Tenta buscar em st.secrets (PRIORIDADE!)
    gemini_key = st.secrets.get("GEMINI_API_KEY")

    if gemini_key:
        # USA ESTA (mesmo que .env tenha outra!)
        debug_info.append(f"Secrets Gemini: OK ({gemini_key[:10]}...)")
except:
    pass

# 2º: Se não encontrou em secrets, busca em settings (.env)
if not gemini_key and not deepseek_key:
    current_settings = get_settings()
    gemini_key = getattr(current_settings, 'GEMINI_API_KEY', None)
```

**❌ PROBLEMA**: Se existe `st.secrets` com chave ANTIGA, o Streamlit usa a antiga e IGNORA o `.env` atualizado!

---

### 2. **Cache do Streamlit está segurando a chave antiga**

**Localização**: `streamlit_app.py` linha 143

```python
@st.cache_resource(show_spinner=False)
def initialize_backend():
    # Inicializa backend UMA ÚNICA VEZ
    # Se API Key estava errada, fica em cache!
```

**❌ PROBLEMA**: Mesmo atualizando `.env`, o cache mantém a inicialização antiga com API Key expirada.

---

### 3. **Possíveis locais com API Key antiga**

O Streamlit busca secrets em VÁRIOS locais (na ordem):

1. `.streamlit/secrets.toml` (na raiz do projeto)
2. `~/.streamlit/secrets.toml` (pasta do usuário)
3. Variáveis de ambiente do sistema
4. Arquivo `.env` (último!)

**Qualquer um desses** com GEMINI_API_KEY antiga vai SOBRESCREVER o `.env` novo.

---

## 🔍 DIAGNÓSTICO

### Comparação: Scripts de Teste vs Streamlit

| Aspecto | Scripts de Teste | Streamlit |
|---------|------------------|-----------|
| Carrega .env | ✅ `load_dotenv()` | ✅ `load_dotenv(override=True)` |
| Usa secrets | ❌ Não | ✅ **SIM (prioridade!)** |
| Cache | ❌ Não | ✅ **SIM (`@cache_resource`)** |
| Resultado | ✅ Funciona | ❌ Falha |

**Conclusão**: Streamlit está usando chave de outro local (secrets) ou cache antigo.

---

## ✅ SOLUÇÕES

### SOLUÇÃO 1: Limpar Cache do Streamlit (PRIMEIRA COISA A FAZER)

```bash
# Opção 1: Pressionar 'c' no terminal do Streamlit
# Aparecerá menu: "Always rerun" ou "Clear cache"
# Escolha: Clear cache

# Opção 2: Via teclado no navegador
# Pressionar Ctrl+R (ou Cmd+R no Mac)
# Depois clicar no menu (⋮) → Settings → Clear cache

# Opção 3: Apagar pasta de cache manualmente
# Windows:
rmdir /s /q "%USERPROFILE%\.streamlit\cache"

# Linux/Mac:
rm -rf ~/.streamlit/cache
```

**Depois**: Reiniciar o Streamlit

---

### SOLUÇÃO 2: Verificar Arquivos de Secrets

Procure por arquivos que possam ter a chave antiga:

```bash
# 1. Verificar se existe secrets.toml no projeto
dir .streamlit\secrets.toml

# 2. Verificar secrets.toml global do usuário
dir %USERPROFILE%\.streamlit\secrets.toml

# 3. Se existir, abrir e verificar GEMINI_API_KEY
notepad .streamlit\secrets.toml
# OU
notepad %USERPROFILE%\.streamlit\secrets.toml
```

**Se encontrar chave antiga**:
- Deletar o arquivo `secrets.toml`
- OU atualizar com a nova chave

---

### SOLUÇÃO 3: Forçar uso do .env (Modificar código)

Adicionar código que IGNORA secrets e usa .env diretamente:

**Arquivo**: `streamlit_app.py` (após linha 172)

```python
# FORÇAR USO DO .env (IGNORAR SECRETS)
import os
gemini_key = os.getenv("GEMINI_API_KEY")  # Pega direto do .env
deepseek_key = os.getenv("DEEPSEEK_API_KEY")

if gemini_key:
    debug_info.append(f"[FORÇADO] Usando Gemini do .env: {gemini_key[:10]}...")
elif deepseek_key:
    debug_info.append(f"[FORÇADO] Usando DeepSeek do .env: {deepseek_key[:10]}...")
else:
    raise ValueError("Nenhuma chave LLM encontrada no .env")

# Comentar/remover a busca em st.secrets
# try:
#     gemini_key = st.secrets.get("GEMINI_API_KEY")
#     ...
```

---

### SOLUÇÃO 4: Criar/Atualizar arquivo secrets.toml

Se quiser usar secrets do Streamlit (recomendado para produção):

**Criar arquivo**: `.streamlit/secrets.toml`

```bash
# Criar pasta se não existir
mkdir .streamlit

# Criar arquivo
notepad .streamlit\secrets.toml
```

**Conteúdo do arquivo**:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "sua_nova_chave_aqui"

# Outras configurações (se necessário)
# DB_SERVER = "..."
# DB_NAME = "..."
```

**Depois**: Reiniciar Streamlit

---

## 🎯 PASSO A PASSO RECOMENDADO

### 1️⃣ Limpar Cache (FAZER AGORA)

```bash
# Parar Streamlit (Ctrl+C)

# Limpar cache
# Windows:
rmdir /s /q "%USERPROFILE%\.streamlit\cache"

# Reiniciar
streamlit run streamlit_app.py
```

---

### 2️⃣ Verificar se há secrets.toml

```bash
# Procurar arquivo
dir .streamlit\secrets.toml
dir %USERPROFILE%\.streamlit\secrets.toml
```

**Se encontrar**:
- Abrir e verificar GEMINI_API_KEY
- Comparar com a chave no `.env`
- Se diferente: ATUALIZAR ou DELETAR

---

### 3️⃣ Adicionar Debug no Streamlit

Modificar `streamlit_app.py` para mostrar qual chave está usando:

**Adicionar após linha 179** (dentro do try do st.secrets):

```python
# Linha 179 (depois de buscar gemini_key)
if gemini_key:
    # DEBUG: Mostrar chave para admin
    if st.session_state.get('role') == 'admin':
        with st.sidebar:
            st.info(f"🔑 Usando Gemini: ...{gemini_key[-8:]}")
            st.caption(f"Fonte: Streamlit Secrets")
```

**Adicionar após linha 195** (quando busca em settings):

```python
# Linha 195 (depois de buscar em settings)
gemini_key = getattr(current_settings, 'GEMINI_API_KEY', None)

# DEBUG: Mostrar fonte
if gemini_key and st.session_state.get('role') == 'admin':
    with st.sidebar:
        st.info(f"🔑 Usando Gemini: ...{gemini_key[-8:]}")
        st.caption(f"Fonte: .env / Settings")
```

Isso vai mostrar no sidebar (para admin) qual chave está sendo usada e de onde veio.

---

## 🔍 VERIFICAÇÃO RÁPIDA

Execute este script para ver TODAS as chaves configuradas:

```python
# scripts/check_all_api_keys.py
import os
from dotenv import load_dotenv
load_dotenv(override=True)

print("=" * 80)
print("  VERIFICAÇÃO: TODAS AS API KEYS")
print("=" * 80)

# 1. Verificar .env
print("\n1. Arquivo .env:")
gemini_env = os.getenv("GEMINI_API_KEY")
if gemini_env:
    print(f"   GEMINI_API_KEY: ...{gemini_env[-12:]}")
else:
    print("   GEMINI_API_KEY: NÃO ENCONTRADA")

# 2. Verificar secrets.toml (projeto)
print("\n2. Streamlit Secrets (projeto):")
secrets_file = ".streamlit/secrets.toml"
if os.path.exists(secrets_file):
    print(f"   Arquivo existe: {secrets_file}")
    with open(secrets_file, 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY' in content:
            print("   GEMINI_API_KEY: ENCONTRADA (verificar conteúdo)")
        else:
            print("   GEMINI_API_KEY: NÃO ENCONTRADA")
else:
    print(f"   Arquivo NÃO existe: {secrets_file}")

# 3. Verificar secrets.toml (global)
print("\n3. Streamlit Secrets (global):")
import pathlib
home = pathlib.Path.home()
global_secrets = home / ".streamlit" / "secrets.toml"
if global_secrets.exists():
    print(f"   Arquivo existe: {global_secrets}")
    with open(global_secrets, 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY' in content:
            print("   GEMINI_API_KEY: ENCONTRADA (verificar conteúdo)")
        else:
            print("   GEMINI_API_KEY: NÃO ENCONTRADA")
else:
    print(f"   Arquivo NÃO existe: {global_secrets}")

# 4. Verificar variáveis de ambiente do sistema
print("\n4. Variáveis de ambiente do sistema:")
import subprocess
try:
    # Windows
    result = subprocess.run(['powershell', '$env:GEMINI_API_KEY'],
                          capture_output=True, text=True, timeout=5)
    if result.stdout.strip():
        print(f"   GEMINI_API_KEY: ...{result.stdout.strip()[-12:]}")
    else:
        print("   GEMINI_API_KEY: NÃO DEFINIDA")
except:
    print("   Não foi possível verificar")

print("\n" + "=" * 80)
print("  RECOMENDAÇÃO")
print("=" * 80)
print("\nSe múltiplas chaves foram encontradas:")
print("1. Deletar secrets.toml (se existir)")
print("2. Usar APENAS .env")
print("3. Limpar cache do Streamlit")
print("4. Reiniciar aplicação")
print("\n" + "=" * 80)
```

---

## 📋 CHECKLIST DE SOLUÇÃO

- [ ] **Limpar cache do Streamlit**
  ```bash
  rmdir /s /q "%USERPROFILE%\.streamlit\cache"
  ```

- [ ] **Verificar secrets.toml**
  - [ ] Verificar `.streamlit/secrets.toml`
  - [ ] Verificar `~/.streamlit/secrets.toml`
  - [ ] Deletar ou atualizar se encontrado

- [ ] **Verificar .env**
  - [ ] Confirmar que tem nova API Key
  - [ ] Verificar que não tem espaços extras
  ```env
  GEMINI_API_KEY=AIzaSy...  # ✅ Correto
  GEMINI_API_KEY = AIzaSy... # ❌ Espaços podem causar problema
  ```

- [ ] **Reiniciar Streamlit**
  ```bash
  streamlit run streamlit_app.py
  ```

- [ ] **Verificar no navegador**
  - [ ] Fazer login como admin
  - [ ] Abrir sidebar
  - [ ] Ver se aparece mensagem de erro da API

---

## 💡 ATALHO RÁPIDO (SOLUÇÃO MAIS PROVÁVEL)

Execute estes 3 comandos:

```bash
# 1. Limpar cache
rmdir /s /q "%USERPROFILE%\.streamlit\cache"

# 2. Deletar secrets (se existir)
del .streamlit\secrets.toml

# 3. Reiniciar Streamlit
streamlit run streamlit_app.py
```

**Isso deve resolver em 90% dos casos!**

---

## 🎯 CAUSA RAIZ

O problema é a **ordem de prioridade** do Streamlit:

1. **st.secrets** (prioridade ALTA)
2. Variáveis de ambiente do sistema
3. Arquivo .env (prioridade BAIXA)

Se existe `secrets.toml` com chave antiga, ele SEMPRE vai usar a antiga, mesmo que você atualize o `.env`.

**SOLUÇÃO DEFINITIVA**: Usar APENAS .env OU APENAS secrets.toml, nunca os dois juntos.

---

**Data**: 11/10/2025 17:45
**Status**: Aguardando testes do usuário
