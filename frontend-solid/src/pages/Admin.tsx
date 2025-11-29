import { Shield, Users, Database, Settings, RefreshCw, CheckCircle, AlertCircle } from 'lucide-solid';
import { createSignal, Show } from 'solid-js';
import { adminApi } from '@/lib/api';

export default function Admin() {
  const [syncing, setSyncing] = createSignal(false);
  const [message, setMessage] = createSignal<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setMessage(null);
    try {
      await adminApi.syncParquet();
      setMessage({ type: 'success', text: 'Sincronização iniciada em segundo plano!' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao iniciar sincronização. Verifique logs.' });
    } finally {
      setSyncing(false);
      // Limpar mensagem após 5s
      setTimeout(() => setMessage(null), 5000);
    }
  };

  return (
    <div class="flex flex-col h-full items-center justify-center text-center p-6">
      <div class="max-w-md space-y-6 w-full">
        <div class="mx-auto w-16 h-16 bg-secondary rounded-full flex items-center justify-center text-muted-foreground">
          <Settings size={32} />
        </div>
        
        <h2 class="text-2xl font-bold">Área Administrativa</h2>
        <p class="text-muted">
          Gerenciamento do sistema e sincronização de dados.
        </p>

        <Show when={message()}>
          <div class={`p-3 rounded-lg flex items-center gap-2 text-sm ${
            message()?.type === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
          }`}>
            {message()?.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            {message()?.text}
          </div>
        </Show>

        <div class="grid grid-cols-1 gap-4 text-left mt-8">
          {/* Botão de Sync */}
          <div 
            onClick={!syncing() ? handleSync : undefined}
            class={`p-4 border rounded-lg bg-card flex items-center gap-4 transition-all ${
              syncing() ? 'opacity-70 cursor-wait' : 'hover:border-primary/50 cursor-pointer hover:bg-secondary/30'
            }`}
          >
            <div class="p-2 bg-purple-500/10 text-purple-400 rounded">
              <RefreshCw size={20} class={syncing() ? 'animate-spin' : ''} />
            </div>
            <div class="flex-1">
              <h4 class="font-semibold">Sincronizar Dados</h4>
              <p class="text-xs text-muted">Atualizar Parquet via SQL Server</p>
            </div>
            {syncing() && <span class="text-xs text-primary animate-pulse">Processando...</span>}
          </div>

          <div class="p-4 border rounded-lg bg-card flex items-center gap-4 hover:border-primary/50 cursor-pointer transition-colors opacity-50">
            <div class="p-2 bg-blue-500/10 text-blue-400 rounded"><Users size={20} /></div>
            <div>
              <h4 class="font-semibold">Gerenciar Usuários</h4>
              <p class="text-xs text-muted">Controle de acesso (Em breve)</p>
            </div>
          </div>

          <div class="p-4 border rounded-lg bg-card flex items-center gap-4 hover:border-primary/50 cursor-pointer transition-colors opacity-50">
            <div class="p-2 bg-green-500/10 text-green-400 rounded"><Shield size={20} /></div>
            <div>
              <h4 class="font-semibold">Logs de Segurança</h4>
              <p class="text-xs text-muted">Auditoria (Em breve)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
