# Plano de Execução da Migração para SolidJS (Versão para LLM)

Este documento detalha as etapas para migrar o projeto de frontend React (localizado em `backups/frontend-react`) para SolidJS, integrando-o ao projeto `frontend-solid` existente. Este plano foi revisado para ser executável por um Large Language Model (LLM) como o Gemini, com instruções granulares e uso explícito de ferramentas.

---

## Orientações de Execução por LLM

*   **Execução Sequencial:** O LLM deve executar cada passo em ordem.
*   **Marcação de Progresso:** Após a conclusão bem-sucedida de um item (incluindo todas as suas sub-etapas), o LLM deve registrar o progresso, idealmente atualizando o status do item na sua lista interna de tarefas (`write_todos`).
*   **Comunicação com o Usuário:** Quando `[USER_INPUT_REQUIRED]` for indicado, o LLM deve solicitar a informação ou decisão ao usuário.
*   **Resumibilidade:** Em caso de interrupção, o LLM deve ser capaz de retomar a execução do último passo concluído. O progresso deve ser rastreado através da lista interna de tarefas do LLM.
*   **Segurança:** Todas as operações que modificam o sistema de arquivos ou o código devem ser previamente explicadas e, se aplicável, confirmadas pelo usuário.
*   **Verificação:** Após cada modificação, o LLM deve tentar verificar a mudança através de leitura de arquivo ou execução de comandos de validação (lint, type-check).
*   **Callbacks:** Cada `[LLM_ACTION: ...]` representa um passo atômico que o LLM deve tentar executar usando suas ferramentas disponíveis (ex: `read_file`, `write_file`, `run_shell_command`, `replace`).
*   **Commit:** O LLM deve solicitar ao usuário para realizar um commit após conjuntos lógicos de tarefas concluídas. O LLM pode *sugerir* a mensagem de commit, mas a execução final do commit é idealmente confirmada pelo usuário ou instruída.

---

## Fases da Migração

### Fase 0: Pré-Migração - Preparação e Avaliação

*   [X] 0.1. Verificação do Ambiente:
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='node -v', description='Verificar versão do Node.js')`
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='pnpm -v', description='Verificar versão do pnpm')`
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='ls -F frontend-solid/package.json', description='Verificar a existência do package.json do frontend-solid')`
    *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='frontend-solid/package.json', description='Ler package.json do frontend-solid para confirmar configuração.')`
        *   **[LLM_VERIFICATION]** Confirmar a presença de `solid-js` e `vite-plugin-solid` nas dependências.
*   [X] 0.2. Criação da Branch de Migração:
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Perguntar ao usuário o nome da branch de migração (sugestão: `feature/migrate-to-solidjs`).
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='git checkout -b [USER_PROVIDED_BRANCH_NAME]', description='Criar nova branch Git para a migração.')`
    *   **[LLM_VERIFICATION]** `run_shell_command(command='git branch', description='Verificar se a branch foi criada com sucesso.')`
*   [X] 0.3. Auditoria do Código React Existente (`backups/frontend-react`):
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='ls -R backups/frontend-react/src', description='Listar recursivamente todos os arquivos .tsx/.jsx na pasta src do frontend React.')`
    *   **[LLM_ACTION: ITERATE_FILES]** Para cada arquivo `.tsx` ou `.jsx` encontrado:
        *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='[PATH_TO_REACT_COMPONENT_FILE]', description='Ler o conteúdo do arquivo de componente React.')`
        *   **[LLM_ACTION: ANALYZE_CONTENT]** Internamente, analisar o conteúdo para identificar:
            *   Componentes React (ex: `function MyComponent(...)`, `const MyComponent = (...) => ...`).
            *   Hooks de estado (ex: `useState`, `useReducer`).
            *   Hooks de efeito (ex: `useEffect`).
            *   Uso de `React.createContext` ou `useContext`.
            *   Props recebidas.
            *   Bibliotecas de terceiros importadas.
            *   Padrões de renderização condicional/listas
        *   **[LLM_ACTION: WRITE_TO_INTERNAL_MEMORY]** Armazenar estas informações para cada componente em uma estrutura de dados interna para referência futura.
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='read_file(file_path=\'backups/frontend-react/package.json\')', description='Ler package.json do frontend React para identificar dependências de terceiros.')`
        *   **[LLM_ACTION: ANALYZE_DEPENDENCIES]** Internamente, extrair lista de `dependencies` e `devDependencies`.
        *   **[LLM_ACTION: WRITE_TO_INTERNAL_MEMORY]** Armazenar a lista de dependências.
*   [X] 0.4. Seleção de um Componente Piloto (PoC):
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Apresentar ao usuário a lista de componentes identificados em `0.3` e pedir para escolher um componente pequeno e isolado para ser o piloto.
    *   **[LLM_ACTION: WRITE_TO_INTERNAL_MEMORY]** Armazenar o caminho do componente piloto escolhido.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit inicial do ambiente base: `git add . && git commit -m "feat: Initial migration setup and React codebase audit"`

### Fase 1: Configuração do Ambiente para a Migração

*   **[ ] 1.1. Integração da Nova Estrutura de Código:**
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Perguntar ao usuário onde os componentes SolidJS migrados devem ser colocados:
        1.  Diretamente em `frontend-solid/src` (misturando com o código existente).
        2.  Em uma nova subpasta dedicada (ex: `frontend-solid/src/migrated-components`).
    *   **[LLM_ACTION: WRITE_TO_INTERNAL_MEMORY]** Armazenar a decisão do usuário sobre a estrutura.
    *   **[LLM_ACTION: RUN_COMMAND_IF_NEEDED]** Se a opção 2 for escolhida: `run_shell_command(command='mkdir -p frontend-solid/src/migrated-components', description='Criar subpasta dedicada para componentes migrados.')`
*   **[ ] 1.2. Configuração do Linting para SolidJS:**
    *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='frontend-solid/eslint.config.mjs', description='Ler a configuração atual do ESLint no frontend-solid.')`
    *   **[LLM_ACTION: ANALYZE_AND_SUGGEST_CHANGE]** Internamente, verificar se `eslint-plugin-solid` está configurado. Se não, gerar o `old_string` e `new_string` para adicioná-lo.
    *   **[LLM_ACTION: USER_CONFIRMATION_OR_REPLACE]** `replace(file_path='frontend-solid/eslint.config.mjs', old_string='[OLD_ESLINT_CONFIG_SNIPPET]', new_string='[NEW_ESLINT_CONFIG_SNIPPET]', instruction='Adicionar/garantir configuração do eslint-plugin-solid.')`
    *   **[LLM_VERIFICATION]** `run_shell_command(command='cd frontend-solid && pnpm lint', description='Executar o linter para verificar a nova configuração.')` (Observar saída para erros de configuração, não de código).
*   **[ ] 1.3. Configuração de Testes para SolidJS:**
    *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='frontend-solid/package.json', description='Ler package.json do frontend-solid para verificar dependências de teste.')`
    *   **[LLM_ACTION: ANALYZE_AND_SUGGEST_CHANGE]** Internamente, verificar a presença de `@solidjs/testing-library` e uma configuração de teste (Jest ou Vitest). Se faltar, gerar `old_string`/`new_string` para adicionar.
    *   **[LLM_ACTION: USER_CONFIRMATION_OR_REPLACE]** `replace(file_path='frontend-solid/package.json', old_string='[OLD_PACKAGE_JSON_SNIPPET]', new_string='[NEW_PACKAGE_JSON_SNIPPET]', instruction='Adicionar/garantir @solidjs/testing-library e configuração de teste.')`
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='cd frontend-solid && pnpm install', description='Instalar novas dependências de teste.')`
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "chore: Configure SolidJS linting and testing environment"`

### Fase 2: Migração da Infraestrutura Principal e Utilitários Compartilhados

*   **[ ] 2.1. Migração de Estilos/CSS:**
    *   **[LLM_ACTION: SEARCH_FILE_CONTENT]** `search_file_content(pattern='import .*\.css', dir_path='backups/frontend-react/src', include='*.tsx,*.jsx', description='Buscar por importações de CSS no React para identificar arquivos de estilo.')`
    *   **[LLM_ACTION: ITERATE_AND_COPY]** Para cada arquivo CSS/SCSS identificado em `backups/frontend-react/src` que não seja específico de um componente:
        *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='[PATH_TO_REACT_CSS_FILE]', description='Ler arquivo CSS/SCSS.')`
        *   **[LLM_ACTION: WRITE_FILE]** `write_file(file_path='frontend-solid/src/styles/[FILENAME]', content='[CONTENT_OF_CSS_FILE]', description='Copiar arquivo CSS/SCSS para o frontend-solid.')`
    *   **[LLM_ACTION: ANALYZE_TAILWIND_CONFIG]** Internamente, verificar `frontend-solid/tailwind.config.mjs` (ou equivalente) para garantir que os arquivos SolidJS migrados serão escaneados.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "feat: Migrate global CSS and ensure Tailwind config compatibility"`
*   **[ ] 2.2. Utilitários Comuns:**
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='ls -F backups/frontend-react/src/utils', description='Listar arquivos no diretório utils do frontend React.')`
    *   **[LLM_ACTION: ITERATE_AND_COPY]** Para cada arquivo de utilitário (ex: `.ts`, `.js`) em `backups/frontend-react/src/utils`:
        *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='[PATH_TO_REACT_UTIL_FILE]', description='Ler arquivo de utilitário React.')`
        *   **[LLM_ACTION: WRITE_FILE]** `write_file(file_path='frontend-solid/src/utils/[FILENAME]', content='[CONTENT_OF_UTIL_FILE]', description='Copiar arquivo de utilitário para o frontend-solid.')`
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "feat: Migrate common utility functions"`

### Fase 3: Migração Componente por Componente (Processo Iterativo)

**Para cada componente React a ser migrado:**

*   **[ ] 3.1. Migração do Componente Piloto (PoC):**
    *   **[LLM_ACTION: READ_FILE]** `read_file(file_path='[PATH_TO_PILOT_REACT_COMPONENT]', description='Ler o código do componente React piloto.')`
    *   **[LLM_ACTION: CONVERT_TO_SOLIDJS]** Internamente, analisar o código React e gerar o equivalente em SolidJS, aplicando as transformações de estado, efeitos, props, renderização e refs.
        *   **[LLM_ACTION: GENERATE_SOLIDJS_CODE]** (Processo interno de LLM para reescrita).
    *   **[LLM_ACTION: WRITE_FILE]** `write_file(file_path='[TARGET_SOLIDJS_PATH_FOR_PILOT]', content='[GENERATED_SOLIDJS_CODE]', description='Escrever o componente SolidJS migrado.')`
    *   **[LLM_ACTION: CREATE_TEST_STUB]** `write_file(file_path='[TARGET_SOLIDJS_TEST_PATH_FOR_PILOT]', content='[SOLIDJS_TEST_STUB]', description='Criar um stub de teste unitário para o componente SolidJS.')`
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Solicitar ao usuário que forneça os detalhes do teste unitário para o componente SolidJS piloto, pois a criação de testes robustos exige compreensão do comportamento esperado.
    *   **[LLM_ACTION: REPLACE_FILE]** `replace(file_path='[TARGET_SOLIDJS_TEST_PATH_FOR_PILOT]', old_string='[SOLIDJS_TEST_STUB]', new_string='[USER_PROVIDED_TEST_CODE]', instruction='Adicionar testes unitários para o componente SolidJS piloto.')`
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='cd frontend-solid && pnpm test -- [TARGET_SOLIDJS_TEST_PATH_FOR_PILOT]', description='Executar testes unitários do componente SolidJS piloto.')`
        *   **[LLM_VERIFICATION]** Analisar a saída para confirmar que os testes passaram. Se falharem, reportar ao usuário para depuração.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "feat: Migrate [Nome do Componente Piloto] to SolidJS and add unit tests"`

*   **[ ] 3.2. Migração Iterativa de Componentes:**
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Perguntar ao usuário qual é o próximo componente React da lista (gerada em `0.3`) a ser migrado.
    *   **[LLM_ACTION: REPEAT_STEPS]** Repetir o processo de leitura, conversão, escrita, teste e commit como em `3.1` para cada componente, adaptando a complexidade da conversão (estado, efeitos, etc.) conforme a análise inicial.
    *   **[LLM_ACTION: USER_CONFIRMATION]** O LLM deve solicitar um commit após cada componente ou grupo de componentes logicamente relacionados.

    *(Detalhes para cada tipo de componente abaixo serão incorporados nas etapas de [LLM_ACTION: CONVERT_TO_SOLIDJS] e [LLM_ACTION: GENERATE_SOLIDJS_CODE] acima)*

    *   **3.3. Migração de Componentes com Estado Local:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, foco em `useState` -> `createSignal`, `useReducer` -> `createStore`)*
    *   **3.4. Migração de Componentes com Efeitos Colaterais:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, foco em `useEffect` -> `createEffect` ou `createMemo`)*
    *   **3.5. Migração da Lógica de Contexto:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, foco em `React.createContext` -> `Solid.createContext`)*
    *   **3.6. Migração de Gerenciamento de Estado Global:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, reimplementação de Redux/Zustand com `createStore`/`createContext` ou `zustand-solid`)*
    *   **3.7. Migração de Roteamento:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, substituição de `react-router-dom`/Next.js Router por `@solidjs/router` e adaptação de links)*
    *   **3.8. Migração de Componentes Complexos e Bibliotecas de Terceiros:**
        *   *(LLM_ACTION: Durante CONVERT_TO_SOLIDJS, lidar com a complexidade, buscando alternativas ou wrappers. Pode exigir mais USER_INPUT_REQUIRED para decisões de reescrita vs wrapper)*

### Fase 4: Testes e Verificação Pós-Migração

*   **[ ] 4.1. Execução de Todos os Testes Unitários:**
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='cd frontend-solid && pnpm test', description='Executar todos os testes unitários do frontend-solid.')`
    *   **[LLM_VERIFICATION]** Analisar a saída para confirmar que todos os testes passaram. Reportar falhas ao usuário.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "test: All SolidJS unit tests passing"`
*   **[ ] 4.2. Testes de Integração:**
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Pedir ao usuário para fornecer instruções sobre como executar os testes de integração (se existirem e forem migrados/criados).
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='[USER_PROVIDED_INTEGRATION_TEST_COMMAND]', description='Executar testes de integração.')`
    *   **[LLM_VERIFICATION]** Analisar a saída.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "test: All SolidJS integration tests passing"`
*   **[ ] 4.3. Testes End-to-End (E2E):**
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Pedir ao usuário para fornecer instruções sobre como executar os testes E2E.
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='[USER_PROVIDED_E2E_TEST_COMMAND]', description='Executar testes End-to-End.')`
    *   **[LLM_VERIFICATION]** Analisar a saída.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "test: All E2E tests passing with SolidJS frontend"`
*   **[ ] 4.4. Testes Manuais e QA:**
    *   **[LLM_ACTION: REPORT_TO_USER]** Informar ao usuário que esta etapa requer testes manuais e QA por um humano para validar a funcionalidade e o UI/UX. O LLM não pode executar esta etapa.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário para notificar o LLM quando esta etapa estiver concluída e fornecer feedback para quaisquer correções.

### Fase 5: Otimização de Performance e Finalização

*   **[ ] 5.1. Análise de Performance:**
    *   **[LLM_ACTION: REPORT_TO_USER]** Informar ao usuário que a análise de performance com Solid Devtools e otimizações subsequentes são tipicamente realizadas por um humano. O LLM pode, no entanto, aplicar otimizações *sugeridas* pelo usuário.
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Perguntar ao usuário se há otimizações específicas que ele gostaria que o LLM aplicasse no código.
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit (se otimizações foram aplicadas manualmente pelo usuário): `git add . && git commit -m "perf: Initial performance optimizations"`
*   **[ ] 5.2. Limpeza do Código Antigo:**
    *   **[LLM_ACTION: RUN_COMMAND]** `run_shell_command(command='rm -rf backups/frontend-react', description='Remover o diretório backups/frontend-react.')`
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "refactor: Remove old React codebase"`
*   **[ ] 5.3. Revisão Final de Código:**
    *   **[LLM_ACTION: REPORT_TO_USER]** Informar ao usuário que uma revisão final de código deve ser feita por um humano para garantir as melhores práticas de SolidJS e a legibilidade.
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Pedir ao usuário para realizar a revisão e indicar se há alguma alteração que o LLM deva fazer.
*   **[ ] 5.4. Documentação Final:**
    *   **[LLM_ACTION: SEARCH_FILE_CONTENT]** `search_file_content(pattern='React', dir_path='.', include='README.md,GEMINI.md', description='Procurar por referências a React nos documentos principais.')`
    *   **[LLM_ACTION: ANALYZE_AND_SUGGEST_CHANGE]** Internamente, analisar as ocorrências e gerar `old_string`/`new_string` para atualizar "React" para "SolidJS" ou remover referências obsoletas.
    *   **[LLM_ACTION: USER_CONFIRMATION_OR_REPLACE]** `replace(file_path='[PATH_TO_DOC_FILE]', old_string='[OLD_DOC_SNIPPET]', new_string='[NEW_DOC_SNIPPET]', instruction='Atualizar documentação do projeto para refletir o frontend SolidJS.')`
    *   **[LLM_ACTION: USER_CONFIRMATION]** Solicitar ao usuário que faça um commit: `git add . && git commit -m "docs: Update project documentation for SolidJS frontend"`
*   **[ ] 5.5. Merge para Main/Produção:**
    *   **[LLM_ACTION: REPORT_TO_USER]** Informar ao usuário que a mesclagem para a branch principal é uma operação crítica e deve ser realizada por um humano após todas as validações.
    *   **[LLM_ACTION: USER_INPUT_REQUIRED]** Pedir ao usuário para realizar a mesclagem e notificar o LLM quando concluído.

---

Este plano serve como um guia abrangente para a execução da migração por um LLM, com pontos de interação explícitos com o usuário.