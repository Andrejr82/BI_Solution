import { createSignal } from 'solid-js';
import { Terminal, Send } from 'lucide-solid';

export default function Playground() {
  const [input, setInput] = createSignal('');
  const [output, setOutput] = createSignal('');
  const [loading, setLoading] = createSignal(false);

  const runPrompt = async (e: Event) => {
    e.preventDefault();
    if (!input()) return;
    
    setLoading(true);
    // Simulação - Conectar ao endpoint real depois
    setTimeout(() => {
      setOutput(`[Simulação] Processado prompt: "${input()}"\n\nTokens: 45\nLatência: 120ms\nModelo: Gemini 2.5 Flash`);
      setLoading(false);
    }, 1000);
  };

  return (
    <div class="p-6 h-full flex flex-col gap-4 max-w-5xl mx-auto">
      <div>
        <h2 class="text-2xl font-bold flex items-center gap-2">
          <Terminal /> Gemini Playground
        </h2>
        <p class="text-muted">Teste prompts brutos e configurações do modelo.</p>
      </div>

      <div class="flex-1 grid grid-cols-2 gap-6">
        <div class="flex flex-col gap-4">
          <div class="card p-4 flex-1 flex flex-col border">
            <label class="text-sm font-medium mb-2">Input (Prompt)</label>
            <textarea 
              class="flex-1 bg-secondary/50 border rounded p-4 font-mono text-sm resize-none focus:outline-none focus:ring-1 focus:ring-primary"
              value={input()}
              onInput={(e) => setInput(e.currentTarget.value)}
              placeholder="Digite seu prompt aqui..."
            />
          </div>
          <button 
            class="btn btn-primary w-full gap-2"
            onClick={runPrompt}
            disabled={loading()}
          >
            {loading() ? 'Executando...' : <><Send size={16}/> Executar</>}
          </button>
        </div>

        <div class="card p-4 flex flex-col border bg-black/20">
          <label class="text-sm font-medium mb-2 text-muted">Output</label>
          <div class="flex-1 font-mono text-sm text-green-400 whitespace-pre-wrap">
            {output() || "// O resultado aparecerá aqui..."}
          </div>
        </div>
      </div>
    </div>
  );
}
