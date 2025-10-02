# 🔧 Scripts de Manutenção

Esta pasta contém scripts utilitários para manutenção e administração do projeto.

## 📄 Scripts Disponíveis

### cleanup_project.ps1
**Plataforma:** Windows PowerShell
**Propósito:** Limpa e reorganiza arquivos do projeto.

**O que faz:**
- Remove arquivos temporários
- Organiza ferramentas de desenvolvimento
- Move arquivos obsoletos para backup

**Como executar:**
```powershell
.\scripts\cleanup_project.ps1
```

⚠️ **AVISO:** Execute apenas se souber o que está fazendo. Faz mudanças em arquivos do projeto.

---

## 📋 Convenções

### Nomenclatura
- `*.ps1` - PowerShell (Windows)
- `*.sh` - Bash (Linux/Mac)
- `*.py` - Python (cross-platform)

### Categorias
- `cleanup_*` - Scripts de limpeza
- `deploy_*` - Scripts de deploy
- `migrate_*` - Scripts de migração
- `backup_*` - Scripts de backup

---

## ✅ Boas Práticas

### Antes de Executar
1. Fazer backup do projeto
2. Ler o script para entender o que faz
3. Testar em ambiente de desenvolvimento primeiro

### Ao Criar Novo Script
1. Adicionar comentários explicativos
2. Incluir mensagens de status
3. Documentar neste README
4. Fazer dry-run antes de aplicar mudanças

---

## 🔗 Links Relacionados

- [Configurações](../config/) - Arquivos de configuração
- [Documentação](../docs/) - Guias técnicos
- [README Principal](../README.md)
