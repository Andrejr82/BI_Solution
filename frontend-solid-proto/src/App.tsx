import { createSignal, onCleanup, batch, For, Show, Switch, Match } from 'solid-js';
import { createStore, produce } from 'solid-js/store';

// --- Ícones SVG (Lucide style) ---
const Icons = {
  Logo: () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>,
  Dashboard: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>,
  Chat: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  Analytics: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>,
  Reports: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>,
  Admin: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>,
  Bell: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>,
  Send: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  Download: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  File: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>,
  Play: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>,
  Pause: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
};

// --- Simulação de Dados ---
const generateData = (count = 1000) => {
  return Array.from({ length: count }).map((_, i) => ({
    id: i,
    product: `PROD-${1000 + i} - Componente Industrial CX-${Math.floor(Math.random() * 99)}`,
    category: ['Eletrônicos', 'Mecânica', 'Automação', 'Serviços'][Math.floor(Math.random() * 4)],
    price: (Math.random() * 5000 + 100).toFixed(2),
    volume: Math.floor(Math.random() * 500),
    trend: Math.random() > 0.5 ? 'up' : 'down',
    status: Math.random() > 0.2 ? 'Active' : 'Low Stock'
  }));
};

// --- Components das Telas ---

const DashboardView = (props: { state: any, toggleSimulation: () => void }) => (
  <div style="max-width: 1400px; margin: 0 auto;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem;">
      <div>
        <h2>Monitoramento em Tempo Real</h2>
        <p>Acompanhamento de métricas de produtos e vendas (Alta Frequência).</p>
      </div>
      <button class="btn btn-outline" onClick={props.toggleSimulation} style="gap: 8px;">
        {props.state.isRunning ? <Icons.Pause /> : <Icons.Play />}
        {props.state.isRunning ? 'Pausar Stream' : 'Retomar Stream'}
      </button>
    </div>

    {/* Stats Cards */}
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <p style="font-size: 0.8rem; font-weight: 500;">Total de Ativos</p>
        <h3 style="font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{props.state.data.length.toLocaleString()}</h3>
        <p style="font-size: 0.75rem; color: #4ade80; margin-top: 4px;">+2.5% este mês</p>
      </div>
      <div class="card">
        <p style="font-size: 0.8rem; font-weight: 500;">Atualizações/seg</p>
        <h3 style="font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{(props.state.updateCount / (performance.now() / 1000)).toFixed(0)}</h3>
        <p style="font-size: 0.75rem; color: #38bdf8; margin-top: 4px;">WebSocket Stream Ativo</p>
      </div>
      <div class="card">
        <p style="font-size: 0.8rem; font-weight: 500;">Volume Total</p>
        <h3 style="font-size: 1.8rem; font-weight: 700; margin-top: 4px;">R$ {(props.state.data.reduce((acc: number, row: any) => acc + parseFloat(row.price), 0) / 1000).toFixed(1)}k</h3>
        <p style="font-size: 0.75rem; color: var(--muted-foreground); margin-top: 4px;">Calculado em tempo real</p>
      </div>
       <div class="card">
        <p style="font-size: 0.8rem; font-weight: 500;">Performance UI</p>
        <h3 style="font-size: 1.8rem; font-weight: 700; margin-top: 4px; color: #a78bfa;">~0.2ms</h3>
        <p style="font-size: 0.75rem; margin-top: 4px;">Sem Virtual DOM</p>
      </div>
    </div>

    {/* High Perf Grid */}
    <div class="grid-container">
      <div class="grid-header-row">
        <div>Produto / SKU</div>
        <div>Categoria</div>
        <div>Preço Atual</div>
        <div>Volume (24h)</div>
        <div>Status</div>
      </div>
      
      <div style="background: var(--card); height: 500px; overflow-y: auto;">
        <For each={props.state.data}>
          {(item: any) => (
            <div class="grid-row">
              <div>
                <div style="font-weight: 500; color: var(--foreground)">{item.product}</div>
                <div style="font-size: 0.75rem; color: var(--muted-foreground)">ID: {item.id.toString().padStart(6, '0')}</div>
              </div>
              
              <div>
                <span style="background: var(--secondary); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                  {item.category}
                </span>
              </div>
              
              <div style="font-family: monospace; font-size: 0.95rem; font-weight: 600; color: #fbbf24">
                 R$ {item.price}
              </div>
              
              <div style="display: flex; align-items: center; gap: 6px;">
                <span>{item.volume}</span>
                <span style={{ 
                   color: item.trend === 'up' ? '#4ade80' : '#f87171',
                   "font-size": '0.7rem'
                }}>
                  {item.trend === 'up' ? '▲' : '▼'}
                </span>
              </div>
              
              <div>
                <span class={`badge ${item.status === 'Active' ? 'badge-success' : 'badge-danger'}`}>
                  {item.status}
                </span>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  </div>
);

const ChatView = () => {
  const [messages, setMessages] = createSignal([
    { role: 'ai', text: 'Olá! Sou o Agente BI. Como posso ajudar com os dados hoje?' }
  ]);
  const [input, setInput] = createSignal('');

  const sendMessage = (e: Event) => {
    e.preventDefault();
    if (!input()) return;
    
    const userMsg = input();
    setMessages(p => [...p, { role: 'user', text: userMsg }]);
    setInput('');
    
    // Simula resposta rápida
    setTimeout(() => {
      setMessages(p => [...p, { role: 'ai', text: `Processando análise para: "${userMsg}"...\n\nEncontrei 3 correlações importantes na base de dados.` }]);
    }, 600);
  };

  return (
    <div style="height: calc(100vh - 100px); display: flex; flex-direction: column; max-width: 900px; margin: 0 auto;">
      <div style="flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px;">
        <For each={messages()}>
          {(msg) => (
            <div style={{ 
              "align-self": msg.role === 'user' ? 'flex-end' : 'flex-start',
              "background": msg.role === 'user' ? '#38bdf8' : '#1e293b',
              "color": msg.role === 'user' ? '#0f172a' : '#f8fafc',
              "padding": '12px 20px',
              "border-radius": '12px',
              "max-width": '80%',
              "font-weight": msg.role === 'user' ? '500' : '400',
              "line-height": '1.5'
            }}>
              {msg.text}
            </div>
          )}
        </For>
      </div>
      
      <div style="padding: 20px; background: var(--background); border-top: 1px solid var(--border);">
        <form onSubmit={sendMessage} style="display: flex; gap: 10px;">
          <input 
            type="text" 
            value={input()}
            onInput={(e) => setInput(e.currentTarget.value)}
            placeholder="Faça uma pergunta sobre seus dados..."
            style="flex: 1; background: var(--card); border: 1px solid var(--border); padding: 12px; border-radius: 8px; color: white; outline: none;"
          />
          <button type="submit" class="btn btn-primary" style="width: 50px;">
            <Icons.Send />
          </button>
        </form>
      </div>
    </div>
  );
};

const AnalyticsView = (props: { state: any }) => (
  <div style="max-width: 1400px; margin: 0 auto;">
    <h2>Analytics Avançado</h2>
    <p style="margin-bottom: 30px;">Análise de tendências e distribuição de categorias.</p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <div class="card">
        <h3 style="margin-bottom: 20px; font-size: 1rem;">Volume por Categoria (Tempo Real)</h3>
        <div style="height: 300px; display: flex; align-items: flex-end; gap: 20px; padding-bottom: 20px;">
          <For each={['Eletrônicos', 'Mecânica', 'Automação', 'Serviços']}>
            {(cat) => {
              const count = () => props.state.data.filter((i: any) => i.category === cat).length;
              return (
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 10px;">
                   <div style={{ 
                     width: '100%',
                     background: '#38bdf8',
                     height: `${Math.min(count(), 200)}px`,
                     "border-radius": '4px 4px 0 0',
                     transition: 'height 0.3s ease'
                   }}></div>
                   <span style="font-size: 0.8rem;">{cat}</span>
                   <span style="font-weight: bold;">{count()}</span>
                </div>
              )
            }}
          </For>
        </div>
      </div>
      
      <div class="card">
        <h3 style="margin-bottom: 20px; font-size: 1rem;">Logs de Atividade</h3>
        <div style="font-family: monospace; font-size: 0.8rem; color: var(--muted-foreground);">
          <p>&gt; [System] Initializing Analysis Engine...</p>
          <p>&gt; [Stream] Connected to WebSocket (wss://api.agentbi.com/v1/stream)</p>
          <p style="color: #4ade80">&gt; [OK] Received {props.state.data.length} records in 12ms</p>
          <For each={Array.from({length: 8})}>
            {(_, i) => (
              <p style="opacity: 0.7">&gt; [Update] Syncing batch #{props.state.updateCount - i} - {Math.floor(Math.random() * 50)} items updated</p>
            )}
          </For>
          <p className="flash" style="color: #38bdf8">&gt; [Live] Listening for incoming data changes...</p>
        </div>
      </div>
    </div>
  </div>
);

const ReportsView = () => (
  <div style="max-width: 1000px; margin: 0 auto;">
    <h2>Relatórios Gerados</h2>
    <p style="margin-bottom: 30px;">Arquivos disponíveis para download.</p>
    
    <div class="card" style="padding: 0;">
      <div class="grid-header-row" style="grid-template-columns: 3fr 1fr 1fr 1fr;">
        <div>Nome do Arquivo</div>
        <div>Data</div>
        <div>Tamanho</div>
        <div>Ação</div>
      </div>
      <For each={[ 
        { name: 'Relatorio_Vendas_Q3.pdf', date: '28/11/2025', size: '2.4 MB' },
        { name: 'Analise_Estoque_Mensal.xlsx', date: '27/11/2025', size: '1.1 MB' },
        { name: 'Performance_Vendedores.pdf', date: '25/11/2025', size: '850 KB' },
        { name: 'Log_Erros_Sistema.txt', date: '24/11/2025', size: '45 KB' },
      ]}> 
        {(file) => (
          <div class="grid-row" style="grid-template-columns: 3fr 1fr 1fr 1fr;">
             <div style="display: flex; align-items: center; gap: 10px;">
               <Icons.File />
               {file.name}
             </div>
             <div>{file.date}</div>
             <div>{file.size}</div>
             <div>
               <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.8rem; gap: 6px;">
                 <Icons.Download /> Baixar
               </button>
             </div>
          </div>
        )}
      </For>
    </div>
  </div>
);

function App() {
  const [state, setState] = createStore({
    data: generateData(1000),
    isRunning: true,
    updateCount: 0,
    lastRenderTime: 0,
    activeTab: 'Dashboard' as 'Dashboard' | 'Chat AI' | 'Analytics' | 'Relatórios' | 'Admin'
  });
  
  let intervalId: number;

  const toggleSimulation = () => {
    if (state.isRunning) {
      clearInterval(intervalId);
      setState('isRunning', false);
    } else {
      startSimulation();
      setState('isRunning', true);
    }
  };

  const startSimulation = () => {
    intervalId = setInterval(() => {
      const start = performance.now();
      batch(() => {
        setState(produce((s) => {
          s.updateCount++;
          for (let i = 0; i < 100; i++) {
            const randomIndex = Math.floor(Math.random() * s.data.length);
            const row = s.data[randomIndex];
            row.price = (parseFloat(row.price) * (1 + (Math.random() * 0.04 - 0.02))).toFixed(2);
            row.volume = Math.floor(Math.random() * 500);
            row.trend = Math.random() > 0.5 ? 'up' : 'down';
            if (Math.random() > 0.9) row.status = Math.random() > 0.5 ? 'Active' : 'Low Stock';
          }
        }));
      });
      const end = performance.now();
      setState('lastRenderTime', (end - start).toFixed(2));
    }, 50);
  };

  startSimulation();
  onCleanup(() => clearInterval(intervalId));

  const NavItem = (props: { name: string; icon: any }) => (
    <div 
      class={`nav-item ${state.activeTab === props.name ? 'active' : ''}`}
      onClick={() => setState('activeTab', props.name as any)}
    >
      <props.icon />
      <span>{props.name}</span>
    </div>
  );

  return (
    <div class="app-layout">
      {/* Sidebar */}
      <div class="sidebar">
        <div class="logo-area">
          <Icons.Logo />
          <span>Agent BI</span>
        </div>
        
        <nav>
          <NavItem name="Dashboard" icon={Icons.Dashboard} />
          <NavItem name="Chat AI" icon={Icons.Chat} />
          <NavItem name="Analytics" icon={Icons.Analytics} />
          <NavItem name="Relatórios" icon={Icons.Reports} />
          <div style="flex: 1"></div>
          <NavItem name="Admin" icon={Icons.Admin} />
        </nav>
      </div>

      {/* Main Content */}
      <div class="main-content">
        {/* Header */}
        <header class="header">
          <div style="display: flex; align-items: center; gap: 12px;">
             <span style="color: var(--muted-foreground)">Organização</span>
             <span style="color: var(--border)">/</span>
             <span style="font-weight: 500">{state.activeTab}</span>
          </div>
          
          <div style="display: flex; align-items: center; gap: 16px;">
             <Show when={state.activeTab === 'Dashboard' || state.activeTab === 'Analytics'}>
               <div style="display: flex; align-items: center; gap: 8px; font-size: 0.75rem; background: var(--muted); padding: 4px 12px; border-radius: 20px; border: 1px solid var(--border)">
                  <span style="color: #38bdf8">●</span>
                  Render: {state.lastRenderTime}ms
               </div>
             </Show>
             <button class="btn btn-outline" style="padding: 6px;">
                <Icons.Bell />
             </button>
             <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #38bdf8, #818cf8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 0.8rem;">
                AD
             </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <main class="content-scroll">
          <Switch>
            <Match when={state.activeTab === 'Dashboard'}>
              <DashboardView state={state} toggleSimulation={toggleSimulation} />
            </Match>
            <Match when={state.activeTab === 'Chat AI'}>
              <ChatView />
            </Match>
            <Match when={state.activeTab === 'Analytics'}>
              <AnalyticsView state={state} />
            </Match>
            <Match when={state.activeTab === 'Relatórios'}>
              <ReportsView />
            </Match>
            <Match when={state.activeTab === 'Admin'}>
              <div style="max-width: 800px; margin: 0 auto; text-align: center; margin-top: 100px; color: var(--muted-foreground)">
                <Icons.Admin />
                <h3>Área Administrativa</h3>
                <p>Configurações de usuários e permissões.</p>
              </div>
            </Match>
          </Switch>
        </main>
      </div>
    </div>
  );
}

export default App;
