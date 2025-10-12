# Relatório de Refatoração: Otimização de Carregamento de Dados com Predicate Pushdown

## Visão Geral

Este documento detalha a refatoração realizada no motor de consulta direta (`DirectQueryEngine`) e no adaptador de dados Parquet (`ParquetAdapter`) para resolver um gargalo crítico de performance relacionado ao carregamento de dados.

## O Problema: Carregamento Ineficiente de Dados

O `DirectQueryEngine` estava carregando o arquivo Parquet (`addmat.parquet`) inteiro na memória para cada consulta do usuário. Esta abordagem, embora funcional, apresentava duas desvantagens principais:

1.  **Alto Consumo de Memória**: Carregar um dataset completo, que pode ter milhões de linhas, consome uma quantidade significativa de RAM, arriscando exceder os limites em ambientes de produção.
2.  **Baixa Performance**: A necessidade de ler todo o arquivo do disco e mantê-lo em memória para então filtrar os dados necessários para a consulta gerava uma latência alta e desnecessária na resposta ao usuário.

A estratégia de amostragem (`sampling`) foi tentada anteriormente, mas se mostrou ineficaz e propensa a bugs, resultando em consultas com "0 resultados" e análises imprecisas.

## A Solução: Predicate Pushdown e Arquitetura Sob Demanda

A solução implementada foi uma refatoração em duas frentes para adotar o padrão **Predicate Pushdown** e uma arquitetura de carregamento de dados sob demanda.

### 1. Refatoração do `ParquetAdapter`

O `ParquetAdapter` foi modificado para "empurrar" os filtros da consulta diretamente para a camada de leitura do arquivo Parquet. A biblioteca `pyarrow`, utilizada pelo `pandas`, suporta a aplicação de filtros durante a leitura, o que significa que apenas as linhas que correspondem aos critérios da consulta são carregadas na memória.

- O método `execute_query` agora converte os dicionários de filtro em um formato compatível com o `pyarrow`.
- A leitura dos dados é feita com `pd.read_parquet(..., filters=pyarrow_filters)`, garantindo que a filtragem ocorra no nível mais baixo e eficiente possível.

### 2. Refatoração do `DirectQueryEngine`

O `DirectQueryEngine` foi re-arquitetado para se alinhar com a nova capacidade do `ParquetAdapter`:

- **Eliminação do Carregamento Antecipado**: O `DirectQueryEngine` não carrega mais o DataFrame completo no início da execução da consulta.
- **Delegação de Responsabilidade**: A responsabilidade de buscar os dados foi delegada aos métodos de consulta individuais (`_query_*`).
- **Nova Assinatura de Método**: Todos os métodos `_query_*` agora recebem a instância do `ParquetAdapter` em vez de um DataFrame pré-carregado.
- **Busca de Dados Sob Demanda**: Cada método `_query_*` agora é responsável por construir seu próprio conjunto de filtros e chamar `adapter.execute_query(filters)` para obter apenas os dados de que precisa.

## Benefícios da Nova Arquitetura

- **Performance Melhorada**: O tempo de resposta para consultas filtradas foi drasticamente reduzido, pois o volume de dados lido do disco e processado em memória é muito menor.
- **Redução do Consumo de Memória**: A aplicação não precisa mais manter o dataset inteiro em memória para responder às consultas, tornando-a mais estável e escalável.
- **Precisão Garantida**: Ao contrário da amostragem, o Predicate Pushdown opera no conjunto de dados completo, garantindo 100% de precisão nos resultados.
- **Código Mais Limpo e Coeso**: A responsabilidade de buscar dados agora reside claramente em cada método de consulta, tornando o código mais fácil de entender e manter.

## Limitações e Próximos Passos

A implementação atual de Predicate Pushdown via `pyarrow` tem limitações em cenários de filtros complexos (ex: aplicar um `OR` em duas colunas diferentes). Para as consultas que necessitam dessa lógica, a solução atual ainda carrega o DataFrame completo para garantir a corretude do filtro. Uma otimização futura pode investigar a construção de um mapa de metadados (ex: `une_nome` para `une_codigo`) na inicialização para permitir que mais consultas se beneficiem do Predicate Pushdown.
