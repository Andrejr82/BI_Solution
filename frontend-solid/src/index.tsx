/* src/index.tsx - Ponto de Entrada da Aplicação SolidJS */
import { render } from 'solid-js/web';
import { Router, Route, Navigate } from '@solidjs/router';
import { Show } from 'solid-js';
import { QueryClient, QueryClientProvider } from '@tanstack/solid-query'; // Added import
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

// Importar Store de Autenticação
import auth from './store/auth';

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

// Componente Principal da Aplicação
function App() {
  return (
    <Router>
      {/* Rota Pública - Login */}
      <Route path="/login" component={Login} />
      
      {/* Rotas Protegidas - Dentro do Layout */}
      <Route path="/" component={Layout}>
        {/* Redirect raiz para dashboard */}
        <Route path="/" component={() => <Navigate href="/dashboard" />} />
        
        {/* Dashboards */}
        <Route path="/dashboard" component={() => <PrivateRoute component={<Dashboard />} />} />
        <Route path="/metrics" component={() => <PrivateRoute component={<Analytics />} />} />
        <Route path="/rupturas" component={() => <PrivateRoute component={<Rupturas />} />} />
        
        {/* Operacional */}
        <Route path="/transfers" component={() => <PrivateRoute component={<Transfers />} />} />
        <Route path="/reports" component={() => <PrivateRoute component={<Reports />} />} />
        
        {/* Inteligência */}
        <Route path="/chat" component={() => <PrivateRoute component={<Chat />} />} />
        <Route path="/learning" component={() => <PrivateRoute component={<Learning />} />} />
        <Route path="/playground" component={() => <PrivateRoute component={<Playground />} />} />
        
        {/* Sistema */}
        <Route path="/diagnostics" component={() => <PrivateRoute component={<Diagnostics />} />} />
        <Route path="/profile" component={() => <PrivateRoute component={<Profile />} />} />
        <Route path="/admin" component={() => <PrivateRoute component={<Admin />} />} />
      </Route>
      
      {/* Fallback - Redirecionar para dashboard */}
      <Route path="*" component={() => <Navigate href="/dashboard" />} />
    </Router>
  );
}

// Renderizar a Aplicação no DOM
const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element not found. Make sure there is a <div id="root"></div> in your index.html');
}

// Create a client
const queryClient = new QueryClient(); // New QueryClient instance

render(() => ( // Wrap App with QueryClientProvider
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
), root);