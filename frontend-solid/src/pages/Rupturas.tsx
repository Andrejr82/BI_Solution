import { For, onMount, onCleanup, Show, createSignal } from 'solid-js';
import { createStore } from 'solid-js/store';
import { AlertTriangle, RefreshCw, Package, TrendingDown } from 'lucide-solid';
import { analyticsApi } from '@/lib/api';

interface RupturaItem {
  product: string;
  une: string;
  estoque: number;
  vendas30d: number;
  status: 'critico' | 'baixo' | 'atencao';
}

export default function Rupturas() {
  const [state, setState] = createStore({
    data: [] as RupturaItem[],
    isLoading: true,
    error: null as string | null,
    lastUpdate: null as Date | null,
  });

  const loadData = async () => {
    setState('isLoading', true);
    setState('error', null);
    
    try {
      const response = await analyticsApi.getData(200);
      
      // Simular dados de ruptura baseado nos dados reais
      const rupturas: RupturaItem[] = response.data
        .filter(item => item.sales < 10) // Produtos com vendas baixas
        .map(item => ({
          product: item.product,
          une: item.une,
          estoque: Math.floor(Math.random() * 20), // Simular estoque baixo
          vendas30d: item.sales,
          status: item.sales < 5 ? 'critico' : item.sales < 10 ? 'baixo' : 'atencao'
        }))
        .slice(0, 50);
      
      setState('data', rupturas);
      setState('lastUpdate', new Date());
    } catch (error: any) {
      console.error('Erro ao carregar rupturas:', error);
      setState('error', error.message || 'Erro ao carregar dados');
    } finally {
      setState('isLoading', false);
    }
  };

  onMount(() => {
    loadData();
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critico': return 'text-red-400 bg-red-900/20 border-red-900';
      case 'baixo': return 'text-orange-400 bg-orange-900/20 border-orange-900';
      case 'atencao': return 'text-yellow-400 bg-yellow-900/20 border-yellow-900';
      default: return 'text-gray-400 bg-gray-900/20 border-gray-900';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'critico': return 'CRÍTICO';
      case 'baixo': return 'BAIXO';
      case 'atencao': return 'ATENÇÃO';
      default: return 'OK';
    }
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div class="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Rupturas Críticas</h2>
          <p class="text-muted">
            Produtos com estoque baixo ou em falta
            {state.lastUpdate && <span class="ml-2 text-xs opacity-70">Atualizado: {state.lastUpdate.toLocaleTimeString()}</span>}
          </p>
        </div>
        <button onClick={loadData} class="btn btn-outline gap-2" disabled={state.isLoading}>
          <RefreshCw size={16} class={state.isLoading ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {/* Stats Cards */}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Produtos em Ruptura</span>
            <AlertTriangle size={16} class="text-red-500" />
          </div>
          <div class="text-2xl font-bold text-red-400">
            {state.data.filter(i => i.status === 'critico').length}
          </div>
          <p class="text-xs text-muted mt-1">Status Crítico</p>
        </div>

        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Estoque Baixo</span>
            <Package size={16} class="text-orange-500" />
          </div>
          <div class="text-2xl font-bold text-orange-400">
            {state.data.filter(i => i.status === 'baixo').length}
          </div>
          <p class="text-xs text-muted mt-1">Requer Atenção</p>
        </div>

        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Total de Alertas</span>
            <TrendingDown size={16} class="text-yellow-500" />
          </div>
          <div class="text-2xl font-bold">
            {state.data.length}
          </div>
          <p class="text-xs text-muted mt-1">Produtos Monitorados</p>
        </div>
      </div>

      <Show when={!state.isLoading} fallback={
        <div class="flex-1 flex items-center justify-center text-muted animate-pulse">
          <RefreshCw size={32} class="animate-spin mb-2" />
          <span class="ml-2">Carregando dados...</span>
        </div>
      }>
        {/* Grid de Rupturas */}
        <div class="border rounded-lg overflow-hidden flex-1 flex flex-col bg-card">
          <div class="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-4 p-4 bg-muted/50 text-xs font-medium text-muted uppercase tracking-wider border-b">
            <div>Produto</div>
            <div>UNE / Loja</div>
            <div>Estoque</div>
            <div>Vendas 30D</div>
            <div>Status</div>
          </div>
          
          <div class="flex-1 overflow-y-auto">
            <For each={state.data}>
              {(item) => (
                <div class="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-4 p-4 border-b items-center hover:bg-muted/30 transition-colors text-sm">
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
                    <span class={item.estoque < 5 ? 'text-red-400 font-bold' : item.estoque < 10 ? 'text-orange-400' : ''}>
                      {item.estoque}
                    </span>
                  </div>
                  
                  <div class="font-mono">
                    {item.vendas30d}
                  </div>
                  
                  <div>
                    <span class={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${getStatusColor(item.status)}`}>
                      {getStatusLabel(item.status)}
                    </span>
                  </div>
                </div>
              )}
            </For>
            
            {state.data.length === 0 && (
              <div class="p-8 text-center text-muted">
                <AlertTriangle size={48} class="mx-auto mb-4 opacity-50" />
                <p>Nenhuma ruptura detectada no momento.</p>
              </div>
            )}
          </div>
        </div>
      </Show>

      <Show when={state.error}>
        <div class="p-4 bg-red-900/20 border border-red-900 rounded text-red-400">
          Erro: {state.error}
        </div>
      </Show>
    </div>
  );
}
