/* src/index.tsx - Versão ULTRA SIMPLIFICADA sem verificação de versão */
import { render } from 'solid-js/web';
import { Router, Route, Navigate } from '@solidjs/router';
import { Show } from 'solid-js';
import { QueryClient, QueryClientProvider } from '@tanstack/solid-query';
import './index.css';

// Importar Layout e Páginas
import Layout from './Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import Learning from './pages/Learning';
import Playground from './pages/Playground';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import Rupturas from './pages/Rupturas';
import Transfers from './pages/Transfers';
import Diagnostics from './pages/Diagnostics';
import Examples from './pages/Examples';
import Help from './pages/Help';
import SharedConversation from './pages/SharedConversation';
import CodeChat from './pages/CodeChat';

// Importar Store de Autenticação
import auth from './store/auth';

console.log('✅ All imports loaded successfully');

// Componente de Proteção de Rotas
function PrivateRoute(props: { component: any }) {
  return (
    <Show
      when={auth.isAuthenticated()}
      fallback={<Navigate href="/login" />}
    >
      {props.component}
    </Show>
  );
}

// Componente de Proteção de Rotas com RBAC
function RoleRoute(props: { component: any; requiredRole: string }) {
  return (
    <Show
      when={auth.isAuthenticated()}
      fallback={<Navigate href="/login" />}
    >
      <Show
        when={auth.user()?.role === props.requiredRole}
        fallback={
          <div class="flex items-center justify-center min-h-screen flex-col gap-4 p-8">
            <h1 class="text-4xl font-bold text-destructive">Acesso Negado</h1>
            <p class="text-lg text-muted-foreground">Você não tem permissão para acessar esta página.</p>
            <p class="text-sm text-muted-foreground">403 - Forbidden</p>
          </div>
        }
      >
        {props.component}
      </Show>
    </Show>
  );
}

// Componente Principal da Aplicação
function App() {
  console.log('✅ App component created');
  return (
    <Router>
      {/* Rotas Públicas */}
      <Route path="/login" component={Login} />
      <Route path="/shared/:share_id" component={SharedConversation} />

      {/* Rota raiz - redireciona baseado em autenticação */}
      <Route path="/" component={() => {
        return (
          <Show
            when={auth.isAuthenticated()}
            fallback={<Navigate href="/login" />}
          >
            <Navigate href="/dashboard" />
          </Show>
        );
      }} />

      {/* Rotas Protegidas - Dentro do Layout */}
      <Route path="/" component={Layout}>
        <Route path="/dashboard" component={() => <PrivateRoute component={<Dashboard />} />} />
        <Route path="/metrics" component={() => <RoleRoute component={<Analytics />} requiredRole="admin" />} />
        <Route path="/rupturas" component={() => <PrivateRoute component={<Rupturas />} />} />
        <Route path="/transfers" component={() => <PrivateRoute component={<Transfers />} />} />
        <Route path="/reports" component={() => <RoleRoute component={<Reports />} requiredRole="admin" />} />
        <Route path="/chat" component={() => <PrivateRoute component={<Chat />} />} />
        <Route path="/examples" component={() => <RoleRoute component={<Examples />} requiredRole="admin" />} />
        <Route path="/learning" component={() => <RoleRoute component={<Learning />} requiredRole="admin" />} />
        <Route path="/playground" component={() => <RoleRoute component={<Playground />} requiredRole="admin" />} />
        <Route path="/code-chat" component={() => <RoleRoute component={<CodeChat />} requiredRole="admin" />} />
        <Route path="/diagnostics" component={() => <RoleRoute component={<Diagnostics />} requiredRole="admin" />} />
        <Route path="/help" component={() => <PrivateRoute component={<Help />} />} />
        <Route path="/profile" component={() => <PrivateRoute component={<Profile />} />} />
        <Route path="/admin" component={() => <RoleRoute component={<Admin />} requiredRole="admin" />} />
      </Route>

      {/* Fallback */}
      <Route path="*" component={() => (
        <Show
          when={auth.isAuthenticated()}
          fallback={<Navigate href="/login" />}
        >
          <Navigate href="/dashboard" />
        </Show>
      )} />
    </Router>
  );
}

// Renderizar a Aplicação no DOM
const root = document.getElementById('root');

if (!root) {
  console.error('❌ ROOT ELEMENT NOT FOUND!');
  throw new Error('Root element not found');
}

console.log('✅ Root element found:', root);

// Create QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

console.log('✅ QueryClient created');

// Render app
try {
  render(() => (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  ), root);
  console.log('✅ App rendered successfully!');
} catch (error) {
  console.error('❌ Error rendering app:', error);
  document.body.innerHTML = `
    <div style="padding: 20px; color: white; background: #1a1a1a; font-family: sans-serif;">
      <h1 style="color: #ef4444;">❌ Erro ao Renderizar Aplicação</h1>
      <pre style="background: #2a2a2a; padding: 10px; border-radius: 5px; overflow: auto;">${error}</pre>
      <p>Verifique o console do navegador (F12) para mais detalhes.</p>
    </div>
  `;
}