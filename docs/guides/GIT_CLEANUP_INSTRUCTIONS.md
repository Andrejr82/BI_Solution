# Instruções Git - Limpeza de Arquivos

**Deploy Agent - 2025-10-17**

## Status Atual do Git

O comando `git status` mostra:
- **118 arquivos** de cache deletados (marcados com `D`)
- Múltiplos arquivos modificados
- Novos arquivos não rastreados

## Entendendo os Marcadores Git

### `D` - Deleted (Deletado)
```
D data/cache/016120b6d6fcef2fab0e3894605739e9.json
```
- Arquivo foi deletado do sistema de arquivos
- Git ainda não registrou a deleção
- Precisa ser staged para commit

### `M` - Modified (Modificado)
```
M core/agents/code_gen_agent.py
```
- Arquivo foi modificado
- Mudanças não estão staged
- Precisa de `git add` para staged

### `??` - Untracked (Não rastreado)
```
?? data/cache/0a0ec4b82070f2d7a9b99b94705cac72.json
```
- Arquivo novo, nunca foi commitado
- Git não está rastreando
- Pode ser adicionado ou ignorado

## Comandos Git para Limpeza

### 1. Verificar Status Detalhado

```bash
# Ver status completo
git status

# Ver status resumido
git status -s

# Ver arquivos deletados
git status | grep "D "

# Contar arquivos deletados
git status -s | grep "^ D" | wc -l
```

### 2. Adicionar Deleções ao Staging

```bash
# Adicionar APENAS deleções ao staging
git add -u

# Explicação:
# -u ou --update = adiciona apenas arquivos já rastreados (modificados ou deletados)
# Não adiciona arquivos novos (untracked)
```

### 3. Adicionar Todas as Mudanças

```bash
# Adicionar TUDO (modificações, deleções, novos arquivos)
git add -A

# Equivalente a:
git add --all

# Ou adicionar diretórios específicos
git add data/cache/
git add core/
```

### 4. Verificar o que Será Commitado

```bash
# Ver arquivos staged (prontos para commit)
git diff --cached --name-only

# Ver mudanças staged (com conteúdo)
git diff --cached

# Ver estatísticas
git diff --cached --stat
```

### 5. Commit das Mudanças

```bash
# Commit com mensagem descritiva
git commit -m "chore: Limpeza de arquivos de cache e reorganização de scripts"

# Commit mais detalhado
git commit -m "chore: Limpeza de arquivos temporários e reorganização

- Remove 118 arquivos de cache desatualizado
- Deleta arquivo temporário temp_read_transferencias.py
- Consolida scripts de limpeza duplicados
- Reorganiza scripts de diagnóstico em subdiretório
- Adiciona documentação de limpeza e manutenção"
```

### 6. Restaurar Arquivos Deletados (Se Necessário)

```bash
# Restaurar UM arquivo deletado
git restore data/cache/016120b6d6fcef2fab0e3894605739e9.json

# Restaurar TODOS os arquivos deletados
git restore .

# Restaurar apenas arquivos de cache
git restore data/cache/
```

### 7. Remover Arquivos do Índice Git (Sem Deletar)

```bash
# Parar de rastrear arquivo (mantém no disco)
git rm --cached temp_read_transferencias.py

# Parar de rastrear diretório inteiro
git rm --cached -r data/cache/

# Depois, adicionar ao .gitignore
echo "temp_*.py" >> .gitignore
echo "data/cache/*.json" >> .gitignore
```

## Workflow Recomendado

### Cenário 1: Confirmar Limpeza de Cache

```bash
# 1. Verificar o que será commitado
git status

# 2. Adicionar deleções de cache
git add -u data/cache/

# 3. Verificar staged
git diff --cached --stat

# 4. Commit
git commit -m "chore: Limpar cache desatualizado (118 arquivos)"

# 5. Push
git push origin main
```

### Cenário 2: Reorganização de Scripts

```bash
# 1. Adicionar novos arquivos e mudanças
git add scripts/diagnostics/
git add cleanup_project.py
git add EXECUTAR_LIMPEZA.bat

# 2. Adicionar deleções
git add -u scripts/

# 3. Commit
git commit -m "refactor: Reorganizar scripts em estrutura modular

- Move scripts de diagnóstico para scripts/diagnostics/
- Consolida scripts de limpeza
- Adiciona documentação"

# 4. Push
git push origin main
```

### Cenário 3: Limpeza Completa (Tudo de Uma Vez)

```bash
# 1. Preview do que será adicionado
git add -A --dry-run

# 2. Adicionar tudo
git add -A

# 3. Revisar staged
git status

# 4. Commit detalhado
git commit -m "chore: Limpeza completa do projeto

Arquivos Removidos:
- temp_read_transferencias.py
- 118 arquivos de cache desatualizado
- Scripts duplicados de limpeza

Reorganização:
- Scripts de diagnóstico -> scripts/diagnostics/
- Scripts de limpeza consolidados

Novos Arquivos:
- cleanup_project.py (limpeza automatizada)
- EXECUTAR_LIMPEZA.bat (interface batch)
- LIMPEZA_README.md (documentação)
- preview_cleanup.py (preview de limpeza)"

# 5. Push
git push origin main
```

## Atualizar .gitignore

### Adicionar Padrões de Exclusão

```bash
# Editar .gitignore
nano .gitignore

# Ou adicionar via echo
echo "" >> .gitignore
echo "# Arquivos temporários de limpeza" >> .gitignore
echo "temp_*.py" >> .gitignore
echo "backup_cleanup/" >> .gitignore
echo ".cleanup_report.*" >> .gitignore
```

### Aplicar .gitignore a Arquivos Já Rastreados

```bash
# Remover arquivos do índice (mantém no disco)
git rm --cached data/cache/*.json

# Commit
git commit -m "chore: Atualizar .gitignore para excluir cache"

# Push
git push origin main
```

## Comandos Úteis de Diagnóstico

### Ver Histórico de Deleções

```bash
# Ver últimas deleções
git log --diff-filter=D --summary

# Ver quando arquivo foi deletado
git log --all --full-history -- data/cache/016120b6d6fcef2fab0e3894605739e9.json
```

### Ver Tamanho do Repositório

```bash
# Tamanho total
git count-objects -vH

# Arquivos maiores
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -20
```

### Limpar Histórico (Avançado)

```bash
# CUIDADO: Reescreve histórico!
# Remover arquivo de todo o histórico
git filter-branch --index-filter 'git rm --cached --ignore-unmatch temp_read_transferencias.py' HEAD

# Limpar reflog e garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Aliases Git Úteis

Adicionar ao `~/.gitconfig`:

```ini
[alias]
    # Status resumido
    st = status -s

    # Adicionar apenas deleções
    addu = add -u

    # Ver arquivos deletados
    deleted = "!git status -s | grep '^ D'"

    # Commit com template
    cm = commit -m

    # Desfazer último commit (mantém mudanças)
    undo = reset HEAD~1 --soft

    # Limpar branches locais órfãs
    cleanup = "!git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d"
```

Usar:
```bash
git st              # Status resumido
git addu            # Adicionar apenas updates
git deleted         # Ver deletados
git cm "mensagem"   # Commit rápido
```

## Troubleshooting

### Erro: "Nothing to commit"

**Causa:** Tudo já está commitado ou não há mudanças staged.

**Solução:**
```bash
git status
git add -A
git commit -m "mensagem"
```

### Erro: "Cannot remove files"

**Causa:** Arquivo ainda existe no sistema de arquivos.

**Solução:**
```bash
# Remover arquivo primeiro
rm temp_read_transferencias.py

# Ou usar git rm (remove arquivo E staged)
git rm temp_read_transferencias.py
```

### Arquivos Não Aparecem no Git

**Causa:** Bloqueados por `.gitignore`.

**Solução:**
```bash
# Verificar se está ignorado
git check-ignore -v arquivo.py

# Forçar adição (não recomendado)
git add -f arquivo.py
```

### Desfazer Mudanças Staged

```bash
# Remover do staging (mantém mudanças)
git restore --staged arquivo.py

# Ou para todos os arquivos
git restore --staged .
```

### Desfazer Commit (Não Pushed)

```bash
# Desfazer último commit (mantém mudanças)
git reset HEAD~1 --soft

# Desfazer último commit (descarta mudanças)
git reset HEAD~1 --hard
```

## Checklist Pré-Commit

- [ ] Executar `git status` para ver mudanças
- [ ] Revisar arquivos modificados com `git diff`
- [ ] Testar código localmente
- [ ] Executar testes (se houver)
- [ ] Verificar .gitignore está atualizado
- [ ] Mensagem de commit é descritiva
- [ ] Não há credenciais ou dados sensíveis
- [ ] Branch está atualizada com main/master

## Comandos de Segurança

### Antes de Commit

```bash
# Verificar se há credenciais
git diff --cached | grep -i "password\|secret\|key\|token"

# Ver exatamente o que será commitado
git diff --cached
```

### Remover Credenciais Acidentais

```bash
# Se commitou mas NÃO fez push
git reset HEAD~1
git restore --staged arquivo_com_credencial.py

# Editar arquivo e remover credencial
nano arquivo_com_credencial.py

# Commit correto
git add arquivo_com_credencial.py
git commit -m "fix: Remove credenciais acidentais"

# Se JÁ fez push - URGENTE!
# 1. Rotacionar credenciais imediatamente
# 2. Force push (cuidado!)
git push --force origin main
```

## Recursos Adicionais

### Documentação Oficial
- [Git Documentation](https://git-scm.com/doc)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

### Tutoriais
- [Git Tutorial - Atlassian](https://www.atlassian.com/git/tutorials)
- [Learn Git Branching](https://learngitbranching.js.org/)

### Ferramentas
- [GitKraken](https://www.gitkraken.com/) - GUI para Git
- [SourceTree](https://www.sourcetreeapp.com/) - Git GUI gratuito
- [Git Graph (VS Code)](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)

---

**Última Atualização:** 2025-10-17
**Deploy Agent**
