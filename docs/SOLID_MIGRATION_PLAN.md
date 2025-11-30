# 🚀 Plano de Migração Robusta: React → SolidJS

**Objetivo:** Substituir o frontend atual (Next.js) por uma aplicação **SolidJS** de alta performance, mantendo a identidade visual (Shadcn/Dark) e integrando totalmente com o Backend FastAPI existente.

**Foco:** Segurança (JWT), Estabilidade (Tipagem Forte/Error Handling) e Qualidade (Arquitetura Limpa).

---

## 🏗️ Arquitetura Proposta

*   **Framework:** SolidJS (Vite)
*   **Linguagem:** TypeScript (Strict Mode)
*   **Roteamento:** `@solidjs/router` (Lazy Loading de rotas)
*   **Estado Global:** Solid `createStore` (Nativo, sem Redux/Zustand)
*   **API Client:** Axios com Interceptors (Gerenciamento automático de Token)
*   **Estilização:** CSS Variables + Modules (Leveza extrema, herdado do protótipo)
*   **Build:** Vite (ESNext target)

---

## 📅 Cronograma de Execução

### Fase 1: Fundação e Configuração 🛡️
- [ ] Criar estrutura do projeto `frontend-solid` (Limpa e Padronizada).
- [ ] Configurar TypeScript (`tsconfig.json`) com *Path Aliases* (`@/`).
- [ ] Configurar Vite para Proxy Reverso (Evitar CORS em dev).
- [ ] Instalar dependências essenciais (`@solidjs/router`, `axios`, `lucide-solid`).

### Fase 2: Núcleo de Segurança e Dados 🔐
- [ ] Implementar `auth.store.ts`: Gerenciamento de Sessão, Login, Logout.
- [ ] Implementar `api.ts`: Cliente HTTP Singleton com injeção de Bearer Token.
- [ ] Criar Guardas de Rota (`ProtectedRoute`): Impedir acesso não autorizado.

### Fase 3: Implementação de Interfaces (UI) 🎨
- [ ] **Layout Principal:** Sidebar, Header, Área de Conteúdo.
- [ ] **Login:** Tela de autenticação real conectada ao endpoint `/api/v1/auth/login`.
- [ ] **Chat AI:** Interface de Chat com Streaming real (SSE) via `/api/v1/chat/stream`.
- [ ] **Dashboard:** Grid de Alta Performance (adaptado do protótipo).

### Fase 4: Integração e Testes 🧪
- [ ] Validar fluxo de Login/Logout com backend.
- [ ] Testar persistência de sessão (F5 na página).
- [ ] Testar Streaming do Chat.
- [ ] Gerar Build de Produção.

### Fase 5: Cutover (Virada de Chave) 🚀
- [ ] Criar script de inicialização atualizado.
- [ ] Gerar Relatório Final de Testes.

---

## 📝 Critérios de Aceite (DoD)

1.  **Zero Config:** O projeto deve rodar com um comando.
2.  **Segurança:** Token JWT nunca deve ser exposto na URL, apenas Headers.
3.  **Performance:** Pontuação Lighthouse > 95.
4.  **Funcionalidade:** Chat deve responder com dados do backend real.
