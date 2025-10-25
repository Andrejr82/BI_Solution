# ⚡ Quick Start - Desenvolvimento

**Guia rápido de comandos diários para desenvolvimento no Agent_Solution_BI**

---

## 🚀 Iniciar Trabalho Diário

```bash
# 1. Ativar ambiente virtual
.venv\Scripts\activate

# 2. Garantir que está na branch de desenvolvimento
git checkout gemini-deepseek-only

# 3. Atualizar código
git pull origin gemini-deepseek-only

# 4. Rodar aplicação
streamlit run streamlit_app.py
```

---

## 💻 Durante o Desenvolvimento

```bash
# Ver status
git status

# Adicionar arquivos modificados
git add .

# Commit
git commit -m "feat: Descrição da alteração"

# Push
git push origin gemini-deepseek-only
```

---

## 🚀 Deploy para Produção (Streamlit Cloud)

```bash
# 1. Trocar para main
git checkout main

# 2. Atualizar
git pull origin main

# 3. Merge da branch de desenvolvimento
git merge gemini-deepseek-only --no-edit

# 4. Push (DISPARA DEPLOY!)
git push origin main

# 5. Voltar para desenvolvimento
git checkout gemini-deepseek-only
```

⏱️ **Aguardar:** 2-3 minutos para deploy automático no Streamlit Cloud

---

## 🔍 Verificar Deploy

1. Acesse: https://share.streamlit.io/
2. Verifique status: **✅ Running**
3. Teste o link público

---

## 📝 Tipos de Commit

```bash
feat:     Nova funcionalidade
fix:      Correção de bug
docs:     Documentação
refactor: Refatoração de código
test:     Adicionar testes
```

---

## 🎯 Branches

- **`gemini-deepseek-only`**: Desenvolvimento (trabalho diário)
- **`main`**: Produção (Streamlit Cloud)

---

## ⚠️ IMPORTANTE

- ❌ NUNCA commite direto em `main`
- ✅ SEMPRE trabalhe em `gemini-deepseek-only`
- ✅ Merge para `main` apenas quando estável

---

**Documentação completa:** `docs/GIT_WORKFLOW.md`
