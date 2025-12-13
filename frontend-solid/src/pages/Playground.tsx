import { createSignal, For, Show, onMount } from 'solid-js';
import { Terminal, Send, Trash2, Settings, Zap } from 'lucide-solid';
import api from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ModelInfo {
  model: string;
  temperature: number;
  max_tokens: number;
  json_mode: boolean;
}

interface CacheStats {
  hits: number;
  misses: number;
  hit_rate: number;
  enabled: boolean;
}

interface ChatResponse {
  response: string;
  model_info: ModelInfo;
  metadata: {
    response_time: number;
    timestamp: string;
    user: string;
  };
  cache_stats: CacheStats;
}

export default function Playground() {
  const [messages, setMessages] = createSignal<Message[]>([]);
  const [input, setInput] = createSignal('');
  const [loading, setLoading] = createSignal(false);

  // Controles do modelo
  const [temperature, setTemperature] = createSignal(1.0);
  const [maxTokens, setMaxTokens] = createSignal(2048);
  const [jsonMode, setJsonMode] = createSignal(false);
  const [streamMode, setStreamMode] = createSignal(false);

  // Info do modelo e cache
  const [modelInfo, setModelInfo] = createSignal<ModelInfo | null>(null);
  const [cacheStats, setCacheStats] = createSignal<CacheStats | null>(null);
  const [responseTime, setResponseTime] = createSignal(0);

  // Exemplos predefinidos
  const examples = [
    {
      title: "Análise de Dados",
      prompt: "Analise as tendências de vendas do último trimestre e identifique os produtos mais vendidos."
    },
    {
      title: "Geração SQL",
      prompt: "Gere uma query SQL para buscar os top 10 produtos com maior giro de estoque."
    },
    {
      title: "Análise Python",
      prompt: "Escreva um código Python usando Polars para calcular a média de vendas por categoria."
    }
  ];

  onMount(async () => {
    try {
      const response = await api.get('/playground/info');
      setModelInfo({
        model: response.data.model,
        temperature: temperature(),
        max_tokens: maxTokens(),
        json_mode: jsonMode()
      });
    } catch (error) {
      console.error('Erro ao carregar info do modelo:', error);
    }
  });

  const sendMessage = async (e?: Event) => {
    e?.preventDefault();
    if (!input().trim() || loading()) return;

    const userMessage: Message = {
      role: 'user',
      content: input(),
      timestamp: new Date().toISOString()
    };

    setMessages([...messages(), userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post<ChatResponse>('/playground/chat', {
        message: userMessage.content,
        history: messages().map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp
        })),
        temperature: temperature(),
        max_tokens: maxTokens(),
        json_mode: jsonMode(),
        stream: streamMode()
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.metadata.timestamp
      };

      setMessages([...messages(), assistantMessage]);
      setModelInfo(response.data.model_info);
      setCacheStats(response.data.cache_stats);
      setResponseTime(response.data.metadata.response_time);

    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Erro: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages([...messages(), errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setMessages([]);
    setCacheStats(null);
    setResponseTime(0);
  };

  const useExample = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div class="p-6 h-full flex flex-col gap-4 max-w-7xl mx-auto">
      {/* Header */}
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <Terminal /> Gemini Playground
          </h2>
          <p class="text-muted">Teste o modelo com controles avançados de temperatura, tokens e modos especiais.</p>
        </div>

        <Show when={modelInfo()}>
          <div class="card p-3 border">
            <div class="text-xs text-muted mb-1">Modelo Atual</div>
            <div class="font-mono text-sm font-semibold">{modelInfo()?.model}</div>
          </div>
        </Show>
      </div>

      {/* Main Layout */}
      <div class="flex-1 grid grid-cols-[1fr_320px] gap-6 min-h-0">
        {/* Chat Area */}
        <div class="flex flex-col gap-4">
          {/* Messages */}
          <div class="flex-1 card p-4 border overflow-y-auto space-y-4">
            <Show when={messages().length === 0}>
              <div class="h-full flex items-center justify-center text-muted">
                <div class="text-center">
                  <Terminal size={48} class="mx-auto mb-4 opacity-50" />
                  <p class="text-lg">Nenhuma mensagem ainda</p>
                  <p class="text-sm">Digite uma mensagem ou use um dos exemplos abaixo</p>
                </div>
              </div>
            </Show>

            <For each={messages()}>
              {(message) => (
                <div class={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    class={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary border'
                    }`}
                  >
                    <div class="text-sm mb-1 opacity-70">
                      {message.role === 'user' ? 'Você' : 'Gemini'}
                    </div>
                    <div class="whitespace-pre-wrap break-words">{message.content}</div>
                    <div class="text-xs mt-2 opacity-50">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              )}
            </For>

            <Show when={loading()}>
              <div class="flex justify-start">
                <div class="bg-secondary border rounded-lg p-4">
                  <div class="flex items-center gap-2">
                    <div class="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                    <span class="text-sm text-muted">Gemini está pensando...</span>
                  </div>
                </div>
              </div>
            </Show>
          </div>

          {/* Input Area */}
          <form onSubmit={sendMessage} class="flex gap-2">
            <input
              type="text"
              class="flex-1 input"
              placeholder="Digite sua mensagem..."
              value={input()}
              onInput={(e) => setInput(e.currentTarget.value)}
              disabled={loading()}
            />
            <button
              type="submit"
              class="btn btn-primary gap-2"
              disabled={loading() || !input().trim()}
            >
              <Send size={16} />
              Enviar
            </button>
            <button
              type="button"
              class="btn btn-outline gap-2"
              onClick={clearHistory}
              disabled={messages().length === 0}
            >
              <Trash2 size={16} />
              Limpar
            </button>
          </form>

          {/* Examples */}
          <div class="card p-4 border">
            <div class="text-sm font-medium mb-3 flex items-center gap-2">
              <Zap size={16} />
              Exemplos Rápidos
            </div>
            <div class="grid grid-cols-3 gap-2">
              <For each={examples}>
                {(example) => (
                  <button
                    class="btn btn-outline text-left text-sm p-3 h-auto"
                    onClick={() => useExample(example.prompt)}
                    disabled={loading()}
                  >
                    <div class="font-medium mb-1">{example.title}</div>
                    <div class="text-xs text-muted line-clamp-2">{example.prompt}</div>
                  </button>
                )}
              </For>
            </div>
          </div>
        </div>

        {/* Sidebar - Controles */}
        <div class="flex flex-col gap-4">
          {/* Configurações do Modelo */}
          <div class="card p-4 border">
            <div class="text-sm font-medium mb-4 flex items-center gap-2">
              <Settings size={16} />
              Configurações do Modelo
            </div>

            {/* Temperature */}
            <div class="mb-4">
              <label class="text-sm text-muted mb-2 block">
                Temperature: {temperature().toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={temperature()}
                onInput={(e) => setTemperature(parseFloat(e.currentTarget.value))}
                class="w-full"
              />
              <div class="flex justify-between text-xs text-muted mt-1">
                <span>Preciso</span>
                <span>Criativo</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div class="mb-4">
              <label class="text-sm text-muted mb-2 block">
                Max Tokens: {maxTokens()}
              </label>
              <input
                type="range"
                min="100"
                max="8192"
                step="100"
                value={maxTokens()}
                onInput={(e) => setMaxTokens(parseInt(e.currentTarget.value))}
                class="w-full"
              />
              <div class="flex justify-between text-xs text-muted mt-1">
                <span>100</span>
                <span>8192</span>
              </div>
            </div>

            {/* JSON Mode */}
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm">JSON Mode</label>
              <input
                type="checkbox"
                checked={jsonMode()}
                onChange={(e) => setJsonMode(e.currentTarget.checked)}
                class="toggle"
              />
            </div>

            {/* Stream Mode */}
            <div class="flex items-center justify-between">
              <label class="text-sm">Stream Mode</label>
              <input
                type="checkbox"
                checked={streamMode()}
                onChange={(e) => setStreamMode(e.currentTarget.checked)}
                class="toggle"
                disabled
              />
            </div>
            <p class="text-xs text-muted mt-1">* Stream em desenvolvimento</p>
          </div>

          {/* Cache Stats */}
          <Show when={cacheStats()}>
            <div class="card p-4 border">
              <div class="text-sm font-medium mb-3">Estatísticas de Cache</div>

              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-muted">Status:</span>
                  <span class={cacheStats()?.enabled ? "text-green-500" : "text-gray-500"}>
                    {cacheStats()?.enabled ? "Ativo" : "Inativo"}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-muted">Hits:</span>
                  <span class="font-mono">{cacheStats()?.hits || 0}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-muted">Misses:</span>
                  <span class="font-mono">{cacheStats()?.misses || 0}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-muted">Hit Rate:</span>
                  <span class="font-mono">{((cacheStats()?.hit_rate || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </Show>

          {/* Response Time */}
          <Show when={responseTime() > 0}>
            <div class="card p-4 border">
              <div class="text-sm font-medium mb-2">Última Resposta</div>
              <div class="text-2xl font-bold font-mono">{responseTime().toFixed(2)}s</div>
              <div class="text-xs text-muted mt-1">Tempo de processamento</div>
            </div>
          </Show>

          {/* Model Info */}
          <Show when={modelInfo()}>
            <div class="card p-4 border bg-secondary/30">
              <div class="text-sm font-medium mb-3">Info do Modelo</div>
              <div class="space-y-1 text-xs font-mono">
                <div class="text-muted">Model: <span class="text-foreground">{modelInfo()?.model}</span></div>
                <div class="text-muted">Temp: <span class="text-foreground">{modelInfo()?.temperature}</span></div>
                <div class="text-muted">Tokens: <span class="text-foreground">{modelInfo()?.max_tokens}</span></div>
                <div class="text-muted">JSON: <span class="text-foreground">{modelInfo()?.json_mode ? 'ON' : 'OFF'}</span></div>
              </div>
            </div>
          </Show>
        </div>
      </div>
    </div>
  );
}
