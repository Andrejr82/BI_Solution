# Sistema de Transferências com Regras de Negócio UNE

## Visão Geral

Sistema inteligente de transferências entre UNEs que aplica regras de negócio baseadas em:
- **Linha Verde** (estoque ideal)
- **MC** (Média Comum de vendas)
- **Histórico de vendas** (últimos 30 dias)
- **Balanceamento de estoque** entre UNEs

## Ferramentas Implementadas

### 1. `validar_transferencia_produto()`

Valida se uma transferência específica é viável e recomendada.

**Parâmetros:**
- `produto_id`: Código do produto
- `une_origem`: ID da UNE que vai enviar
- `une_destino`: ID da UNE que vai receber
- `quantidade`: Quantidade a transferir

**Retorna:**
- `valido`: Boolean indicando se a transferência é válida
- `prioridade`: "URGENTE", "ALTA", "NORMAL", "BAIXA" ou "NAO_RECOMENDADA"
- `score_prioridade`: Pontuação 0-100 (quanto maior, mais prioritária)
- `quantidade_recomendada`: Quantidade ideal para transferir
- `detalhes_origem`: Dados completos da origem
- `detalhes_destino`: Dados completos do destino
- `recomendacoes`: Lista de ações sugeridas

**Regras de Validação:**

1. **Estoque Suficiente na Origem**
   - Valida se origem tem a quantidade solicitada

2. **Não Comprometer Origem**
   - Transferência não pode deixar origem com < 50% da linha verde
   - Evita criar novo problema ao resolver outro

3. **Score de Prioridade** (0-100 pontos):
   - **Necessidade do Destino** (0-40 pontos):
     - < 25% LV: 40 pontos
     - 25-50% LV: 30 pontos
     - 50-75% LV: 20 pontos
     - > 75% LV: 5 pontos

   - **Excesso na Origem** (0-30 pontos):
     - > 150% LV: 30 pontos
     - 125-150% LV: 20 pontos
     - 100-125% LV: 10 pontos

   - **Demanda no Destino** (0-30 pontos):
     - < 7 dias de estoque: 30 pontos
     - 7-15 dias: 20 pontos
     - 15-30 dias: 10 pontos

**Exemplo de Uso:**

```python
from core.tools.une_tools import validar_transferencia_produto

resultado = validar_transferencia_produto(
    produto_id=12345,
    une_origem=1,
    une_destino=3,
    quantidade=50
)

if resultado['valido']:
    print(f"Prioridade: {resultado['prioridade']}")
    print(f"Score: {resultado['score_prioridade']}/100")
    print(f"Quantidade recomendada: {resultado['quantidade_recomendada']}")

    for rec in resultado['recomendacoes']:
        print(f"  - {rec}")
else:
    print(f"Transferência inválida: {resultado['motivo']}")
```

---

### 2. `sugerir_transferencias_automaticas()`

Gera sugestões inteligentes de transferências entre UNEs.

**Parâmetros:**
- `limite`: Número máximo de sugestões (padrão: 20)

**Retorna:**
- `total_sugestoes`: Número de sugestões geradas
- `sugestoes`: Lista de sugestões ordenadas por prioridade
- `estatisticas`: Resumo das sugestões

**Cada Sugestão Contém:**
- `produto_id`, `nome_produto`, `segmento`
- `une_origem`, `une_destino`
- `quantidade_sugerida`
- `prioridade`: "URGENTE", "ALTA", "NORMAL", "BAIXA"
- `score`: Pontuação de prioridade
- `motivo`: Justificativa da sugestão
- `beneficio_estimado`: Melhoria esperada no destino
- `detalhes`: Dados completos de origem e destino

**Lógica de Sugestão:**

1. **Identificação de Oportunidades:**
   - UNEs com **excesso**: > 100% da linha verde
   - UNEs com **falta**: < 75% da linha verde
   - Cruza produtos iguais entre UNEs

2. **Cálculo de Quantidade:**
   - Disponível na origem: `estoque - linha_verde`
   - Necessário no destino: `linha_verde - estoque`
   - Quantidade sugerida: `min(disponível, necessário)`

3. **Priorização:**
   - **Score baseado em 3 fatores** (0-100 pontos):
     - Criticidade do destino (0-50 pontos)
     - Excesso na origem (0-25 pontos)
     - Demanda do produto no destino (0-25 pontos)

4. **Ordenação:**
   - Sugestões ordenadas por score (maior primeiro)
   - Limitado ao número solicitado

**Estatísticas Geradas:**
- Total de sugestões
- Breakdown por prioridade (urgentes, altas, normais, baixas)
- Total de unidades a transferir
- Número de produtos únicos
- Número de UNEs envolvidas (origem e destino)

**Exemplo de Uso:**

```python
from core.tools.une_tools import sugerir_transferencias_automaticas

resultado = sugerir_transferencias_automaticas(limite=10)

print(f"Total de sugestões: {resultado['total_sugestoes']}")

stats = resultado['estatisticas']
print(f"Urgentes: {stats['urgentes']}")
print(f"Altas: {stats['altas']}")
print(f"Total de unidades: {stats['total_unidades']}")

for sug in resultado['sugestoes'][:5]:
    print(f"\nProduto: {sug['nome_produto']}")
    print(f"  UNE {sug['une_origem']} → UNE {sug['une_destino']}")
    print(f"  Quantidade: {sug['quantidade_sugerida']}")
    print(f"  Prioridade: {sug['prioridade']} (Score: {sug['score']})")
    print(f"  Motivo: {sug['motivo']}")
```

---

## Integração com Sistema Existente

### Integração com Página de Transferências

As novas ferramentas podem ser integradas à página `pages/7_📦_Transferências.py`:

```python
from core.tools.une_tools import (
    validar_transferencia_produto,
    sugerir_transferencias_automaticas
)

# Ao adicionar produto ao carrinho:
validacao = validar_transferencia_produto(
    produto_id=codigo,
    une_origem=une_origem,
    une_destino=une_destino,
    quantidade=qtd
)

if validacao['valido']:
    if validacao['prioridade'] == 'URGENTE':
        st.error(f"⚠️ URGENTE: {validacao['motivo']}")
    elif validacao['prioridade'] == 'ALTA':
        st.warning(f"⚡ ALTA: {validacao['motivo']}")
    else:
        st.success(f"✓ Transferência válida")

    # Mostrar recomendações
    for rec in validacao['recomendacoes']:
        st.info(rec)
else:
    st.error(f"❌ {validacao['motivo']}")
```

### Nova Funcionalidade: Sugestões Automáticas

Adicionar botão na página de transferências:

```python
if st.button("🤖 Gerar Sugestões Automáticas"):
    sugestoes = sugerir_transferencias_automaticas(limite=20)

    st.success(f"✓ {sugestoes['total_sugestoes']} sugestões geradas")

    # Mostrar estatísticas
    stats = sugestoes['estatisticas']
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Urgentes", stats['urgentes'])
    with col2:
        st.metric("Altas", stats['altas'])
    with col3:
        st.metric("Total Unidades", stats['total_unidades'])
    with col4:
        st.metric("Produtos", stats['produtos_unicos'])

    # Mostrar sugestões
    for sug in sugestoes['sugestoes']:
        with st.expander(f"🎯 {sug['nome_produto']} - {sug['prioridade']}"):
            st.write(f"**UNE {sug['une_origem']} → UNE {sug['une_destino']}**")
            st.write(f"Quantidade: {sug['quantidade_sugerida']} unidades")
            st.write(f"Score: {sug['score']:.1f}/100")
            st.write(f"Motivo: {sug['motivo']}")
            st.write(f"Benefício: {sug['beneficio_estimado']}")

            if st.button("Adicionar ao Carrinho", key=f"add_{sug['produto_id']}"):
                # Adicionar ao carrinho de transferências
                pass
```

---

## Casos de Uso

### Caso 1: Validação de Transferência Manual

**Cenário:** Usuário quer transferir 100 unidades de um produto da UNE 1 para UNE 3.

**Fluxo:**
1. Sistema valida estoque na origem
2. Calcula score de prioridade
3. Verifica se transferência não compromete origem
4. Retorna recomendações

**Resultado:**
- Se válido: Mostra prioridade e recomendações
- Se inválido: Explica o motivo e sugere alternativas

### Caso 2: Sugestões Automáticas para Balanceamento

**Cenário:** Gestor quer saber quais transferências fazer para otimizar estoque.

**Fluxo:**
1. Sistema analisa todas as UNEs
2. Identifica UNEs com excesso e falta
3. Cruza produtos compatíveis
4. Calcula scores de prioridade
5. Ordena e retorna top sugestões

**Resultado:**
- Lista priorizada de transferências
- Estatísticas gerais
- Benefícios estimados para cada transferência

### Caso 3: Transferência Urgente

**Cenário:** UNE 5 tem produto crítico (< 25% linha verde).

**Fluxo:**
1. Sistema identifica criticidade
2. Busca UNEs com excesso desse produto
3. Sugere transferência com prioridade URGENTE
4. Calcula quantidade ideal

**Resultado:**
- Alerta de urgência
- Sugestão de transferência imediata
- Quantidade que resolve o problema sem comprometer origem

---

## Métricas e KPIs

### Métricas de Validação

- **Taxa de Aprovação**: % de transferências validadas como viáveis
- **Score Médio**: Média dos scores de prioridade
- **Distribuição de Prioridades**: Breakdown por nível

### Métricas de Sugestões

- **Oportunidades Identificadas**: Total de transferências possíveis
- **Taxa de Cobertura**: % de UNEs com falta que podem ser supridas
- **Eficiência de Balanceamento**: Redução estimada de desbalanceamento

### Métricas de Impacto

- **Transferências Realizadas**: Total executado
- **Unidades Balanceadas**: Total de unidades transferidas
- **UNEs Beneficiadas**: Número de UNEs que melhoraram estoque
- **Redução de Rupturas**: % de redução de produtos críticos

---

## Testes

Execute os testes com:

```bash
python tests/test_une_transferencias.py
```

**Testes Implementados:**
1. Validação de transferência válida
2. Validação de transferência inválida (quantidade excessiva)
3. Sugestões automáticas
4. Validação com origem = destino (deve falhar)

---

## Próximos Passos

### Fase 2: Automação
- [ ] Transferências automáticas para casos URGENTES
- [ ] Agendamento de transferências
- [ ] Integração com sistema de logística

### Fase 3: Analytics
- [ ] Dashboard de transferências
- [ ] Histórico de balanceamento
- [ ] Previsão de necessidades futuras

### Fase 4: Otimização
- [ ] Algoritmo de otimização multi-UNE
- [ ] Consideração de custos de transferência
- [ ] Rotas otimizadas de transferência

---

## Documentação Técnica

### Dependências

- `pandas`: Manipulação de dados
- `langchain_core.tools`: Decorador @tool para LangChain
- Arquivo Parquet: `data/parquet/admmat_extended.parquet`

### Estrutura de Dados

**Colunas Necessárias no Parquet:**
- `codigo`: ID do produto
- `nome_produto`: Nome do produto
- `une`: ID da UNE
- `estoque_atual`: Estoque atual
- `linha_verde`: Estoque ideal (máximo)
- `mc`: Média Comum (média de vendas)
- `venda_30_d`: Vendas dos últimos 30 dias
- `nomesegmento`: Segmento do produto

### Logging

Todas as operações são logadas com o módulo `logging`:
- INFO: Operações normais
- WARNING: Situações inesperadas
- ERROR: Erros com traceback completo

---

## Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Executar testes unitários
3. Validar estrutura do arquivo Parquet
4. Consultar documentação do código (docstrings)

---

**Versão:** 1.0
**Data:** 2025-01-14
**Autor:** Agent_Solution_BI Team
