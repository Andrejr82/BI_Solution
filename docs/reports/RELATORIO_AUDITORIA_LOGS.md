# AUDITORIA URGENTE - SISTEMA DE LOGS
**Data: 2025-10-21 | Status: EM ANÁLISE**

## PLANO DE AÇÃO RÁPIDO

### Fase 1: Análise Estruturada
1. Verificar se `logging_config.py` existe e tem `setup_logging()`
2. Verificar se `streamlit_app.py` chama `setup_logging()`
3. Verificar se diretório `logs/` existe
4. Verificar instrumentação de Plano A em `direct_query_engine.py`

### Fase 2: Correções Essenciais (Se Necessário)
- [ ] Criar/corrigir `logging_config.py` com `setup_logging()`
- [ ] Adicionar chamada `setup_logging()` em `streamlit_app.py`
- [ ] Garantir diretório `logs/` existe
- [ ] Instrumentar `direct_query_engine.py` com logs de Plano A

### Fase 3: Validação
- [ ] Criar arquivo de log hoje (activity_2025-10-21.log)
- [ ] Verificar que logs estão sendo escritos
- [ ] Testar logs de Plano A

## ESTRUTURA DE LOGS ESPERADA

```
logs/
  activity_2025-10-21.log     <- Logs estruturados do dia
  activity_2025-10-20.log
  activity_2025-10-19.log

data/learning/
  error_log_2025-10-21.jsonl  <- Logs de erro em JSON
  successful_queries_2025-10-21.jsonl
  error_counts_2025-10-21.json
```

## ARQUIVOS A MODIFICAR (SE NECESSÁRIO)

1. **core/config/logging_config.py**
   - Implementar `setup_logging()`
   - Criar RotatingFileHandler
   - Adicionar logging de Plano A

2. **streamlit_app.py**
   - Importar setup_logging
   - Chamar setup_logging() no início
   - Adicionar logging de inicialização

3. **core/business_intelligence/direct_query_engine.py**
   - Adicionar logger
   - Log quando load_data recebe filtros
   - Log de performance (tempo, linhas)
   - Log de fallback

---
**Próximo passo: Executar scripts de diagnóstico**
