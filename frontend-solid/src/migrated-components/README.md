# Componentes Migrados do React para SolidJS

Esta pasta contém todos os componentes migrados do frontend React original para SolidJS.

## Estrutura

```
migrated-components/
├── components/     # Componentes reutilizáveis
├── pages/          # Páginas da aplicação
├── services/       # Serviços e integrações com API
└── utils/          # Utilitários e helpers
```

## Status da Migração

- [ ] Componentes básicos
- [ ] Páginas principais
- [ ] Serviços de API
- [ ] Utilitários compartilhados

## Convenções

- Todos os componentes devem usar SolidJS signals (`createSignal`, `createStore`)
- Efeitos devem usar `createEffect` ou `createMemo`
- Testes devem usar `@solidjs/testing-library`
