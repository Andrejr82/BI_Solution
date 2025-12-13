# Guia de Gerenciamento de Usuários - Agent Solution BI

## 🎉 Sistema Implementado com Sucesso!

O sistema de gerenciamento de usuários foi implementado com integração completa ao Supabase Auth.

## 🚀 Como Usar

### 1. Criar o Primeiro Usuário Admin no Supabase

Antes de acessar o sistema, você precisa criar o usuário admin inicial no Supabase.

#### Opção A: Via SQL Editor do Supabase (Recomendado)

1. Acesse [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. Vá em **SQL Editor**
4. Execute o script `scripts/create_supabase_users.sql` (cria usuários no auth.users)
5. Execute o script `scripts/insert_user_profiles.sql` (cria perfis na tabela user_profiles)

#### Opção B: Via Interface do Supabase

1. Acesse o Supabase Dashboard
2. Vá em **Authentication** → **Users**
3. Clique em **Add user** → **Create new user**
4. Crie com:
   - Email: `admin@agentbi.com`
   - Password: `Admin@2024`
   - Auto Confirm User: ✅ (marcar)

5. Depois, no **SQL Editor**, execute:
```sql
INSERT INTO public.user_profiles (id, username, role, full_name)
SELECT id, 'admin', 'admin', 'Administrator'
FROM auth.users WHERE email = 'admin@agentbi.com';
```

### 2. Fazer Login no Sistema

1. Acesse a aplicação: `http://localhost:3000`
2. Faça login com:
   - Email: `admin@agentbi.com`
   - Senha: `Admin@2024`

### 3. Acessar o Painel de Administração

1. Após o login, clique no menu **Admin** no sidebar
2. Você verá duas abas:
   - **Sincronização**: Para sincronizar dados do SQL Server
   - **Usuários**: Para gerenciar usuários

### 4. Gerenciar Usuários

Na aba **Usuários**, você pode:

#### ✅ Criar Novo Usuário
1. Clique em **"Novo Usuário"**
2. Preencha:
   - **Username**: Nome de usuário único
   - **Email**: Email válido (será usado para login)
   - **Senha**: Mínimo 8 caracteres
   - **Role**: Escolha entre:
     - `viewer`: Apenas visualização
     - `user`: Usuário comum
     - `admin`: Administrador completo

3. Clique em **"Criar"**
4. ✨ **O usuário é criado automaticamente no Supabase Auth + user_profiles**

#### ✏️ Editar Usuário
1. Clique no ícone de **lápis** ao lado do usuário
2. Modifique os campos desejados
3. Para alterar senha, preencha o campo (deixe vazio para não alterar)
4. Clique em **"Salvar"**

#### 🔄 Ativar/Desativar Usuário
1. Clique no badge de status (**Ativo**/**Inativo**)
2. O usuário será ativado ou desativado automaticamente no Supabase

#### 🗑️ Excluir Usuário
1. Clique no ícone de **lixeira**
2. Confirme a exclusão
3. ⚠️ **Importante**: Você não pode excluir sua própria conta

## 🔧 Detalhes Técnicos

### Backend

**Arquivo**: `backend/app/core/supabase_user_service.py`

Serviço que gerencia usuários no Supabase com as seguintes funcionalidades:
- `create_user()`: Cria usuário no auth.users + user_profiles
- `list_users()`: Lista todos os usuários
- `get_user()`: Obtém um usuário específico
- `update_user()`: Atualiza dados do usuário
- `delete_user()`: Remove usuário (auth + profile)

**Endpoints**: `backend/app/api/v1/endpoints/admin.py`

- `GET /api/v1/admin/users` - Listar usuários
- `POST /api/v1/admin/users` - Criar usuário
- `PUT /api/v1/admin/users/{user_id}` - Atualizar usuário
- `DELETE /api/v1/admin/users/{user_id}` - Excluir usuário

### Frontend

**Arquivo**: `frontend-solid/src/pages/Admin.tsx`

Interface completa com:
- Tabela de usuários com dados em tempo real
- Modal para criar/editar usuários
- Botões para ativar/desativar
- Confirmação antes de excluir
- Mensagens de sucesso/erro

**API**: `frontend-solid/src/lib/api.ts`

Métodos adicionados:
```typescript
adminApi.getUsers()
adminApi.createUser(userData)
adminApi.updateUser(userId, userData)
adminApi.deleteUser(userId)
```

## 🔐 Segurança

- ✅ Todos os endpoints requerem role `admin`
- ✅ Usuários não podem deletar a própria conta
- ✅ Senhas são gerenciadas pelo Supabase Auth (bcrypt)
- ✅ Emails são validados automaticamente
- ✅ Tokens JWT para autenticação

## 📋 Estrutura de Dados

### Tabela: `user_profiles`

```sql
CREATE TABLE public.user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  username TEXT UNIQUE,
  role TEXT DEFAULT 'user',
  full_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Roles Disponíveis

- **admin**: Acesso total, pode gerenciar usuários
- **user**: Acesso normal ao sistema
- **viewer**: Apenas visualização (pode ser expandido futuramente)

## 🐛 Resolução de Problemas

### Erro: "User database not found"
- Certifique-se de ter criado a tabela `user_profiles` no Supabase
- Execute o script `scripts/create_user_profiles.sql`

### Erro: "Forbidden" ao criar usuário
- Verifique se você está logado como admin
- Verifique se o token está válido (faça logout e login novamente)

### Erro: "Invalid login credentials"
- Verifique se o usuário foi criado corretamente no Supabase Auth
- Confirme que o perfil existe na tabela `user_profiles`
- Execute o script `scripts/insert_user_profiles.sql`

### Usuários não aparecem na listagem
- Verifique se `USE_SUPABASE_AUTH=true` no `.env` do backend
- Confirme que a API do Supabase está acessível
- Verifique os logs do backend para erros

## 🎯 Próximos Passos (Opcional)

- [ ] Adicionar filtros na tabela de usuários
- [ ] Implementar paginação para muitos usuários
- [ ] Adicionar campo `allowed_segments` na interface
- [ ] Criar logs de auditoria para ações admin
- [ ] Implementar recuperação de senha via email

## 📞 Suporte

Se encontrar problemas, verifique:
1. Console do navegador (F12) para erros frontend
2. Logs do backend para erros de API
3. Logs do Supabase Dashboard para erros de autenticação

---

**✨ Sistema 100% funcional e integrado ao Supabase!**
