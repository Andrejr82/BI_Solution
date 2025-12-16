import { createSignal, For, Show, onMount, createEffect } from 'solid-js';
import { Terminal, Send, Trash2, Settings, Zap, Activity, Clock, Cpu, Info, Code, FileJson, Save, Play, X, ChevronDown, ChevronRight, Pencil } from 'lucide-solid';
import api from '../lib/api';
import { MessageActions } from '../components/MessageActions';
import 'github-markdown-css/github-markdown.css';
import './chat-markdown.css';

interface Message {
  id: string; 
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ModelInfo {
  model: string;
  temperature: number;
  max_tokens: number;
  json_mode: boolean;
  default_temperature?: number;
  default_max_tokens?: number;
  max_temperature_limit?: number;
  max_tokens_limit?: number;
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
  const [systemInstruction, setSystemInstruction] = createSignal('');
  const [loading, setLoading] = createSignal(false);
  let messagesEndRef: HTMLDivElement | undefined;
  const [showCodeModal, setShowCodeModal] = createSignal(false);
  const [systemExpanded, setSystemExpanded] = createSignal(false);

  // Controls
  const [temperature, setTemperature] = createSignal(1.0);
  const [maxTokens, setMaxTokens] = createSignal(2048);
  const [jsonMode, setJsonMode] = createSignal(false);
  const [streamMode, setStreamMode] = createSignal(false);

  // Stats & Info
  const [modelInfo, setModelInfo] = createSignal<ModelInfo | null>(null);
  const [cacheStats, setCacheStats] = createSignal<CacheStats | null>(null);
  const [responseTime, setResponseTime] = createSignal(0);

  // Editing state
  const [editingMessageId, setEditingMessageId] = createSignal<string | null>(null);
  const [editText, setEditText] = createSignal('');

  // Examples
  const examples = [
    {
      title: "Análise Financeira",
      system: "Você é um analista financeiro sênior. Responda de forma concisa e use tabelas markdown quando apropriado.",
      prompt: "Analise o ROI de uma campanha de marketing que custou R$ 50.000 e gerou R$ 120.000 em vendas."
    },
    {
      title: "SQL Expert",
      system: "Você é um DBA especialista em SQL Server. Forneça apenas o código SQL otimizado sem explicações verbosas.",
      prompt: "Escreva uma query para encontrar produtos que não venderam nos últimos 6 meses."
    },
    {
      title: "Python Data",
      system: "Você é um engenheiro de dados Python. Prefira a biblioteca Polars sobre Pandas.",
      prompt: "Crie um script para ler um arquivo Parquet e filtrar linhas onde 'status' é 'error'."
    }
  ];

  onMount(async () => {
    try {
      const response = await api.get('/playground/info');
      
      // Update ModelInfo with all details from the backend
      setModelInfo(response.data);

      // Set initial maxTokens and temperature from backend defaults
      if (response.data.default_max_tokens) {
        setMaxTokens(response.data.default_max_tokens);
      }
      if (response.data.default_temperature) {
        setTemperature(response.data.default_temperature);
      }

    } catch (error) {
      console.error('Erro ao carregar info do modelo:', error);
    }
  });

  createEffect(() => {
    if (messages()) {
       setTimeout(() => messagesEndRef.scrollIntoView({ behavior: 'smooth' }), 100);
    }
  });

  const sendMessage = async (e?: Event) => {
    e?.preventDefault();
    if (!input().trim() || loading()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input(),
      timestamp: new Date().toISOString()
    };

    setMessages([...messages(), userMessage]);
    setInput('');
    setLoading(true);

    await executeRequest([...messages(), userMessage]);
  };

  const executeRequest = async (currentHistory: Message[]) => {
    try {
      const response = await api.post<ChatResponse>('/playground/chat', {
        message: currentHistory[currentHistory.length - 1].content,
        system_instruction: systemInstruction(),
        history: currentHistory.slice(0, -1).map(m => ({
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
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.metadata.timestamp
      };

      setMessages([...currentHistory, assistantMessage]);
      setModelInfo(response.data.model_info);
      setCacheStats(response.data.cache_stats);
      setResponseTime(response.data.metadata.response_time);

    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ **Erro na execução**: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages([...currentHistory, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    if (confirm('Deseja limpar o histórico e começar do zero?')) {
      setMessages([]);
      setResponseTime(0);
    }
  };

  const loadExample = (ex: any) => {
    setSystemInstruction(ex.system);
    setInput(ex.prompt);
    setSystemExpanded(true);
  };

  const generateCodeSnippet = () => {
    const pyCode = `
import requests

url = "http://localhost:8000/api/v1/playground/chat"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
payload = {
    "system_instruction": "${systemInstruction().replace(/"/g, '\\"')}",
    "message": "${messages().length > 0 ? messages()[messages().length - 1].content.replace(/"/g, '\\"') : ''}",
    "history": ${JSON.stringify(messages().slice(0, -1).map(m => ({ role: m.role, content: m.content }))).replace(/"/g, '\\"')},
    "temperature": ${temperature()},
    "max_tokens": ${maxTokens()},
    "json_mode": ${jsonMode()}
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
    `.trim();
    return pyCode;
  };

  return (
    <div class="h-full flex flex-col bg-background max-w-[1800px] mx-auto relative">
      {/* 1. Context7: Executive Header with KPIs */}
      <div class="border-b bg-card/50 backdrop-blur-sm p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 z-10">
        <div>
          <h2 class="text-xl font-bold flex items-center gap-2 text-foreground">
            <Terminal class="text-primary" /> 
            Playground <span class="text-muted font-normal text-sm border-l pl-2 ml-2">Ambiente de Desenvolvimento</span>
          </h2>
        </div>

        {/* Live Metrics Strip */}
        <div class="flex gap-4">
           <div class="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-lg border border-border/50">
              <Clock size={16} class="text-blue-500" />
              <div>
                 <div class="text-[10px] text-muted uppercase tracking-wider font-semibold">Latência</div>
                 <div class="text-sm font-mono font-bold">{responseTime() > 0 ? `${responseTime().toFixed(2)}s` : '--'}</div>
              </div>
           </div>
           
           <div class="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-lg border border-border/50">
              <Cpu size={16} class="text-purple-500" />
              <div>
                 <div class="text-[10px] text-muted uppercase tracking-wider font-semibold">Modelo</div>
                 <div class="text-sm font-mono font-bold">{modelInfo()?.model || 'Gemini 2.5'}</div>
              </div>
           </div>

           <button 
             onClick={() => setShowCodeModal(true)}
             class="btn btn-outline gap-2"
             title="Ver Código"
           >
              <Code size={16} /> <span class="hidden md:inline">Ver Código</span>
           </button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-[1fr_350px]">
        {/* Main Workspace */}
        <div class="flex flex-col min-h-0 bg-background/50 relative">
          
          {/* System Instruction Panel - Context7: Define Persona First */}
          <div class="border-b bg-card/20 transition-all duration-300">
             <button 
                onClick={() => setSystemExpanded(!systemExpanded())}
                class="w-full flex items-center justify-between p-3 text-xs font-bold uppercase tracking-wider text-muted hover:bg-card/40"
             >
                <div class="flex items-center gap-2">
                   <Settings size={14} /> Instruções do Sistema (Persona)
                </div>
                {systemExpanded() ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
             </button>
             
             <Show when={systemExpanded()}>
                <div class="p-4 pt-0 animate-in slide-in-from-top-2">
                   <textarea 
                      class="input w-full min-h-[100px] font-mono text-sm bg-background" 
                      placeholder="Ex: Você é um assistente especialista em análise de dados. Responda sempre em JSON."
                      value={systemInstruction()}
                      onInput={(e) => setSystemInstruction(e.currentTarget.value)}
                   />
                </div>
             </Show>
          </div>

          {/* Messages */}
          <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
            <Show when={messages().length === 0}>
              <div class="h-full flex flex-col items-center justify-center text-muted gap-6 animate-in fade-in zoom-in duration-500">
                <div class="p-6 bg-secondary/30 rounded-full">
                   <FileJson size={64} class="opacity-20" />
                </div>
                <div class="text-center max-w-md space-y-2">
                  <h3 class="text-xl font-bold text-foreground">Playground de Desenvolvimento</h3>
                  <p>Defina uma persona, configure os parâmetros e teste prompts complexos antes de implementar.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 w-full max-w-4xl mt-4">
                   <For each={examples}>
                      {(example) => (
                         <button 
                            onClick={() => loadExample(example)}
                            class="p-4 rounded-xl border border-border/50 hover:border-primary/50 hover:bg-secondary/50 transition-all text-left group"
                         >
                            <div class="font-semibold text-sm group-hover:text-primary transition-colors mb-1 flex items-center gap-2">
                               <Play size={14} /> {example.title}
                            </div>
                            <div class="text-xs text-muted line-clamp-2">{example.system}</div>
                         </button>
                      )}
                   </For>
                </div>
              </div>
            </Show>

            <For each={messages()}>
              {(message) => (
                <div class={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 group`}>
                  <div
                    class={`max-w-[85%] rounded-2xl p-5 shadow-sm relative ${
                      message.role === 'user'
                        ? 'bg-primary/10 border border-primary/20 text-foreground rounded-tr-none'
                        : 'bg-card border text-card-foreground rounded-tl-none'
                    }`}
                  >
                    <div class="flex items-center gap-2 mb-2 opacity-70 border-b border-border/10 pb-2">
                      <span class="text-xs font-bold uppercase tracking-wider">
                         {message.role === 'user' ? 'User' : 'Model'}
                      </span>
                      <span class="text-[10px] ml-auto">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <div class="markdown-body text-sm leading-relaxed" style="background: transparent;">
                       <pre class="whitespace-pre-wrap font-sans bg-transparent border-0 p-0 m-0 text-current">{message.content}</pre>
                    </div>

                    <Show when={message.role === 'assistant'}>
                        <div class="mt-3 pt-2 border-t border-border/10">
                           <MessageActions messageText={message.content} messageId={message.id} />
                        </div>
                    </Show>
                  </div>
                </div>
              )}
            </For>
            
            <Show when={loading()}>
               <div class="flex justify-start">
                  <div class="bg-card border rounded-2xl rounded-tl-none p-4 flex items-center gap-3">
                     <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce"></div>
                     </div>
                     <span class="text-xs text-muted font-medium">Gerando resposta...</span>
                  </div>
               </div>
            </Show>
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div class="p-4 border-t bg-background/80 backdrop-blur-md">
            <form onSubmit={sendMessage} class="flex gap-3 max-w-4xl mx-auto">
              <button
                type="button"
                onClick={clearHistory}
                class="btn btn-ghost btn-icon text-muted hover:text-destructive"
                title="Limpar Histórico"
              >
                <Trash2 size={20} />
              </button>
              
              <div class="flex-1 relative">
                 <input
                   type="text"
                   class="input w-full pr-12 shadow-sm font-mono text-sm"
                   placeholder="Digite sua mensagem..."
                   value={input()}
                   onInput={(e) => setInput(e.currentTarget.value)}
                   disabled={loading()}
                 />
              </div>

              <button
                type="submit"
                class="btn btn-primary shadow-md hover:shadow-lg transition-all"
                disabled={loading() || !input().trim()}
              >
                <Show when={!loading()} fallback={<Clock size={20} class="animate-spin" />}>
                   <Send size={20} />
                </Show>
              </button>
            </form>
          </div>
        </div>

        {/* Right Sidebar - Configuration */}
        <div class="border-l bg-card/30 p-6 overflow-y-auto hidden lg:block">
           <div class="sticky top-0 space-y-8">
              {/* Settings Group */}
              <div class="space-y-4">
                 <h3 class="font-bold flex items-center gap-2 text-foreground/80">
                    <Settings size={18} /> Parâmetros
                 </h3>
                 
                 <div class="space-y-4 p-4 bg-background border rounded-xl shadow-sm">
                    {/* Temperature */}
                    <div class="space-y-3">
                       <div class="flex justify-between items-center">
                          <label class="text-sm font-medium">Temperatura</label>
                          <span class="text-xs font-mono bg-secondary px-2 py-1 rounded">{temperature().toFixed(1)}</span>
                       </div>
                       <input
                          type="range" min="0" max="2" step="0.1"
                          value={temperature()}
                          onInput={(e) => setTemperature(parseFloat(e.currentTarget.value))}
                          class="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                       />
                    </div>

                    <div class="h-px bg-border/50"></div>

                    {/* Max Tokens */}
                    <div class="space-y-3">
                       <div class="flex justify-between items-center">
                          <label class="text-sm font-medium">Max Tokens</label>
                          <span class="text-xs font-mono bg-secondary px-2 py-1 rounded">{maxTokens()}</span>
                       </div>
                       <input
                          type="range" min="100" max={modelInfo()?.max_tokens_limit || 8192} step="100"
                          value={maxTokens()}
                          onInput={(e) => setMaxTokens(parseInt(e.currentTarget.value))}
                          class="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                       />
                    </div>
                 </div>
              </div>

              {/* Modes Group */}
              <div class="space-y-4">
                 <h3 class="font-bold flex items-center gap-2 text-foreground/80">
                    <Cpu size={18} /> Output
                 </h3>
                 
                 <div class="space-y-3 p-4 bg-background border rounded-xl shadow-sm">
                    <div class="flex items-center justify-between group">
                       <div class="space-y-0.5">
                          <label class="text-sm font-medium">JSON Mode</label>
                          <p class="text-xs text-muted">Estrutura rígida</p>
                       </div>
                       <input
                          type="checkbox"
                          checked={jsonMode()}
                          onChange={(e) => setJsonMode(e.currentTarget.checked)}
                          class="toggle toggle-sm toggle-primary"
                       />
                    </div>
                 </div>
              </div>

              {/* Context7 Help Box */}
              <div class="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-xl space-y-2">
                 <div class="flex items-center gap-2 text-yellow-600 font-bold text-sm">
                    <Info size={16} /> Best Practice
                 </div>
                 <p class="text-xs text-muted leading-relaxed">
                    Use <strong>System Instructions</strong> para definir o comportamento base antes de iniciar a conversa. Isso economiza tokens e melhora a consistência.
                 </p>
              </div>

           </div>
        </div>
      </div>

      {/* Code Modal */}
      <Show when={showCodeModal()}>
        <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
           <div class="bg-card w-full max-w-2xl rounded-xl shadow-2xl border animate-in zoom-in-95">
              <div class="flex items-center justify-between p-4 border-b">
                 <h3 class="font-bold flex items-center gap-2"><Code size={20} /> Snippet de Integração</h3>
                 <button onClick={() => setShowCodeModal(false)} class="btn btn-ghost btn-icon btn-sm"><X size={18} /></button>
              </div>
              <div class="p-0 overflow-hidden">
                 <pre class="bg-secondary/50 p-4 text-xs font-mono overflow-x-auto text-foreground">
                    {generateCodeSnippet()}
                 </pre>
              </div>
              <div class="p-4 border-t flex justify-end gap-2">
                 <button onClick={() => setShowCodeModal(false)} class="btn btn-outline">Fechar</button>
                 <button class="btn btn-primary" onClick={() => {
                    navigator.clipboard.writeText(generateCodeSnippet());
                    setShowCodeModal(false);
                 }}>Copiar Código</button>
              </div>
           </div>
        </div>
      </Show>
    </div>
  );
}
