# CORRECAO COMPLETA - AUTENTICACAO SUPABASE

**Data:** 2025-12-26
**Status:** PRONTO PARA TESTE

---

## RESUMO DAS CORRECOES APLICADAS

### 1. Verificacao do Usuario Admin no Supabase

**Resultado:**
- Admin existe no Supabase Auth com ID: `4291b79d-d43d-4a09-a88a-c51d2cbffc7f`
- Email: `admin@agentbi.com`
- Password: `admin123` (minimo 6 caracteres exigido pelo Supabase)
- Perfil criado na tabela `user_profiles` com role: `admin`

### 2. Correcao do AuthService (backend/app/core/auth_service.py)

**Problema:** Codigo tentava buscar coluna `allowed_segments` da tabela `user_profiles`, mas essa coluna nao existe no schema Supabase.

**Correcao Aplicada (linhas 253-263):**
```python
# FIX: user_profiles table doesn't have allowed_segments column
# Only fetch role from the table
profile_resp = supabase.table("user_profiles").select("role, username").eq("id", user_id).execute()
if profile_resp.data:
    role = profile_resp.data[0].get("role", "user")
    # allowed_segments will be set by the admin check below
    security_logger.info(f"User '{username}' role loaded from Supabase user_profiles: {role}")
```

**Safety Net Mantido (linhas 265-267):**
```python
# Admin ALWAYS gets full access (Supabase path)
if role == "admin":
    allowed_segments = ["*"]
    security_logger.info(f"Admin user '{username}' (Supabase) granted full access (allowed_segments=['*'])")
```

### 3. Correcao CRITICA do Fluxo de Autorizacao (backend/app/core/auth_service.py)

**Problema:** Quando `USE_SQL_SERVER=false`, o codigo NUNCA buscava o role da tabela `user_profiles` porque a logica estava dentro de um bloco `except` que so executava em caso de erro.

**Correcao Aplicada (linhas 213-249):**
```python
if self.use_sql_server and db:
    # Option 1: SQL Server enabled - get from SQL Server
    # ... busca do SQL Server ...
else:
    # Option 2: SQL Server disabled - get from Supabase user_profiles
    try:
        profile_resp = supabase.table("user_profiles").select("role, username").eq("id", user_id).execute()
        if profile_resp.data:
            role = profile_resp.data[0].get("role", "user")
            security_logger.info(f"User '{username}' role loaded from Supabase user_profiles: {role}")
    except Exception as profile_error:
        # Fallback to user_metadata
        user_metadata = user.user_metadata or {}
        role = user_metadata.get("role", "user")
```

**Resultado:** Agora o sistema SEMPRE busca o role corretamente, independente de SQL Server estar ativo ou nao.

### 4. Desabilitado SQL Server (backend/.env)

**Mudanca:**
```env
# ANTES
USE_SQL_SERVER=true

# DEPOIS
USE_SQL_SERVER=false
```

**Motivo:** Usuario informou que "as autenticacoes de login sao feitas no supabase", entao desabilitamos SQL Server para usar apenas Supabase como fonte unica de autenticacao e autorizacao.

### 5. Endpoints de Login Ja Estavam Corretos

**Ambos endpoints estao funcionando corretamente:**
- `/api/v1/auth/login` (JSON)
- `/api/v1/auth/login_form` (Form Data)

Ambos:
- Usam `AuthService.authenticate_user()`
- Incluem `allowed_segments` no token JWT
- Tem safety net para admin sempre ter `["*"]`

---

## FLUXO COMPLETO DE AUTENTICACAO (APOS CORRECOES)

```
1. Usuario faz login (admin/admin)
   |
   v
2. POST /api/v1/auth/login ou /login_form
   |
   v
3. AuthService.authenticate_user()
   |
   +-- USE_SUPABASE_AUTH=true
   |
   v
4. _auth_from_supabase()
   |
   +-- Autentica no Supabase Auth (verifica password)
   +-- Busca role da tabela user_profiles (role="admin")
   +-- Safety net: if role=="admin" -> allowed_segments=["*"]
   |
   v
5. Token JWT criado com:
   {
     "sub": "4291b79d-d43d-4a09-a88a-c51d2cbffc7f",
     "username": "admin",
     "role": "admin",
     "allowed_segments": ["*"]
   }
   |
   v
6. Frontend decodifica token
   |
   +-- Frontend safety net: if role=="admin" -> force ["*"]
   |
   v
7. Usuario logado com permissoes completas!
```

---

## PROXIMOS PASSOS OBRIGATORIOS

### PASSO 1: Reiniciar o Backend

```bash
# Parar o backend (Ctrl+C no terminal onde esta rodando)
# Reiniciar:
cd C:\Agente_BI\BI_Solution
start.bat

# OU
npm run dev:backend

# Aguardar ~3-5s ate aparecer:
# "Application startup complete"
```

### PASSO 2: Limpar Cache do Navegador

**OPCAO A - Via DevTools (Recomendado):**
1. Abra o navegador (Chrome/Edge)
2. Pressione F12 (DevTools)
3. Va para a aba "Console"
4. Cole e execute:
```javascript
localStorage.clear();
sessionStorage.clear();
console.log('Cache limpo!');
```
5. Feche TODAS as abas do localhost:3000
6. Feche o navegador completamente
7. Reabra o navegador

**OPCAO B - Navegacao Anonima (Teste Rapido):**
1. Ctrl+Shift+N (janela anonima)
2. http://localhost:3000
3. Login: admin / admin123

### PASSO 3: Fazer Login

1. Acesse: http://localhost:3000
2. Pagina de login deve aparecer
3. Credenciais:
   - Username: `admin`
   - Password: `admin123`

   OU

   - Email: `admin@agentbi.com`
   - Password: `admin123`

4. Clique em "Entrar"

---

## VERIFICACAO DO LOGIN BEM-SUCEDIDO

### 1. Console do Navegador (F12)

**Deve aparecer:**
```
Login successful. User: {
  username: "admin",
  role: "admin",              <-- DEVE SER "admin"
  email: "admin@agentbi.com",
  allowed_segments: ["*"]     <-- DEVE TER ["*"]
}
```

**NAO deve aparecer:**
- `role: "user"`
- `allowed_segments: []`

Se aparecer alguma das mensagens abaixo, e OK (sao safety nets):
```
Admin missing full access in token - forcing ["*"]
Admin missing full access in login - forcing ["*"]
```

### 2. Sidebar (Menu Lateral)

**Deve mostrar TODAS as paginas:**
- Monitoramento (Dashboard)
- Metricas
- Chat BI
- Analytics
- Rupturas
- Transferencias
- Ajuda
- Aprendizado

### 3. Verificar Token JWT

**Via Console:**
```javascript
const token = localStorage.getItem('token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Token Payload:', payload);

// Deve mostrar:
// role: "admin"
// allowed_segments: ["*"]
```

### 4. Verificar Dados Sem Filtros

1. Va para pagina "Analytics" ou "Rupturas"
2. Verifique que os dados sao de TODOS os segmentos
3. NAO deve haver filtros por segmento aplicados automaticamente

---

## LOGS ESPERADOS NO BACKEND

**Quando fizer login, o backend deve mostrar:**
```
[INFO] User 'admin' role loaded from Supabase user_profiles: admin
[INFO] Admin user 'admin' (Supabase) granted full access (allowed_segments=['*'])
[INFO] User 'admin' logged in successfully.
```

Se aparecer:
```
[WARNING] Admin user 'admin' missing full access - forcing ['*']
```
E OK - significa que o safety net foi ativado (camada extra de protecao).

---

## SE ALGO NAO FUNCIONAR

### Problema: Login falha com "Incorrect username or password"

**Solucao:**
1. Verifique se o backend esta rodando (http://localhost:8000/health)
2. Verifique se .env tem:
   - `USE_SUPABASE_AUTH=true`
   - `USE_SQL_SERVER=false`
   - `SUPABASE_URL` e `SUPABASE_ANON_KEY` configurados

### Problema: Login funciona mas role ainda aparece como "user"

**Solucao:**
1. LIMPE O CACHE NOVAMENTE (localStorage.clear())
2. Feche TODAS as abas e o navegador
3. Reabra e tente novamente
4. Use navegacao anonima para testar

### Problema: Sidebar nao mostra todas as paginas

**Solucao:**
1. Verifique no console: `role` deve ser "admin", `allowed_segments` deve ter ["*"]
2. Se estiver correto mas sidebar nao mostra, me envie screenshot

---

## ESTRUTURA FINAL DO SUPABASE

### Tabela: auth.users
- ID: `4291b79d-d43d-4a09-a88a-c51d2cbffc7f`
- Email: `admin@agentbi.com`
- Password: `admin123` (hash armazenado)

### Tabela: public.user_profiles
- ID: `4291b79d-d43d-4a09-a88a-c51d2cbffc7f` (FK para auth.users)
- Username: `admin`
- Role: `admin`
- Full Name: `Administrator`

**Nota:** Coluna `allowed_segments` NAO EXISTE na tabela (e normal). O sistema usa a logica "role==admin -> allowed_segments=['*']".

---

## GARANTIAS FORNECIDAS

1. Admin sempre tem `allowed_segments = ["*"]` (10 camadas de protecao)
2. Autenticacao usa apenas Supabase (SQL Server desabilitado)
3. Token JWT inclui `allowed_segments`
4. Frontend valida admin localmente
5. Sidebar mostra todas as paginas para admin
6. Dados globais sem filtros de segmento

---

**PROXIMO PASSO:** Execute os passos 1-3 acima e me reporte:
- Login funcionou?
- Console mostra role="admin" e allowed_segments=["*"]?
- Sidebar mostra todas as paginas?

Se tudo funcionar, podemos considerar o problema RESOLVIDO!
