# Teste de 80 Perguntas de Negócio - DirectQueryEngine

## 📋 Visão Geral

Este teste avalia a capacidade do **DirectQueryEngine** de processar 80 perguntas de negócio organizadas em 10 categorias, **sem usar tokens da LLM**.

## 🎯 Objetivo

Validar que o sistema consegue responder perguntas de negócio complexas usando apenas:
- Padrões pré-definidos
- Cache inteligente
- Consultas diretas ao Parquet
- **Zero consumo de tokens LLM**

## 📁 Arquivos

- `test_80_perguntas_completo.py` - Script principal de teste
- `run_test_80_perguntas.py` - Script auxiliar para executar o teste
- `README_TESTE_80_PERGUNTAS.md` - Este arquivo

## 🚀 Como Executar

### Opção 1: Script Auxiliar (Recomendado)

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python tests/run_test_80_perguntas.py
```

### Opção 2: Diretamente

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python tests/test_80_perguntas_completo.py
```

## 📊 Categorias de Perguntas

O teste cobre 10 categorias principais:

1. **🎯 Vendas por Produto** (8 perguntas)
   - Gráficos de vendas
   - Evolução temporal
   - Comparativos entre UNEs
   - Top performers

2. **🏪 Análises por Segmento** (8 perguntas)
   - Rankings por segmento
   - Comparativos
   - Distribuição ABC
   - Sazonalidade

3. **🏬 Análises por UNE/Loja** (8 perguntas)
   - Performance por loja
   - Potencial de crescimento
   - Diversidade de produtos
   - Eficiência de vendas

4. **📈 Análises Temporais** (8 perguntas)
   - Sazonalidade
   - Tendências
   - Previsões
   - Alertas de declínio

5. **💰 Performance e ABC** (8 perguntas)
   - Classificação ABC
   - Migração entre classes
   - Frequência de vendas
   - Consistência

6. **📦 Estoque e Logística** (8 perguntas)
   - Ponto de pedido
   - Rotação de estoque
   - Excesso/falta
   - Eficiência logística

7. **🏭 Análises por Fabricante** (8 perguntas)
   - Rankings
   - Diversidade
   - Concentração
   - Oportunidades

8. **🎨 Categoria/Grupo** (8 perguntas)
   - Performance por categoria
   - Cross-selling
   - Gap analysis
   - Expansão de linha

9. **📊 Dashboards Executivos** (8 perguntas)
   - KPIs consolidados
   - Scorecards
   - Alertas
   - Indicadores de saúde

10. **🔍 Análises Específicas** (8 perguntas)
    - Canibalização
    - Impacto de promoções
    - Previsão de demanda
    - Simulações

## 📈 Métricas Avaliadas

Para cada pergunta, o teste registra:

- ✅ **SUCCESS**: Processado com sucesso pelo DirectQueryEngine
- ⚠️ **FALLBACK**: Necessita processamento pela LLM (objetivo: minimizar)
- ❌ **ERROR**: Erro durante processamento
- ❓ **UNKNOWN**: Tipo de resultado desconhecido

## 📄 Relatório Gerado

O teste gera um arquivo JSON detalhado:

```
tests/relatorio_teste_80_perguntas_YYYYMMDD_HHMMSS.json
```

### Estrutura do Relatório

```json
{
  "metadata": {
    "timestamp": "2025-10-19T...",
    "total_perguntas": 80,
    "total_categorias": 10
  },
  "estatisticas": {
    "SUCCESS": 65,
    "FALLBACK": 10,
    "ERROR": 5,
    "UNKNOWN": 0
  },
  "resultados": [
    {
      "id": 1,
      "categoria": "🎯 Vendas por Produto",
      "pergunta": "Gere um gráfico...",
      "status": "SUCCESS",
      "mensagem": "Processado como chart",
      "tipo_resultado": "chart",
      "tempo_processamento": 0.45,
      "timestamp": "2025-10-19T..."
    }
  ]
}
```

## 🔍 Interpretação dos Resultados

### Meta de Sucesso
- **Ótimo**: SUCCESS > 70% (56+ perguntas)
- **Bom**: SUCCESS > 60% (48+ perguntas)
- **Aceitável**: SUCCESS > 50% (40+ perguntas)
- **Precisa melhorias**: SUCCESS < 50%

### Análise de Fallback
- Perguntas que caem em FALLBACK indicam padrões que ainda não foram implementados
- Use o relatório para identificar novos padrões a adicionar no DirectQueryEngine

### Análise de Erros
- Erros indicam problemas de implementação ou dados
- Revise o log de cada erro para correção

## 🛠️ Pré-requisitos

### Dependências Python
```bash
pip install pandas dask pyarrow
```

### Arquivos de Dados
O teste procura automaticamente por:
1. `data/parquet/admmat_extended.parquet` (preferencial)
2. `data/parquet/admmat.parquet` (fallback)

## 🐛 Troubleshooting

### Erro: "Parquet file not found"
```bash
# Verifique se o arquivo existe
ls data/parquet/
```

### Erro: "Module not found"
```bash
# Instale dependências
pip install -r requirements.txt
```

### Problemas de Encoding (Windows)
O script tem tratamento automático para problemas de encoding com emojis.
Se ainda houver problemas, execute com:
```bash
python -X utf8 tests/run_test_80_perguntas.py
```

### Lentidão na Execução
- Normal: 80 perguntas levam ~2-5 minutos
- Se levar muito mais, verifique o tamanho do arquivo parquet
- Considere usar `admmat.parquet` em vez de `admmat_extended.parquet`

## 📝 Logs

Durante a execução, você verá:

```
================================================================================
TESTE COMPLETO DAS 80 PERGUNTAS DE NEGÓCIO
================================================================================
Início: 2025-10-19 10:30:00

Inicializando DirectQueryEngine...
   Carregando dados de: C:\...\admmat_extended.parquet
[OK] Engine inicializada

================================================================================
[CATEGORIA] 🎯 Vendas por Produto
================================================================================

[1/80] Testando: Gere um gráfico de vendas do produto 369947 na UNE SCR...
[OK] SUCCESS: Processado como chart (0.45s)

[2/80] Testando: Mostre a evolução de vendas mensais do produto 369947...
[OK] SUCCESS: Processado como chart (0.38s)

...
```

## 🎯 Próximos Passos

Após executar o teste:

1. **Revise o relatório JSON** gerado
2. **Analise perguntas FALLBACK** - adicione novos padrões
3. **Corrija erros** identificados
4. **Otimize performance** de queries lentas
5. **Execute novamente** para validar melhorias

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verifique os logs detalhados
2. Consulte o relatório JSON
3. Revise a documentação do DirectQueryEngine
4. Abra uma issue no projeto

---

**Última atualização**: 2025-10-19
**Versão**: 1.0
