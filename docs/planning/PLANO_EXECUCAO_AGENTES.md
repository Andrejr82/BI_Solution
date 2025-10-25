# 🎯 PLANO DE EXECUÇÃO - IMPLEMENTAÇÃO UNE (3 DIAS)

## 📊 GESTÃO DE TOKENS

### **Budget Total:** 200.000 tokens
### **Consumido:** 81.721 tokens (40.9%)
### **Disponível:** 118.279 tokens (59.1%)
### **Necessário:** ~97.750 tokens (48.9%)
### **Margem:** ~20.529 tokens (10.2%) ✅

---

## 🤖 DISTRIBUIÇÃO DE AGENTES

### **DIA 1: FUNDAÇÃO + CÁLCULOS (40h tokens)**

#### **Tarefa 1.1: Processar Parquet e Adicionar Colunas Calculadas**
**Agente:** `@data-agent`
**Tokens:** ~15.000
**Arquivos:**
- Input: `data/parquet/admmat.parquet`
- Output: `data/parquet/admmat_extended.parquet`

**Prompt para data-agent:**
```
Leia o arquivo data/parquet/admmat.parquet e adicione as seguintes colunas calculadas:

1. mc (float): Cálculo de Média Comum
   - Se existirem colunas mes_01 a mes_12: MC = (média dos 12 + média dos 3 últimos + mes_01) / 3
   - Se não existirem: MC = venda_30_d * 1.2 (aproximação)

2. linha_verde (float):
   - linha_verde = estoque_atual + estoque_gondola_lv (ou 0 se não existir) + estoque_ilha_lv (ou 0 se não existir)

3. ranking (int): Mapear por segmento
   - TECIDOS: 0
   - PAPELARIA: 1
   - ARMARINHO E CONFECÇÃO: 2
   - Demais: 1 (padrão)

4. precisa_abastecimento (bool):
   - True se estoque_atual <= (linha_verde * 0.5)
   - False caso contrário

5. qtd_a_abastecer (float):
   - max(0, linha_verde - estoque_atual)

6. preco_varejo (float):
   - Se ranking == 0: preco_38_percent * 1.30
   - Se ranking == 1: preco_38_percent
   - Se ranking == 2: preco_38_percent * 1.30
   - Se ranking == 3: preco_38_percent (sem desconto)
   - Se ranking == 4: preco_38_percent * 1.24

7. preco_atacado (float):
   - Sempre preco_38_percent

Salve o resultado em data/parquet/admmat_extended.parquet

Retorne um relatório com:
- Total de linhas processadas
- Amostra de 5 produtos com todas as colunas
- Estatísticas: média de MC, total de produtos que precisam abastecimento
- Tempo de processamento
```

---

#### **Tarefa 1.2: Criar Ferramentas UNE**
**Agente:** `@code-agent`
**Tokens:** ~15.000
**Arquivo:** `core/tools/une_tools.py`

**Prompt para code-agent:**
```
Crie o arquivo core/tools/une_tools.py com 3 ferramentas LangChain:

1. @tool
   def calcular_abastecimento_une(une_id: int, segmento: str = None) -> dict:
       """
       Calcula produtos que precisam de abastecimento em uma UNE.

       Regra: ESTOQUE_UNE <= 50% LINHA_VERDE

       Args:
           une_id: ID da UNE (1-10)
           segmento: Filtro opcional (ex: "TECIDOS", "PAPELARIA")

       Returns:
           dict com:
           - total_produtos: int (total que precisa abastecimento)
           - produtos: list[dict] (top 20 produtos)
           - regra_aplicada: str
       """
       # Carregar data/parquet/admmat_extended.parquet
       # Filtrar por une_id e segmento (se fornecido)
       # Retornar produtos onde precisa_abastecimento == True
       # Ordernar por qtd_a_abastecer DESC
       # Limitar a 20 produtos

2. @tool
   def calcular_mc_produto(produto_id: int, une_id: int) -> dict:
       """
       Calcula Média Comum (MC) de um produto específico.

       MC = (Média 12 meses + Média 3 meses + Mês ano anterior) / 3

       Args:
           produto_id: Código do produto
           une_id: ID da UNE

       Returns:
           dict com:
           - produto_id: int
           - nome: str
           - mc_calculada: float
           - media_12_meses: float
           - media_3_meses: float
           - estoque_gondola: float
           - recomendacao: str ("Aumentar ESTOQUE" ou "Manter")
       """
       # Buscar produto no Parquet
       # Calcular MC conforme fórmula
       # Comparar com estoque_gondola_lv
       # Retornar análise

3. @tool
   def calcular_preco_final_une(valor_compra: float, ranking: int, forma_pagamento: str) -> dict:
       """
       Calcula preço final aplicando política de preços UNE.

       Args:
           valor_compra: Valor total da compra (R$)
           ranking: Ranking do produto (0-4)
           forma_pagamento: 'vista', '30d', '90d', '120d'

       Returns:
           dict com:
           - valor_original: float
           - tipo: str ("Atacado" ou "Varejo")
           - ranking: int
           - desconto_ranking: str
           - forma_pagamento: str
           - desconto_pagamento: str
           - preco_final: float
           - economia: float
       """
       # Implementar lógica de ranking
       # Aplicar limite de atacado (>= R$ 750)
       # Aplicar desconto por forma de pagamento
       # Retornar cálculo detalhado

IMPORTANTE:
- Use pandas para ler Parquet
- Adicione type hints completos
- Docstrings detalhadas
- Tratamento de erros (try/except)
- Logging de operações
- Imports: from langchain_core.tools import tool
```

---

### **DIA 2: INTEGRAÇÃO + TESTES (32h tokens)**

#### **Tarefa 2.1: Integrar Ferramentas no CaculinhaBI**
**Agente:** `@code-agent`
**Tokens:** ~20.000
**Arquivo:** `core/agents/caculinha_bi_agent.py`

**Prompt para code-agent:**
```
Modifique core/agents/caculinha_bi_agent.py para integrar as 3 novas ferramentas:

1. Na função create_caculinha_bi_agent():
   - Importar: from core.tools.une_tools import calcular_abastecimento_une, calcular_mc_produto, calcular_preco_final_une
   - Adicionar à lista bi_tools: [query_product_data, list_table_columns, generate_and_execute_python_code, calcular_abastecimento_une, calcular_mc_produto, calcular_preco_final_une]

2. Modificar tool_selection_prompt para incluir descrições das novas ferramentas:
   - calcular_abastecimento_une: Para perguntas sobre "quais produtos precisam abastecimento", "linha verde", "estoque baixo"
   - calcular_mc_produto: Para perguntas sobre "média comum", "MC", "histórico de vendas"
   - calcular_preco_final_une: Para perguntas sobre "preço", "quanto custa", "desconto", "varejo", "atacado"

3. Atualizar agent_runnable_logic para rotear corretamente:
   - Detectar intent "abastecimento" → calcular_abastecimento_une
   - Detectar intent "mc" ou "media comum" → calcular_mc_produto
   - Detectar intent "preco" → calcular_preco_final_une

Retorne o diff das modificações.
```

---

#### **Tarefa 2.2: Criar Testes Automatizados**
**Agente:** `@code-agent`
**Tokens:** ~12.000
**Arquivo:** `tests/test_une_operations.py`

**Prompt para code-agent:**
```
Crie tests/test_une_operations.py com testes para as 3 ferramentas:

import pytest
from core.tools.une_tools import calcular_abastecimento_une, calcular_mc_produto, calcular_preco_final_une

def test_calcular_abastecimento():
    """Testa se calcula abastecimento corretamente"""
    result = calcular_abastecimento_une(une_id=5, segmento="TECIDOS")
    assert result['total_produtos'] >= 0
    assert 'produtos' in result
    assert 'regra_aplicada' in result
    print(f"✅ Abastecimento: {result['total_produtos']} produtos")

def test_calcular_mc():
    """Testa cálculo de MC"""
    result = calcular_mc_produto(produto_id=369947, une_id=5)
    assert 'mc_calculada' in result
    assert result['mc_calculada'] >= 0
    assert 'recomendacao' in result
    print(f"✅ MC: {result['mc_calculada']}")

def test_calcular_preco():
    """Testa política de preços"""
    result = calcular_preco_final_une(valor_compra=600, ranking=0, forma_pagamento='30d')
    assert result['preco_final'] > 0
    assert result['preco_final'] <= result['valor_original']
    assert result['tipo'] == "Varejo"
    print(f"✅ Preço: R$ {result['preco_final']}")

def test_calcular_preco_atacado():
    """Testa preço atacado (>= R$ 750)"""
    result = calcular_preco_final_une(valor_compra=800, ranking=0, forma_pagamento='vista')
    assert result['tipo'] == "Atacado"
    print(f"✅ Atacado: R$ {result['preco_final']}")

if __name__ == "__main__":
    test_calcular_abastecimento()
    test_calcular_mc()
    test_calcular_preco()
    test_calcular_preco_atacado()
    print("\n🎉 Todos os testes passaram!")
```

---

### **DIA 3: DOCUMENTAÇÃO + DEMO (25h tokens)**

#### **Tarefa 3.1: Documentação Técnica**
**Agente:** `@doc-agent`
**Tokens:** ~8.000
**Arquivo:** `docs/IMPLEMENTACAO_UNE_MVP.md`

**Prompt para doc-agent:**
```
Crie documentação completa em docs/IMPLEMENTACAO_UNE_MVP.md com:

# Implementação MVP - Regras UNE

## 1. Visão Geral
- Resumo das regras implementadas
- Arquitetura da solução

## 2. Regras de Negócio Implementadas
### 2.1 Cálculo de MC (Média Comum)
- Fórmula oficial
- Implementação técnica
- Exemplo de uso

### 2.2 Linha Verde
- Definição
- Cálculo
- Exemplo

### 2.3 Disparo de Abastecimento
- Regra (50% LV)
- Implementação
- Query de exemplo

### 2.4 Política de Preços
- Tabela de rankings
- Limite atacado/varejo
- Exemplos de cálculo

## 3. Arquivos Criados/Modificados
- data/parquet/admmat_extended.parquet
- core/tools/une_tools.py
- core/agents/caculinha_bi_agent.py (modificado)
- tests/test_une_operations.py

## 4. Queries Suportadas
Liste 10 exemplos de queries funcionais

## 5. Testes e Validação
- Como executar testes
- Resultados esperados

## 6. Roadmap Futuro
- Features não implementadas
- Próximos passos

Incluir exemplos de código, tabelas e diagramas quando aplicável.
```

---

#### **Tarefa 3.2: Script de Demonstração**
**Agente:** `@bi-agent`
**Tokens:** ~5.000
**Arquivo:** `demo/demo_une_operations.py`

**Prompt para bi-agent:**
```
Crie um script de demonstração interativo em demo/demo_une_operations.py:

from core.agents.caculinha_bi_agent import initialize_agent_for_session
import json

def demo_completa():
    """Executa demonstração completa das funcionalidades UNE"""

    agent = initialize_agent_for_session()

    print("🚀 DEMO: Operações UNE - MVP")
    print("=" * 60)

    # Demo 1: Abastecimento
    print("\n📦 DEMO 1: Cálculo de Abastecimento")
    print("Query: 'Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 5?'")
    result1 = agent.process_query("Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 5?")
    print(f"✅ Resultado:\n{json.dumps(result1['output'], indent=2, ensure_ascii=False)}")

    # Demo 2: Cálculo MC
    print("\n📊 DEMO 2: Cálculo de Média Comum (MC)")
    print("Query: 'Calcule a MC do produto 369947 na UNE 5'")
    result2 = agent.process_query("Calcule a MC do produto 369947 na UNE 5")
    print(f"✅ Resultado:\n{json.dumps(result2['output'], indent=2, ensure_ascii=False)}")

    # Demo 3: Política de Preços
    print("\n💰 DEMO 3: Política de Preços")
    print("Query: 'Quanto fica uma compra de R$ 600 com ranking 0 pagando em 30 dias?'")
    result3 = agent.process_query("Quanto fica uma compra de R$ 600 com ranking 0 pagando em 30 dias?")
    print(f"✅ Resultado:\n{json.dumps(result3['output'], indent=2, ensure_ascii=False)}")

    # Demo 4: Preço Atacado
    print("\n🏪 DEMO 4: Preço Atacado (>= R$ 750)")
    print("Query: 'Quanto fica uma compra de R$ 800 pagando à vista?'")
    result4 = agent.process_query("Quanto fica uma compra de R$ 800 pagando à vista?")
    print(f"✅ Resultado:\n{json.dumps(result4['output'], indent=2, ensure_ascii=False)}")

    print("\n" + "=" * 60)
    print("✅ Demonstração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Robô automático de MC (virada de mês)")
    print("2. Arredondamento de múltiplos")
    print("3. Dashboard gerencial")

if __name__ == "__main__":
    demo_completa()
```

---

## 📊 CONTROLE DE EXECUÇÃO

### **Checklist Dia 1:**
- [ ] data-agent: Processar Parquet → admmat_extended.parquet
- [ ] code-agent: Criar une_tools.py (3 ferramentas)
- [ ] Validação: Verificar colunas adicionadas no Parquet
- [ ] Teste manual: Importar une_tools e chamar cada função

### **Checklist Dia 2:**
- [ ] code-agent: Modificar caculinha_bi_agent.py
- [ ] code-agent: Criar test_une_operations.py
- [ ] Validação: Executar pytest tests/test_une_operations.py
- [ ] Teste end-to-end: Query conversacional funcionando

### **Checklist Dia 3:**
- [ ] doc-agent: Criar IMPLEMENTACAO_UNE_MVP.md
- [ ] bi-agent: Criar demo_une_operations.py
- [ ] Validação: Executar demo e verificar saídas
- [ ] Preparar apresentação final

---

## 🎯 TOKENS POR AGENTE

| Agente | Tarefas | Tokens Estimados | % do Total |
|--------|---------|------------------|------------|
| **data-agent** | Processar Parquet | 15.000 | 15.3% |
| **code-agent** | Criar tools + Integrar + Testes | 47.000 | 48.1% |
| **doc-agent** | Documentação | 8.000 | 8.2% |
| **bi-agent** | Demo script | 5.000 | 5.1% |
| **orchestrator** | Coordenação | 10.000 | 10.2% |
| **Contingência** | Ajustes/Debug | 12.750 | 13.1% |
| **TOTAL** | - | **97.750** | **100%** |

---

## ✅ CRITÉRIOS DE SUCESSO

1. ✅ Parquet estendido com colunas calculadas corretas
2. ✅ 3 ferramentas UNE funcionando via LangChain
3. ✅ Integração com CaculinhaBI funcionando
4. ✅ Testes automatizados passando (4/4)
5. ✅ Documentação completa e clara
6. ✅ Demo executável mostrando funcionalidades
7. ✅ Consumo de tokens < 100.000 (50% do budget)

---

## 🚨 PLANO DE CONTINGÊNCIA

**Se tokens acabarem antes do fim:**

1. **Prioridade 1 (Essencial):**
   - ✅ Parquet estendido (data-agent)
   - ✅ une_tools.py (code-agent)
   - ✅ Integração CaculinhaBI (code-agent)

2. **Prioridade 2 (Importante):**
   - ⚠️ Testes automatizados
   - ⚠️ Documentação básica

3. **Prioridade 3 (Desejável):**
   - 📋 Demo elaborada
   - 📋 Documentação detalhada

**Estratégia:** Se atingir 90% dos tokens (108k), parar e gerar relatório do que foi implementado.
