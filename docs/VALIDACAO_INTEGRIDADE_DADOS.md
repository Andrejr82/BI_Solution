# Validacao de Integridade de Dados e Performance
## Agent_Solution_BI - BI Agent (Caçulinha BI)

Este documento descreve o sistema de validação de integridade de dados e análise de performance implementado no projeto.

---

## Visão Geral

O sistema de validação realiza análises abrangentes em:

1. **Arquivos Parquet** - Integridade e consistência dos dados
2. **Sistema de Cache** - Eficiência e uso de memória
3. **Sistema de Learning** - Eficácia do aprendizado
4. **KPIs do Sistema** - Métricas de performance

---

## Scripts Disponíveis

### 1. validacao_integridade_dados.py

Script principal que realiza validação completa do sistema.

**Localização**: `./scripts/validacao_integridade_dados.py`

**Execução**:
```bash
# Via Python
python scripts/validacao_integridade_dados.py

# Via Batch (Windows)
scripts\VALIDAR_INTEGRIDADE.bat
```

**O que faz**:
- Valida todos os arquivos Parquet em `data/`
- Verifica schemas e detecta inconsistências
- Analisa sistema de cache (JSON e Agent Graph)
- Avalia sistema de learning
- Calcula KPIs do sistema
- Gera Health Score (0-100)
- Produz relatório detalhado em Markdown

**Saídas**:
- `reports/data_integrity_report_[timestamp].md` - Relatório Markdown
- `reports/data_integrity_report_[timestamp].json` - Dados JSON

---

### 2. analise_rapida_cache.py

Script para análise rápida de métricas de cache.

**Localização**: `./scripts/analise_rapida_cache.py`

**Execução**:
```bash
python scripts/analise_rapida_cache.py
```

**O que faz**:
- Analisa hit rate estimado do cache
- Identifica padrões de uso
- Calcula eficiência do cache
- Detecta arquivos vazios ou antigos

---

## Estrutura do Relatório de Validação

O relatório gerado contém as seguintes seções:

### 1. Sumário Executivo
- **Health Score** (0-100)
- **Status** (EXCELENTE, BOM, REGULAR, CRÍTICO)
- Métricas principais em tabela

### 2. Análise de Arquivos Parquet
Para cada arquivo:
- Status (OK, WARNING, ERROR)
- Número de linhas e colunas
- Tamanho e uso de memória
- Linhas duplicadas
- Valores nulos por coluna
- Lista de colunas

### 3. Análise de Sistema de Cache

#### Cache JSON
- Total de arquivos
- Tamanho total e médio
- Cache antigo (>24h)
- Arquivo mais antigo/recente

#### Cache Agent Graph
- Total de arquivos
- Tamanho total

### 4. Análise do Sistema de Learning

#### Queries Bem-Sucedidas
- Total de queries
- Padrões únicos
- Distribuição por tipo

#### Análise de Erros
- Total de erros
- Distribuição por tipo

### 5. Problemas Identificados

Agrupados por severidade:
- **CRITICAL** - Problemas críticos que afetam o sistema
- **WARNING** - Avisos que requerem atenção
- **INFO** - Informações relevantes

### 6. Recomendações Priorizadas

Agrupadas por prioridade:
- **HIGH** - Ações urgentes
- **MEDIUM** - Ações importantes
- **LOW** - Melhorias sugeridas

### 7. Comentário do Analista

Análise contextualizada baseada no Health Score com:
- Pontos fortes
- Áreas de atenção
- Ações recomendadas
- Próximos passos

---

## KPIs Calculados

O sistema calcula os seguintes KPIs:

| KPI | Descrição | Cálculo |
|-----|-----------|---------|
| **success_rate_percent** | Taxa de sucesso de queries | (Queries OK / Total) * 100 |
| **error_rate_percent** | Taxa de erro de queries | (Erros / Total) * 100 |
| **data_quality_score** | Qualidade dos dados Parquet | (Arquivos OK / Total) * 100 |
| **total_queries** | Total de queries processadas | Sucesso + Erros |
| **total_data_rows** | Total de linhas nos Parquets | Soma de todas as linhas |
| **total_parquet_size_mb** | Tamanho total dos Parquets | Soma em MB |
| **cache_entries** | Entradas em cache | Total de arquivos JSON |
| **cache_size_mb** | Tamanho do cache | Soma em MB |
| **avg_cache_size_kb** | Tamanho médio de cache | Média em KB |

---

## Cálculo do Health Score

O Health Score (0-100) é calculado com base em:

**Score Base**: 100 pontos

**Penalidades**:
- Problemas CRITICAL: -15 pontos cada
- Problemas WARNING: -5 pontos cada
- Qualidade de dados < 80%: -(80 - qualidade) / 2
- Taxa de erro > 10%: -(taxa_erro - 10)
- Cache > 100 MB: -(tamanho - 100) / 10

**Classificação**:
- 90-100: EXCELENTE
- 75-89: BOM
- 60-74: REGULAR
- 0-59: CRÍTICO

---

## Problemas Detectados

### Tipos de Problemas

#### Arquivos Parquet
- Valores nulos excessivos (>30%)
- Linhas duplicadas (>10%)
- Colunas faltando no schema
- Erros de leitura
- Dados corrompidos

#### Cache
- Cache antigo (>24h) em excesso
- Tamanho excessivo (>50 MB)
- Arquivos vazios
- Cache corrompido

#### Learning
- Poucas queries registradas (<50)
- Taxa de erro alta (>10%)
- Erros recorrentes

---

## Recomendações Comuns

### Prioridade Alta
1. **Corrigir erros críticos de dados**
   - Restaurar backups se necessário
   - Validar integridade de arquivos corrompidos

2. **Investigar taxa de erro elevada**
   - Analisar logs de erro
   - Corrigir padrões recorrentes

### Prioridade Média
1. **Limpar cache antigo**
   - Executar `scripts/limpar_cache.bat`
   - Implementar política de TTL

2. **Otimizar tamanho de cache**
   - Revisar estratégia de caching
   - Comprimir dados em cache

3. **Remover duplicatas**
   - Executar deduplicação em Parquets
   - Prevenir duplicação futura

### Prioridade Baixa
1. **Aumentar coleta de learning**
   - Registrar mais queries de treinamento
   - Diversificar padrões

2. **Documentar schemas**
   - Criar documentação de estruturas de dados
   - Versionar schemas

---

## Interpretação dos Resultados

### Health Score: 90-100 (EXCELENTE)
- Sistema operando perfeitamente
- Dados íntegros e consistentes
- Performance otimizada
- **Ação**: Manter monitoramento regular

### Health Score: 75-89 (BOM)
- Sistema em boas condições
- Alguns pontos de atenção menores
- **Ação**: Implementar recomendações de média prioridade

### Health Score: 60-74 (REGULAR)
- Sistema funcional mas com problemas
- Requer atenção e correções
- **Ação**: Priorizar correção de avisos e warnings

### Health Score: 0-59 (CRÍTICO)
- Sistema comprometido
- Problemas graves detectados
- **Ação**: Intervenção imediata necessária

---

## Automatização

### Execução Agendada

Para monitoramento contínuo, agende a validação:

**Windows (Task Scheduler)**:
```batch
# Criar tarefa agendada diária
schtasks /create /tn "BI_Validacao_Diaria" /tr "C:\Users\André\Documents\Agent_Solution_BI\scripts\VALIDAR_INTEGRIDADE.bat" /sc daily /st 08:00
```

**Cron (Linux/Mac)**:
```bash
# Adicionar ao crontab para execução diária às 8h
0 8 * * * cd /path/to/Agent_Solution_BI && python scripts/validacao_integridade_dados.py
```

---

## Integração com CI/CD

### GitHub Actions

Exemplo de workflow para validação em CI:

```yaml
name: Data Integrity Check

on:
  schedule:
    - cron: '0 8 * * *'  # Diariamente às 8h
  workflow_dispatch:  # Manual

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install pandas pyarrow

      - name: Run validation
        run: |
          python scripts/validacao_integridade_dados.py

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: integrity-report
          path: reports/data_integrity_report_*.md

      - name: Check health score
        run: |
          # Falhar CI se health score < 60
          python -c "
          import json
          from pathlib import Path
          report = sorted(Path('reports').glob('data_integrity_report_*.json'))[-1]
          data = json.loads(report.read_text())
          assert data['health_score'] >= 60, f'Health score too low: {data[\"health_score\"]}'
          "
```

---

## Troubleshooting

### Erro: "Nenhum arquivo Parquet encontrado"

**Causa**: Diretório `data/` não contém arquivos `.parquet`

**Solução**:
1. Verificar se dados foram carregados
2. Confirmar caminho correto
3. Executar scripts de carga de dados

### Erro: "Arquivo corrompido"

**Causa**: Arquivo Parquet danificado

**Solução**:
1. Restaurar de backup
2. Reprocessar dados de origem
3. Validar processo de geração

### Cache muito grande

**Causa**: Acúmulo de cache sem limpeza

**Solução**:
```bash
# Limpar cache manualmente
scripts\limpar_cache.bat

# Ou via Python
python scripts/limpar_cache.py
```

### Taxa de erro alta

**Causa**: Problemas recorrentes em queries

**Solução**:
1. Analisar `data/learning/error_log_*.jsonl`
2. Identificar padrão de erros
3. Corrigir código/dados causadores

---

## Boas Práticas

### Execução Regular
- Executar validação **diariamente** em produção
- Executar antes de deploys importantes
- Após mudanças significativas em dados

### Monitoramento
- Acompanhar tendência do Health Score
- Criar alertas para score < 70
- Revisar recomendações mensalmente

### Manutenção
- Limpar cache semanalmente
- Revisar e corrigir warnings
- Manter documentação atualizada

### Backup
- Fazer backup antes de correções
- Versionar arquivos Parquet importantes
- Manter histórico de relatórios

---

## Métricas de Referência

### Valores Ideais

| Métrica | Ideal | Aceitável | Crítico |
|---------|-------|-----------|---------|
| Health Score | ≥90 | 75-89 | <60 |
| Taxa de Sucesso | ≥95% | 85-94% | <85% |
| Taxa de Erro | ≤5% | 6-15% | >15% |
| Qualidade de Dados | 100% | ≥90% | <80% |
| Cache < 24h | ≥80% | 60-79% | <60% |
| Tamanho de Cache | <50 MB | 50-100 MB | >100 MB |

---

## Extensões Futuras

### Planejadas
1. **Dashboard de Métricas**
   - Visualização em tempo real
   - Histórico de Health Score
   - Alertas automáticos

2. **Validação de Schema Automática**
   - Detectar breaking changes
   - Versionamento de schemas
   - Migrações automáticas

3. **Análise Preditiva**
   - Prever necessidade de limpeza
   - Detectar tendências de degradação
   - Sugerir otimizações proativas

4. **Integração com Alertas**
   - Email/Slack para score < 70
   - Notificações de problemas críticos
   - Relatórios semanais automáticos

---

## Referências

- **Código Fonte**: `scripts/validacao_integridade_dados.py`
- **Relatórios**: `reports/data_integrity_report_*.md`
- **Dados JSON**: `reports/data_integrity_report_*.json`

---

**Última Atualização**: 2025-10-17
**Versão**: 1.0
**Autor**: BI Agent (Caçulinha BI)
