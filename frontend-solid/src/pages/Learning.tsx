import { createSignal, onMount, For, Show } from 'solid-js';
import { BookOpen, ThumbsUp, ThumbsDown, AlertTriangle } from 'lucide-solid';

// Mock data enquanto criamos o endpoint
const learningData = [
  { id: 1, query: "vendas da semana", feedback: "positive", timestamp: "2025-11-28 10:00" },
  { id: 2, query: "preço produto xyz", feedback: "negative", error: "Produto não encontrado", timestamp: "2025-11-28 10:05" },
  { id: 3, query: "estoque loja 5", feedback: "positive", timestamp: "2025-11-28 11:30" },
];

export default function Learning() {
  const [stats, setStats] = createSignal({ success: 85, errors: 12, feedbackScore: 4.5 });

  return (
    <div class="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h2 class="text-2xl font-bold">Sistema de Aprendizado</h2>
        <p class="text-muted">Monitoramento de qualidade das respostas do Agente.</p>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="card p-6 bg-green-500/10 border-green-500/20">
          <div class="flex items-center gap-2 mb-2 text-green-400 font-semibold">
            <ThumbsUp size={20} /> Taxa de Sucesso
          </div>
          <div class="text-3xl font-bold text-green-400">{stats().success}%</div>
        </div>
        <div class="card p-6 bg-red-500/10 border-red-500/20">
          <div class="flex items-center gap-2 mb-2 text-red-400 font-semibold">
            <AlertTriangle size={20} /> Erros
          </div>
          <div class="text-3xl font-bold text-red-400">{stats().errors}</div>
        </div>
        <div class="card p-6 bg-primary/10 border-primary/20">
          <div class="flex items-center gap-2 mb-2 text-primary font-semibold">
            <BookOpen size={20} /> Nota Média
          </div>
          <div class="text-3xl font-bold text-primary">{stats().feedbackScore}/5</div>
        </div>
      </div>

      <div class="card border rounded-lg overflow-hidden">
        <div class="p-4 bg-muted/50 border-b font-medium text-sm grid grid-cols-[2fr_1fr_2fr_1fr] gap-4">
          <div>Query</div>
          <div>Feedback</div>
          <div>Observação</div>
          <div>Data</div>
        </div>
        <div class="divide-y divide-border">
          <For each={learningData}>
            {(item) => (
              <div class="p-4 text-sm grid grid-cols-[2fr_1fr_2fr_1fr] gap-4 items-center hover:bg-muted/30">
                <div class="font-mono text-xs bg-secondary p-1 rounded w-fit px-2">{item.query}</div>
                <div>
                  {item.feedback === 'positive' 
                    ? <span class="text-green-400 flex items-center gap-1"><ThumbsUp size={14} /> Útil</span> 
                    : <span class="text-red-400 flex items-center gap-1"><ThumbsDown size={14} /> Falha</span>
                  }
                </div>
                <div class="text-muted">{item.error || '-'}</div>
                <div class="text-muted text-xs">{item.timestamp}</div>
              </div>
            )}
          </For>
        </div>
      </div>
    </div>
  );
}
