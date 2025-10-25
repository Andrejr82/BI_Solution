# 🗄️ Configuração de Banco de Dados no Streamlit Cloud

## 📋 Visão Geral

O sistema Agent_BI possui **dois modos de operação**:

1. **🌤️ Modo Cloud** - Autenticação hardcoded (sem banco de dados)
2. **🗄️ Modo SQL Server** - Autenticação completa com banco de dados

O sistema detecta automaticamente qual modo usar baseado nas credenciais disponíveis.

---

## ✅ Status Atual

### **Configuração Implementada:**
- ✅ Fallback automático para modo cloud
- ✅ Carregamento de secrets do Streamlit Cloud
- ✅ Validação de credenciais em tempo real
- ✅ Página de diagnóstico (`9_Diagnostico_DB.py`)

### **Usuários Disponíveis (Modo Cloud):**
```python
admin / admin      # Role: admin
user / user123     # Role: user
cacula / cacula123 # Role: user
```

---

## 🔧 Como Configurar SQL Server no Streamlit Cloud

### **Passo 1: Acessar Secrets**

1. Vá para [Streamlit Cloud](https://share.streamlit.io/)
2. Selecione seu app
3. Clique em **Settings** → **Secrets**

### **Passo 2: Adicionar Credenciais**

Cole o seguinte no editor de secrets (substituindo pelos valores reais):

```toml
# ===================================
# Configuração de Banco de Dados
# ===================================

DB_SERVER = "seu_servidor.database.windows.net"
DB_NAME = "Projeto_Caculinha"
DB_USER = "AgenteVirtual"
DB_PASSWORD = "sua_senha_secreta"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_TRUST_SERVER_CERTIFICATE = "yes"

# ===================================
# LLM APIs (obrigatório)
# ===================================

GEMINI_API_KEY = "AIzaSy..."
DEEPSEEK_API_KEY = "sk-af1b..."
LLM_MODEL_NAME = "gemini-2.5-flash"
```

### **Passo 3: Salvar e Redeployar**

1. Clique em **Save**
2. O app irá reiniciar automaticamente
3. As credenciais estarão disponíveis via `st.secrets`

---

## 🧪 Testar Conectividade

### **Opção 1: Página de Diagnóstico (Recomendado)**

1. Faça login como **admin**
2. Acesse **Diagnóstico de Banco de Dados** no menu
3. Clique em **🔌 Testar Conexão com SQL Server**

A página mostrará:
- ✅ Credenciais detectadas
- ✅ String de conexão (mascarada)
- ✅ Teste de conectividade
- ✅ Lista de tabelas disponíveis

### **Opção 2: Via Código**

```python
from core.config.safe_settings import get_safe_settings

settings = get_safe_settings()

if settings.is_database_available():
    print("✅ Banco configurado!")
    print(f"Server: {settings.DB_SERVER}")
    print(f"Database: {settings.DB_NAME}")
else:
    print("🌤️ Modo cloud ativo")
```

---

## 🔍 Como o Sistema Detecta o Modo

### **Arquivo: `core/config/safe_settings.py`**

```python
def _get_secret_or_env(self, key, default=""):
    """Prioriza Streamlit secrets, fallback para .env"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            value = st.secrets[key]
            if value:
                return value
    except:
        pass

    return os.getenv(key, default)
```

### **Arquivo: `core/database/sql_server_auth_db.py`**

```python
def autenticar_usuario(username, password):
    """Autentica com SQL Server ou fallback local"""

    if not is_database_configured():
        return _autenticar_local(username, password)  # Modo cloud

    # Modo SQL Server
    conn = get_db_connection()
    # ... autentica no banco
```

---

## ⚠️ Problemas Comuns

### **1. "Banco de dados não disponível"**

**Causa:** Credenciais não configuradas nos Secrets

**Solução:**
1. Verifique se TODOS os campos estão preenchidos:
   - `DB_SERVER`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

2. Não deixe valores vazios como `DB_SERVER = ""`

### **2. "Erro de conexão SQL Server"**

**Causa:** Firewall bloqueando Streamlit Cloud

**Solução:**
1. No Azure SQL Server, vá em **Firewall and virtual networks**
2. Adicione regra permitindo IPs do Streamlit Cloud:
   - Nome: `Streamlit-Cloud`
   - Start IP: `0.0.0.0`
   - End IP: `255.255.255.255`

   ⚠️ **Não recomendado para produção!** Use IP ranges específicos.

### **3. "Driver ODBC não disponível"**

**Causa:** Driver não instalado no ambiente Streamlit Cloud

**Solução:**
1. Verifique se `pyodbc` está em `requirements.txt`
2. No Streamlit Cloud, o driver **ODBC 17** está disponível por padrão
3. Se não funcionar, tente:
   ```toml
   DB_DRIVER = "ODBC Driver 18 for SQL Server"
   ```

---

## 📊 Monitoramento

### **Logs Disponíveis:**

```python
# Ver modo de operação
if settings.is_database_available():
    logger.info("🗄️ Modo SQL Server ativo")
else:
    logger.info("🌤️ Modo Cloud ativo")
```

### **Métricas na UI:**

- **Página Monitoramento** → Status dos Serviços
  - Backend LangGraph
  - Banco de Dados SQL
  - LLMs (Gemini/DeepSeek)

---

## 🚀 Boas Práticas

1. **Desenvolvimento Local:**
   - Use arquivo `.env` com credenciais de desenvolvimento
   - Não comite `.env` no Git

2. **Streamlit Cloud:**
   - Configure secrets via interface web
   - Use variáveis diferentes para dev/prod

3. **Segurança:**
   - Nunca exponha senhas em logs
   - Use `TrustServerCertificate=yes` apenas para Azure SQL
   - Rotacione credenciais periodicamente

4. **Fallback:**
   - Sistema funciona mesmo sem banco
   - Usuários hardcoded para demos/testes
   - Migração automática quando banco estiver disponível

---

## 📝 Checklist de Deploy

- [ ] Secrets configurados no Streamlit Cloud
- [ ] Firewall do SQL Server liberado
- [ ] Teste de conectividade executado com sucesso
- [ ] Página de diagnóstico acessível
- [ ] Logs verificados (sem erros de conexão)
- [ ] Usuários conseguem autenticar

---

## 🔗 Referências

- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Azure SQL Firewall Rules](https://learn.microsoft.com/en-us/azure/azure-sql/database/firewall-configure)
- [PyODBC Connection Strings](https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows)

---

*Última atualização: 2025-10-02*
