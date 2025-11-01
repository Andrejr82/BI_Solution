# Guia Rapido - Sistema de Analise de Erros (FASE 3.1)

## Inicio Rapido

### 1. Executar Analise Completa

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python scripts/run_error_analyzer.py
```

**O que acontece:**
- Analisa logs dos ultimos 7 dias
- Identifica top 10 erros mais frequentes
- Gera sugestoes de correcao
- Exporta JSON e relatorio Markdown

**Arquivos gerados:**
- `data/learning/error_analysis.json` - Dados estruturados
- `data/reports/error_analysis_fase31_*.md` - Relatorio completo

---

### 2. Executar Testes

```bash
python scripts/tests/test_error_analyzer.py
```

**Valida:**
- Carregamento de logs
- Agrupamento por tipo
- Calculo de frequencia
- Geracao de sugestoes
- Ranking de erros
- Exportacao JSON/Markdown
- Precisao de 100% no top 5

---

### 3. Uso Programatico

```python
from pathlib import Path
import sys

# Adicionar ao path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir))

# Importar modulo (use o script run_error_analyzer.py)
# Ou copie a classe ErrorAnalyzer para core/learning/

# Exemplo de uso basico
from scripts.run_error_analyzer import ErrorAnalyzer

# Criar analisador
analyzer = ErrorAnalyzer()

# Analisar ultimos 7 dias
results = analyzer.analyze_errors(days=7)

# Acessar resultados
print(f"Total de erros: {results['total_errors']}")
print(f"Tipos: {list(results['errors_by_type'].keys())}")

# Top 5 erros
for error in results['top_errors'][:5]:
    print(f"{error['rank']}. {error['error_type']} - {error['count']} ocorrencias")

# Sugestoes CRITICAL
critical = [s for s in results['suggestions'] if s['priority'] == 'CRITICAL']
for sug in critical:
    print(f"[CRITICAL] {sug['error_type']}")
    print(f"  Acao: {sug['action']}")

# Exportar
analyzer.export_analysis()
report = analyzer.generate_report()
```

---

## Entendendo os Resultados

### Estrutura do JSON

```json
{
  "total_errors": 150,           # Total de erros no periodo
  "period_days": 7,               # Dias analisados
  "analysis_date": "2025-10-29", # Data da analise

  "errors_by_type": {            # Distribuicao por tipo
    "KeyError": 85,
    "RuntimeError": 40,
    "ValueError": 25
  },

  "top_errors": [                # Ranking de erros
    {
      "rank": 1,
      "error_type": "KeyError",
      "count": 45,
      "impact": "HIGH",          # CRITICAL/HIGH/MEDIUM/LOW
      "error_message": "...",
      "first_seen": "2025-10-23T10:30:00",
      "last_seen": "2025-10-27T15:45:00",
      "sample_query": "SELECT * FROM..."
    }
  ],

  "suggestions": [               # Sugestoes de correcao
    {
      "priority": "CRITICAL",    # CRITICAL/HIGH/MEDIUM/LOW
      "error_type": "KeyError",
      "frequency": 45,
      "suggestion": "Corrigir mapeamento...",
      "action": "Atualizar config/une_mapping.py",
      "affected_queries": 12
    }
  ],

  "error_timeline": {            # Evolucao temporal
    "2025-10-23": 18,
    "2025-10-24": 22,
    "2025-10-25": 28
  }
}
```

---

## Interpretando Niveis de Severidade

### CRITICAL
- **Quando:** Erros RuntimeError/SystemError OU >20 ocorrencias
- **Acao:** Corrigir IMEDIATAMENTE
- **Impacto:** Bloqueia funcionalidade principal

### HIGH
- **Quando:** 11-20 ocorrencias
- **Acao:** Corrigir em ate 24h
- **Impacto:** Afeta multiplas queries

### MEDIUM
- **Quando:** 3-10 ocorrencias
- **Acao:** Corrigir em ate 1 semana
- **Impacto:** Afeta queries especificas

### LOW
- **Quando:** <3 ocorrencias
- **Acao:** Monitorar
- **Impacto:** Casos isolados

---

## Acoes Recomendadas por Tipo de Erro

### KeyError (coluna nao encontrada)

**Sugestao:**
```python
# Antes (causa erro)
df.select("UNE_NOME")

# Depois (validado)
from core.utils.column_validator import validate_columns

if validate_columns(df, ["UNE_NOME"]):
    df.select("UNE_NOME")
else:
    # Usar nome alternativo ou mapear
    df.select("NOME_UNE")
```

### RuntimeError (LazyFrame)

**Sugestao:**
```python
# Antes (causa erro)
result = df.lazy().filter(...).group_by(...)
print(result)  # Erro!

# Depois (correto)
result = df.lazy().filter(...).group_by(...).collect()
print(result)  # OK
```

### ValueError (conversao de tipo)

**Sugestao:**
```python
# Antes (causa erro)
df.with_columns(pl.col("valor").cast(pl.Int64))

# Depois (com tratamento)
df.with_columns(
    pl.col("valor").str.strip_chars()
    .cast(pl.Int64, strict=False)
    .fill_null(0)
)
```

---

## Agendamento Automatico

### Windows (Task Scheduler)

1. Abrir Task Scheduler
2. Criar nova tarefa
3. Trigger: Diario as 08:00
4. Acao:
   - Program: `python.exe`
   - Arguments: `C:\Users\André\Documents\Agent_Solution_BI\scripts\run_error_analyzer.py`
   - Start in: `C:\Users\André\Documents\Agent_Solution_BI`

### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa diariamente as 08:00)
0 8 * * * cd /path/to/Agent_Solution_BI && python scripts/run_error_analyzer.py
```

---

## Alertas por Email (Opcional)

Adicione ao final do `run_error_analyzer.py`:

```python
def send_alert_email(results):
    """Envia email se houver erros CRITICAL"""
    import smtplib
    from email.mime.text import MIMEText

    critical_count = len([s for s in results['suggestions'] if s['priority'] == 'CRITICAL'])

    if critical_count > 0:
        subject = f"[ALERTA] {critical_count} erros CRITICAL detectados"
        body = f"Analise completa em: data/learning/error_analysis.json\n\n"
        body += f"Total de erros: {results['total_errors']}\n"
        body += f"Erros CRITICAL: {critical_count}\n"

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'seu_email@example.com'
        msg['To'] = 'destinatario@example.com'

        # Configurar SMTP conforme seu provedor
        # smtp = smtplib.SMTP('smtp.gmail.com', 587)
        # smtp.starttls()
        # smtp.login('usuario', 'senha')
        # smtp.send_message(msg)
        # smtp.quit()

# Chamar no main()
if critical_count > 0:
    send_alert_email(results)
```

---

## Troubleshooting

### Problema: "Nenhum erro encontrado nos logs"

**Causa:** Logs nao estao em `data/learning/error_log_*.jsonl`

**Solucao:**
1. Verificar se o sistema de logging esta ativo
2. Confirmar formato dos arquivos: `error_log_YYYYMMDD.jsonl`
3. Executar algumas queries para gerar logs de teste

### Problema: "Modulo nao encontrado"

**Causa:** Path do Python nao configurado

**Solucao:**
```python
import sys
from pathlib import Path

base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir))
```

### Problema: "Erro ao processar arquivo de log"

**Causa:** Formato JSON invalido no arquivo

**Solucao:**
1. Validar formato JSONL (um JSON por linha)
2. Remover linhas corrompidas
3. Regenerar logs se necessario

---

## FAQ

**P: Quantos dias devo analisar?**
R: Recomendamos 7 dias para balanco entre volume e relevancia. Use 30 dias para analise trimestral.

**P: Como adicionar novos patterns de correcao?**
R: Edite a lista `fix_patterns` em `suggest_fixes()` no arquivo `run_error_analyzer.py`.

**P: Posso filtrar apenas erros CRITICAL?**
R: Sim, use:
```python
critical_only = [e for e in results['top_errors'] if e['impact'] == 'CRITICAL']
```

**P: Como integrar com sistema de tickets?**
R: Crie um script que leia o JSON e crie tickets automaticamente para erros CRITICAL/HIGH.

---

## Proximos Passos

1. **Executar primeira analise:**
   ```bash
   python scripts/run_error_analyzer.py
   ```

2. **Revisar relatorio gerado:**
   ```bash
   # Abrir ultimo relatorio
   start data/reports/error_analysis_fase31_*.md
   ```

3. **Priorizar correcoes:**
   - Focar em erros CRITICAL primeiro
   - Depois erros HIGH com alta frequencia
   - Criar backlog para MEDIUM/LOW

4. **Agendar execucao diaria**

5. **Configurar alertas** (se necessario)

---

## Suporte

Para duvidas ou problemas, consulte:
- `reports/FASE_3_1_IMPLEMENTACAO_COMPLETA.md` - Documentacao completa
- `scripts/tests/test_error_analyzer.py` - Exemplos de uso
- Logs do sistema em `data/learning/`

---

**Versao:** 1.0 (FASE 3.1)
**Data:** 2025-10-29
**Autor:** BI Agent (Caçulinha BI)
