# 🔐 Credenciais Streamlit Cloud

**Data:** 2025-10-13
**Status:** ✅ Atualizado

---

## 👥 Usuários Disponíveis no Streamlit Cloud

| Usuário | Senha      | Papel | Acesso              |
|---------|------------|-------|---------------------|
| admin   | admin      | admin | ✅ Acesso completo  |
| cacula  | cacula123  | admin | ✅ Acesso completo  |
| user    | user123    | user  | ⚠️ Acesso limitado  |
| renan   | renan      | user  | ⚠️ Acesso limitado  |

---

## 🔧 Troubleshooting: Login Não Funciona

### **Problema 1: "Usuário ou senha inválidos"**

**Possíveis causas:**
1. Senha digitada incorretamente
2. Rate limit atingido (5 tentativas em 5 minutos)
3. Deploy ainda não completou
4. Cache do navegador

**Soluções:**

#### **1. Verificar senha correta:**
```
Usuário: admin
Senha: admin (minúsculas, sem espaços)
```

#### **2. Rate limit atingido:**
Se você tentou login 5 vezes com senha errada:
- ⏰ **Aguarde 5 minutos** antes de tentar novamente
- 🔄 Ou abra em **janela anônima** (Ctrl+Shift+N)

#### **3. Deploy não completou:**
- Acesse: https://share.streamlit.io/
- Verifique se o app está **verde** (Running)
- Status **amarelo/vermelho** = ainda fazendo deploy
- ⏰ Aguarde deploy completar (~2-3 minutos após push)

#### **4. Limpar cache do navegador:**
```
Chrome/Edge: Ctrl+Shift+Delete
Firefox: Ctrl+Shift+Del
Safari: Cmd+Option+E
```
Ou abra em **janela anônima/privada**

---

### **Problema 2: "Muitas tentativas de login"**

**Mensagem:**
```
⚠️ Muitas tentativas de login. Tente novamente em X segundos.
```

**Solução:**
- ⏰ Aguarde 5 minutos
- 🔄 Ou abra em janela anônima
- 🌐 Ou use outro navegador

---

### **Problema 3: Deploy com Erro**

**Sinais:**
- App não carrega
- Erro 500
- Logs mostram erros Python

**Solução:**
1. Acesse: https://share.streamlit.io/
2. Clique em **"Manage app"**
3. Verifique **Logs** para erros
4. Se houver erro, reporte no GitHub ou para o desenvolvedor

---

## 🧪 Testar Login

### **Método 1: Janela Anônima**
```
Chrome/Edge: Ctrl+Shift+N
Firefox: Ctrl+Shift+P
Safari: Cmd+Shift+N
```

1. Abra janela anônima
2. Acesse o link do Streamlit Cloud
3. Digite:
   - Usuário: `admin`
   - Senha: `admin`
4. Clique em **Entrar**

### **Método 2: Aguardar Rate Limit**
Se você tentou várias vezes:
- ⏰ Aguarde **5 minutos completos**
- 🔄 Recarregue a página (F5)
- 🔐 Tente login novamente

---

## 📝 Localização no Código

**Arquivo:** `core/auth.py`
**Linhas:** 59-64

```python
CLOUD_USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
    "cacula": {"password": "cacula123", "role": "admin"},
    "renan": {"password": "renan", "role": "user"}
}
```

---

## 🔄 Alterar Senha (Desenvolvedor)

Se quiser alterar a senha do admin:

1. **Edite `core/auth.py`:**
   ```python
   "admin": {"password": "nova_senha_aqui", "role": "admin"}
   ```

2. **Commit e push:**
   ```bash
   git add core/auth.py
   git commit -m "chore: Atualizar senha do admin"
   git checkout main
   git merge gemini-deepseek-only
   git push origin main
   git checkout gemini-deepseek-only
   ```

3. **Aguarde redeploy** (~2-3 min)

---

## ⚠️ Segurança

### **Senhas Padrão (Não Seguro!)**

As senhas atuais são **simples demais** para produção:
- ❌ `admin` / `admin`
- ❌ `cacula` / `cacula123`

### **Recomendação para Produção:**

Antes de compartilhar o link publicamente, **ALTERE AS SENHAS** para senhas fortes:

```python
CLOUD_USERS = {
    "admin": {"password": "S3nh@F0rt3!2025", "role": "admin"},
    "cacula": {"password": "C4cul4$3cur3!", "role": "admin"},
    # ...
}
```

**Ou** use **Streamlit Secrets** para gerenciar senhas de forma segura.

---

## 📞 Suporte

Se nenhuma solução funcionar:

1. **Verifique logs do Streamlit Cloud**
   - https://share.streamlit.io/ → Manage app → Logs

2. **Reporte no GitHub**
   - https://github.com/devAndrejr/Agents_Solution_BI/issues

3. **Contate o desenvolvedor**

---

**Desenvolvido por:** Claude Code
**Última atualização:** 2025-10-13
