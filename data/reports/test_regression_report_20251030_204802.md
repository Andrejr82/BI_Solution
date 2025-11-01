
================================================================================
                   RELATORIO DE TESTES DE REGRESSAO
                           30/10/2025 20:48:02
================================================================================

RESUMO GERAL
--------------------------------------------------------------------------------
  Total de Queries Testadas: 28
  [OK] Sucessos: 0 (0.0%)
  [FAIL] Falhas: 28 (100.0%)

  Meta do Roadmap: 95% de taxa de sucesso
  [AVISO] Faltam 95.0% para atingir meta

RESULTADOS POR CATEGORIA
--------------------------------------------------------------------------------

  [FAIL] GRAFICOS_TEMPORAIS
     Sucesso: 0/4 (0.0%)

  [FAIL] RANKINGS
     Sucesso: 0/4 (0.0%)

  [FAIL] TOP_N
     Sucesso: 0/4 (0.0%)

  [FAIL] AGREGACOES
     Sucesso: 0/4 (0.0%)

  [FAIL] COMPARACOES
     Sucesso: 0/3 (0.0%)

  [FAIL] VALIDACAO_COLUNAS
     Sucesso: 0/3 (0.0%)

  [FAIL] QUERIES_AMPLAS
     Sucesso: 0/3 (0.0%)

  [FAIL] GRAFICOS_COMPLEXOS
     Sucesso: 0/3 (0.0%)


ERROS ENCONTRADOS (28)
--------------------------------------------------------------------------------

  1. [graficos_temporais] gere um gráfico de evolução dos segmentos na une tij
     Erro: No module named 'core.llm'...

  2. [graficos_temporais] mostre a evolução temporal de vendas do segmento tecidos
     Erro: No module named 'core.llm'...

  3. [graficos_temporais] evolução de vendas nos últimos 6 meses
     Erro: No module named 'core.llm'...

  4. [graficos_temporais] gráfico de tendência de vendas por mês
     Erro: No module named 'core.llm'...

  5. [rankings] ranking de vendas do segmento tecidos
     Erro: No module named 'core.llm'...

  6. [rankings] ranking completo de vendas por produto
     Erro: No module named 'core.llm'...

  7. [rankings] ranking de vendas na une scr
     Erro: No module named 'core.llm'...

  8. [rankings] ranking de produtos mais vendidos
     Erro: No module named 'core.llm'...

  9. [top_n] top 10 produtos mais vendidos
     Erro: No module named 'core.llm'...

  10. [top_n] top 5 segmentos com maiores vendas
     Erro: No module named 'core.llm'...

  ... e mais 18 erros


VALIDACAO DAS CORRECOES IMPLEMENTADAS
--------------------------------------------------------------------------------
  [FAIL] FALHOU Fase 1.1: Column Validator: 0.0%
  [FAIL] FALHOU Fase 1.2: Fallback Queries Amplas: 0.0%
  [FAIL] FALHOU Fase 1.3: Gráficos Temporais: 0.0%
  [FAIL] FALHOU Fase 2: Few-Shot Learning (Rankings): 0.0%
  [FAIL] FALHOU Fase 2: Few-Shot Learning (Top N): 0.0%


DADOS SALVOS EM
--------------------------------------------------------------------------------
  Arquivo JSON: data/reports/test_regression_results_20251030_204802.json
  Logs Completos: logs/tests/regression_20251030.log

================================================================================
                            FIM DO RELATORIO
================================================================================
