# Documento de Integração: `field_mapper.py`

**Data:** 09/10/2025
**Autor:** Gemini
**Status:** ✅ Implementado

## 1. Visão Geral

Este documento detalha a integração do módulo `core/utils/field_mapper.py` com o `DirectQueryEngine`, o motor de consultas diretas do Agent_BI. Esta integração é um passo crucial para centralizar a lógica de negócio e aumentar a precisão e manutenibilidade do sistema.

O `field_mapper.py` atua como um **dicionário de negócios**, traduzindo termos em linguagem natural (ex: "preço", "estoque") para os nomes técnicos das colunas no banco de dados (ex: `LIQUIDO_38`, `ESTOQUE_UNE`).

## 2. O Problema Original

Antes desta integração, o `DirectQueryEngine` possuía uma lógica interna e codificada para interpretar as perguntas dos usuários. Isso resultava em vários problemas:

- **Duplicação de Lógica:** A lógica de mapeamento de palavras-chave estava espalhada e duplicada.
- **Baixa Manutenibilidade:** Adicionar suporte a novas perguntas exigia alterações complexas no código do motor de consultas.
- **Inconsistência:** O sistema poderia interpretar a mesma pergunta de maneiras diferentes dependendo do fluxo de execução, como no caso da consulta sobre "categorias com estoque 0", que era incorretamente direcionada para um gráfico de pizza.

## 3. A Solução: Integração Profunda

A refatoração implementada integrou profundamente o `field_mapper.py` no `DirectQueryEngine`. As seguintes alterações foram realizadas:

### 3.1. Inicialização Centralizada

O `DirectQueryEngine` agora inicializa uma instância do `FieldMapper` em seu construtor, tornando-o disponível para todos os seus métodos.

```python
# core/business_intelligence/direct_query_engine.py

from core.utils.field_mapper import get_field_mapper

class DirectQueryEngine:
    def __init__(self, parquet_adapter: ParquetAdapter):
        # ...
        self.field_mapper = get_field_mapper()
        # ...
```

### 3.2. Classificação de Intenção Guiada pelo Mapeador

O método `classify_intent_direct` foi refatorado para usar o `field_mapper` como sua principal fonte de inteligência:

1.  **Padrões de Regex (Alta Prioridade):** O sistema ainda utiliza os padrões de regex do arquivo `query_patterns_training.json` para identificar perguntas muito específicas e estruturadas.

2.  **Busca por Palavras-Chave (Nova Lógica):** Se nenhum padrão de regex for encontrado, o método agora consulta o `field_mapper.get_all_mappings()` para procurar palavras-chave de negócio na pergunta do usuário.

3.  **Roteamento Inteligente:** Com base na combinação de palavras-chave encontradas, o sistema roteia a consulta para o método de execução apropriado. Por exemplo, a presença de "categorias" e "estoque 0" agora direciona corretamente para o método `_query_distribuicao_categoria`.

### 3.3. Geração de Gráficos Dinâmica

O método `_query_distribuicao_categoria` foi aprimorado para não gerar sempre um gráfico de pizza. Agora, ele conta o número de categorias a serem exibidas:

- **Até 8 categorias:** Gera um **gráfico de pizza**.
- **Mais de 8 categorias:** Gera um **gráfico de barras**, que é muito mais legível para um volume maior de dados.

```python
# core/business_intelligence/direct_query_engine.py

# No método _query_distribuicao_categoria
num_categorias = len(categorias)
chart_type = "bar" if num_categorias > 8 else "pie"

chart_data = {
    "type": chart_type,
    # ...
}
```

## 4. Fluxo de uma Consulta: Exemplo Prático

Vamos ver como a consulta **"quais sao as categorias do segmento tecidos com estoque 0?"** é processada agora:

1.  **Entrada:** A consulta é recebida pelo `DirectQueryEngine`.
2.  **Classificação:** O `classify_intent_direct` é chamado.
    - Ele não encontra um padrão de regex exato.
    - Ele detecta as palavras-chave "categorias", "segmento" e "estoque 0".
    - A nova regra de classificação identifica esta combinação e roteia para o método `_query_distribuicao_categoria`, passando os parâmetros `segmento='TECIDOS'` e um indicador de `estoque_zero`.
3.  **Execução:** O método `_query_distribuicao_categoria` é executado.
    - Ele filtra o DataFrame para o segmento "TECIDOS".
    - Em seguida, aplica o filtro para `estoque_atual == 0`.
    - Ele agrupa os resultados por categoria e conta o número de produtos.
4.  **Geração do Gráfico:**
    - O método conta o número de categorias resultantes (ex: 85).
    - Como 85 é maior que 8, ele define `chart_type` como `"bar"`.
    - Ele prepara os dados para um gráfico de barras.
5.  **Resposta:** O sistema retorna uma resposta do tipo `chart` contendo a especificação para um gráfico de barras, que a interface do Streamlit renderiza corretamente.

## 5. Benefícios da Nova Arquitetura

- **Precisão Aumentada:** A interpretação das perguntas agora é baseada em um dicionário de negócios centralizado, reduzindo significativamente as chances de erro.
- **Manutenção Simplificada:** Para adicionar suporte a novos termos de negócio ou ajustar o comportamento de consultas, basta atualizar o `field_mapper.py` e os arquivos de templates, sem a necessidade de alterar a lógica complexa do motor de consultas.
- **Consistência Garantida:** Todos os componentes do sistema que precisam entender a linguagem de negócio podem agora usar o `field_mapper`, garantindo uma interpretação uniforme em toda a aplicação.
