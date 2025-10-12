# Guia Conceitual de Refatoração para Dask

**Objetivo:** Refatorar o arquivo `core/business_intelligence/direct_query_engine.py` para usar Dask, eliminando o carregamento de dados em memória e prevenindo travamentos.

**Arquivo-Alvo:** `core/business_intelligence/direct_query_engine.py`

---

### Princípios da Refatoração

1.  **Abandono do Padrão "Carregar Tudo":** O padrão atual de carregar todo o arquivo Parquet em um DataFrame Pandas com `adapter.execute_query({})` no início de cada método de consulta deve ser completamente eliminado.

2.  **Adoção do Processamento "Lazy" (Preguiçoso):** A nova abordagem deve ser:
    *   Criar um DataFrame Dask que apenas aponta para o arquivo, sem carregar dados.
    *   Realizar todas as operações de agregação (`groupby`, `sum`, `nlargest`, etc.) de forma "lazy" sobre este DataFrame Dask.
    *   Apenas no final, chamar o método `.compute()` sobre o resultado já agregado e pequeno para trazê-lo para a memória.

---

### Passos da Implementação

1.  **Adicionar Dependências:** Garanta que `dask[dataframe]` e `pyarrow` estejam no arquivo `requirements.txt` e instalados no ambiente virtual.

2.  **Adicionar Import:** No topo do arquivo `direct_query_engine.py`, adicione a importação: `import dask.dataframe as dd`.

3.  **Centralizar a Criação do DataFrame:**
    *   Crie um novo método auxiliar na classe, como `_get_base_dask_df()`. 
    *   A responsabilidade deste método é criar o DataFrame Dask base (`dd.read_parquet(...)`) e adicionar a coluna calculada `vendas_total` de forma "lazy".
    *   Este será o único ponto no código que lê o arquivo Parquet.

4.  **Refatorar o `execute_direct_query`:**
    *   Altere este método para que ele não carregue mais nenhum dado.
    *   Sua única função deve ser despachar a chamada para o método `_query_*` correto.
    *   Implemente uma lógica para tratar o `query_type == 'fallback'` no início, retornando uma mensagem informativa sem tentar processar dados.

5.  **Refatorar os Métodos de Consulta (`_query_*`):
    *   Altere a assinatura de todos os métodos de consulta que recebiam `(self, adapter, params)` ou `(self, df, params)` para receber apenas `(self, params)`.
    *   Reescreva o corpo de cada método que faz agregações em todo o dataset (ex: `_query_produto_mais_vendido`, `_query_segmento_campao`, `_query_ranking_vendas_unes`, etc.).
    *   A nova lógica deve seguir o padrão "lazy":
        1.  Chamar `self._get_base_dask_df()` para obter o DataFrame Dask.
        2.  Aplicar as operações de agregação do Dask.
        3.  Chamar `.compute()` no resultado final e pequeno.
        4.  Usar o DataFrame Pandas resultante (pequeno) para formatar a resposta JSON e os dados do gráfico.

6.  **Manter Métodos Eficientes:**
    *   Métodos que já trabalham com filtros específicos (ex: `_query_consulta_produto_especifico`) não precisam de uma refatoração completa da lógica, mas devem ser adaptados para usar o `ParquetAdapter` que agora retorna um DataFrame Pandas (após o `.compute()` interno), em vez de um dicionário.

---

### Verificação Final

Após aplicar todas as alterações conceituais acima, execute a suíte de testes para validar a implementação:

```bash
pytest tests/test_direct_queries.py -v
```
