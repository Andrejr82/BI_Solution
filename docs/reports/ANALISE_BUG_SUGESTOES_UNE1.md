# ANÁLISE: Bug Sugestões Automáticas Limitadas à UNE 1

**Data:** 2025-10-16
**Autor:** UNE Operations Agent
**Arquivo:** `core/tools/une_tools.py` (linhas 815-1054)

---

## PROBLEMA REPORTADO

1. Sugestões automáticas só mostram produtos da UNE 1 como origem
2. Sempre aparece "PONTEIRA METAL SINO ASPIRAL J207 14.5MM" para qualquer filtro
3. Filtro de fabricante não é dinâmico

---

## CAUSA RAIZ IDENTIFICADA

### PROBLEMA 1: Lógica de Agrupamento Incorreta

**Arquivo:** `core/tools/une_tools.py`
**Linhas:** 900-920 (aproximadamente)

```python
# CÓDIGO ATUAL (BUGADO):
sugestoes = []

for _, produto in df_match.iterrows():
    une_origem = int(produto['une_id'])
    produto_id = int(produto['produto_id'])

    # Buscar informações da UNE origem
    info_origem = df[(df['produto_id'] == produto_id) &
                     (df['une_id'] == une_origem)].iloc[0]

    # Buscar informações da UNE destino
    info_destino = df[(df['produto_id'] == produto_id) &
                      (df['une_id'] == une_destino_id)].iloc[0]

    sugestao = {
        'produto_id': produto_id,
        'produto_nome': produto.get('nome', ''),
        'une_origem_id': une_origem,
        'une_destino_id': une_destino_id,
        # ...
    }
    sugestoes.append(sugestao)
```

**PROBLEMA:** A função está iterando `df_match` que JÁ contém apenas produtos filtrados, mas não está verificando se o mesmo produto existe em múltiplas UNEs. Ela retorna sempre a primeira ocorrência.

### PROBLEMA 2: Ordenação Fixa

**Linhas:** 940-950 (aproximadamente)

```python
# Ordenar por potencial de transferência
sugestoes_df = pd.DataFrame(sugestoes)
sugestoes_df = sugestoes_df.sort_values(
    by=['superavit_origem', 'deficit_destino'],
    ascending=[False, False]
)
```

**PROBLEMA:** Se houver apenas um produto que satisfaz os critérios e ele está na UNE 1, ele sempre será retornado primeiro e será o único dentro do limite.

### PROBLEMA 3: Filtro de Matching Muito Restritivo

**Linhas:** 870-890 (aproximadamente)

```python
# Filtrar produtos com superavit na origem
df_superavit = df[df['deficit'] < 0].copy()

# Filtrar produtos com deficit no destino
df_deficit = df[
    (df['une_id'] == une_destino_id) &
    (df['deficit'] > 0)
].copy()

# Produtos em comum
produtos_match = set(df_superavit['produto_id']) & set(df_deficit['produto_id'])
df_match = df_superavit[df_superavit['produto_id'].isin(produtos_match)]
```

**PROBLEMA:** Esta lógica está correta CONCEITUALMENTE, mas não está agrupando corretamente por produto para permitir múltiplas origens.

---

## ANÁLISE DO ALGORITMO ATUAL

### Fluxo Atual:
```
1. Carregar admmat.parquet
2. Calcular deficit = linha_verde - estoque
3. Filtrar produtos com superavit (deficit < 0)
4. Filtrar produtos com deficit na UNE destino
5. Fazer intersecção dos conjuntos
6. Iterar df_match (que contém UNE origem já definida)
7. Retornar primeiras N sugestões
```

### Por que só retorna UNE 1?

O `df_match` após os filtros contém múltiplas linhas, mas como o DataFrame não está agrupado por produto, ele retorna a primeira linha de cada produto que encontra. Se o Parquet está ordenado por UNE (1, 2, 3...), sempre pega UNE 1 primeiro.

---

## SOLUÇÃO PROPOSTA

### Abordagem: Reestruturar Algoritmo para Agrupar por Produto

```python
def sugerir_transferencias_automaticas(
    une_destino_id: int,
    segmento: Optional[str] = None,
    fabricante: Optional[str] = None,
    limite: int = 10
) -> Dict:
    """
    Sugere transferências automáticas baseadas em deficit/superavit

    NOVO ALGORITMO:
    1. Identificar produtos em deficit na UNE destino
    2. Para cada produto em deficit:
       a. Buscar TODAS as UNEs com superavit desse produto
       b. Ordenar por maior superavit
       c. Calcular quantidade ótima de transferência
    3. Rankear sugestões por impacto (maior deficit + maior superavit)
    """

    try:
        # Carregar dados
        df = pd.read_parquet(CAMINHO_PARQUET)

        # Calcular deficit
        df['deficit'] = df['linha_verde'] - df['estoque']

        # Aplicar filtros
        if segmento:
            df = df[df['segmento'] == segmento]
        if fabricante:
            df = df[df['fabricante'] == fabricante]

        # PASSO 1: Produtos em deficit na UNE destino
        df_destino = df[
            (df['une_id'] == une_destino_id) &
            (df['deficit'] > 0)
        ].copy()

        if df_destino.empty:
            return {
                'status': 'success',
                'sugestoes': [],
                'mensagem': 'Nenhum produto em deficit na UNE destino'
            }

        # PASSO 2: Para cada produto, buscar melhores origens
        sugestoes = []

        for _, prod_destino in df_destino.iterrows():
            produto_id = prod_destino['produto_id']
            deficit_qtd = prod_destino['deficit']

            # Buscar TODAS as UNEs com superavit deste produto
            df_origens = df[
                (df['produto_id'] == produto_id) &
                (df['une_id'] != une_destino_id) &
                (df['deficit'] < 0)  # Tem superavit
            ].copy()

            if df_origens.empty:
                continue

            # Ordenar por maior superavit (abs do deficit negativo)
            df_origens['superavit'] = abs(df_origens['deficit'])
            df_origens = df_origens.sort_values('superavit', ascending=False)

            # Pegar melhor origem
            melhor_origem = df_origens.iloc[0]

            # Calcular quantidade ótima
            qtd_transferir = min(
                deficit_qtd,  # Não transferir mais que o deficit
                melhor_origem['superavit'],  # Não transferir mais que o superavit
                melhor_origem['estoque']  # Não transferir mais que o estoque
            )

            # Criar sugestão
            sugestao = {
                'produto_id': int(produto_id),
                'produto_nome': prod_destino.get('nome', ''),
                'codigo_barras': prod_destino.get('codigo_barras', ''),
                'une_origem_id': int(melhor_origem['une_id']),
                'une_origem_nome': melhor_origem.get('une_nome', ''),
                'une_destino_id': une_destino_id,
                'une_destino_nome': prod_destino.get('une_nome', ''),
                'estoque_origem': int(melhor_origem['estoque']),
                'estoque_destino': int(prod_destino['estoque']),
                'linha_verde_origem': int(melhor_origem['linha_verde']),
                'linha_verde_destino': int(prod_destino['linha_verde']),
                'superavit_origem': int(melhor_origem['superavit']),
                'deficit_destino': int(deficit_qtd),
                'quantidade_sugerida': int(qtd_transferir),
                'segmento': prod_destino.get('segmento', ''),
                'fabricante': prod_destino.get('fabricante', ''),
                'prioridade': deficit_qtd * melhor_origem['superavit']  # Métrica de impacto
            }

            sugestoes.append(sugestao)

        # PASSO 3: Rankear por prioridade
        sugestoes_df = pd.DataFrame(sugestoes)
        sugestoes_df = sugestoes_df.sort_values('prioridade', ascending=False)

        # Limitar resultados
        sugestoes_final = sugestoes_df.head(limite).to_dict('records')

        return {
            'status': 'success',
            'sugestoes': sugestoes_final,
            'total_analisado': len(df_destino),
            'total_sugestoes': len(sugestoes_final)
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'sugestoes': []
        }
```

---

## SOLUÇÃO PARA PROBLEMA 2: Filtro de Fabricante Dinâmico

**Arquivo:** `pages/7_📦_Transferências.py`

### Código Atual (Problema):
```python
# Filtro de fabricante está fixo
fabricantes = df['fabricante'].unique().tolist()
fabricante_selecionado = st.selectbox('Fabricante', fabricantes)
```

### Código Corrigido:
```python
# Filtrar fabricantes baseado no segmento selecionado
if segmento_selecionado and segmento_selecionado != 'Todos':
    fabricantes_filtrados = df[
        df['segmento'] == segmento_selecionado
    ]['fabricante'].unique().tolist()
else:
    fabricantes_filtrados = df['fabricante'].unique().tolist()

fabricantes_filtrados = ['Todos'] + sorted(fabricantes_filtrados)
fabricante_selecionado = st.selectbox(
    'Fabricante',
    fabricantes_filtrados,
    key='filtro_fabricante_dinamico'
)
```

---

## RESUMO DAS MUDANÇAS

### Arquivo: `core/tools/une_tools.py`

**Mudança 1:** Reestruturar loop principal
- ANTES: Iterar `df_match` (uma linha por produto-UNE)
- DEPOIS: Iterar produtos em deficit e buscar TODAS as origens possíveis

**Mudança 2:** Adicionar agrupamento por produto
- ANTES: Primeira UNE encontrada
- DEPOIS: Todas as UNEs com superavit, ordenadas por melhor opção

**Mudança 3:** Métrica de prioridade
- ANTES: Ordenar por superavit e deficit separadamente
- DEPOIS: Criar métrica combinada (deficit * superavit)

### Arquivo: `pages/7_📦_Transferências.py`

**Mudança 1:** Filtro cascata
- Quando seleciona segmento, atualizar lista de fabricantes
- Usar `st.session_state` para controlar dependências

---

## VALIDAÇÃO PROPOSTA

### Testes Unitários:
```python
# Teste 1: Verificar múltiplas origens
assert len(set(sug['une_origem_id'] for sug in sugestoes)) > 1

# Teste 2: Verificar ordenação por prioridade
assert sugestoes[0]['prioridade'] >= sugestoes[1]['prioridade']

# Teste 3: Verificar quantidade não excede estoque
for sug in sugestoes:
    assert sug['quantidade_sugerida'] <= sug['estoque_origem']
```

### Teste de Integração:
1. Selecionar UNE destino = 2
2. Verificar se aparecem origens diferentes (UNE 1, 3, 4, etc.)
3. Mudar segmento e verificar se fabricantes mudam

---

## IMPACTO E PRIORIDADE

**Severidade:** ALTA
**Impacto:** Sistema não está cumprindo função principal
**Urgência:** CRÍTICA
**Estimativa de correção:** 2-4 horas

---

## PRÓXIMOS PASSOS

1. Implementar novo algoritmo em `une_tools.py`
2. Adicionar testes unitários
3. Implementar filtro cascata em Streamlit
4. Testar com dados reais
5. Validar com stakeholders

---

## ARQUIVOS PARA MODIFICAR

- `C:\Users\André\Documents\Agent_Solution_BI\core\tools\une_tools.py` (linhas 815-1054)
- `C:\Users\André\Documents\Agent_Solution_BI\pages\7_📦_Transferências.py` (linhas de filtros)

---

**STATUS:** Análise concluída - Aguardando aprovação para implementação
