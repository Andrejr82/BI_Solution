# Regras de Negócio para Transferência de Produtos

Este documento descreve as regras de negócio que governam o sistema de transferência de produtos entre Unidades de Negócio (UNEs). A lógica é dividida em duas funcionalidades principais: a **validação de transferências manuais** e a **sugestão automática de transferências**.

---

## 1. Validação de Transferência Manual (`validar_transferencia_produto`)

Esta funcionalidade atua como um "juiz" para uma transferência específica que o usuário tenta realizar. Ela avalia se a operação é recomendada.

### Processo de Validação

1.  **Coleta de Dados:** O sistema analisa o produto na **origem** e no **destino**, focando em:
    *   `estoque_atual`: A quantidade física do produto.
    *   `linha_verde`: O nível de estoque máximo recomendado para a UNE.
    *   `mc` (Média Comum): A média histórica de vendas.
    *   `venda_30_d`: O total de vendas nos últimos 30 dias.

2.  **Regras de Bloqueio (Critérios Eliminatórios):**
    A transferência é **imediatamente bloqueada** se:
    *   A quantidade solicitada for maior que o `estoque_atual` da origem.
    *   A transferência deixar o estoque da origem em um nível crítico (abaixo de 50% de sua `linha_verde`).

3.  **Cálculo do "Score de Prioridade" (0 a 100):**
    Se a transferência não for bloqueada, uma pontuação é calculada para definir sua prioridade. A nota é a soma de três fatores:

    *   **Fator 1: Necessidade do Destino (até 40 pontos)**
        *   Estoque do destino `< 25%` da linha verde: **+40 pontos**
        *   Estoque do destino `< 50%` da linha verde: **+30 pontos**
        *   Estoque do destino `< 75%` da linha verde: **+20 pontos**

    *   **Fator 2: Excesso na Origem (até 30 pontos)**
        *   Estoque da origem `> 150%` da linha verde: **+30 pontos**
        *   Estoque da origem `> 125%` da linha verde: **+20 pontos**
        *   Estoque da origem `> 100%` da linha verde: **+10 pontos**

    *   **Fator 3: Demanda no Destino (até 30 pontos)**
        *   Estoque atual cobre `< 7 dias` de venda: **+30 pontos**
        *   Estoque atual cobre `< 15 dias` de venda: **+20 pontos**
        *   Estoque atual cobre `< 30 dias` de venda: **+10 pontos**

4.  **Classificação da Prioridade:**
    Com base na pontuação final, a transferência é classificada como:
    *   `>= 80`: **URGENTE**
    *   `>= 60`: **ALTA**
    *   `>= 40`: **NORMAL**
    *   `< 40`: **BAIXA** ou **NÃO RECOMENDADA**

---

## 2. Sugestão Automática de Transferências (`sugerir_transferencias_automaticas`)

Esta funcionalidade atua como um "consultor proativo", varrendo todo o sistema em busca de oportunidades de balanceamento de estoque.

### Processo de Geração de Sugestões

1.  **Análise Global:** O sistema carrega os dados de estoque de **todos os produtos em todas as UNEs**.

2.  **Mapeamento de Oportunidades:** São identificados dois cenários:
    *   **Excesso:** Produtos com estoque acima de 100% da `linha_verde`.
    *   **Falta:** Produtos com estoque abaixo de 75% da `linha_verde`.

3.  **Busca por Combinações:** O sistema cruza as listas para encontrar "pares perfeitos": um produto que está sobrando em uma UNE e faltando em outra.

4.  **Cálculo de Score e Priorização:**
    Para cada par encontrado, um score de prioridade é calculado (com lógica similar à da validação manual) para ranquear as melhores oportunidades.

5.  **Geração da Sugestão:**
    As melhores oportunidades são transformadas em sugestões, contendo:
    *   O produto, a origem e o destino.
    *   A **quantidade sugerida** (calculada para ser ideal para ambos os lados).
    *   A prioridade, o score e o motivo da sugestão.
    *   O **benefício estimado** (ex: "Elevará o estoque do destino de 20% para 85% da linha verde").

6.  **Ranking Final:** As sugestões são ordenadas pelo score, e as mais relevantes são apresentadas ao usuário.
