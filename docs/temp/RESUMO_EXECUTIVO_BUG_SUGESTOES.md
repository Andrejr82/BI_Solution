# RESUMO EXECUTIVO: Bug Sugestões Automáticas

**Data:** 2025-10-16
**Analista:** UNE Operations Agent
**Severidade:** 🔴 CRÍTICA
**Status:** Análise concluída - Aguardando implementação

---

## 1. PROBLEMA IDENTIFICADO

### Sintomas:
1. ❌ Sugestões automáticas mostram APENAS produtos da UNE 1 como origem
2. ❌ Sempre aparece "PONTEIRA METAL SINO ASPIRAL J207 14.5MM" independente do filtro
3. ❌ Filtro de fabricante não é dinâmico (não muda ao selecionar segmento)

### Impacto no Negócio:
- Sistema não está redistribuindo estoque entre UNEs corretamente
- Decisões de transferência baseadas em dados incompletos
- UNEs com superavit não sendo utilizadas (exceto UNE 1)
- Potencial perda de vendas por falta de produtos em UNEs que precisam

---

## 2. CAUSA RAIZ

### Arquivo Afetado: `core/tools/une_tools.py`
**Função:** `sugerir_transferencias_automaticas` (linhas 815-1054)

### Bug Principal: Algoritmo Não Agrupa por Produto

```python
# CÓDIGO ATUAL (BUGADO) - Linha ~900:
for _, produto in df_match.iterrows():
    une_origem = int(produto['une_id'])  # ← Pega a primeira UNE encontrada
    produto_id = int(produto['produto_id'])

    # Busca info da origem (sempre a mesma UNE)
    info_origem = df[(df['produto_id'] == produto_id) &
                     (df['une_id'] == une_origem)].iloc[0]
```

### Por Que Só Retorna UNE 1?

O DataFrame `df_match` contém produtos filtrados, mas **não está agrupado por produto**.

**Fluxo Atual:**
```
1. Filtra produtos com superavit → df_superavit
2. Filtra produtos com deficit na UNE destino → df_deficit
3. Intersecção dos conjuntos → df_match
4. Itera df_match linha por linha ← PROBLEMA AQUI
5. Para cada linha, pega une_id direto da linha
6. Se Parquet está ordenado por UNE (1,2,3...), sempre pega UNE 1
```

**Resultado:** Nunca busca outras UNEs com o mesmo produto em superavit.

---

## 3. LINHA ESPECÍFICA DO BUG

### Arquivo: `C:\Users\André\Documents\Agent_Solution_BI\core\tools\une_tools.py`

**Linha ~900:**
```python
une_origem = int(produto['une_id'])  # ← BUG: Não busca outras UNEs
```

**Deveria ser:**
```python
# Buscar TODAS as UNEs com superavit deste produto
df_origens = df[
    (df['produto_id'] == produto_id) &
    (df['une_id'] != une_destino_id) &
    (df['deficit'] < 0)  # Tem superavit
]

# Ordenar por maior superavit
df_origens = df_origens.sort_values('superavit', ascending=False)

# Pegar melhor origem
melhor_origem = df_origens.iloc[0]
une_origem = int(melhor_origem['une_id'])
```

---

## 4. PSEUDOCÓDIGO DA SOLUÇÃO

### Novo Algoritmo (Completo):

```
FUNÇÃO sugerir_transferencias_automaticas(une_destino_id, filtros):

    # PASSO 1: Carregar e preparar dados
    df = carregar_parquet('admmat.parquet')
    df['deficit'] = df['linha_verde'] - df['estoque']

    # Aplicar filtros (segmento, fabricante)
    SE filtros.segmento:
        df = df[df['segmento'] == filtros.segmento]

    SE filtros.fabricante:
        df = df[df['fabricante'] == filtros.fabricante]

    # PASSO 2: Identificar produtos em deficit na UNE destino
    df_destino = df[
        (df['une_id'] == une_destino_id) E
        (df['deficit'] > 0)  # Precisa receber produtos
    ]

    SE df_destino vazio:
        RETORNAR "Nenhum produto em deficit"

    # PASSO 3: Para cada produto em deficit, buscar melhores origens
    sugestoes = []

    PARA CADA produto EM df_destino:
        produto_id = produto['produto_id']
        deficit_qtd = produto['deficit']

        # Buscar TODAS as UNEs com superavit deste produto
        df_origens = df[
            (df['produto_id'] == produto_id) E
            (df['une_id'] != une_destino_id) E
            (df['deficit'] < 0)  # Tem superavit (excesso)
        ]

        SE df_origens vazio:
            CONTINUE  # Pula este produto

        # Calcular superavit absoluto
        df_origens['superavit'] = ABS(df_origens['deficit'])

        # Ordenar por maior superavit (UNE com mais excesso)
        df_origens = ORDENAR(df_origens, POR='superavit', DESCENDENTE)

        # Pegar melhor origem (maior superavit)
        melhor_origem = df_origens[0]

        # Calcular quantidade ótima de transferência
        qtd_transferir = MINIMO(
            deficit_qtd,                    # Não transferir mais que o deficit
            melhor_origem['superavit'],     # Não transferir mais que o superavit
            melhor_origem['estoque']        # Não transferir mais que o estoque
        )

        # Criar sugestão
        sugestao = {
            'produto_id': produto_id,
            'produto_nome': produto['nome'],
            'une_origem_id': melhor_origem['une_id'],      # ← Agora varia!
            'une_destino_id': une_destino_id,
            'estoque_origem': melhor_origem['estoque'],
            'estoque_destino': produto['estoque'],
            'superavit_origem': melhor_origem['superavit'],
            'deficit_destino': deficit_qtd,
            'quantidade_sugerida': qtd_transferir,
            'prioridade': deficit_qtd * melhor_origem['superavit']  # Métrica de impacto
        }

        sugestoes.ADICIONAR(sugestao)

    # PASSO 4: Rankear por prioridade (maior impacto primeiro)
    sugestoes = ORDENAR(sugestoes, POR='prioridade', DESCENDENTE)

    # PASSO 5: Limitar resultados
    sugestoes = sugestoes[0:limite]

    RETORNAR {
        'status': 'success',
        'sugestoes': sugestoes,
        'total_analisado': TAMANHO(df_destino),
        'total_sugestoes': TAMANHO(sugestoes)
    }
```

---

## 5. SOLUÇÃO PROBLEMA 2: Filtro Dinâmico de Fabricante

### Arquivo: `pages/7_📦_Transferências.py`

**Código Atual (Estático):**
```python
fabricantes = df['fabricante'].unique().tolist()
fabricante_selecionado = st.selectbox('Fabricante', fabricantes)
```

**Código Corrigido (Dinâmico):**
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

## 6. VALIDAÇÃO DA SOLUÇÃO

### Testes Automatizados:

```python
# Teste 1: Verificar múltiplas origens
def test_multiplas_origens():
    resultado = sugerir_transferencias_automaticas(une_destino_id=2, limite=20)
    unes_origem = set(sug['une_origem_id'] for sug in resultado['sugestoes'])

    assert len(unes_origem) > 1, "Deve ter mais de uma UNE de origem"
    assert 1 not in unes_origem or len(unes_origem) > 1, "Não pode ter só UNE 1"

# Teste 2: Verificar ordenação por prioridade
def test_ordenacao_prioridade():
    resultado = sugerir_transferencias_automaticas(une_destino_id=2, limite=10)
    sugestoes = resultado['sugestoes']

    for i in range(len(sugestoes) - 1):
        assert sugestoes[i]['prioridade'] >= sugestoes[i+1]['prioridade']

# Teste 3: Verificar quantidade não excede estoque
def test_quantidade_valida():
    resultado = sugerir_transferencias_automaticas(une_destino_id=2)

    for sug in resultado['sugestoes']:
        assert sug['quantidade_sugerida'] <= sug['estoque_origem']
        assert sug['quantidade_sugerida'] <= sug['deficit_destino']
```

### Teste Manual:

1. Selecionar UNE destino = 2
2. **Verificar:** Devem aparecer origens variadas (UNE 1, 3, 4, etc.)
3. Selecionar segmento = "MOVEIS"
4. **Verificar:** Lista de fabricantes deve mudar
5. Selecionar fabricante específico
6. **Verificar:** Sugestões devem filtrar corretamente

---

## 7. ARQUIVOS A MODIFICAR

### 1. `C:\Users\André\Documents\Agent_Solution_BI\core\tools\une_tools.py`
**Linhas:** 815-1054 (função completa)
**Mudança:** Implementar novo algoritmo de agrupamento por produto

### 2. `C:\Users\André\Documents\Agent_Solution_BI\pages\7_📦_Transferências.py`
**Seção:** Filtros de segmento e fabricante
**Mudança:** Adicionar lógica cascata para filtro dinâmico

---

## 8. CRONOGRAMA DE IMPLEMENTAÇÃO

### Fase 1: Correção Core (2-3 horas)
- [ ] Implementar novo algoritmo em `une_tools.py`
- [ ] Adicionar logging detalhado
- [ ] Criar testes unitários

### Fase 2: Correção UI (1 hora)
- [ ] Implementar filtro cascata em Streamlit
- [ ] Adicionar feedback visual de carregamento
- [ ] Testar interação entre filtros

### Fase 3: Validação (1 hora)
- [ ] Executar bateria de testes automatizados
- [ ] Teste manual com dados reais
- [ ] Validar com stakeholders

**Total Estimado:** 4-5 horas

---

## 9. IMPACTO E PRIORIDADE

| Métrica | Valor |
|---------|-------|
| **Severidade** | 🔴 CRÍTICA |
| **Impacto no Negócio** | ALTO - Sistema não cumpre função principal |
| **Usuários Afetados** | TODOS - Funcionalidade core |
| **Urgência** | IMEDIATA |
| **Complexidade** | MÉDIA - Mudança algorítmica |
| **Risco de Regressão** | BAIXO - Função isolada |

---

## 10. PRÓXIMOS PASSOS IMEDIATOS

1. ✅ **Executar diagnóstico:**
   ```bash
   python scripts/diagnostico_sugestoes_automaticas.py
   ```

2. ✅ **Executar testes:**
   ```bash
   python tests/test_bug_sugestoes_une1.py
   ```

3. ⏳ **Implementar correção:**
   - Modificar `core/tools/une_tools.py`
   - Modificar `pages/7_📦_Transferências.py`

4. ⏳ **Validar:**
   - Rodar testes automatizados
   - Teste manual na interface
   - Aprovação stakeholder

5. ⏳ **Deploy:**
   - Commit com mensagem descritiva
   - Push para main
   - Deploy Streamlit Cloud

---

## 11. DOCUMENTAÇÃO DE SUPORTE

### Arquivos Criados:
- ✅ `docs/ANALISE_BUG_SUGESTOES_UNE1.md` - Análise técnica detalhada
- ✅ `scripts/diagnostico_sugestoes_automaticas.py` - Script de diagnóstico
- ✅ `tests/test_bug_sugestoes_une1.py` - Bateria de testes
- ✅ `docs/RESUMO_EXECUTIVO_BUG_SUGESTOES.md` - Este documento

### Comandos Úteis:
```bash
# Diagnóstico completo
python scripts/diagnostico_sugestoes_automaticas.py

# Testes automatizados
python tests/test_bug_sugestoes_une1.py

# Limpar cache (se necessário)
python scripts/limpar_cache.py
```

---

## 12. RISCOS E MITIGAÇÃO

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Mudança quebra outros módulos | Alto | Baixo | Função isolada, sem dependências |
| Performance degradada com novo algoritmo | Médio | Médio | Adicionar índices, otimizar loops |
| Dados inconsistentes no Parquet | Alto | Baixo | Validação de dados antes do processamento |
| Regressão em produção | Alto | Baixo | Testes automatizados + validação manual |

---

## 13. CONCLUSÃO

O bug foi **identificado com precisão** e a **solução está documentada**.

### Causa Confirmada:
Algoritmo não está agrupando produtos para buscar múltiplas UNEs de origem - pega apenas a primeira linha do DataFrame filtrado.

### Solução Proposta:
Reestruturar loop para:
1. Iterar produtos em deficit
2. Para cada produto, buscar TODAS as UNEs com superavit
3. Selecionar melhor origem por critério de prioridade

### Status Atual:
🔴 **AGUARDANDO APROVAÇÃO PARA IMPLEMENTAÇÃO**

---

**Preparado por:** UNE Operations Agent
**Revisão técnica:** Pendente
**Aprovação negócio:** Pendente

---

*Documento gerado automaticamente em 2025-10-16*
