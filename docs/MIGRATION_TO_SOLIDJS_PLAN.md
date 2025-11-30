# Plano de Migração para SolidJS

Este documento descreve a estratégia, ferramentas e práticas ideais para migrar um projeto (especialmente o frontend React encontrado em `backups/frontend-react`) para SolidJS. Ele serve como um guia conceitual para a transição.

## 1. Entendimento das Diferenças Fundamentais (React vs. SolidJS)

A migração exige uma mudança de mentalidade significativa, pois SolidJS e React operam em paradigmas diferentes:

*   **Reatividade:**
    *   **React:** Utiliza um Virtual DOM e um processo de reconciliação. A reatividade é baseada em "dirty checking" (comparações) e re-renderizações de componentes inteiros quando o estado ou props mudam. Hooks como `useState` e `useReducer` disparam essas re-renderizações.
    *   **SolidJS:** Implementa um sistema de reatividade fina (fine-grained reactivity). As atualizações são direcionadas *apenas* aos nós do DOM que dependem de um valor reativo específico. Isso é gerenciado por primitivos reativos como `createSignal`, `createEffect` e `createMemo`. Não há Virtual DOM, nem re-renderizações de componentes no sentido React.

*   **Ciclo de Vida e Renderização:**
    *   **React:** Componentes são funções que rodam a cada re-renderização, gerando um novo VDOM que é comparado com o anterior. Hooks como `useEffect` gerenciam efeitos colaterais após a renderização e limpeza.
    *   **SolidJS:** Componentes são funções que rodam *uma única vez* durante a fase de montagem para construir o gráfico reativo inicial. As atualizações subsequentes do DOM são tratadas diretamente pela reatividade, sem re-execução do componente.

*   **Hooks vs. Primitivos:**
    *   **React:** Usa Hooks para adicionar funcionalidades de estado e ciclo de vida a componentes funcionais.
    *   **SolidJS:** Utiliza "primitivos" reativos (ex: `createSignal`, `createEffect`, `createMemo`, `createStore`) diretamente para definir e gerenciar comportamento reativo.

*   **Transformação JSX:**
    *   **React:** O JSX é compilado para chamadas de `React.createElement` que constroem a árvore do Virtual DOM.
    *   **SolidJS:** O compilador SolidJS transforma o JSX em código JavaScript que cria e atualiza diretamente os nós do DOM. Isso resulta em código extremamente eficiente com performance próxima ao JavaScript vanilla.

## 2. Estratégia de Migração: Abordagem Componente por Componente

Uma migração completa é um esforço de reescrita substancial. Uma abordagem incremental e sistemática é crucial:

### 2.1. Análise e Preparação

*   **Inventário de Componentes e Lógica:** Liste todos os componentes React do projeto `backups/frontend-react`, identificando suas props, estado local (`useState`, `useReducer`), contexto global, efeitos colaterais (`useEffect`) e lógica de negócio.
*   **Análise de Dependências:** Avalie todas as bibliotecas de terceiros usadas no projeto React. Verifique se existem equivalentes SolidJS ou se são agnósticas a frameworks.
*   **Seleção de Prova de Conceito (PoC):** Escolha um componente pequeno, isolado e com poucas dependências para migrar primeiro. Isso ajudará a validar o processo e a construir experiência.

### 2.2. Conversão da Lógica

*   **Gerenciamento de Estado:**
    *   **`useState` (React) -> `createSignal` (SolidJS):** Transfira o estado local para sinais. Lembre-se que `createSignal` retorna um getter e um setter.
    *   **`useReducer` (React) -> `createSignal` / `createEffect` ou `createStore` (SolidJS):** Para estados mais complexos, `createStore` do Solid é uma ótima opção para estados aninhados e mutáveis.
    *   **Estado Global (React Context, Redux, Zustand):**
        *   **`React.createContext` -> `Solid.createContext`:** A API é similar, mas a reatividade subjacente é diferente.
        *   **Bibliotecas agnósticas/integradas:** Se usar Zustand, considere suas integrações SolidJS (`zustand-solid`). Para outras, talvez seja necessário reimplementar a lógica com primitivos SolidJS.

*   **Efeitos Colaterais:**
    *   **`useEffect` (React) -> `createEffect` (SolidJS):** `createEffect` é para efeitos que não produzem um valor reativo (e.g., log, manipulação DOM direta, subscriptions, sincronização com APIs externas). Use-o com moderação, pois muitas vezes `createMemo` ou a reatividade intrínseca do Solid já resolvem.
    *   **Valores Derivados:** Para valores que dependem de outros reativos, use `createMemo` para cachear o resultado e recomputar apenas quando as dependências mudarem.

*   **Props e Fluxo de Dados:**
    *   Em SolidJS, as `props` são *getters* reativos por padrão. Evite desestruturá-las diretamente no escopo do componente para não perder a reatividade. Acesse-as via `props.nomeDaProp`. Se precisar de um valor reativo derivado de uma prop, use `createMemo`.

*   **Renderização Condicional e Listas:**
    *   **Condicionais:** Substitua `&&` e operadores ternários por componentes de controle de fluxo otimizados do SolidJS como `<Show>` para renderização condicional.
    *   **Listas:** Substitua o `.map()` dentro do JSX por `<For>` ou `<Index>` para renderizar listas de forma performática e reativa.

*   **Refs e Manipulação Direta do DOM:**
    *   **`useRef` (React) -> Atribuição direta em SolidJS:** Atribua o ref diretamente ao elemento JSX (ex: `<div ref={myDivRef}>`).

*   **Event Handlers:**
    *   São semelhantes, mas a função do handler é criada uma vez e reutilizada, aproveitando a natureza de "rodar uma vez" dos componentes SolidJS.

### 2.3. Adaptação do Build e Testes

*   **Sistema de Build:** O projeto `frontend-solid` já usa **Vite** com **`vite-plugin-solid`**, que é a configuração ideal. Certifique-se de que o pipeline de build esteja configurado para transacionar corretamente os arquivos migrados.
*   **Testes:**
    *   **Componentes:** Adapte os testes existentes do React Testing Library (`@testing-library/react`) para o Solid Testing Library (`@solidjs/testing-library`).
    *   **Lógica de Negócio:** Testes unitários para lógica de negócio e estados (usando `createSignal`, `createStore`) devem ser reescritos para usar as APIs reativas do Solid.

### 2.4. Otimização e Melhorias Contínuas

*   **Solid Devtools:** Utilize as ferramentas de desenvolvimento do SolidJS para inspecionar o gráfico de reatividade, depurar fluxos de dados e identificar possíveis gargalos.
*   **Anti-padrões:** Fique atento a anti-padrões comuns, como usar `createEffect` onde `createMemo` seria mais apropriado, ou criar primitivos reativos em loops sem o devido gerenciamento.

## 3. Ferramentas e Bibliotecas Essenciais

*   **Bibliotecas Core:**
    *   `solid-js`
    *   `@solidjs/router` (se necessário)
    *   `@solidjs/testing-library`
    *   `@tanstack/solid-query` (se houver uso de TanStack Query)
*   **Build Tool:**
    *   `vite`
    *   `vite-plugin-solid`
*   **Gerenciamento de Estado (exemplos):**
    *   Próprio `createStore` do Solid
    *   `zustand-solid` (se migrar de Zustand)
*   **Utilidades:**
    *   `clsx`, `tailwind-merge` (agnósticos a frameworks)
    *   `axios` (agnóstico a frameworks)
    *   `lucide-solid` (para ícones, se usado `lucide-react`)
*   **Qualidade de Código:**
    *   **ESLint:** Configure com `eslint-plugin-solid` para regras específicas.
    *   **TypeScript:** Mantenha a tipagem para robustez.

## 4. Melhores Práticas de Desenvolvimento SolidJS

*   **Pense Reativo, Não em Re-renderizações:** Este é o pilar do SolidJS. Cada "renderização" do componente acontece uma vez; as atualizações são diretas e reativas.
*   **Prefira `createMemo` para Valores Derivados:** Ele otimiza a recomputação, executando-a apenas quando suas dependências mudam.
*   **Use `createEffect` com Propósito:** Apenas para efeitos colaterais que não modificam outros sinais de forma reativa.
*   **Componentes de Controle de Fluxo são seus Amigos:** `<Show>`, `<For>`, `<Index>` são mais performáticos e idiomáticos que as contrapartes do React.
*   **Entenda as Props como Getters:** Sempre que acessar uma prop, você está "lendo" um valor reativo.

Ao seguir estas diretrizes, a migração para SolidJS será mais suave e resultará em uma aplicação mais performática e eficiente.
