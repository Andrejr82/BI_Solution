import { For, onMount, createSignal, Show } from 'solid-js';
import { createStore } from 'solid-js/store';
import { Truck, RefreshCw, ArrowRight, CheckCircle, Clock, XCircle } from 'lucide-solid';

interface Transfer {
  id: string;
  produto: string;
  origem: string;
  destino: string;
  quantidade: number;
  status: 'pendente' | 'em_transito' | 'concluida' | 'cancelada';
  data: string;
}

export default function Transfers() {
  const [state, setState] = createStore({
    data: [] as Transfer[],
    isLoading: true,
    lastUpdate: null as Date | null,
  });

  const loadData = async () => {
    setState('isLoading', true);
    
    // Simular dados de transferências
    // TODO: Integrar com endpoint real quando disponível
    setTimeout(() => {
      const mockData: Transfer[] = [
        {
          id: 'TRF-001',
          produto: 'Notebook Dell Inspiron 15',
          origem: 'CD CENTRAL',
          destino: 'LOJA MATRIZ',
          quantidade: 5,
          status: 'concluida',
          data: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 'TRF-002',
          produto: 'Mouse Logitech MX Master',
          origem: 'LOJA MATRIZ',
          destino: 'LOJA FILIAL 01',
          quantidade: 10,
          status: 'em_transito',
          data: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 'TRF-003',
          produto: 'Teclado Mecânico Redragon',
          origem: 'CD CENTRAL',
          destino: 'LOJA FILIAL 02',
          quantidade: 8,
          status: 'pendente',
          data: new Date().toISOString()
        },
        {
          id: 'TRF-004',
          produto: 'Monitor LG 24" Full HD',
          origem: 'LOJA FILIAL 01',
          destino: 'LOJA MATRIZ',
          quantidade: 3,
          status: 'cancelada',
          data: new Date(Date.now() - 172800000).toISOString()
        },
      ];
      
      setState('data', mockData);
      setState('lastUpdate', new Date());
      setState('isLoading', false);
    }, 500);
  };

  onMount(() => {
    loadData();
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'concluida': return CheckCircle;
      case 'em_transito': return Truck;
      case 'pendente': return Clock;
      case 'cancelada': return XCircle;
      default: return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'concluida': return 'text-green-400 bg-green-900/20 border-green-900';
      case 'em_transito': return 'text-blue-400 bg-blue-900/20 border-blue-900';
      case 'pendente': return 'text-yellow-400 bg-yellow-900/20 border-yellow-900';
      case 'cancelada': return 'text-red-400 bg-red-900/20 border-red-900';
      default: return 'text-gray-400 bg-gray-900/20 border-gray-900';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'concluida': return 'Concluída';
      case 'em_transito': return 'Em Trânsito';
      case 'pendente': return 'Pendente';
      case 'cancelada': return 'Cancelada';
      default: return status;
    }
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6">
      {/* Header */}
      <div class="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Transferências</h2>
          <p class="text-muted">
            Gestão de transferências entre unidades
            {state.lastUpdate && <span class="ml-2 text-xs opacity-70">Atualizado: {state.lastUpdate.toLocaleTimeString()}</span>}
          </p>
        </div>
        <button onClick={loadData} class="btn btn-outline gap-2" disabled={state.isLoading}>
          <RefreshCw size={16} class={state.isLoading ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {/* Stats Cards */}
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Pendentes</span>
            <Clock size={16} class="text-yellow-500" />
          </div>
          <div class="text-2xl font-bold text-yellow-400">
            {state.data.filter(t => t.status === 'pendente').length}
          </div>
        </div>

        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Em Trânsito</span>
            <Truck size={16} class="text-blue-500" />
          </div>
          <div class="text-2xl font-bold text-blue-400">
            {state.data.filter(t => t.status === 'em_transito').length}
          </div>
        </div>

        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Concluídas</span>
            <CheckCircle size={16} class="text-green-500" />
          </div>
          <div class="text-2xl font-bold text-green-400">
            {state.data.filter(t => t.status === 'concluida').length}
          </div>
        </div>

        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div class="flex flex-row items-center justify-between space-y-0 pb-2">
            <span class="text-sm font-medium text-muted">Total</span>
            <Truck size={16} class="text-muted" />
          </div>
          <div class="text-2xl font-bold">
            {state.data.length}
          </div>
        </div>
      </div>

      <Show when={!state.isLoading} fallback={
        <div class="flex-1 flex items-center justify-center text-muted animate-pulse">
          <RefreshCw size={32} class="animate-spin mb-2" />
          <span class="ml-2">Carregando transferências...</span>
        </div>
      }>
        {/* Grid de Transferências */}
        <div class="border rounded-lg overflow-hidden flex-1 flex flex-col bg-card">
          <div class="grid grid-cols-[1fr_2fr_2fr_1fr_1fr_1fr] gap-4 p-4 bg-muted/50 text-xs font-medium text-muted uppercase tracking-wider border-b">
            <div>ID</div>
            <div>Produto</div>
            <div>Rota</div>
            <div>Quantidade</div>
            <div>Data</div>
            <div>Status</div>
          </div>
          
          <div class="flex-1 overflow-y-auto">
            <For each={state.data}>
              {(transfer) => {
                const StatusIcon = getStatusIcon(transfer.status);
                return (
                  <div class="grid grid-cols-[1fr_2fr_2fr_1fr_1fr_1fr] gap-4 p-4 border-b items-center hover:bg-muted/30 transition-colors text-sm">
                    <div class="font-mono text-xs text-muted">
                      {transfer.id}
                    </div>
                    
                    <div class="font-medium text-foreground truncate" title={transfer.produto}>
                      {transfer.produto}
                    </div>
                    
                    <div class="flex items-center gap-2 text-xs">
                      <span class="px-2 py-1 bg-secondary rounded font-mono">{transfer.origem}</span>
                      <ArrowRight size={14} class="text-muted" />
                      <span class="px-2 py-1 bg-secondary rounded font-mono">{transfer.destino}</span>
                    </div>
                    
                    <div class="font-mono">
                      {transfer.quantidade}
                    </div>
                    
                    <div class="text-xs text-muted">
                      {new Date(transfer.data).toLocaleDateString()}
                    </div>
                    
                    <div>
                      <span class={`inline-flex items-center gap-1 rounded border px-2 py-1 text-xs font-medium ${getStatusColor(transfer.status)}`}>
                        <StatusIcon size={12} />
                        {getStatusLabel(transfer.status)}
                      </span>
                    </div>
                  </div>
                );
              }}
            </For>
            
            {state.data.length === 0 && (
              <div class="p-8 text-center text-muted">
                <Truck size={48} class="mx-auto mb-4 opacity-50" />
                <p>Nenhuma transferência registrada.</p>
              </div>
            )}
          </div>
        </div>
      </Show>

      {/* Info Box */}
      <div class="p-4 bg-blue-900/10 border border-blue-900/30 rounded-lg text-sm text-blue-300">
        <p class="font-medium mb-1">ℹ️ Funcionalidade em Desenvolvimento</p>
        <p class="text-xs text-blue-400/80">
          Esta página exibe dados simulados. A integração com o backend para transferências reais será implementada em breve.
        </p>
      </div>
    </div>
  );
}
