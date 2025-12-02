# Workflow de Testes com TestSprite

## 🔄 Fluxo de Trabalho Completo

Este documento descreve o workflow completo para usar TestSprite no projeto Agent Solution BI.

## 📅 Rotina de Testes

### Diariamente (Smoke Tests)

Execute testes críticos para garantir que funcionalidades essenciais estão funcionando:

```bash
# Testes de autenticação e dashboard
npx playwright test auth.spec.ts dashboard.spec.ts --project=chromium
```

**Tempo estimado**: 2-3 minutos

### Semanalmente (Regression Suite)

Execute a suite completa de testes de regressão:

```bash
# Suite completa em todos os navegadores
npm run test:e2e
```

**Tempo estimado**: 15-20 minutos

### Mensalmente (Performance Benchmarking)

Execute testes de performance e valide métricas:

```bash
# Testes com métricas de performance
npx playwright test --reporter=html,json
```

Revise o relatório e compare com benchmarks anteriores.

### Por Release (Suite Completa)

Antes de cada release, execute:

1. Suite completa de testes
2. Testes em todos os navegadores
3. Testes mobile
4. Validação de performance

```bash
npm run test:e2e
```

## 🎯 Workflow de Desenvolvimento

### 1. Antes de Começar a Trabalhar

```bash
# Pull das últimas alterações
git pull origin main

# Atualizar dependências
cd frontend-solid && pnpm install
cd ../backend && pip install -r requirements.txt

# Executar smoke tests
cd ..
npx playwright test auth.spec.ts --project=chromium
```

### 2. Durante o Desenvolvimento

#### Para Novas Features

1. **Desenvolva a feature**
2. **Execute testes relacionados em modo watch**:
```bash
npx playwright test --headed --debug
```

3. **Ajuste conforme necessário**

#### Para Bug Fixes

1. **Identifique o teste que falha**
2. **Execute em modo debug**:
```bash
npx playwright test nome-do-teste.spec.ts --debug
```

3. **Corrija o bug**
4. **Verifique se o teste passa**

### 3. Antes de Fazer Commit

```bash
# Execute testes afetados
npm run test:e2e

# Verifique o relatório
npm run test:e2e:report

# Se tudo passou, faça commit
git add .
git commit -m "feat: sua mensagem"
```

### 4. Antes de Abrir PR

```bash
# Execute suite completa
npm run test:e2e

# Verifique cobertura
# Revise screenshots/vídeos de falhas

# Abra PR apenas se todos os testes passarem
```

## 🤖 Usando TestSprite via MCP

### Geração Automática de Testes

1. **Abra seu IDE** (Cursor, Windsurf, etc.)

2. **Ative o TestSprite MCP Server**
   - O servidor deve estar configurado em `mcp_config.json`

3. **Solicite geração de testes**:
   ```
   "Gere testes end-to-end para a funcionalidade de Chat BI"
   ```

4. **TestSprite irá**:
   - Analisar o PRD (`TESTSPRITE_PRD.md`)
   - Analisar o código fonte
   - Gerar casos de teste
   - Criar scripts Playwright
   - Executar testes em cloud
   - Fornecer relatório

### Análise de Bugs

1. **Quando um teste falhar**:
   ```
   "Analise a falha no teste dashboard.spec.ts"
   ```

2. **TestSprite irá**:
   - Analisar screenshots e traces
   - Identificar causa raiz
   - Sugerir correção
   - Opcionalmente aplicar fix automaticamente

### Atualização de Testes

Quando você modificar código:

```
"Atualize os testes para refletir as mudanças no componente Button"
```

TestSprite irá:
- Detectar mudanças no código
- Atualizar testes relevantes
- Re-executar testes
- Validar que tudo ainda funciona

## 📊 Análise de Resultados

### Relatório HTML

Após cada execução, revise:

1. **Taxa de Sucesso**: Meta > 95%
2. **Tempo de Execução**: Monitorar tendências
3. **Falhas**: Investigar imediatamente
4. **Screenshots**: Validar visualmente

### Métricas de Performance

Monitore no relatório JSON:

```json
{
  "initialLoad": 2500,  // Meta: < 3000ms
  "navigation": 450,    // Meta: < 500ms
  "apiResponse": 800    // Meta: < 1000ms
}
```

### Tendências

Mantenha histórico de execuções:

```bash
# Salvar resultado com timestamp
cp test-results/results.json test-results/results-$(date +%Y%m%d).json
```

## 🔧 Manutenção de Testes

### Quando Atualizar Testes

- ✅ Nova feature adicionada
- ✅ Bug fix que requer novo caso de teste
- ✅ Mudança na UI que quebra seletores
- ✅ Mudança na API que altera contratos
- ✅ Novos requisitos de negócio

### Como Atualizar

1. **Identifique testes afetados**
2. **Atualize manualmente** ou **use TestSprite**:
   ```
   "Atualize testes para a nova API de relatórios"
   ```
3. **Execute testes atualizados**
4. **Valide resultados**
5. **Commit alterações**

### Limpeza de Testes Obsoletos

Mensalmente, revise e remova:
- Testes duplicados
- Testes para features removidas
- Testes que sempre passam (podem ser redundantes)

## 🚨 Tratamento de Falhas

### Falha em Teste Único

1. **Execute em modo debug**:
```bash
npx playwright test nome-teste.spec.ts --debug
```

2. **Analise o trace**:
```bash
npx playwright show-trace test-results/trace.zip
```

3. **Corrija o problema**
4. **Re-execute**

### Falhas Múltiplas

1. **Verifique se backend/frontend estão rodando**
2. **Verifique logs do servidor**
3. **Execute smoke tests primeiro**
4. **Investigue falhas por categoria**

### Falhas Intermitentes (Flaky Tests)

1. **Identifique padrão**:
```bash
# Execute 10 vezes
for i in {1..10}; do npm run test:e2e; done
```

2. **Aumente timeouts se necessário**
3. **Adicione waits explícitos**
4. **Considere usar `test.retry()`**

## 📈 Métricas e KPIs

### Acompanhe

- **Taxa de Sucesso**: > 95%
- **Tempo de Execução**: < 20 minutos (suite completa)
- **Cobertura de Código**: > 80%
- **Bugs Encontrados**: Tendência decrescente
- **Tempo para Fix**: < 24 horas

### Dashboard de Métricas (Futuro)

Considere criar dashboard com:
- Histórico de execuções
- Tendências de performance
- Bugs por categoria
- Cobertura por módulo

## 🔗 Integração CI/CD

### GitHub Actions (Planejado)

O workflow `.github/workflows/testsprite.yml` irá:

1. **Trigger**: Em cada PR e push para main
2. **Setup**: Instalar dependências
3. **Start Services**: Backend e Frontend
4. **Run Tests**: Suite completa
5. **Report**: Comentar resultados no PR
6. **Block Merge**: Se testes falharem

### Comandos CI

```yaml
- name: Run E2E Tests
  run: npm run test:e2e
  
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## 📚 Recursos e Documentação

- [TESTSPRITE_SETUP.md](./TESTSPRITE_SETUP.md) - Guia de instalação
- [TESTSPRITE_PRD.md](./TESTSPRITE_PRD.md) - Especificação de testes
- [Playwright Docs](https://playwright.dev)
- [TestSprite Docs](https://docs.testsprite.com)

## ✅ Checklist de Boas Práticas

- [ ] Execute smoke tests diariamente
- [ ] Execute suite completa semanalmente
- [ ] Revise relatórios após cada execução
- [ ] Investigue falhas imediatamente
- [ ] Mantenha testes atualizados
- [ ] Documente novos casos de teste
- [ ] Monitore métricas de performance
- [ ] Limpe testes obsoletos mensalmente
- [ ] Use TestSprite para geração automática
- [ ] Mantenha histórico de resultados
