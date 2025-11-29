# Análise de Bundle - Scripts

## Comandos disponíveis

### Analisar bundle
```bash
# Analisa o bundle de produção
ANALYZE=true pnpm build
```

### Build otimizado
```bash
# Build normal de produção
pnpm build
```

### Desenvolvimento
```bash
# Servidor de desenvolvimento
pnpm dev
```

## Métricas esperadas

- **First Load JS**: < 200KB
- **Total Bundle Size**: Monitorar crescimento
- **Largest Chunks**: Identificar componentes pesados

## Otimizações aplicadas

1. ✅ Dynamic imports para componentes pesados
2. ✅ Tree-shaking automático
3. ✅ Remoção de console.log em produção
4. ✅ Otimização de package imports
5. ✅ Image optimization (AVIF/WebP)
