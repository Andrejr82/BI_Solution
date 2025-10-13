# 🔄 Fluxo de Trabalho Git - Agent_Solution_BI

**Data:** 2025-10-13
**Status:** ✅ **OPERACIONAL**

---

## 📋 Estrutura de Branches

### **Branch `main` (Produção)**
- 🚀 **Uso:** Código estável e testado
- 🌐 **Deploy:** Streamlit Cloud (automático)
- ⚠️ **NUNCA** commitar diretamente nesta branch
- ✅ Apenas recebe merges de `gemini-deepseek-only`

### **Branch `gemini-deepseek-only` (Desenvolvimento)**
- 🛠️ **Uso:** Desenvolvimento ativo, testes, experimentos
- 👨‍💻 **Trabalho diário:** Todos os commits vão aqui
- ✅ Pode ter código experimental ou em progresso
- 🔄 Faz merge para `main` quando estável

---

## 🎯 Workflow Completo

### **1. Desenvolvimento Diário**

```bash
# Sempre trabalhe em gemini-deepseek-only
git checkout gemini-deepseek-only

# Verificar status
git status

# Fazer alterações no código...
# ...

# Adicionar arquivos
git add <arquivos>

# Commit
git commit -m "feat: Descrição da funcionalidade"

# Push para o remote
git push origin gemini-deepseek-only
```

---

### **2. Quando Feature Está Estável**

```bash
# 1. Garantir que gemini-deepseek-only está atualizada
git checkout gemini-deepseek-only
git pull origin gemini-deepseek-only

# 2. Trocar para main
git checkout main
git pull origin main

# 3. Fazer merge
git merge gemini-deepseek-only --no-edit

# 4. Push para main (DISPARA DEPLOY NO STREAMLIT CLOUD!)
git push origin main

# 5. Voltar para gemini-deepseek-only
git checkout gemini-deepseek-only
```

⚠️ **IMPORTANTE:** O push para `main` dispara **deploy automático** no Streamlit Cloud (~2-3 minutos)!

---

### **3. Verificar Deploy no Streamlit Cloud**

1. Acesse: https://share.streamlit.io/
2. Verifique o status do deploy (deve ficar verde)
3. Teste a aplicação no link público
4. Se tiver problema, pode fazer rollback:
   ```bash
   git checkout main
   git reset --hard HEAD~1  # Volta 1 commit
   git push --force origin main  # CUIDADO: Apenas se necessário!
   ```

---

## 📝 Convenções de Commit

Use prefixos semânticos para clareza:

```bash
feat:     Nova funcionalidade
fix:      Correção de bug
docs:     Documentação
style:    Formatação (não afeta lógica)
refactor: Refatoração de código
test:     Adicionar testes
chore:    Tarefas de manutenção
perf:     Melhorias de performance
```

**Exemplos:**
```bash
git commit -m "feat: Adicionar filtro de data no dashboard"
git commit -m "fix: Corrigir erro de SQL injection"
git commit -m "docs: Atualizar README com novos requisitos"
```

---

## 🔐 Proteções e Boas Práticas

### **Proteções Recomendadas (GitHub)**

No repositório GitHub → **Settings → Branches → Branch protection rules**:

**Para `main`:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ❌ Allow force pushes (manter desabilitado)

### **Boas Práticas:**

1. **NUNCA faça `git push --force` em `main`**
2. **Sempre teste em `gemini-deepseek-only` antes do merge**
3. **Use commits pequenos e descritivos**
4. **Merge para `main` apenas quando funcionalidade está completa**
5. **Sempre verifique o deploy após merge para `main`**

---

## 🚨 Situações de Emergência

### **Rollback Rápido (Deploy com Bug)**

```bash
# Opção 1: Reverter último commit (recomendado)
git checkout main
git revert HEAD
git push origin main

# Opção 2: Reset forçado (PERIGOSO!)
git checkout main
git reset --hard HEAD~1
git push --force origin main
```

### **Sincronizar Branches Desatualizadas**

```bash
# Atualizar main com remote
git checkout main
git pull origin main

# Atualizar gemini-deepseek-only com remote
git checkout gemini-deepseek-only
git pull origin gemini-deepseek-only

# Se main tiver commits que gemini não tem
git merge main
```

---

## 📊 Exemplo de Fluxo Completo

### **Cenário: Adicionar Nova Funcionalidade**

```bash
# DIA 1: Começar desenvolvimento
git checkout gemini-deepseek-only
# ... codificar nova feature ...
git add .
git commit -m "feat: Adicionar filtro avançado de relatórios"
git push origin gemini-deepseek-only

# DIA 2: Continuar desenvolvimento
# ... mais código ...
git add .
git commit -m "feat: Adicionar validações no filtro"
git push origin gemini-deepseek-only

# DIA 3: Testar e finalizar
# ... testes locais ...
git add .
git commit -m "test: Adicionar testes para filtro avançado"
git push origin gemini-deepseek-only

# DIA 4: Feature está estável → Deploy para produção
git checkout main
git pull origin main
git merge gemini-deepseek-only --no-edit
git push origin main  # 🚀 DEPLOY AUTOMÁTICO!

# Verificar deploy no Streamlit Cloud
# ... aguardar 2-3 minutos ...
# Testar no link público

# Voltar para desenvolvimento
git checkout gemini-deepseek-only
```

---

## 🎯 Checklist Antes de Merge para Main

- [ ] Código foi testado localmente
- [ ] Sem erros no console
- [ ] Funcionalidade está completa
- [ ] Documentação atualizada (se necessário)
- [ ] Commit messages estão claros
- [ ] Nenhum arquivo sensível (.env) foi adicionado
- [ ] Branch `gemini-deepseek-only` está atualizada com remote

---

## 🛠️ Comandos Úteis

```bash
# Ver histórico de commits
git log --oneline --graph --all --decorate -10

# Ver diferenças entre branches
git diff main..gemini-deepseek-only

# Ver branches locais e remotas
git branch -a

# Limpar stash
git stash clear

# Ver status detalhado
git status -v

# Desfazer último commit (mantém alterações)
git reset --soft HEAD~1

# Desfazer último commit (apaga alterações)
git reset --hard HEAD~1
```

---

## 📚 Recursos Adicionais

- **GitHub Flow:** https://guides.github.com/introduction/flow/
- **Semantic Versioning:** https://semver.org/
- **Conventional Commits:** https://www.conventionalcommits.org/

---

## ✅ Status Atual das Branches

```bash
# Verificar no terminal
git log --oneline --graph --all --decorate -5
```

**Última sincronização:** 2025-10-13
**Commit atual:** `69e3dee` (Sistema de gerenciamento de usuários cloud)
**Branches sincronizadas:** ✅ main = gemini-deepseek-only

---

**Desenvolvido por:** Claude Code
**Versão:** 1.0
**Última atualização:** 2025-10-13
