# INSTRUCOES SIMPLES - Corrigir Logs em 5 MINUTOS

Data: 2025-10-21 | Status: URGENTE | Tempo: 5 minutos

---

## PROBLEMA
Logs estruturados estão inativos desde 12/10/2025. Sistema de learning logs funciona, mas logs gerais não.

## SOLUÇÃO EM 3 PASSOS

### PASSO 1: Copiar arquivo de configuração
```powershell
# No terminal/PowerShell, na raiz do projeto:
Copy-Item LOGGING_CONFIG_NOVO.py core/config/logging_config.py
```

**Verificar:**
```powershell
dir core/config/logging_config.py
```

---

### PASSO 2: Adicionar inicialização em streamlit_app.py

Abrir `streamlit_app.py` e adicionar no INÍCIO da função `main()`:

```python
from core.config.logging_config import setup_logging

def main():
    # ADICIONAR ESTAS 2 LINHAS
    setup_logging()

    # ... resto do código continua ...
```

**Se não tiver def main():**
Adicionar logo após os imports principais:

```python
from core.config.logging_config import setup_logging

setup_logging()

# ... resto do código ...
```

---

### PASSO 3: Testar

```powershell
# Rodar streamlit
streamlit run streamlit_app.py
```

**Verificar que arquivo de log foi criado:**
```powershell
# Ver se arquivo foi criado
dir logs/

# Deve aparecer algo como:
# activity_2025-10-21.log
```

---

## VALIDAÇÃO RÁPIDA

### ✓ Se viu o arquivo logs/activity_2025-10-21.log
Sucesso! Logs estão funcionando.

### ✓ Ver conteúdo do log
```powershell
# Mostrar primeiras linhas
Get-Content logs/activity_2025-10-21.log -Head 20

# Procurar por "LOGGING INICIALIZADO"
Select-String "LOGGING INICIALIZADO" logs/activity_2025-10-21.log
```

### ✗ Se não viu o arquivo
Verificar:
1. Erros no console do streamlit
2. Se importação de setup_logging está correta
3. Se streamlit_app.py salvo com sucesso

---

## PRÓXIMA ETAPA (Opcional, mas recomendada)

Instrumentar Plano A em `core/business_intelligence/direct_query_engine.py`:

No início do arquivo:
```python
from core.config.logging_config import (
    log_plano_a_load_data,
    log_plano_a_performance,
    get_logger
)
import time

logger = get_logger(__name__)
```

Na função `load_data()`, adicionar:
```python
def load_data(filters=None, ...):
    start_time = time.time()

    if filters:
        log_plano_a_load_data(filters, source="direct_query_engine")

    try:
        # ... código existente ...
        df = ...  # resultado

        duration_ms = (time.time() - start_time) * 1000
        log_plano_a_performance(duration_ms, rows_loaded=len(df))

        return df
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise
```

---

## RESUMO

| Ação | Tempo | Resultado |
|------|-------|-----------|
| Copiar arquivo | 1 min | logging_config.py atualizado |
| Adicionar setup_logging() | 2 min | Inicialização automática |
| Testar | 2 min | logs/activity_2025-10-21.log criado |

**Total: 5 minutos**

---

## DOCUMENTAÇÃO COMPLETA

Para detalhes técnicos, ver:
- **RELATORIO_AUDITORIA_FINAL.md** - Relatório completo com tabelas
- **DIAGNOSTICO_COMPLETO.md** - Análise técnica profunda
- **AUDIT_RESULTS.json** - Dados estruturados

---

## SUPORTE

Arquivos fornecidos:
- `LOGGING_CONFIG_NOVO.py` - Nova configuração (copiar para core/config/logging_config.py)
- `APLICAR_CORRECOES.py` - Script para aplicar automaticamente
- `RELATORIO_AUDITORIA_FINAL.md` - Documentação completa

Dúvidas? Consulte RELATORIO_AUDITORIA_FINAL.md seção "INSTRUÇÕES DE IMPLEMENTAÇÃO"
