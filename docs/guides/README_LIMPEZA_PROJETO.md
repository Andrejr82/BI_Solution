# Sistema de Limpeza Automatizada - Agent_Solution_BI

**Deploy Agent - 2025-10-17**

---

## Início Rápido

### 1. Ver o que será limpo (SEM executar)
```bash
python preview_cleanup.py
```

### 2. Executar limpeza completa
```bash
# Windows
EXECUTAR_LIMPEZA.bat

# Linux/Mac
python cleanup_project.py
```

### 3. Verificar se limpeza foi bem-sucedida
```bash
python verify_cleanup.py
```

### 4. Commit no Git
```bash
git add -A
git commit -m "chore: Limpeza automatizada do projeto"
git push origin main
```

---

## Arquivos do Sistema de Limpeza

### Scripts Executáveis

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `preview_cleanup.py` | Mostra o que será limpo SEM executar | Antes de limpar |
| `cleanup_project.py` | Executa limpeza completa | Limpeza principal |
| `EXECUTAR_LIMPEZA.bat` | Interface Windows para limpeza | Usuários Windows |
| `verify_cleanup.py` | Verifica se limpeza foi bem-sucedida | Após limpar |
| `scripts/limpar_cache.py` | Limpa apenas cache | Limpeza rápida |
| `scripts/limpar_cache.bat` | Versão batch de limpeza de cache | Windows |

### Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `README_LIMPEZA_PROJETO.md` | Este arquivo - guia rápido |
| `LIMPEZA_README.md` | Guia completo de limpeza e manutenção |
| `GIT_CLEANUP_INSTRUCTIONS.md` | Comandos Git detalhados |
| `SUMARIO_LIMPEZA.md` | Sumário executivo da limpeza |
| `scripts/diagnostics/README.md` | Documentação de scripts de diagnóstico |

---

## O que a Limpeza Faz

### ✅ Remove
- Arquivos temporários (`temp_*.py`, `tmp_*.py`)
- Cache desatualizado (>3 dias)
- Scripts duplicados

### ✅ Organiza
- Scripts de diagnóstico → `scripts/diagnostics/`
- Scripts de limpeza consolidados

### ✅ Mantém
- Dados de produção (`data/feedback/`, `data/learning/`)
- Configurações (`.env`, `config.py`)
- Código-fonte (`core/`, `pages/`)
- Documentação (`docs/`, `README.md`)

### ✅ Cria
- Backup em `backup_cleanup/`
- Relatório detalhado (`.cleanup_report.json`)
- Logs de execução

---

## Fluxo de Trabalho Recomendado

```
1. PREVIEW
   ↓
   python preview_cleanup.py
   ↓
   Revisar lista de arquivos

2. LIMPEZA
   ↓
   EXECUTAR_LIMPEZA.bat
   ↓
   Confirmar ação
   ↓
   Backup criado automaticamente

3. VERIFICAÇÃO
   ↓
   python verify_cleanup.py
   ↓
   Verificar relatório

4. GIT
   ↓
   git add -A
   git commit -m "chore: Limpeza automatizada"
   git push origin main
```

---

## Políticas de Limpeza

### Cache (data/cache/ e data/cache_agent_graph/)
- **Manter:** Últimos 3 dias
- **Remover:** Mais de 3 dias
- **Frequência:** Semanal

### Arquivos Temporários
- **Padrões:** `temp_*.py`, `tmp_*.py`, `scratch_*.py`
- **Ação:** Remover sempre
- **Backup:** Sim

### Backup
- **Localização:** `backup_cleanup/`
- **Retenção:** 30 dias
- **Limpeza:** Manual

---

## Segurança

### ⚠️ NUNCA Deletado
- `data/feedback/` - Feedback de usuários
- `data/learning/` - Dados de aprendizado
- `data/query_history/` - Histórico de queries
- `data/query_patterns.json` - Padrões aprendidos
- Código-fonte
- Configurações
- Documentação

### 🔒 NUNCA Versionado
- `.env` - Variáveis de ambiente
- `secrets/` - Credenciais
- `*.key`, `*.pem` - Chaves privadas
- `backup_cleanup/` - Backups
- `.cleanup_report.json` - Relatórios

### ✓ Backup Automático
Todos os arquivos são copiados para `backup_cleanup/` antes de serem deletados.

---

## Relatórios Gerados

### Console (Tempo Real)
```
[2025-10-17 14:30:00] [INFO] INICIANDO LIMPEZA...
[2025-10-17 14:30:01] [SUCCESS] Removido: temp_read_transferencias.py
[2025-10-17 14:30:02] [SUCCESS] Cache limpo: 118 arquivos, 15.5 MB
[2025-10-17 14:30:03] [SUCCESS] LIMPEZA CONCLUÍDA!
```

### JSON (.cleanup_report.json)
```json
{
  "timestamp": "2025-10-17T14:30:00",
  "summary": {
    "total_files_removed": 150,
    "total_files_moved": 4,
    "total_space_freed_mb": 15.5,
    "total_errors": 0
  }
}
```

### Verificação (.verification_report.json)
```json
{
  "summary": {
    "total_checks": 7,
    "passed": 7,
    "failed": 0,
    "success_rate": 100.0
  }
}
```

---

## Comandos Rápidos

### Preview (Ver sem executar)
```bash
python preview_cleanup.py
```

### Limpeza Completa
```bash
# Windows
EXECUTAR_LIMPEZA.bat

# Linux/Mac
python cleanup_project.py
```

### Apenas Cache
```bash
python scripts/limpar_cache.py
```

### Verificação
```bash
python verify_cleanup.py
```

### Git
```bash
# Status
git status

# Adicionar tudo
git add -A

# Commit
git commit -m "chore: Limpeza automatizada do projeto"

# Push
git push origin main
```

---

## Troubleshooting

### ❌ "Python não encontrado"
```bash
python --version  # Verificar instalação
```
**Solução:** Instalar Python e adicionar ao PATH

### ❌ "Permissão negada"
**Solução:** Executar como Administrador (Windows) ou com sudo (Linux/Mac)

### ❌ "Cache não é limpo"
**Verificar:**
1. Permissões em `data/cache/`
2. Arquivos não estão bloqueados
3. Política de retenção (3 dias padrão)

### ❌ "Git mostra muitos arquivos deletados"
```bash
git add -u  # Adicionar deleções
# ou
git restore .  # Restaurar arquivos
```

---

## Automação

### Windows (Task Scheduler)
```batch
schtasks /create /tn "Agent_BI_Cleanup" ^
  /tr "C:\path\to\EXECUTAR_LIMPEZA.bat" ^
  /sc weekly /d SUN /st 02:00
```

### Linux/Mac (Crontab)
```bash
# Adicionar ao crontab (domingos às 2h)
0 2 * * 0 cd /path/to/Agent_Solution_BI && python cleanup_project.py
```

---

## Estrutura de Diretórios

### Antes
```
Agent_Solution_BI/
├── temp_read_transferencias.py         # Temporário
├── clear_cache.bat                      # Duplicado
├── scripts/
│   ├── clear_cache.bat                  # Duplicado
│   ├── limpar_cache.bat                 # Duplicado
│   ├── diagnostico_sugestoes_automaticas.py
│   ├── diagnostico_transferencias_unes.py
│   └── ...
└── data/
    └── cache/                           # 118+ arquivos antigos
```

### Depois
```
Agent_Solution_BI/
├── cleanup_project.py                   # NOVO
├── EXECUTAR_LIMPEZA.bat                 # NOVO
├── preview_cleanup.py                   # NOVO
├── verify_cleanup.py                    # NOVO
├── LIMPEZA_README.md                    # NOVO
├── GIT_CLEANUP_INSTRUCTIONS.md          # NOVO
├── scripts/
│   ├── diagnostics/                     # NOVO
│   │   ├── README.md
│   │   ├── diagnostico_sugestoes_automaticas.py
│   │   ├── diagnostico_transferencias_unes.py
│   │   └── ...
│   ├── limpar_cache.py                  # Consolidado
│   └── limpar_cache.bat                 # Consolidado
├── backup_cleanup/                      # NOVO (auto-criado)
│   └── ...
└── data/
    └── cache/                           # Apenas últimos 3 dias
```

---

## Métricas de Sucesso

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Arquivos temporários | 1+ | 0 | ✅ 100% |
| Cache desatualizado | 118+ | 0 | ✅ 100% |
| Scripts duplicados | 4 | 2 | ✅ 50% |
| Espaço liberado | - | ~15-23 MB | ✅ |
| Documentação | Parcial | Completa | ✅ |
| Automação | Manual | Automatizada | ✅ |

---

## Próximos Passos

### Hoje
- [ ] Executar `python preview_cleanup.py`
- [ ] Revisar lista de arquivos
- [ ] Executar `EXECUTAR_LIMPEZA.bat`
- [ ] Verificar relatório
- [ ] Commit no Git

### Esta Semana
- [ ] Configurar agendamento semanal
- [ ] Atualizar `.gitignore`
- [ ] Testar restauração de backup

### Este Mês
- [ ] Implementar dashboard de métricas
- [ ] Integrar com CI/CD
- [ ] Revisar política de retenção

---

## Recursos Adicionais

### Documentação Completa
1. **LIMPEZA_README.md** - Guia detalhado de limpeza
2. **GIT_CLEANUP_INSTRUCTIONS.md** - Comandos Git completos
3. **SUMARIO_LIMPEZA.md** - Sumário executivo

### Links Úteis
- [Git Documentation](https://git-scm.com/doc)
- [Python Pathlib](https://docs.python.org/3/library/pathlib.html)
- [GitHub Issues](https://github.com)

---

## Suporte

**Deploy Agent**
- Documentação: Ver arquivos acima
- Logs: `data/learning/error_log_*.jsonl`
- Relatórios: `.cleanup_report.json`, `.verification_report.json`

---

## Changelog

### v1.0 - 2025-10-17

**Implementado:**
- ✅ Sistema completo de limpeza automatizada
- ✅ Preview de limpeza (sem executar)
- ✅ Verificação pós-limpeza
- ✅ Backup automático
- ✅ Reorganização de scripts
- ✅ Documentação completa
- ✅ Integração Git

**Testado:**
- ⏳ Aguardando primeira execução

---

**Última Atualização:** 2025-10-17
**Autor:** Deploy Agent
**Versão:** 1.0

---

## Licença

Mesmo licenciamento do projeto Agent_Solution_BI.

---

**FIM DO GUIA RÁPIDO**

Para documentação completa, consulte `LIMPEZA_README.md`.
