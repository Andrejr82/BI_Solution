# ⚙️ Configurações do Projeto

Esta pasta contém templates e arquivos de configuração para diferentes ambientes.

## 📄 Arquivos

### streamlit_secrets.toml
**Propósito:** Template de secrets para Streamlit Cloud.

**Como usar:**
1. Copie TODO o conteúdo deste arquivo
2. Acesse seu app no Streamlit Cloud
3. Vá em Settings → Secrets
4. Cole o conteúdo na caixa de texto
5. Substitua os valores placeholder pelas chaves reais

**Secrets obrigatórios:**
```toml
GEMINI_API_KEY = "AIzaSy..."        # Chave do Google Gemini (LLM principal)
DEEPSEEK_API_KEY = "sk-af1b..."    # Chave do DeepSeek (LLM fallback)
LLM_MODEL_NAME = "gemini-2.5-flash" # Modelo a usar
```

**Secrets opcionais (SQL Server):**
```toml
DB_SERVER = "servidor.database.windows.net"
DB_NAME = "Projeto_Caculinha"
DB_USER = "AgenteVirtual"
DB_PASSWORD = "senha_aqui"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_TRUST_SERVER_CERTIFICATE = "yes"
```

⚠️ **IMPORTANTE:** Nunca commite este arquivo com valores reais! Use apenas como template.

---

### runtime.txt
**Propósito:** Especifica a versão do Python para Streamlit Cloud.

**Conteúdo:**
```
python-3.11.9
```

**Por que Python 3.11?**
- Compatibilidade com todas as dependências
- Melhor performance que 3.10
- Estável no Streamlit Cloud

---

## 🔐 Segurança

### ❌ NÃO faça:
- Commitar arquivos com secrets reais
- Compartilhar API keys publicamente
- Usar mesmas keys em dev e prod

### ✅ FAÇA:
- Use `.env` local para desenvolvimento
- Configure secrets no dashboard do Streamlit Cloud
- Rotate API keys periodicamente
- Use diferentes keys para ambientes diferentes

---

## 🌍 Ambientes

### Local (Desenvolvimento)
**Arquivo:** `.env` (na raiz, gitignored)
```bash
GEMINI_API_KEY=sua_chave_dev
DEEPSEEK_API_KEY=sua_chave_dev
DB_SERVER=localhost
# ...
```

### Streamlit Cloud (Produção)
**Configuração:** Dashboard → Settings → Secrets
- Usa `config/streamlit_secrets.toml` como template
- Secrets são criptografados
- Acessíveis via `st.secrets`

---

## 📋 Checklist de Configuração

### Primeira vez (Desenvolvimento)
- [ ] Copiar `.env.example` para `.env`
- [ ] Preencher variáveis no `.env`
- [ ] Testar localmente: `streamlit run streamlit_app.py`

### Primeira vez (Streamlit Cloud)
- [ ] Criar conta no Streamlit Cloud
- [ ] Conectar repositório GitHub
- [ ] Copiar conteúdo de `config/streamlit_secrets.toml`
- [ ] Colar em Settings → Secrets
- [ ] Substituir placeholders por valores reais
- [ ] Fazer deploy

### Atualizações
- [ ] Atualizar `config/streamlit_secrets.toml` template se adicionar novos secrets
- [ ] Documentar novos secrets neste README
- [ ] Atualizar secrets no Streamlit Cloud dashboard

---

## 🔗 Links Relacionados

- [Documentação de Deploy](../docs/DEPLOY_STREAMLIT_CLOUD.md)
- [Variáveis de Ambiente (.env.example)](../.env.example)
- [README Principal](../README.md)

---

## 📝 Histórico de Mudanças

### 2025-10-01
- ✅ Migração completa para Gemini + DeepSeek
- ❌ Removido `OPENAI_API_KEY` (não mais usado)
- ✅ Adicionado `LLM_MODEL_NAME` configurável
