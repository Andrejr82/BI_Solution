import { createSignal, For, Show, onMount, createEffect } from 'solid-js';
import { Code, Send, Trash2, FileCode, Database, Zap, Clock, Info, BookOpen, Search, ChevronDown, ChevronRight } from 'lucide-solid';
import api from '../lib/api';
import { MessageActions } from '../components/MessageActions';
import 'github-markdown-css/github-markdown.css';
import './chat-markdown.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  code_references?: CodeReference[];
}

interface CodeReference {
  file: string;
  score: number;
  content: string;
  lines: string;
}

interface IndexStats {
  status: string;
  total_files: number;
  total_functions: number;
  total_classes: number;
  total_lines: number;
  indexed_at: string | null;
  languages: string[];
}

export default function CodeChat() {
  const [messages, setMessages] = createSignal<Message[]>([]);
  const [input, setInput] = createSignal('');
  const [loading, setLoading] = createSignal(false);
  const [indexStats, setIndexStats] = createSignal<IndexStats | null>(null);
  const [examplesExpanded, setExamplesExpanded] = createSignal(true);
  let messagesEndRef: HTMLDivElement | undefined;

  // Examples de perguntas
  const examples = [
    {
      title: "Estrutura do Código",
      prompt: "Quais são os principais módulos do backend?"
    },
    {
      title: "Autenticação",
      prompt: "Como funciona o sistema de autenticação?"
    },
    {
      title: "API Endpoints",
      prompt: "Liste todos os endpoints da API de chat"
    },
    {
      title: "Frontend Components",
      prompt: "Quais componentes SolidJS existem no projeto?"
    }
  ];

  onMount(async () => {
    // Load index stats
    try {
      const response = await api.get('/code-chat/stats');
      setIndexStats(response.data);
      
      // Welcome message
      const welcomeMsg: Message = {
        id: '0',
        role: 'assistant',
        content: `🤖 **Olá! Sou seu Agente Fullstack de Código.**\n\nPosso responder qualquer pergunta sobre este projeto:\n\n- 📁 **${response.data.total_files.toLocaleString()}** arquivos indexados\n- 📝 **${response.data.total_functions.toLocaleString()}** funções\n- 🏗️ **${response.data.total_classes.toLocaleString()}** classes\n- 💻 **${response.data.languages.join(', ')}**\n\nFaça uma pergunta sobre o código!`,
        timestamp: new Date().toISOString()
      };
      setMessages([welcomeMsg]);
      
    } catch (error: any) {
      console.error('Erro ao carregar stats:', error);
      const errorMsg: Message = {
        id: '0',
        role: 'assistant',
        content: '⚠️ **Índice não disponível**\n\nO índice de código não foi gerado ainda.\n\nExecute: `python scripts/index_codebase.py`',
        timestamp: new Date().toISOString()
      };
      setMessages([errorMsg]);
    }
  });

  createEffect(() => {
    if (messages()) {
      setTimeout(() => messagesEndRef?.scrollIntoView({ behavior: 'smooth' }), 100);
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

    try {
      const response = await api.post('/code-chat/query', {
        message: userMessage.content,
        history: messages().slice(-5).map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp
        }))
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.metadata.timestamp,
        code_references: response.data.code_references
      };

      setMessages([...messages(), userMessage, assistantMessage]);

    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ **Erro**: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages([...messages(), userMessage, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    if (confirm('Deseja limpar o histórico?')) {
      setMessages([messages()[0]]); // Keep welcome message
    }
  };

  const loadExample = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div class="h-full flex flex-col bg-background max-w-[1800px] mx-auto">
      {/* Context7: Executive Header with KPIs */}
      <div class="border-b bg-card/50 backdrop-blur-sm p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold flex items-center gap-2 text-foreground">
            <Code class="text-primary" />
            Code Chat <span class="text-muted font-normal text-sm border-l pl-2 ml-2">Agente Fullstack</span>
          </h2>
        </div>

        {/* Live Metrics Strip */}
        <Show when={indexStats()}>
          <div class="flex gap-4">
            <div class="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-lg border border-border/50">
              <FileCode size={16} class="text-blue-500" />
              <div>
                <div class="text-[10px] text-muted uppercase tracking-wider font-semibold">Arquivos</div>
                <div class="text-sm font-mono font-bold">{indexStats()!.total_files.toLocaleString()}</div>
              </div>
            </div>

            <div class="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-lg border border-border/50">
              <Zap size={16} class="text-purple-500" />
              <div>
                <div class="text-[10px] text-muted uppercase tracking-wider font-semibold">Funções</div>
                <div class="text-sm font-mono font-bold">{indexStats()!.total_functions.toLocaleString()}</div>
              </div>
            </div>

            <div class="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-lg border border-border/50">
              <Database size={16} class="text-green-500" />
              <div>
                <div class="text-[10px] text-muted uppercase tracking-wider font-semibold">Status</div>
                <div class="text-sm font-mono font-bold">{indexStats()!.status === 'ready' ? '✅ Pronto' : '⚠️ Indexando'}</div>
              </div>
            </div>
          </div>
        </Show>
      </div>

      <div class="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-[1fr_350px]">
        {/* Main Chat Area */}
        <div class="flex flex-col min-h-0 bg-background/50">
          {/* Messages */}
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <For each={messages()}>
              {(message) => (
                <div class={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
                  <div
                    class={`max-w-[85%] rounded-2xl p-5 shadow-sm ${
                      message.role === 'user'
                        ? 'bg-primary/10 border border-primary/20 text-foreground rounded-tr-none'
                        : 'bg-card border text-card-foreground rounded-tl-none'
                    }`}
                  >
                    <div class="flex items-center gap-2 mb-2 opacity-70 border-b border-border/10 pb-2">
                      <span class="text-xs font-bold uppercase tracking-wider">
                        {message.role === 'user' ? 'Você' : 'Agente'}
                      </span>
                      <span class="text-[10px] ml-auto">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    <div class="markdown-body text-sm leading-relaxed" style="background: transparent;">
                      <pre class="whitespace-pre-wrap font-sans bg-transparent border-0 p-0 m-0 text-current">{message.content}</pre>
                    </div>

                    {/* Code References */}
                    <Show when={message.code_references && message.code_references.length > 0}>
                      <div class="mt-4 pt-4 border-t border-border/10 space-y-2">
                        <div class="text-xs font-bold text-muted uppercase tracking-wider mb-2">
                          📄 Referências de Código ({message.code_references!.length})
                        </div>
                        <For each={message.code_references}>
                          {(ref) => (
                            <div class="bg-secondary/30 border rounded-lg p-3 text-xs font-mono">
                              <div class="flex items-center justify-between mb-2">
                                <span class="font-bold text-primary">{ref.file}</span>
                                <span class="text-muted">Score: {(ref.score * 100).toFixed(1)}%</span>
                              </div>
                              <pre class="text-[11px] text-muted overflow-x-auto whitespace-pre-wrap">{ref.content}</pre>
                            </div>
                          )}
                        </For>
                      </div>
                    </Show>

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
                  <span class="text-xs text-muted font-medium">Analisando código...</span>
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
                  placeholder="Pergunte sobre o código..."
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

        {/* Right Sidebar - Examples & Info */}
        <div class="border-l bg-card/30 p-6 overflow-y-auto hidden lg:block">
          <div class="sticky top-0 space-y-8">
            {/* Examples */}
            <div class="space-y-4">
              <button
                onClick={() => setExamplesExpanded(!examplesExpanded())}
                class="w-full flex items-center justify-between text-sm font-bold uppercase tracking-wider text-muted hover:text-foreground"
              >
                <div class="flex items-center gap-2">
                  <BookOpen size={14} />
                  Exemplos
                </div>
                {examplesExpanded() ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </button>

              <Show when={examplesExpanded()}>
                <div class="space-y-2 animate-in slide-in-from-top-2">
                  <For each={examples}>
                    {(example) => (
                      <button
                        onClick={() => loadExample(example.prompt)}
                        class="w-full p-3 rounded-lg border border-border/50 hover:border-primary/50 hover:bg-secondary/50 transition-all text-left group"
                      >
                        <div class="font-semibold text-sm group-hover:text-primary transition-colors mb-1 flex items-center gap-2">
                          <Search size={12} />
                          {example.title}
                        </div>
                        <div class="text-xs text-muted line-clamp-2">{example.prompt}</div>
                      </button>
                    )}
                  </For>
                </div>
              </Show>
            </div>

            {/* Index Info */}
            <Show when={indexStats()}>
              <div class="p-4 bg-blue-500/5 border border-blue-500/10 rounded-xl space-y-2">
                <div class="flex items-center gap-2 text-blue-600 font-bold text-sm">
                  <Info size={16} />
                  Informações do Índice
                </div>
                <div class="text-xs text-muted space-y-1">
                  <div>📁 {indexStats()!.total_files.toLocaleString()} arquivos</div>
                  <div>📝 {indexStats()!.total_functions.toLocaleString()} funções</div>
                  <div>🏗️ {indexStats()!.total_classes.toLocaleString()} classes</div>
                  <div>💾 {indexStats()!.total_lines.toLocaleString()} linhas</div>
                  <Show when={indexStats()!.indexed_at}>
                    <div class="pt-2 border-t border-border/10">
                      Indexado: {new Date(indexStats()!.indexed_at!).toLocaleString()}
                    </div>
                  </Show>
                </div>
              </div>
            </Show>

            {/* Help */}
            <div class="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-xl space-y-2">
              <div class="flex items-center gap-2 text-yellow-600 font-bold text-sm">
                <Info size={16} />
                Dicas de Uso
              </div>
              <p class="text-xs text-muted leading-relaxed">
                Faça perguntas específicas sobre o código, arquitetura, ou funcionalidades. 
                O agente busca semanticamente em todo o projeto e fornece respostas contextualizadas.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
