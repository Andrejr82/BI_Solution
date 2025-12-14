import { A, useLocation } from '@solidjs/router';
import auth from '@/store/auth';
import {
  LayoutDashboard, MessageSquare, PieChart, FileText, Settings, LogOut,
  AlertTriangle, Truck, BookOpen, Terminal, Database, Lock, Shield, Lightbulb, HelpCircle
} from 'lucide-solid';
import { For, Show, children } from 'solid-js';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Logo } from '@/components';

export default function Layout(props: any) {
  const location = useLocation();
  const userRole = () => auth.user()?.role || 'user'; // fallback para 'user' garante visibilidade

  // Definição dos Itens de Menu com Permissões
  const menuItems = [
    {
      group: 'Dashboards',
      items: [
        { href: '/dashboard', icon: LayoutDashboard, label: 'Monitoramento', roles: ['admin', 'user'] },
        { href: '/metrics', icon: PieChart, label: 'Métricas', roles: ['admin'] },
        { href: '/rupturas', icon: AlertTriangle, label: 'Rupturas Críticas', roles: ['admin'] },
      ]
    },
    {
      group: 'Operacional',
      items: [
        { href: '/transfers', icon: Truck, label: 'Transferências', roles: ['admin'] },
        { href: '/reports', icon: FileText, label: 'Relatórios', roles: ['admin'] },
      ]
    },
    {
      group: 'Inteligência',
      items: [
        { href: '/chat', icon: MessageSquare, label: 'Chat BI', roles: ['admin', 'user'] },
        { href: '/examples', icon: Lightbulb, label: 'Exemplos', roles: ['admin', 'user'] },
        { href: '/learning', icon: BookOpen, label: 'Aprendizado', roles: ['admin', 'user'] },
        { href: '/playground', icon: Terminal, label: 'Playground', roles: ['admin', 'user'] },
      ]
    },
    {
      group: 'Sistema',
      items: [
        { href: '/diagnostics', icon: Database, label: 'Diagnóstico DB', roles: ['admin'] },
        { href: '/help', icon: HelpCircle, label: 'Ajuda', roles: ['admin', 'user'] },
        { href: '/profile', icon: Lock, label: 'Alterar Senha', roles: ['admin', 'user'] },
        { href: '/admin', icon: Shield, label: 'Administração', roles: ['admin', 'user'] }, // Compradores veem versão limitada
      ]
    }
  ];

  const NavItem = (props: { href: string; icon: any; label: string }) => (
    <A 
      href={props.href} 
      class={`nav-item ${location.pathname.includes(props.href) ? 'active' : ''}`}
    >
      <props.icon size={18} />
      <span>{props.label}</span>
    </A>
  );

  return (
    <div class="app-layout">
      <aside class="sidebar">
        <div class="p-6 flex flex-col gap-3">
          <div class="flex items-center gap-3">
            <Logo size="md" />
            <span class="text-xs font-normal text-muted px-2 py-1 rounded bg-secondary border border-border capitalize">
              {String(userRole())}
            </span>
          </div>
          <div class="flex flex-col gap-0.5">
            <h2 class="text-base font-bold text-primary">CAÇULINHA BI</h2>
            <span class="text-xs text-muted-foreground">Inteligência de Negócios</span>
          </div>
        </div>
        
        <nav class="flex-1 overflow-y-auto py-2">
          <For each={menuItems}>
            {(group) => {
              // Filtrar itens baseados na role
              const visibleItems = group.items.filter(item => item.roles.includes(userRole()) || item.roles.includes('*'));
              
              return (
                <Show when={visibleItems.length > 0}>
                  <div class="mb-6">
                    <div class="px-6 mb-2 text-xs font-semibold text-muted uppercase tracking-wider opacity-70">
                      {group.group}
                    </div>
                    <For each={visibleItems}>
                      {(item) => (
                        <NavItem href={item.href} icon={item.icon} label={item.label} />
                      )}
                    </For>
                  </div>
                </Show>
              );
            }}
          </For>
        </nav>

        <div class="p-4 border-t border-border">
          <button onClick={auth.logout} class="nav-item w-full justify-start text-destructive hover:bg-destructive/10 hover:text-destructive m-0">
            <LogOut size={18} />
            <span>Sair</span>
          </button>
        </div>
      </aside>

      <div class="flex flex-col h-screen overflow-hidden">
        <header class="header justify-between">
          <div class="text-sm text-muted">
            Organização <span class="text-border mx-2">/</span> <span class="text-foreground font-medium capitalize">{location.pathname.replace('/', '') || 'Dashboard'}</span>
          </div>
          
          <div class="flex items-center gap-4">
             <div class="text-right hidden md:block">
                <div class="text-sm font-medium">{auth.user()?.username || 'Usuário'}</div>
                <div class="text-xs text-muted">{auth.user()?.email}</div>
             </div>
             <div class="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center font-bold text-white text-xs uppercase shadow-sm">
                {(auth.user()?.username || 'U').slice(0, 2).toUpperCase()}
             </div>
          </div>
        </header>
        <main class="flex-1 overflow-y-auto relative bg-background">
          <ErrorBoundary>
            {props.children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}