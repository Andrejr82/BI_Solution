# Plano de Melhorias para a Interface

Este documento descreve as possíveis melhorias para a interface do agente de BI, com um plano de implementação para cada uma.

## 1. Sugestões Proativas

*   **Objetivo:** Após uma resposta, o agente sugere perguntas ou análises relevantes para o usuário.
*   **Plano de Implementação:**
    1.  **Modificar a Lógica do Agente:** No arquivo `core/agents/caculinha_bi_agent.py`, após a geração de uma resposta, adicionar um novo passo para gerar perguntas de acompanhamento.
    2.  **Criar um Novo Prompt:** Desenvolver um prompt específico para o LLM, que irá gerar perguntas relevantes com base na consulta do usuário e na resposta fornecida.
    3.  **Atualizar a Interface:** No arquivo `streamlit_app.py`, exibir as perguntas sugeridas como botões clicáveis abaixo da resposta do agente. Ao clicar em um botão, a pergunta correspondente será enviada como uma nova consulta.

## 2. Feedback Granular do Usuário

*   **Objetivo:** Permitir que os usuários forneçam feedback sobre partes específicas da resposta do agente (por exemplo, um gráfico ou uma tabela).
*   **Plano de Implementação:**
    1.  **Atualizar o Componente de Feedback:** Modificar o arquivo `ui/feedback_component.py` para incluir opções de feedback mais específicas (ex: "Este gráfico foi útil?", "Os dados estão corretos?").
    2.  **Integrar o Componente de Feedback:** No `streamlit_app.py`, chamar o componente de feedback atualizado após a exibição de um gráfico ou tabela.
    3.  **Armazenar o Feedback:** Modificar o mecanismo de armazenamento de feedback para salvar as informações granulares, associando-as à parte específica da resposta a que se referem.

## 3. Recurso "Você quis dizer?"

*   **Objetivo:** Sugerir correções para consultas ambíguas ou com erros de digitação.
*   **Plano de Implementação:**
    1.  **Criar um Componente "Corretor de Consultas":** Este componente receberá a consulta do usuário como entrada e retornará uma versão corrigida ou uma lista de sugestões.
    2.  **Utilizar uma Biblioteca de Verificação Ortográfica:** Integrar uma biblioteca Python como `pyspellchecker` ou uma abordagem mais avançada, utilizando um modelo de linguagem pré-treinado. Adicionar a biblioteca ao `requirements.txt`.
    3.  **Integrar o Corretor:** No `core/agents/caculinha_bi_agent.py`, antes de processar a consulta do usuário, passá-la pelo corretor. Se o corretor sugerir uma alteração, pedir a confirmação do usuário antes de prosseguir.

## 4. Mensagens de Espera Mais Envolventes

*   **Objetivo:** Exibir mensagens mais informativas e envolventes enquanto o usuário aguarda uma resposta.
*   **Plano de Implementação:**
    1.  **Criar uma Lista de Mensagens:** Elaborar uma lista de fatos curiosos, dicas ou citações relacionadas à análise de dados.
    2.  **Modificar o `st.spinner`:** No `streamlit_app.py`, dentro da função `query_backend`, modificar o `st.spinner` para exibir uma mensagem aleatória da lista.
    3.  **Adicionar um Botão "Cancelar":** Enquanto o usuário aguarda, fornecer um botão "Cancelar" para interromper o processamento da consulta.

## 5. Personalização

*   **Objetivo:** O agente aprende com as preferências do usuário ao longo do tempo para oferecer uma experiência mais personalizada.
*   **Plano de Implementação:**
    1.  **Estender a Ferramenta `save_memory`:** Ampliar a ferramenta `save_memory` para armazenar preferências mais complexas do usuário, como regiões, produtos ou tipos de gráficos preferidos.
    2.  **Utilizar a Memória para Personalizar Respostas:** No `core/agents/caculinha_bi_agent.py`, antes de gerar uma resposta, recuperar as preferências do usuário da memória e usá-las para adaptar a resposta.
    3.  **Aprendizado Implícito de Preferências:** O agente também pode aprender as preferências de forma implícita, analisando as consultas e o feedback do usuário. Por exemplo, se um usuário frequentemente pede dados de uma região específica, o agente pode inferir que esta é uma região de preferência.

## 6. Visualizações de Dados Avançadas

*   **Objetivo:** Gerar visualizações de dados mais avançadas e interativas.
*   **Plano de Implementação:**
    1.  **Integrar uma Nova Biblioteca de Visualização:** Utilizar uma biblioteca como `deck.gl` para mapas, `holoviews` para gráficos interativos, ou `vtk` para gráficos 3D. Adicionar a biblioteca ao `requirements.txt`.
    2.  **Criar Novas Ferramentas para Visualizações Avançadas:** Desenvolver novas ferramentas em `core/tools/` que utilizem a nova biblioteca para gerar as visualizações.
    3.  **Atualizar a Lógica do Agente:** No `core/agents/caculinha_bi_agent.py`, atualizar o `tool_selection_prompt` para incluir as novas ferramentas de visualização.
