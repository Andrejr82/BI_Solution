import { A, useLocation } from '@solidjs/router';
import auth from '@/store/auth';
import { 
  LayoutDashboard, MessageSquare, PieChart, FileText, Settings, LogOut, 
  AlertTriangle, Truck, BookOpen, Terminal, Database, Lock, Shield
} from 'lucide-solid';
import { For, Show, children } from 'solid-js';

export default function Layout(props: any) {
  const location = useLocation();
  const userRole = () => auth.user()?.role || 'viewer'; // 'admin' | 'user'

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
        { href: '/learning', icon: BookOpen, label: 'Aprendizado', roles: ['admin', 'user'] },
        { href: '/playground', icon: Terminal, label: 'Playground', roles: ['admin', 'user'] },
      ]
    },
    {
      group: 'Sistema',
      items: [
        { href: '/diagnostics', icon: Database, label: 'Diagnóstico DB', roles: ['admin'] },
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
        <div class="p-6 text-xl font-bold text-primary flex items-center gap-2">
          <span>Agent BI</span>
          <span class="text-xs font-normal text-muted px-2 py-1 rounded bg-secondary border border-border capitalize">
            {String(userRole())}
          </span>
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
          <button onClick={auth.logout} class="nav-item w-full justify-start text-red-400 hover:bg-red-900/10 hover:text-red-400 m-0">
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
             <div class="w-8 h-8 bg-gradient-to-br from-primary to-indigo-500 rounded-full flex items-center justify-center font-bold text-white text-xs uppercase">
                {(auth.user()?.username || 'U').slice(0, 2).toUpperCase()}
             </div>
          </div>
        </header>
        <main class="flex-1 overflow-hidden relative bg-background">
          {props.children}
        </main>
      </div>
    </div>
  );
}