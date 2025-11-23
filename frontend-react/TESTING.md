# Guia de Testes

## Executando Testes

### Testes Unitários

```bash
# Executar todos os testes
pnpm test

# Modo watch (desenvolvimento)
pnpm test:watch

# Com coverage
pnpm test:coverage

# CI mode
pnpm test:ci
```

## Estrutura de Testes

```
src/
├── __tests__/
│   ├── components/     # Testes de componentes React
│   ├── hooks/          # Testes de hooks customizados
│   └── lib/            # Testes de utilitários
```

## Escrevendo Testes

### Componentes

```typescript
import { render, screen } from '@testing-library/react';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Hooks

```typescript
import { renderHook } from '@testing-library/react';
import { useMyHook } from '@/hooks/useMyHook';

describe('useMyHook', () => {
  it('returns expected value', () => {
    const { result } = renderHook(() => useMyHook());
    expect(result.current).toBe(true);
  });
});
```

## Coverage

Meta de coverage: **70%** (branches, functions, lines, statements)

Visualizar coverage:
```bash
pnpm test:coverage
# Abrir coverage/lcov-report/index.html
```

## CI/CD

Os testes rodam automaticamente no GitHub Actions em:
- Push para `main` ou `develop`
- Pull requests

Pipeline inclui:
1. Lint
2. Type check
3. Unit tests com coverage
4. Build

## Boas Práticas

1. **Arrange-Act-Assert**: Organize testes em 3 seções
2. **Descrições claras**: Use `describe` e `it` descritivos
3. **Isolamento**: Cada teste deve ser independente
4. **Mocks**: Use mocks para dependências externas
5. **Coverage**: Foque em código crítico primeiro
