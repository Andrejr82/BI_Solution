Aqui está um plano de migração para o projeto Agent Solution BI. Ele se concentra na criação de um novo frontend com SolidJS, usando Tailwind CSS para estilização e Vitest para testes. O objetivo é manter a compatibilidade total com o backend existente e garantir uma transição suave para uma experiência de usuário mais moderna e eficiente.

**Plano de Migração para Frontend SolidJS**

**Fase 1: Preparação e Configuração Inicial (Dias 1-3)**

1.  **Análise e Documentação do Frontend Existente (React/Next.js):**
    *   Revisar a estrutura atual do frontend (React/Next.js).
    *   Identificar componentes reutilizáveis, lógica de estado, chamadas de API (Axios), e rotas.
    *   Documentar as funcionalidades existentes e o fluxo de dados.
    *   **Ferramentas:** `codebase_investigator` (para análise de código), `read_file`, `list_directory`.

2.  **Configuração do Ambiente de Desenvolvimento:**
    *   Criar um novo diretório `frontend-solid` na raiz do projeto.
    *   Inicializar um novo projeto SolidJS dentro de `frontend-solid` usando o `vite` (ex: `pnpm create vite frontend-solid --template solid-ts`).
    *   Configurar o TypeScript, ESLint e Prettier para o novo projeto, espelhando as configurações do frontend React/Next.js existente onde apropriado.
    *   Instalar dependências básicas: `solid-js`, `solid-app-router`, `tailwindcss`, `postcss`, `autoprefixer`, `vitest`, `jsdom`.
    *   **Ferramentas:** `run_shell_command` (para `pnpm create vite`, `pnpm install`), `write_file` (para configurações).

3.  **Configuração do Tailwind CSS:**
    *   Gerar os arquivos `tailwind.config.js` e `postcss.config.js`.
    *   Configurar o `tailwind.config.js` para escanear os arquivos SolidJS (`.html`, `.tsx`).
    *   Importar as diretivas do Tailwind no CSS principal do projeto SolidJS.
    *   **Ferramentas:** `run_shell_command` (para `npx tailwindcss init -p`), `write_file` (para modificação dos arquivos de configuração e CSS).

**Fase 2: Migração de Componentes e Estilização (Dias 4-10)**

1.  **Migração dos Componentes Comuns/Reutilizáveis:**
    *   Começar pelos componentes menores e mais independentes (botões, inputs, modais).
    *   Reescrever a lógica do React/Next.js para SolidJS, aproveitando a reatividade granular do Solid.
    *   Aplicar estilização com Tailwind CSS, mantendo a fidelidade visual com o design existente.
    *   **Ferramentas:** `read_file` (para componentes React), `write_file` (para novos componentes SolidJS), `run_shell_command` (para testes unitários).

2.  **Migração das Telas/Páginas Principais:**
    *   Migrar gradualmente as páginas principais da aplicação.
    *   Estabelecer as rotas usando `solid-app-router`.
    *   Integrar os componentes migrados nas novas páginas.
    *   **Ferramentas:** `read_file`, `write_file`, `run_shell_command`.

3.  **Integração com a API Existente:**
    *   Garantir que as chamadas de API (Axios) no frontend SolidJS funcionem perfeitamente com o backend FastAPI.
    *   Adaptar os serviços de API existentes ou criar novos, mantendo os mesmos contratos de requisição/resposta.
    *   **Ferramentas:** `read_file` (para serviços de API existentes), `write_file` (para novos serviços).

**Fase 3: Testes e Otimização (Dias 11-14)**

1.  **Implementação de Testes Unitários e de Componentes:**
    *   Escrever testes unitários para a lógica dos componentes SolidJS usando Vitest e `@testing-library/solid`.
    *   Garantir uma cobertura de teste adequada.
    *   **Ferramentas:** `write_file` (para arquivos de teste), `run_shell_command` (para `vitest run`).

2.  **Testes de Integração:**
    *   Realizar testes de integração para garantir que o frontend SolidJS se comunica corretamente com o backend e que os fluxos de usuário funcionam como esperado.
    *   **Ferramentas:** `run_shell_command` (para testes de ponta a ponta, se houver).

3.  **Otimização de Performance e Acessibilidade:**
    *   Avaliar o desempenho do novo frontend SolidJS.
    *   Garantir que as práticas de acessibilidade estão sendo seguidas.
    *   **Ferramentas:** `run_shell_command` (para Lighthouse, outras ferramentas de auditoria).

**Fase 4: Implantação e Monitoramento (Dia 15)**

1.  **Construção e Implantação:**
    *   Configurar o processo de build para o frontend SolidJS.
    *   Implantar o novo frontend.
    *   **Ferramentas:** `run_shell_command` (para `pnpm build`).

2.  **Monitoramento e Feedback:**
    *   Monitorar o desempenho e erros após a implantação.
    *   Coletar feedback dos usuários para ajustes finais.
    *   **Ferramentas:** Ferramentas de monitoramento de produção.

**Observações:**

*   Manter o backend inalterado durante a migração do frontend.
*   Utilizar controle de versão (Git) para gerenciar as mudanças e permitir reversões.
*   Comunicar-se regularmente com a equipe sobre o progresso e quaisquer desafios.
*   Esta é uma estimativa de cronograma; pode ser ajustado conforme necessário.