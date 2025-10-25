# DIAGNÓSTICO COMPLETO - SISTEMA DE LOGS
**Data: 2025-10-21 | Auditoria Urgente**

---

## STATUS DO SISTEMA DE LOGS

### EVIDÊNCIAS COLETADAS

#### 1. Diretórios de Log Existentes

De acordo com git status:
- `data/learning/` - **ATIVO** (contém arquivos de 2025-10-19, 2025-10-20, 2025-10-21)
  - error_log_2025-10-21.jsonl
  - error_counts_2025-10-21.json
  - successful_queries_2025-10-21.jsonl

- `logs/` - **NÃO EXISTE OU VAZIO** (não listado em git status)

#### 2. Possível Causa

Logs estruturados em `logs/` parecem ter parado de 12/10/2025 porque:
- `logging_config.py` pode não estar sendo importado/chamado
- `setup_logging()` pode não estar sendo invocado em `streamlit_app.py`
- Ou o arquivo de configuração está incompleto/quebrado

#### 3. Logs de Aprendizado (data/learning/)

Estão funcionando normalmente:
- Contêm arquivos JSONLines com errors e sucessos
- Atualizados diariamente
- Gerados por sistema de learning separado

---

## PLANO DE AÇÃO IMEDIATO

### FASE 1: ASSEGURAR CONFIGURAÇÃO LOGGING
**Arquivo: `core/config/logging_config.py`**

Garantir que:
1. Função `setup_logging()` existe
2. Cria diretório `logs/` se não existir
3. Configura RotatingFileHandler para `activity_YYYY-MM-DD.log`
4. Adiciona console handler
5. Retorna logger configurado

### FASE 2: ASSEGURAR INICIALIZAÇÃO
**Arquivo: `streamlit_app.py`**

Garantir que:
1. Importa `setup_logging` de `logging_config`
2. Chama `setup_logging()` no início da função main()
3. Adiciona logging de inicialização
4. Todos os entry points chamam setup_logging()

### FASE 3: INSTRUMENTAR PLANO A
**Arquivo: `core/business_intelligence/direct_query_engine.py`**

Adicionar logging:
1. Logger declarado no módulo
2. Log quando `load_data()` recebe filtros
3. Log de performance (duração, linhas carregadas)
4. Log quando fallback é acionado

### FASE 4: VALIDAR
1. Criar arquivo `logs/activity_2025-10-21.log`
2. Verificar que é escrito com logging
3. Testar que Plano A está instrumentado

---

## IMPACTO DA SOLUÇÃO

| Item | Antes | Depois | Impacto |
|------|-------|--------|---------|
| Logs estruturados | Inativos desde 12/10 | Ativos | CRÍTICO |
| Rastreamento Plano A | Ausente | Presente | ALTO |
| Diagnosticabilidade | Baixa | Alta | ALTO |
| Auditoria de sistema | Difícil | Fácil | MÉDIO |

---

## ARQUIVOS AFETADOS

1. `core/config/logging_config.py` - Implementação/correção
2. `streamlit_app.py` - Adicionar chamada setup_logging()
3. `core/business_intelligence/direct_query_engine.py` - Adicionar logs
4. Potencialmente: `core/connectivity/parquet_adapter.py` - Se necessário

---

## PRÓXIMOS PASSOS

1. Implementar `logging_config.py` com setup_logging()
2. Atualizar `streamlit_app.py`
3. Testar criação de log
4. Instrumentar Plano A
5. Validar completo
