import { createSignal, onMount, For, Show } from 'solid-js';
import { reportsApi, Report } from '@/lib/api';
import { FileText, Download, Filter, Calendar, Trash2 } from 'lucide-solid';

export default function Reports() {
  const [reports, setReports] = createSignal<Report[]>([]);
  const [loading, setLoading] = createSignal(true);

  onMount(async () => {
    try {
      const res = await reportsApi.getAll();
      setReports(res.data);
    } catch (err) {
      console.error("Error fetching reports:", err);
    } finally {
      setLoading(false);
    }
  });

  return (
    <div class="flex flex-col h-full p-6 gap-6 max-w-5xl mx-auto">
      <div class="flex justify-between items-end">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Relatórios e Exportações</h2>
          <p class="text-muted">Arquivos gerados pelo sistema ou solicitados via Chat AI.</p>
        </div>
        <button class="btn btn-primary gap-2">
          <Filter size={16} />
          Filtrar
        </button>
      </div>

      <div class="border rounded-lg bg-card overflow-hidden min-h-[300px]">
        <div class="grid grid-cols-[3fr_1fr_1fr_1fr] gap-4 p-4 bg-muted/50 text-xs font-medium text-muted uppercase border-b">
          <div>Nome do Arquivo</div>
          <div>Status</div>
          <div>Data Criação</div>
          <div class="text-right">Ação</div>
        </div>

        <Show when={!loading} fallback={<div class="p-8 text-center text-muted">Carregando relatórios...</div>}>
          <div class="divide-y divide-border">
            <For each={reports()}>
              {(file) => (
                <div class="grid grid-cols-[3fr_1fr_1fr_1fr] gap-4 p-4 items-center hover:bg-muted/30 transition-colors text-sm">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-secondary rounded text-primary">
                      <FileText size={18} />
                    </div>
                    <div>
                      <div class="font-medium">{file.title}</div>
                      <div class="text-xs text-muted truncate max-w-[300px]">{file.description}</div>
                    </div>
                  </div>
                  
                  <div>
                    <span class={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                      file.status === 'completed' ? 'bg-green-400/10 text-green-400 ring-green-400/30' :
                      file.status === 'pending' ? 'bg-yellow-400/10 text-yellow-400 ring-yellow-400/30' :
                      'bg-red-400/10 text-red-400 ring-red-400/30'
                    }`}>
                      {file.status}
                    </span>
                  </div>
                  
                  <div class="flex items-center gap-2 text-muted">
                    <Calendar size={14} />
                    {new Date(file.created_at).toLocaleDateString()}
                  </div>
                  
                  <div class="text-right flex justify-end gap-2">
                    <button class="btn btn-outline px-3 py-1.5 h-auto text-xs gap-2 hover:text-primary hover:border-primary">
                      <Download size={14} />
                      Baixar
                    </button>
                  </div>
                </div>
              )}
            </For>
            
            {reports().length === 0 && (
              <div class="p-12 text-center text-muted">
                Nenhum relatório encontrado. Peça ao Agente para gerar um.
              </div>
            )}
          </div>
        </Show>
      </div>
    </div>
  );
}