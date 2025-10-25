# 📝 Git Cheat Sheet - Agent_Solution_BI

**Guia Rápido de Comandos Git para Desenvolvimento Local**

---

## 🚀 Início Rápido

### Verificar Estado Atual
```bash
git status                          # Ver branch atual e arquivos modificados
git branch                          # Listar branches locais
git branch -a                       # Listar todas as branches (local + remoto)
git log --oneline -10              # Ver últimos 10 commits
```

### Criar Nova Branch
```bash
git checkout main                   # Ir para main
git pull origin main               # Atualizar main
git checkout -b feature/nome-aqui  # Criar e mudar para nova branch
```

---

## 📂 Trabalhando com Arquivos

### Ver Mudanças
```bash
git status                         # Ver arquivos modificados
git diff                          # Ver todas as diferenças
git diff arquivo.py               # Ver diferenças de arquivo específico
git diff main..feature/minha      # Comparar branches
```

### Adicionar Arquivos
```bash
git add arquivo.py                # Adicionar arquivo específico
git add .                         # Adicionar tudo
git add core/                     # Adicionar pasta inteira
git add *.py                      # Adicionar por padrão
```

### Remover do Stage (antes do commit)
```bash
git reset arquivo.py              # Remover do stage (volta para modified)
git reset                         # Remover tudo do stage
```

### Descartar Mudanças
```bash
git checkout -- arquivo.py        # Descartar mudanças de arquivo (CUIDADO!)
git checkout -- .                 # Descartar TODAS as mudanças (CUIDADO!)
```

---

## 💾 Commits

### Fazer Commit
```bash
git commit -m "feat: Mensagem curta"                    # Commit simples
git commit -m "feat: Título" -m "Descrição detalhada"  # Com descrição
git commit                                              # Abre editor para mensagem
```

### Tipos de Commit (Conventional Commits)
```bash
git commit -m "feat: Nova funcionalidade"
git commit -m "fix: Correção de bug"
git commit -m "refactor: Refatoração de código"
git commit -m "test: Adicionar testes"
git commit -m "docs: Atualizar documentação"
git commit -m "style: Formatação de código"
git commit -m "perf: Melhoria de performance"
git commit -m "chore: Tarefas diversas"
```

### Desfazer Commits
```bash
git reset --soft HEAD~1           # Desfazer último commit (mantém mudanças)
git reset --hard HEAD~1           # Desfazer e DELETAR mudanças (CUIDADO!)
git reset --soft HEAD~3           # Desfazer últimos 3 commits
```

### Alterar Último Commit
```bash
git commit --amend -m "Nova mensagem"           # Alterar mensagem
git add arquivo.py && git commit --amend        # Adicionar mais arquivos
git commit --amend --no-edit                    # Adicionar sem mudar mensagem
```

---

## 🌿 Branches

### Listar e Navegar
```bash
git branch                        # Listar branches locais
git branch -a                     # Listar todas (local + remoto)
git checkout nome-branch          # Mudar para branch existente
git checkout -b nova-branch       # Criar e mudar para nova branch
```

### Deletar Branches
```bash
git branch -d nome-branch         # Deletar branch local (seguro)
git branch -D nome-branch         # Forçar deleção (CUIDADO!)
git push origin --delete branch   # Deletar branch remota
```

### Renomear Branch
```bash
git branch -m novo-nome           # Renomear branch atual
git branch -m velho novo          # Renomear outra branch
```

---

## 🔄 Sincronizar com Remoto

### Baixar Mudanças
```bash
git pull                          # Baixar e fazer merge (branch atual)
git pull origin main              # Baixar main do remoto
git fetch                         # Baixar sem fazer merge
git fetch origin                  # Baixar todas as branches
```

### Enviar Mudanças
```bash
git push                          # Enviar commits (branch atual)
git push origin branch-nome       # Enviar branch específica
git push -u origin branch-nome    # Primeira vez (cria tracking)
git push --force                  # Forçar push (CUIDADO!)
```

### Ver Remoto
```bash
git remote -v                     # Ver URLs do remoto
git remote show origin            # Ver detalhes do remoto
```

---

## 🔀 Merge e Rebase

### Merge
```bash
git checkout main                 # Ir para branch de destino
git merge feature/minha           # Fazer merge
git merge feature/minha --no-ff   # Merge sem fast-forward
```

### Rebase
```bash
git checkout feature/minha        # Ir para sua branch
git rebase main                   # Rebasear com main
git rebase --continue             # Continuar após resolver conflito
git rebase --abort                # Cancelar rebase
```

### Resolver Conflitos
```bash
# 1. Git avisa do conflito
# 2. Abrir arquivos e resolver manualmente
# 3. Depois:
git add arquivo-resolvido.py
git commit -m "merge: Resolver conflitos"
# OU se for rebase:
git rebase --continue
```

---

## 💼 Stash (Guardar Trabalho Temporário)

### Salvar e Recuperar
```bash
git stash                         # Guardar mudanças
git stash save "mensagem"         # Guardar com descrição
git stash list                    # Listar stashes salvos
git stash pop                     # Recuperar último stash (remove da lista)
git stash apply                   # Recuperar sem remover
git stash apply stash@{2}         # Recuperar stash específico
git stash drop                    # Deletar último stash
git stash clear                   # Deletar todos os stashes
```

---

## 🔍 Histórico e Log

### Ver Histórico
```bash
git log                           # Log completo
git log --oneline                 # Log resumido
git log --oneline -10             # Últimos 10 commits
git log --graph --oneline         # Log com gráfico
git log --author="Andre"          # Commits de autor
git log --since="2 weeks ago"     # Commits recentes
git log -- arquivo.py             # Histórico de arquivo
```

### Ver Mudanças Específicas
```bash
git show <commit-hash>            # Ver detalhes de commit
git show HEAD                     # Ver último commit
git show HEAD~3                   # Ver 3 commits atrás
git blame arquivo.py              # Ver quem mudou cada linha
```

---

## 🆘 Comandos de Emergência

### Voltar Arquivo Específico
```bash
git checkout <commit-hash> -- arquivo.py   # Voltar arquivo para commit antigo
git checkout HEAD -- arquivo.py            # Descartar mudanças locais
```

### Resetar Branch para Estado Remoto
```bash
git fetch origin
git reset --hard origin/main      # CUIDADO: perde mudanças locais!
```

### Recuperar Commit Deletado
```bash
git reflog                        # Ver histórico completo
git checkout <commit-hash>        # Voltar para commit
git checkout -b recuperacao       # Criar branch do commit recuperado
```

### Limpar Arquivos Não Rastreados
```bash
git clean -n                      # Ver o que seria deletado
git clean -f                      # Deletar arquivos não rastreados
git clean -fd                     # Deletar arquivos e pastas
```

---

## 🎯 Workflows Comuns

### Workflow 1: Feature Branch
```bash
# 1. Criar branch
git checkout main
git pull origin main
git checkout -b feature/nova-funcionalidade

# 2. Trabalhar
git add .
git commit -m "feat: Implementar nova funcionalidade"

# 3. Enviar
git push -u origin feature/nova-funcionalidade

# 4. Mais commits...
git add .
git commit -m "feat: Adicionar testes"
git push

# 5. Finalizar (merge)
git checkout main
git pull origin main
git merge feature/nova-funcionalidade --no-ff
git push origin main
git branch -d feature/nova-funcionalidade
```

---

### Workflow 2: Hotfix Rápido
```bash
# 1. Criar branch de hotfix
git checkout main
git pull origin main
git checkout -b hotfix/corrigir-bug-critico

# 2. Corrigir
git add arquivo-corrigido.py
git commit -m "fix: Corrigir bug crítico X"

# 3. Merge direto
git checkout main
git merge hotfix/corrigir-bug-critico
git push origin main

# 4. Limpar
git branch -d hotfix/corrigir-bug-critico
```

---

### Workflow 3: Atualizar Feature com Main
```bash
# Sua feature está desatualizada, main teve novos commits
git checkout main
git pull origin main

git checkout feature/minha
git merge main
# OU
git rebase main

# Resolver conflitos se houver
git add .
git commit -m "merge: Atualizar com main"
# OU (se rebase)
git rebase --continue
```

---

### Workflow 4: Salvar Trabalho e Mudar de Branch
```bash
# Você está no meio de algo mas precisa mudar de branch
git stash save "WIP: implementando validador"
git checkout outra-branch

# Fazer o que precisa na outra branch...

# Voltar e continuar
git checkout feature/minha
git stash pop
```

---

## 📋 Template de Mensagem de Commit

### Formato Recomendado
```
<tipo>: <título curto (50 chars max)>

<descrição opcional detalhada (72 chars por linha)>
- O que foi feito
- Por que foi feito
- Impacto esperado

<footer opcional>
Fixes #123
Refs #456
```

### Exemplo Completo
```bash
git commit -m "feat: Implementar Few-Shot Learning com PatternMatcher

- Criar data/query_patterns.json com 25 padrões de queries
- Implementar core/learning/pattern_matcher.py
- Integrar no CodeGenAgent para injeção de exemplos
- Adicionar testes unitários

Impacto esperado: +20% de precisão em queries similares

Refs #42"
```

---

## 🔐 Configuração Inicial (Se Necessário)

### Configurar Identidade
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### Ver Configuração
```bash
git config --list                 # Todas as configs
git config user.name              # Config específica
```

### Aliases Úteis
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph"

# Agora pode usar:
git st          # = git status
git co main     # = git checkout main
git lg          # = git log --oneline --graph
```

---

## 🎨 Comandos Git Bonitos (Com Cores)

### Log Bonito
```bash
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit

# Salvar como alias:
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# Usar:
git lg
```

### Status Resumido
```bash
git status -s                     # Status curto e limpo
```

---

## ⚠️ Avisos Importantes

### ❌ NUNCA Faça (Sem Certeza)
```bash
git push --force origin main      # Pode quebrar histórico de todos
git reset --hard                  # Perde mudanças permanentemente
git clean -fd                     # Deleta arquivos não rastreados
git rebase main                   # Em branch compartilhada
```

### ✅ Sempre Faça
```bash
git status                        # Antes de qualquer operação
git diff                          # Antes de commitar
git pull                          # Antes de começar a trabalhar
git branch                        # Para saber onde está
```

### 💡 Boas Práticas
```bash
# Commits pequenos e frequentes
git add arquivo.py
git commit -m "feat: Adicionar validação X"

# Testar antes de push
python -m pytest
git push

# Sempre trabalhar em branch
git checkout -b feature/minha
# NUNCA trabalhar direto na main
```

---

## 🆘 Troubleshooting

### Problema: "Your branch is ahead of 'origin/main'"
```bash
git push                          # Enviar commits locais
```

### Problema: "Your branch is behind 'origin/main'"
```bash
git pull                          # Baixar commits remotos
```

### Problema: "Merge conflict"
```bash
# 1. Abrir arquivo e resolver manualmente
# 2. Procurar por <<<<<<< e =======
# 3. Escolher versão correta
# 4. Depois:
git add arquivo-resolvido.py
git commit -m "merge: Resolver conflito"
```

### Problema: "Commitei na branch errada"
```bash
# Se ainda não fez push:
git log                           # Copiar hash do commit
git reset --hard HEAD~1           # Desfazer commit
git checkout branch-correta       # Ir para branch certa
git cherry-pick <commit-hash>     # Aplicar commit lá
```

### Problema: "Preciso desfazer push"
```bash
# CUIDADO: Só se ninguém mais baixou
git reset --hard HEAD~1
git push --force origin branch

# Melhor: Reverter criando novo commit
git revert HEAD
git push origin branch
```

---

## 📚 Recursos Úteis

### Visualizadores Git
- **GitKraken**: https://www.gitkraken.com/
- **GitHub Desktop**: https://desktop.github.com/
- **SourceTree**: https://www.sourcetreeapp.com/
- **VS Code Git**: Integrado no editor

### Documentação
- **Git Docs**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Git Flight Rules**: https://github.com/k88hudson/git-flight-rules

### Praticar
- **Learn Git Branching**: https://learngitbranching.js.org/
- **Git Exercises**: https://gitexercises.fracz.com/

---

## 🎯 Comandos Mais Usados (Top 10)

```bash
1.  git status                    # Verificar estado
2.  git add .                     # Adicionar tudo
3.  git commit -m "mensagem"      # Commitar
4.  git push                      # Enviar
5.  git pull                      # Baixar
6.  git checkout -b branch        # Criar branch
7.  git checkout branch           # Mudar branch
8.  git log --oneline            # Ver histórico
9.  git diff                      # Ver mudanças
10. git stash                     # Guardar trabalho
```

---

## 🚀 Workflow Recomendado - Agent_Solution_BI

```bash
# === DIA A DIA ===

# Manhã: Começar
git checkout main
git pull origin main
git checkout feature/llm-improvements  # Ou criar nova

# Trabalhar...
git status                        # Frequentemente
git diff                          # Antes de commitar

# Commitar frequentemente
git add arquivo.py
git commit -m "feat: Adicionar X"

# Fim do dia: Salvar
git push origin feature/llm-improvements

# === QUANDO TERMINAR FEATURE ===

# Atualizar com main
git checkout main
git pull origin main
git checkout feature/llm-improvements
git merge main

# Testes
python -m pytest
streamlit run streamlit_app.py

# Merge final
git checkout main
git merge feature/llm-improvements --no-ff
git push origin main

# Limpar
git branch -d feature/llm-improvements
git push origin --delete feature/llm-improvements
```

---

**Versão:** 1.0
**Data:** 2025-01-14
**Mantenha este arquivo sempre à mão!** 📌

---

💡 **Dica:** Imprima ou tenha este arquivo sempre aberto enquanto trabalha com Git!
