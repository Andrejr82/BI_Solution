import { onMount, Show } from 'solid-js';
import { createStore } from 'solid-js/store';
import { Database, Server, HardDrive, Activity, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-solid';

interface SystemMetrics {
  parquetSize: string;
  parquetRows: number;
  parquetColumns: number;
  backendStatus: 'online' | 'offline';
  databaseStatus: 'connected' | 'disconnected';
  cacheStatus: 'active' | 'inactive';
  lastSync: Date;
}

export default function Diagnostics() {
  const [state, setState] = createStore({
    metrics: null as SystemMetrics | null,
    isLoading: true,
    error: null as string | null,
  });

  const loadDiagnostics = async () => {
    setState('isLoading', true);
    setState('error', null);
    
    try {
      // Tentar buscar health check do backend
      const response = await fetch('/api/v1/health');
      const healthData = await response.json();
      
      // Simular métricas do sistema
      // TODO: Criar endpoint específico para diagnóstico
      const metrics: SystemMetrics = {
        parquetSize: '245 MB',
        parquetRows: 100010,
        parquetColumns: 25,
        backendStatus: response.ok ? 'online' : 'offline',
        databaseStatus: 'connected',
        cacheStatus: 'active',
        lastSync: new Date(),
      };
      
      setState('metrics', metrics);
    } catch (error: any) {
      console.error('Erro ao carregar diagnóstico:', error);
      setState('error', error.message || 'Erro ao conectar com o backend');
      
      // Definir métricas offline
      setState('metrics', {
        parquetSize: 'N/A',
        parquetRows: 0,
        parquetColumns: 0,
        backendStatus: 'offline',
        databaseStatus: 'disconnected',
        cacheStatus: 'inactive',
        lastSync: new Date(),
      });
    } finally {
      setState('isLoading', false);
    }
  };

  onMount(() => {
    loadDiagnostics();
  });

  const getStatusColor = (status: string) => {
    if (status === 'online' || status === 'connected' || status === 'active') {
      return 'text-green-400 bg-green-900/20 border-green-900';
    }
    return 'text-red-400 bg-red-900/20 border-red-900';
  };

  const getStatusIcon = (status: string) => {
    if (status === 'online' || status === 'connected' || status === 'active') {
      return CheckCircle;
    }
    return AlertTriangle;
  };

  return (
    <div class="flex flex-col h-full p-6 gap-6 max-w-5xl mx-auto">
      {/* Header */}
      <div class="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Diagnóstico do Sistema</h2>
          <p class="text-muted">
            Informações sobre conexões e status dos serviços
          </p>
        </div>
        <button onClick={loadDiagnostics} class="btn btn-outline gap-2" disabled={state.isLoading}>
          <RefreshCw size={16} class={state.isLoading ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      <Show when={!state.isLoading && state.metrics} fallback={
        <div class="flex-1 flex items-center justify-center text-muted animate-pulse">
          <RefreshCw size={32} class="animate-spin mb-2" />
          <span class="ml-2">Carregando diagnóstico...</span>
        </div>
      }>
        {/* Status Cards */}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Backend API</span>
              <Server size={16} class="text-primary" />
            </div>
            <div class="mt-4">
              {(() => {
                const StatusIcon = getStatusIcon(state.metrics!.backendStatus);
                return (
                  <span class={`inline-flex items-center gap-2 rounded border px-3 py-1.5 text-sm font-medium ${getStatusColor(state.metrics!.backendStatus)}`}>
                    <StatusIcon size={16} />
                    {state.metrics!.backendStatus === 'online' ? 'Online' : 'Offline'}
                  </span>
                );
              })()}
            </div>
          </div>

          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Banco de Dados</span>
              <Database size={16} class="text-primary" />
            </div>
            <div class="mt-4">
              {(() => {
                const StatusIcon = getStatusIcon(state.metrics!.databaseStatus);
                return (
                  <span class={`inline-flex items-center gap-2 rounded border px-3 py-1.5 text-sm font-medium ${getStatusColor(state.metrics!.databaseStatus)}`}>
                    <StatusIcon size={16} />
                    {state.metrics!.databaseStatus === 'connected' ? 'Conectado' : 'Desconectado'}
                  </span>
                );
              })()}
            </div>
          </div>

          <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between space-y-0 pb-2">
              <span class="text-sm font-medium text-muted">Cache Parquet</span>
              <Activity size={16} class="text-primary" />
            </div>
            <div class="mt-4">
              {(() => {
                const StatusIcon = getStatusIcon(state.metrics!.cacheStatus);
                return (
                  <span class={`inline-flex items-center gap-2 rounded border px-3 py-1.5 text-sm font-medium ${getStatusColor(state.metrics!.cacheStatus)}`}>
                    <StatusIcon size={16} />
                    {state.metrics!.cacheStatus === 'active' ? 'Ativo' : 'Inativo'}
                  </span>
                );
              })()}
            </div>
          </div>
        </div>

        {/* Parquet Metrics */}
        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <h3 class="font-semibold flex items-center gap-2 mb-4">
            <HardDrive size={18} />
            Métricas do Parquet (admmat.parquet)
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p class="text-sm text-muted mb-1">Tamanho do Arquivo</p>
              <p class="text-2xl font-bold text-primary">{state.metrics!.parquetSize}</p>
            </div>
            
            <div>
              <p class="text-sm text-muted mb-1">Total de Linhas</p>
              <p class="text-2xl font-bold">{state.metrics!.parquetRows.toLocaleString()}</p>
            </div>
            
            <div>
              <p class="text-sm text-muted mb-1">Colunas</p>
              <p class="text-2xl font-bold">{state.metrics!.parquetColumns}</p>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div class="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
          <h3 class="font-semibold mb-4">Informações do Sistema</h3>
          
          <div class="space-y-3 text-sm">
            <div class="flex justify-between py-2 border-b border-border">
              <span class="text-muted">Última Sincronização</span>
              <span class="font-mono">{state.metrics!.lastSync.toLocaleString()}</span>
            </div>
            
            <div class="flex justify-between py-2 border-b border-border">
              <span class="text-muted">Ambiente</span>
              <span class="font-mono">Development</span>
            </div>
            
            <div class="flex justify-between py-2 border-b border-border">
              <span class="text-muted">Versão do Backend</span>
              <span class="font-mono">1.0.0</span>
            </div>
            
            <div class="flex justify-between py-2">
              <span class="text-muted">Limite de Dados (Métricas)</span>
              <span class="font-mono text-primary">10,000 linhas</span>
            </div>
            
            <div class="flex justify-between py-2">
              <span class="text-muted">Limite de Dados (Analytics)</span>
              <span class="font-mono text-primary">5,000 linhas</span>
            </div>
          </div>
        </div>
      </Show>

      <Show when={state.error}>
        <div class="p-4 bg-red-900/20 border border-red-900 rounded text-red-400">
          <p class="font-medium mb-1">Erro ao carregar diagnóstico</p>
          <p class="text-sm">{state.error}</p>
        </div>
      </Show>
    </div>
  );
}
