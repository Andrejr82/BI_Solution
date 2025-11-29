import { For, onMount, onCleanup, Show } from 'solid-js';
import dashboard from '@/store/dashboard';
import { Play, Pause, Activity, DollarSign, Zap, Users, RefreshCw } from 'lucide-solid';

export default function Dashboard() {
  const { state, togglePolling, startPolling, stopPolling } = dashboard;

  onMount(() => {
    startPolling();
  });

  onCleanup(() => {
    stopPolling();
  });

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      
      {/* Header Area */}
      <div class="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Monitoramento em Tempo Real</h2>
          <p class="text-muted">
            Dados reais do Parquet • Atualização a cada 5s
            {state.lastUpdate && <span class="ml-2 text-xs opacity-70">Last: {state.lastUpdate.toLocaleTimeString()}</span>}
          </p>
        </div>
        <div class="flex gap-2">
          <button onClick={togglePolling} class={`btn btn-outline gap-2 ${state.isLive ? 'text-green-400 border-green-400/30' : ''}`}>
            {state.isLive ? <Activity size={16} class="animate-pulse" /> : <Pause size={16} />}
            {state.isLive ? 'Live Sync' : 'Pausado'}
          </button>
        </div>
      </div>

      <Show when={!state.isLoading} fallback={
        <div class="flex-1 flex items-center justify-center text-muted animate-pulse">
          <RefreshCw size={32} class="animate-spin mb-2" />
          <span class="ml-2">Carregando dados do servidor...</span>
        </div>
      }>
        
        {/* KPI Cards (Dados Reais) */}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Receita Total</span>
              <DollarSign size={16} class="text-green-500" />
            </div>
            <div class="text-2xl font-bold">
              R$ {(state.summary?.revenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <p class="text-xs text-muted mt-1">Mês Atual (MES_01)</p>
          </div>

          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Vendas (30 Dias)</span>
              <Zap size={16} class="text-primary" />
            </div>
            <div class="text-2xl font-bold text-primary">
              {(state.summary?.totalSales || 0).toLocaleString()}
            </div>
            <p class="text-xs text-muted mt-1">
              {state.summary?.salesGrowth.toFixed(1)}% vs mês anterior
            </p>
          </div>

          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Produtos Ativos</span>
              <Activity size={16} class="text-muted" />
            </div>
            <div class="text-2xl font-bold">{(state.summary?.productsCount || 0).toLocaleString()}</div>
            <p class="text-xs text-muted mt-1">Catálogo Total</p>
          </div>

          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Lojas / UNEs</span>
              <Users size={16} class="text-amber-500" />
            </div>
            <div class="text-2xl font-bold">{(state.summary?.totalUsers || 0)}</div>
            <p class="text-xs text-muted mt-1">Pontos de Venda Ativos</p>
          </div>
        </div>

        {/* High Performance Grid (Dados Reais) */}
        <div class="border rounded-lg overflow-hidden flex-1 flex flex-col bg-card">
          <div class="grid grid-cols-[2fr_1fr_1fr_1fr] gap-4 p-4 bg-muted/50 text-xs font-medium text-muted uppercase tracking-wider border-b">
            <div>Produto</div>
            <div>UNE / Loja</div>
            <div>Vendas (30D)</div>
            <div>Receita (Mês)</div>
          </div>
          
          <div class="flex-1 overflow-y-auto">
            <For each={state.data}>
              {(item) => (
                <div class="grid grid-cols-[2fr_1fr_1fr_1fr] gap-4 p-4 border-b items-center hover:bg-muted/30 transition-colors text-sm">
                  <div>
                    <div class="font-medium text-foreground truncate" title={item.product}>
                      {item.product}
                    </div>
                  </div>
                  
                  <div>
                    <span class="inline-flex items-center rounded border px-2 py-0.5 text-xs font-mono bg-secondary text-secondary-foreground">
                      {item.une}
                    </span>
                  </div>
                  
                  <div class="font-mono">
                     {item.sales.toLocaleString()}
                  </div>
                  
                  <div class="font-mono font-medium text-amber-400">
                     R$ {item.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                </div>
              )}
            </For>
            
            {state.data.length === 0 && (
              <div class="p-8 text-center text-muted">Nenhum dado disponível. Verifique se o arquivo admmat.parquet está carregado.</div>
            )}
          </div>
        </div>
      </Show>
    </div>
  );
}