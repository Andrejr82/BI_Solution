# Plano REVISADO: Implementação 100% Completa - Todas as Páginas

## ⚠️ GAPS IDENTIFICADOS (Críticos)

### 1. 🔴 BLOQUEADOR: UUID Mismatch
**Problema**: Token Supabase usa UUID diferente do Parquet  
**Impacto**: TODOS os endpoints retornam 401  
**Solução**: Sincronizar UUIDs ANTES de qualquer outra coisa

### 2. 🔴 CRÍTICO: Endpoints Faltantes
**Faltam 6 endpoints**:
- `/api/v1/rupturas/*` - Rupturas críticas
- `/api/v1/transfers/*` - Transferências
- `/api/v1/diagnostics/*` - Diagnóstico DB
- `/api/v1/auth/change-password` - Alterar senha
- `/api/v1/learning/*` - Aprendizado IA
- `/api/v1/playground/*` - Playground queries

### 3. 🟡 IMPORTANTE: Frontend Error Handling
**Problema**: Nenhuma página trata erro 401 gracefully  
**Impacto**: Tela branca/loading infinito  
**Solução**: Adicionar error boundaries em TODAS as páginas

### 4. 🟡 IMPORTANTE: SECRET_KEY Validation
**Problema**: Não validamos se SECRET_KEY está configurada  
**Impacto**: JWT pode falhar silenciosamente  
**Solução**: Validar no startup do backend

### 5. 🟢 DESEJÁVEL: Testes E2E
**Problema**: Apenas auth.spec.ts existe  
**Impacto**: Sem garantia de funcionalidade  
**Solução**: Criar testes para cada página

---

## 🎯 PLANO REVISADO - Ordem de Execução

### FASE 0: Pré-requisitos (BLOQUEADOR) ⏱️ 15min

#### 0.1 Sincronizar UUIDs Supabase ↔ Parquet
```python
# Script: scripts/sync_supabase_uuids.py
import pandas as pd

# UUIDs do Supabase (extraídos do token JWT)
ADMIN_UUID = "4291b79d-d43d-4a09-a88a-c51d2cbffc7f"
USER_UUID = "buscar-no-supabase-dashboard"  # Ir em Auth > Users

# Atualizar Parquet
df = pd.read_parquet('data/parquet/users.parquet')
df.loc[df['username'] == 'admin', 'id'] = ADMIN_UUID
df.loc[df['username'] == 'user', 'id'] = USER_UUID
df.to_parquet('data/parquet/users.parquet', index=False)
print("✅ UUIDs sincronizados!")
```

#### 0.2 Validar SECRET_KEY
```python
# backend/app/config/settings.py
@model_validator(mode="after")
def validate_secret_key(self) -> "Settings":
    if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters")
    return self
```

#### 0.3 Testar Endpoint Protegido
```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@2024"}'

# 2. Copiar access_token

# 3. Testar metrics
curl http://127.0.0.1:8000/api/v1/metrics/summary \
  -H "Authorization: Bearer TOKEN_AQUI"

# Deve retornar 200 com dados ✅
```

---

### FASE 1: Páginas com Endpoints Existentes ⏱️ 2h

#### 1.1 Dashboard ✅ (Endpoint existe)
- [x] Endpoint: `/api/v1/metrics/summary` ✅
- [ ] Testar com token válido
- [ ] Adicionar error handling
- [ ] Validar dados exibidos

#### 1.2 Analytics ✅ (Endpoint existe)
- [x] Endpoint: `/api/v1/analytics/data` ✅
- [ ] Testar paginação
- [ ] Adicionar filtros
- [ ] Implementar gráficos

#### 1.3 Chat BI ✅ (Endpoint existe)
- [x] Endpoint: `/api/v1/chat/stream` ✅
- [ ] Testar SSE streaming
- [ ] Validar Gemini integration
- [ ] Adicionar histórico

#### 1.4 Reports ✅ (Endpoint existe)
- [x] Endpoint: `/api/v1/reports` ✅
- [ ] Testar CRUD completo
- [ ] Validar SQL Server connection
- [ ] Adicionar exportação

#### 1.5 Admin ✅ (Endpoint existe)
- [x] Endpoint: `/api/v1/admin/*` ✅
- [ ] Listar usuários
- [ ] CRUD de usuários
- [ ] Audit logs

---

### FASE 2: Criar Endpoints Faltantes ⏱️ 3h

#### 2.1 Rupturas (NOVO)
**Endpoint**: `/api/v1/rupturas/critical`

```python
# backend/app/api/v1/endpoints/rupturas.py
@router.get("/critical")
async def get_critical_rupturas(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 50
):
    """Produtos com ruptura crítica (estoque zero + vendas altas)"""
    df = data_scope_service.get_filtered_dataframe(current_user)
    
    # Filtrar: VENDA_30DD > 0 AND ESTOQUE == 0
    rupturas = df.filter(
        (pl.col("VENDA_30DD") > 0) & (pl.col("ESTOQUE") == 0)
    ).head(limit)
    
    return rupturas.to_dicts()
```

#### 2.2 Transfers (NOVO)
**Endpoint**: `/api/v1/transfers/list`

```python
# backend/app/api/v1/endpoints/transfers.py
@router.get("/list")
async def get_transfers(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 100
):
    """Transferências entre UNEs"""
    df = data_scope_service.get_filtered_dataframe(current_user)
    
    # Analisar movimentação entre meses
    transfers = df.select([
        "PRODUTO", "NOME", "UNE", 
        "MES_01", "MES_02", "ESTOQUE"
    ]).head(limit)
    
    return transfers.to_dicts()
```

#### 2.3 Diagnostics (NOVO)
**Endpoint**: `/api/v1/diagnostics/db-status`

```python
# backend/app/api/v1/endpoints/diagnostics.py
@router.get("/db-status")
async def get_db_status(
    current_user: Annotated[User, Depends(require_role("admin"))]
):
    """Status de conexões e dados"""
    from pathlib import Path
    
    # Verificar Parquet
    parquet_path = Path("data/parquet/admmat.parquet")
    parquet_ok = parquet_path.exists()
    parquet_size = parquet_path.stat().st_size if parquet_ok else 0
    
    # Verificar SQL Server
    sql_ok = settings.USE_SQL_SERVER
    
    return {
        "parquet": {
            "status": "ok" if parquet_ok else "error",
            "size_mb": round(parquet_size / 1024 / 1024, 2),
            "path": str(parquet_path)
        },
        "sql_server": {
            "status": "ok" if sql_ok else "disabled"
        },
        "supabase": {
            "status": "ok" if settings.SUPABASE_URL else "disabled"
        }
    }
```

#### 2.4 Profile - Change Password (NOVO)
**Endpoint**: `/api/v1/auth/change-password`

```python
# backend/app/api/v1/endpoints/auth.py
@router.post("/change-password")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    old_password: str,
    new_password: str
):
    """Alterar senha do usuário"""
    # Verificar senha atual
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(400, "Senha atual incorreta")
    
    # Atualizar no Parquet
    df = pl.read_parquet("data/parquet/users.parquet")
    new_hash = get_password_hash(new_password)
    
    df = df.with_columns(
        pl.when(pl.col("id") == current_user.id)
        .then(pl.lit(new_hash))
        .otherwise(pl.col("hashed_password"))
        .alias("hashed_password")
    )
    
    df.write_parquet("data/parquet/users.parquet")
    return {"message": "Senha alterada com sucesso"}
```

#### 2.5 Learning (NOVO)
**Endpoint**: `/api/v1/learning/insights`

```python
# backend/app/api/v1/endpoints/learning.py
@router.get("/insights")
async def get_insights(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Insights gerados por IA sobre os dados"""
    df = data_scope_service.get_filtered_dataframe(current_user, max_rows=1000)
    
    # Análises básicas
    top_product = df.sort("VENDA_30DD", descending=True).head(1)
    worst_product = df.filter(pl.col("VENDA_30DD") > 0).sort("VENDA_30DD").head(1)
    
    return {
        "insights": [
            {
                "type": "top_performer",
                "title": "Produto Mais Vendido",
                "description": f"{top_product['NOME'][0]} com {top_product['VENDA_30DD'][0]} vendas"
            },
            {
                "type": "low_performer",
                "title": "Produto com Baixa Performance",
                "description": f"{worst_product['NOME'][0]} precisa de atenção"
            }
        ]
    }
```

#### 2.6 Playground (NOVO)
**Endpoint**: `/api/v1/playground/query`

```python
# backend/app/api/v1/endpoints/playground.py
@router.post("/query")
async def execute_query(
    current_user: Annotated[User, Depends(require_role("admin"))],
    query: str,
    limit: int = 100
):
    """Executar query segura em Polars"""
    # IMPORTANTE: Validar query para evitar SQL injection
    # Apenas permitir SELECT simples
    
    df = data_scope_service.get_filtered_dataframe(current_user)
    
    # Executar query Polars (não SQL!)
    # Por segurança, apenas retornar head(limit)
    result = df.head(limit)
    
    return {
        "rows": result.to_dicts(),
        "count": len(result),
        "columns": result.columns
    }
```

---

### FASE 3: Frontend Error Handling ⏱️ 1h

#### Criar Error Boundary Component
```typescript
// frontend-solid/src/components/ErrorBoundary.tsx
export function ErrorBoundary(props: { children: any }) {
  const [error, setError] = createSignal<Error | null>(null);
  
  onError((err) => {
    console.error('Error caught:', err);
    setError(err as Error);
  });
  
  return (
    <Show
      when={!error()}
      fallback={
        <div class="p-8 text-center">
          <h2 class="text-2xl font-bold text-destructive">Erro</h2>
          <p class="text-muted">{error()?.message}</p>
          <button onClick={() => window.location.reload()}>
            Recarregar Página
          </button>
        </div>
      }
    >
      {props.children}
    </Show>
  );
}
```

#### Aplicar em TODAS as páginas
```typescript
// Exemplo: Dashboard.tsx
export default function Dashboard() {
  return (
    <ErrorBoundary>
      {/* conteúdo existente */}
    </ErrorBoundary>
  );
}
```

---

### FASE 4: Testes E2E ⏱️ 2h

#### Criar testes para cada página
```typescript
// tests/e2e/pages.spec.ts
test.describe('Todas as Páginas', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('Admin@2024');
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForURL(/.*dashboard/);
  });
  
  test('Dashboard carrega dados', async ({ page }) => {
    await expect(page.getByText(/Receita Total/i)).toBeVisible();
  });
  
  test('Analytics carrega', async ({ page }) => {
    await page.goto('/metrics');
    await expect(page).toHaveURL(/.*metrics/);
  });
  
  // ... mais 10 testes
});
```

---

## ✅ CHECKLIST FINAL COMPLETO

### Pré-requisitos
- [ ] UUIDs sincronizados Supabase ↔ Parquet
- [ ] SECRET_KEY validada (>= 32 chars)
- [ ] Endpoint `/metrics/summary` retorna 200
- [ ] Backend rodando sem erros
- [ ] Frontend rodando sem erros

### Backend - Endpoints
- [ ] `/api/v1/metrics/*` (3 endpoints) ✅ Existem
- [ ] `/api/v1/analytics/*` ✅ Existe
- [ ] `/api/v1/chat/*` ✅ Existe
- [ ] `/api/v1/reports/*` ✅ Existe
- [ ] `/api/v1/admin/*` ✅ Existe
- [ ] `/api/v1/rupturas/*` ❌ Criar
- [ ] `/api/v1/transfers/*` ❌ Criar
- [ ] `/api/v1/diagnostics/*` ❌ Criar
- [ ] `/api/v1/auth/change-password` ❌ Criar
- [ ] `/api/v1/learning/*` ❌ Criar
- [ ] `/api/v1/playground/*` ❌ Criar

### Frontend - Páginas
- [ ] Dashboard - dados reais
- [ ] Analytics - dados reais
- [ ] Chat - streaming funciona
- [ ] Reports - CRUD completo
- [ ] Admin - gerenciamento usuários
- [ ] Rupturas - lista críticas
- [ ] Transfers - lista transferências
- [ ] Diagnostics - status DBs
- [ ] Profile - alterar senha
- [ ] Learning - insights IA
- [ ] Playground - executar queries

### Frontend - Error Handling
- [ ] ErrorBoundary criado
- [ ] Aplicado em TODAS as 12 páginas
- [ ] Mensagens de erro amigáveis
- [ ] Botão de retry/reload

### Testes
- [ ] auth.spec.ts (9/9 passando) ✅
- [ ] pages.spec.ts (12 testes novos)
- [ ] Todos os testes passando (21/21)

### Validação Final
- [ ] Login funciona
- [ ] Todas as 12 páginas carregam
- [ ] Dados reais aparecem
- [ ] Sem erros 401
- [ ] Sem telas brancas
- [ ] Performance aceitável (<3s)

---

## 🚨 RISCOS E MITIGAÇÕES

### Risco 1: UUID sync falha
**Mitigação**: Usar username como fallback no token

### Risco 2: Parquet muito grande (98MB)
**Mitigação**: Limitar queries a 10k linhas, adicionar paginação

### Risco 3: Gemini API timeout
**Mitigação**: Timeout de 30s, fallback para mensagem de erro

### Risco 4: SQL Server indisponível
**Mitigação**: Reports usa apenas Parquet como fallback

---

## 📊 ESTIMATIVA DE TEMPO

- Fase 0 (Pré-requisitos): **15 min**
- Fase 1 (Páginas existentes): **2h**
- Fase 2 (Novos endpoints): **3h**
- Fase 3 (Error handling): **1h**
- Fase 4 (Testes): **2h**

**TOTAL: ~8h de trabalho**

---

## 🎯 CRITÉRIO DE SUCESSO

✅ **100% Completo quando**:
1. Login funciona
2. Todas as 12 páginas carregam sem erro
3. Dados reais aparecem em todas as páginas
4. 21/21 testes E2E passando
5. Nenhum erro 401 em endpoints protegidos
6. Performance < 3s para carregar qualquer página
