import { createSignal, createEffect, onCleanup, onMount, For, Show } from 'solid-js';
import auth from '@/store/auth';
import { TypingIndicator } from '@/components';
import { PlotlyChart } from '@/components/PlotlyChart';
import { DataTable } from '@/components/DataTable';
import { FeedbackButtons } from '@/components/FeedbackButtons';
import { DownloadButton } from '@/components/DownloadButton';
import { MessageActions } from '@/components/MessageActions';
import { ExportMenu } from '@/components/ExportMenu';
import { ShareButton } from '@/components/ShareButton';
import { formatTimestamp } from '@/lib/formatters';
import { marked } from 'marked'; // Renderizador de Markdown
import { Trash2, StopCircle, Pencil, Check, X } from 'lucide-solid';
import 'github-markdown-css/github-markdown.css';
import './chat-markdown.css';

// ✅ SEGURANÇA: Função de sanitização básica para prevenir XSS
// Para produção, considere instalar: pnpm add dompurify @types/dompurify
const sanitizeHTML = (html: string): string => {
  // Remove tags script e eventos inline
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '')
    .replace(/on\w+='[^']*'/gi, '');
};

// Configurar marked para renderizar tabelas corretamente
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown (suporta tabelas)
  breaks: true, // Quebras de linha automáticas
});

// ✅ CORREÇÃO: Helper seguro para renderizar Markdown com sanitização
const renderMarkdown = (text: string): string => {
  try {
    const rawHtml = marked.parse(text) as string;
    // Sanitizar HTML para prevenir XSS
    return sanitizeHTML(rawHtml);
  } catch (e) {
    console.error('Erro ao renderizar Markdown:', e);
    return sanitizeHTML(text); // Sanitizar mesmo em caso de erro
  }
};

// Interface para mensagem - Atualizada para suportar estrutura JSON do backend
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
  timestamp: number;
  type?: 'text' | 'chart' | 'table' | 'final' | 'error' | 'loading_chart' | 'loading_table'; // Tipo da resposta do assistente
  chart_spec?: any; // Especificação JSON do Plotly
  data?: any[]; // Dados tabulares
  response_id?: string; // ID da resposta para feedback
  isOptimistic?: boolean; // UI Otimista
}

export default function Chat() {
  const [messages, setMessages] = createSignal<Message[]>([
    { id: '0', role: 'assistant', text: 'Olá! Sou seu assistente de BI. Pergunte sobre vendas, produtos ou estoque.', timestamp: Date.now(), type: 'text', response_id: 'initial_greeting' }
  ]);
  const [input, setInput] = createSignal('');
  const [isStreaming, setIsStreaming] = createSignal(false);
  const [isWaitingForResponse, setIsWaitingForResponse] = createSignal(false);
  const [sessionId, setSessionId] = createSignal<string>('');
  const [currentEventSource, setCurrentEventSource] = createSignal<EventSource | null>(null);
  const [lastUserMessage, setLastUserMessage] = createSignal<string>('');
  const [editingMessageId, setEditingMessageId] = createSignal<string | null>(null);
  const [editText, setEditText] = createSignal('');
  const [currentStatus, setCurrentStatus] = createSignal<string>('');
  const [slowResponseTimer, setSlowResponseTimer] = createSignal<number | null>(null);
  // ✅ CORREÇÃO: Estado para reconnection
  const [retryCount, setRetryCount] = createSignal(0);
  const [connectionStatus, setConnectionStatus] = createSignal<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected');
  const MAX_RETRIES = 5;
  let messagesEndRef: HTMLDivElement | undefined;
  let scrollTimeoutId: number | undefined;

  // Check for example query from Examples page & Init Session
  onMount(async () => {
    // 1. Initialize Session First
    let storedSession = localStorage.getItem('chat_session_id');
    if (!storedSession) {
      storedSession = crypto.randomUUID();
      localStorage.setItem('chat_session_id', storedSession);
    }
    setSessionId(storedSession);

    // 2. Check for Example Query
    const exampleQuery = localStorage.getItem('example_query');
    if (exampleQuery) {
      localStorage.removeItem('example_query');

      // Directly add the user message to the chat
      const userMsg: Message = { id: Date.now().toString(), role: 'user', text: exampleQuery, timestamp: Date.now() };
      setMessages(prev => [...prev, userMsg]);

      // And immediately process it
      await processUserMessage(exampleQuery);
    }
  });

  // ✅ CORREÇÃO: Auto-scroll com debounce proper
  createEffect(() => {
    messages(); // Re-run effect when messages change

    // Limpar timeout anterior
    if (scrollTimeoutId !== undefined) {
      clearTimeout(scrollTimeoutId);
    }

    // Usar setTimeout para garantir que o DOM foi atualizado
    scrollTimeoutId = window.setTimeout(() => {
      if (messagesEndRef) {
        messagesEndRef.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    }, 100);
  });

  // ✅ CORREÇÃO: Cleanup completo on unmount
  onCleanup(() => {
    const es = currentEventSource();
    if (es) {
      es.close();
    }
    const timerId = slowResponseTimer();
    if (timerId) {
      clearTimeout(timerId);
    }
    if (scrollTimeoutId !== undefined) {
      clearTimeout(scrollTimeoutId);
    }
  });

  const stopGeneration = () => {
    const es = currentEventSource();
    if (es) {
      console.log('⏹️ Stopping generation...');
      es.close();
      setCurrentEventSource(null);
      setIsStreaming(false);

      // Add stop message to last assistant message
      setMessages(prev => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg && lastMsg.role === 'assistant') {
          return prev.slice(0, -1).concat({
            ...lastMsg,
            text: lastMsg.text + '\n\n_[Geração interrompida pelo usuário]_'
          });
        }
        return prev;
      });
    }
  };

  const clearConversation = () => {
    if (confirm('Tem certeza que deseja limpar toda a conversa?')) {
      // Cancel slow response timer if active
      const timerId = slowResponseTimer();
      if (timerId) {
        clearTimeout(timerId);
        setSlowResponseTimer(null);
      }

      // Clear messages
      setMessages([
        { id: '0', role: 'assistant', text: 'Olá! Sou seu assistente de BI. Pergunte sobre vendas, produtos ou estoque.', timestamp: Date.now(), type: 'text', response_id: 'initial_greeting' }
      ]);

      // Create new session
      const newSession = crypto.randomUUID();
      setSessionId(newSession);
      localStorage.setItem('chat_session_id', newSession);

      console.log('🗑️ Conversation cleared, new session:', newSession);
    }
  };

  const regenerateLastResponse = () => {
    const lastMsg = lastUserMessage();
    if (!lastMsg) {
      console.warn('No last user message to regenerate');
      return;
    }

    // Remove last assistant message(s) if any
    setMessages(prev => {
      const userMessages = prev.filter(m => m.role === 'user');
      const lastUserMsg = userMessages[userMessages.length - 1];
      const lastUserIndex = prev.findIndex(m => m === lastUserMsg);

      // Keep everything up to and including the last user message
      return prev.slice(0, lastUserIndex + 1);
    });

    // Resend the last user message
    console.log('🔄 Regenerating response for:', lastMsg);
    processUserMessage(lastMsg);
  };

  const startEditMessage = (messageId: string, currentText: string) => {
    setEditingMessageId(messageId);
    setEditText(currentText);
  };

  const cancelEditMessage = () => {
    setEditingMessageId(null);
    setEditText('');
  };

  const saveEditedMessage = async (messageId: string) => {
    const newText = editText().trim();
    if (!newText) return;

    // Find message index
    const msgIndex = messages().findIndex(m => m.id === messageId);
    if (msgIndex === -1) return;

    // Update message text
    setMessages(prev => prev.map(m =>
      m.id === messageId ? { ...m, text: newText } : m
    ));

    // Remove all messages after this one
    setMessages(prev => prev.slice(0, msgIndex + 1));

    // Update last user message
    setLastUserMessage(newText);

    // Clear edit mode
    setEditingMessageId(null);
    setEditText('');

    // Reprocess with edited message
    console.log('✏️ Message edited, reprocessing:', newText);
    await processUserMessage(newText);
  };

  // Heurística Client-Side para UI Otimista
  const predictIntent = (text: string): 'loading_chart' | 'loading_table' | 'text' => {
    const lower = text.toLowerCase();
    if (lower.match(/gráfico|plot|visualiz|chart|ranking|evolução|tendência/i)) return 'loading_chart';
    if (lower.match(/tabela|lista|dados|planilha|relatório|csv|excel/i)) return 'loading_table';
    return 'text';
  };

  const processUserMessage = async (userText: string) => {
    // Validar autenticação
    const token = auth.token();
    if (!token) {
      console.error('❌ Token não encontrado');
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        text: '[Erro: Você não está autenticado. Por favor, faça login novamente.]',
        timestamp: Date.now(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }

    setIsStreaming(true);
    setIsWaitingForResponse(true);

    // Start slow response timer - warn user if taking too long (15s+)
    const slowTimer = window.setTimeout(() => {
      setCurrentStatus('Isso está demorando um pouco mais que o normal. Processando...');
    }, 15000);
    setSlowResponseTimer(slowTimer);

    // Prepara mensagem do assistente com UI Otimista
    const assistantId = (Date.now() + 1).toString();
    const predictedType = predictIntent(userText);
    
    // Se for gráfico/tabela, mostra o skeleton específico. Se for texto, mostra vazio (typing indicator cuida)
    const initialType = predictedType === 'text' ? 'text' : predictedType;
    
    const newMessage: Message = { 
      id: assistantId, 
      role: 'assistant', 
      text: '', 
      timestamp: Date.now(), 
      type: initialType,
      isOptimistic: true // Flag para controlar o skeleton
    };
    
    setMessages(prev => [...prev, newMessage]);

    try {
      // Conexão SSE Real com Backend
      console.log('📡 Iniciando SSE com token:', token.substring(0, 20) + '...', 'Session:', sessionId());
      const eventSource = new EventSource(`/api/v1/chat/stream?q=${encodeURIComponent(userText)}&token=${encodeURIComponent(token)}&session_id=${sessionId()}`);
      setCurrentEventSource(eventSource);

      let fullResponseContent = ''; // Para acumular texto e gerar response_id
      let currentMessageId = assistantId;
      let firstTokenReceived = false;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Ao receber o primeiro dado real (que não seja progress), remove o estado otimista
          if (!firstTokenReceived && data.type !== 'tool_progress' && data.type !== 'keepalive') {
            firstTokenReceived = true;
            setIsWaitingForResponse(false);
            
            // Remove a flag otimista da mensagem atual
            setMessages(prev => prev.map(msg => 
              msg.id === currentMessageId ? { ...msg, isOptimistic: false } : msg
            ));
          }

          if (data.done) {
            console.log('✅ Stream concluído');

            // Clear slow response timer
            const timerId = slowResponseTimer();
            if (timerId) {
              clearTimeout(timerId);
              setSlowResponseTimer(null);
            }

            eventSource.close();
            setCurrentEventSource(null);
            setIsStreaming(false);
            setIsWaitingForResponse(false);
            setCurrentStatus('');

            // ✅ CORREÇÃO: Finaliza a mensagem do assistente com UUID único
            const responseId = crypto.randomUUID();
            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, response_id: responseId, isOptimistic: false } : msg
            ));

            // Reset retry count on successful completion
            setRetryCount(0);
            setConnectionStatus('disconnected');
            return;
          }

          if (data.type === 'tool_progress') {
            const statusMap: Record<string, string> = {
              'Pensando': 'Analisando sua pergunta...',
              'consultar_dados_flexivel': 'Consultando o Data Lake...',
              'consultar_dados_gerais': 'Buscando informações gerais...',
              'gerar_grafico_universal': 'Gerando visualização...',
              'Processando resposta': 'Finalizando análise...'
            };
            const statusMsg = statusMap[data.tool] || 'Processando sua solicitação...';
            setCurrentStatus(statusMsg);
          } else if (data.type === 'text') {
            setCurrentStatus('Escrevendo...');
            setMessages(prev => prev.map(msg => {
              if (msg.id === currentMessageId) {
                // Se era um loading_chart/table otimista e veio texto, converte para text
                // Isso acontece se o LLM decidir explicar algo antes de mostrar o gráfico
                // ou se ele decidir não mostrar gráfico.
                const currentType = (msg.type === 'loading_chart' || msg.type === 'loading_table') ? 'text' : msg.type;
                
                const newText = msg.text + data.text;
                fullResponseContent = newText;
                
                return { ...msg, text: newText, type: currentType, isOptimistic: false };
              }
              return msg;
            }));
          } else if (data.type === 'chart' && data.chart_spec) {
            // Se a mensagem atual era um placeholder de gráfico, atualiza ela mesma
            // Se não, cria uma nova
            
            const lastMsg = messages()[messages().length - 1];
            
            if (lastMsg.id === currentMessageId && (lastMsg.type === 'loading_chart' || lastMsg.text === '')) {
                // Atualiza o placeholder existente
                setMessages(prev => prev.map(msg => 
                    msg.id === currentMessageId ? {
                        ...msg,
                        text: 'Aqui está o gráfico que você pediu:',
                        type: 'chart',
                        chart_spec: data.chart_spec,
                        isOptimistic: false,
                        response_id: btoa(JSON.stringify(data.chart_spec)).substring(0, 16)
                    } : msg
                ));
            } else {
                // Adiciona nova mensagem
                const chartMsgId = (Date.now() + 2).toString();
                setMessages(prev => [...prev, {
                  id: chartMsgId,
                  role: 'assistant',
                  text: 'Aqui está o gráfico que você pediu:',
                  timestamp: Date.now(),
                  type: 'chart',
                  chart_spec: data.chart_spec,
                  response_id: btoa(JSON.stringify(data.chart_spec)).substring(0, 16)
                }]);
                currentMessageId = chartMsgId;
            }
            
          } else if (data.type === 'table' && data.data) {
             // Lógica similar para tabelas
            const lastMsg = messages()[messages().length - 1];
            
            if (lastMsg.id === currentMessageId && (lastMsg.type === 'loading_table' || lastMsg.text === '')) {
                setMessages(prev => prev.map(msg => 
                    msg.id === currentMessageId ? {
                        ...msg,
                        text: 'Aqui estão os dados tabulares:',
                        type: 'table',
                        data: data.data,
                        isOptimistic: false,
                        response_id: btoa(JSON.stringify(data.data)).substring(0, 16)
                    } : msg
                ));
            } else {
                const tableMsgId = (Date.now() + 3).toString();
                setMessages(prev => [...prev, {
                  id: tableMsgId,
                  role: 'assistant',
                  text: 'Aqui estão os dados tabulares:',
                  timestamp: Date.now(),
                  type: 'table',
                  data: data.data,
                  response_id: btoa(JSON.stringify(data.data)).substring(0, 16)
                }]);
                currentMessageId = tableMsgId;
            }
          }
          else if (data.type === 'final' && data.text) {
            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, text: msg.text + data.text, type: 'text', isOptimistic: false } : msg
            ));
          }

          if (data.error) {
            console.error('❌ Erro do servidor:', data.error);

            // Clear slow response timer
            const timerId = slowResponseTimer();
            if (timerId) {
              clearTimeout(timerId);
              setSlowResponseTimer(null);
            }

            const errorMessage = data.error || 'Não foi possível processar sua solicitação. Por favor, tente novamente.';

            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, text: errorMessage, type: 'error', isOptimistic: false } : msg
            ));
            eventSource.close();
            setCurrentEventSource(null);
            setIsStreaming(false);
            setIsWaitingForResponse(false);
            setCurrentStatus('');
          }

        } catch (err) {
          console.error("❌ SSE Parse Error", err);
        }
      };

      // ✅ CORREÇÃO: EventSource com lógica de reconnection
      eventSource.onerror = (err) => {
        // ... (código existente mantido)
        console.error("❌ EventSource failed:", err);
         const timerId = slowResponseTimer();
        if (timerId) {
          clearTimeout(timerId);
          setSlowResponseTimer(null);
        }

        eventSource.close();
        setCurrentEventSource(null);

        const currentRetry = retryCount();
        if (currentRetry < MAX_RETRIES) {
           // ... retry logic
           const delay = Math.min(1000 * Math.pow(2, currentRetry), 30000);
           setConnectionStatus('connecting');
           setTimeout(() => {
            setRetryCount(currentRetry + 1);
            processUserMessage(userText);
          }, delay);
        } else {
           setConnectionStatus('error');
           setIsStreaming(false);
           setIsWaitingForResponse(false);
           setMessages(prev => prev.map(msg =>
            msg.id === currentMessageId ? { ...msg, text: "Erro de conexão.", type: 'error', isOptimistic: false } : msg
          ));
        }
      };

    } catch (err) {
      console.error("❌ Chat error:", err);
       // ... error handling
       setIsStreaming(false);
       setIsWaitingForResponse(false);
       setMessages(prev => prev.map(msg =>
        msg.id === assistantId ? { ...msg, text: "Erro ao iniciar.", type: 'error', isOptimistic: false } : msg
      ));
    }
  };

  const sendMessage = async (e: Event) => {
    e.preventDefault();
    if (!input() || isStreaming()) return;

    const userText = input();
    setInput('');
    setLastUserMessage(userText);

    // Adiciona mensagem do usuário
    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: userText, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);

    // Process message
    await processUserMessage(userText);
  };

  const handleFeedback = async (messageId: string, feedbackType: 'positive' | 'negative' | 'partial', comment?: string) => {
    const token = auth.token();
    if (!token) {
      console.error('❌ Token não encontrado para feedback.');
      alert('Você não está autenticado para enviar feedback.');
      return;
    }

    try {
      const response = await fetch('/api/v1/chat/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          response_id: messageId,
          feedback_type: feedbackType,
          comment: comment
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log(`Feedback ${feedbackType} enviado para ${messageId}`);
    } catch (error) {
      console.error('Erro ao enviar feedback:', error);
      alert('Erro ao enviar feedback.');
    }
  };


  return (
    <div class="absolute inset-0 flex flex-col w-full max-w-7xl mx-auto bg-background">
      {/* ✅ CORREÇÃO: Connection status banner */}
      <Show when={connectionStatus() === 'connecting'}>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800 px-4 py-2 text-sm text-yellow-800 dark:text-yellow-200">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-yellow-600 animate-pulse" />
            {currentStatus() || 'Conectando...'}
          </div>
        </div>
      </Show>
      <Show when={connectionStatus() === 'error'}>
        <div class="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-2 text-sm text-red-800 dark:text-red-200">
          <div class="flex items-center justify-between">
            <span>Desconectado. Verifique sua conexão.</span>
            <button
              onClick={() => {
                setRetryCount(0);
                setConnectionStatus('disconnected');
                const lastMsg = lastUserMessage();
                if (lastMsg) processUserMessage(lastMsg);
              }}
              class="text-xs underline hover:no-underline"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </Show>

      {/* Header with actions */}
      <div class="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b bg-background/50 backdrop-blur">
        <h2 class="text-base sm:text-lg font-semibold">Chat BI</h2>
        <div class="flex items-center gap-1 sm:gap-2">
          <Show when={isStreaming()}>
            <button
              onClick={stopGeneration}
              class="flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
              title="Parar geração"
            >
              <StopCircle size={16} />
              <span>Parar</span>
            </button>
          </Show>
          <ShareButton messages={messages} sessionId={sessionId()} />
          <ExportMenu messages={messages} sessionId={sessionId()} />
          <button
            onClick={clearConversation}
            class="flex items-center gap-2 px-3 py-2 text-sm rounded-lg border hover:bg-muted transition-colors"
            title="Limpar conversa"
          >
            <Trash2 size={16} />
            <span>Limpar</span>
          </button>
        </div>
      </div>

      {/* ✅ CORREÇÃO: Área de mensagens responsiva */}
      <div 
        class="flex-1 overflow-auto px-4 sm:px-6 md:px-8 py-4 sm:py-6 space-y-4 sm:space-y-6"
      >
        <For each={messages()}>
          {(msg, index) => (
            <div class={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                class={`${msg.type === 'chart' ? 'max-w-[95%] sm:max-w-[90%] md:max-w-[85%]' : 'max-w-[85%] sm:max-w-[80%] md:max-w-[75%]'} rounded-lg p-3 sm:p-4 text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                  ? 'bg-primary/10 border border-primary/20 text-foreground'
                  : 'bg-card border text-card-foreground'
                  }`}
              >
                <Show when={msg.role === 'assistant' && msg.type === 'chart' && msg.chart_spec}>
                  <div class="w-full min-w-[300px] sm:min-w-[400px] md:min-w-[500px]">
                    <PlotlyChart chartSpec={() => msg.chart_spec} height="420px" />
                  </div>
                </Show>
                <Show when={msg.role === 'assistant' && msg.type === 'table' && msg.data}>
                  <DataTable data={() => msg.data || []} caption={msg.text} />
                </Show>

                {/* ✅ CONTEXT7: Optimistic Skeleton UI */}
                <Show when={msg.type === 'loading_chart'}>
                  <div class="w-full min-w-[300px] sm:min-w-[400px] md:min-w-[500px] h-[420px] bg-secondary/10 rounded-lg border border-border/20 flex flex-col items-center justify-center gap-4 animate-pulse">
                     <div class="w-16 h-16 rounded-full bg-secondary/20 flex items-center justify-center">
                        <svg class="w-8 h-8 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                     </div>
                     <div class="space-y-2 text-center">
                        <div class="text-sm font-medium text-muted-foreground">Gerando visualização...</div>
                        <div class="text-xs text-muted-foreground/60">Analisando dados</div>
                     </div>
                  </div>
                </Show>

                <Show when={msg.type === 'loading_table'}>
                   <div class="w-full space-y-3 animate-pulse">
                      <div class="h-8 bg-secondary/20 rounded w-full"></div>
                      <div class="space-y-2">
                         <div class="h-10 bg-secondary/10 rounded w-full"></div>
                         <div class="h-10 bg-secondary/10 rounded w-full"></div>
                         <div class="h-10 bg-secondary/10 rounded w-full"></div>
                      </div>
                      <div class="flex justify-center mt-2">
                         <span class="text-xs text-muted-foreground">Processando tabela...</span>
                      </div>
                   </div>
                </Show>

                {/* ✅ CORREÇÃO: Typing indicator fix - mostrar markdown E typing quando apropriado */}
                <Show when={msg.role === 'assistant' && msg.type === 'text'}>
                  <div
                    class="markdown-body"
                    innerHTML={renderMarkdown(msg.text + (isStreaming() && msg.id === messages()[messages().length - 1].id ? ' ▍' : ''))}
                  />
                  {/* Typing indicator APENAS quando esperando resposta E texto está vazio */}
                  <Show when={isWaitingForResponse() && msg.id === messages()[messages().length - 1].id && msg.text === ''}>
                    <TypingIndicator />
                  </Show>
                  {/* Status indicator durante streaming */}
                  <Show when={isStreaming() && msg.id === messages()[messages().length - 1].id && currentStatus()}>
                    <div class="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-primary/10 border border-primary/20 text-primary animate-pulse mt-2 w-fit">
                      <div class="w-2 h-2 rounded-full bg-primary animate-ping" />
                      {currentStatus()}
                    </div>
                  </Show>
                </Show>
                <Show when={msg.role === 'user'}>
                  <Show
                    when={editingMessageId() === msg.id}
                    fallback={
                      <div
                        class="markdown-body"
                        innerHTML={renderMarkdown(msg.text)}
                      />
                    }
                  >
                    <div class="space-y-2">
                      <textarea
                        class="input w-full min-h-[80px] resize-y"
                        value={editText()}
                        onInput={(e) => setEditText(e.currentTarget.value)}
                        autofocus
                      />
                      <div class="flex gap-2">
                        <button
                          onClick={() => saveEditedMessage(msg.id)}
                          class="flex items-center gap-1 px-3 py-1 text-sm rounded bg-primary text-primary-foreground hover:opacity-90"
                        >
                          <Check size={14} />
                          <span>Salvar</span>
                        </button>
                        <button
                          onClick={cancelEditMessage}
                          class="flex items-center gap-1 px-3 py-1 text-sm rounded border hover:bg-muted"
                        >
                          <X size={14} />
                          <span>Cancelar</span>
                        </button>
                      </div>
                    </div>
                  </Show>

                  {/* Edit button for user messages */}
                  <Show when={editingMessageId() !== msg.id && !isStreaming()}>
                    <button
                      onClick={() => startEditMessage(msg.id, msg.text)}
                      class="flex items-center gap-1 px-2 py-1 mt-2 text-xs rounded hover:bg-primary/10 transition-colors"
                      title="Editar mensagem"
                    >
                      <Pencil size={12} />
                      <span>Editar</span>
                    </button>
                  </Show>
                </Show>
                <Show when={msg.type === 'error'}>
                  <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                    <div class="flex items-start gap-3">
                      <div class="text-amber-600 dark:text-amber-400 mt-0.5">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <p class="text-sm font-medium text-amber-800 dark:text-amber-200 mb-1">
                          Oops! Algo deu errado
                        </p>
                        <p class="text-sm text-amber-700 dark:text-amber-300">
                          {msg.text}
                        </p>
                      </div>
                    </div>
                  </div>
                </Show>

                {/* Message Actions */}
                <Show when={msg.role === 'assistant' && !isStreaming()}>
                  <MessageActions
                    messageText={msg.text}
                    messageId={msg.id}
                    canRegenerate={index() === messages().length - 1 && lastUserMessage() !== ''}
                    onRegenerate={regenerateLastResponse}
                  />
                </Show>

                <Show when={msg.role === 'assistant' && !isStreaming() && msg.response_id}>
                  <div class="flex items-center space-x-2 mt-2">
                    <FeedbackButtons messageId={msg.response_id!} onFeedback={handleFeedback} />
                    <Show when={msg.data}>
                      <DownloadButton data={msg.data!} filename={`data-${msg.response_id}.json`} />
                    </Show>
                  </div>
                </Show>
                <div class="text-xs text-muted-foreground mt-1">
                  {formatTimestamp(msg.timestamp)}
                </div>
              </div>
            </div>
          )}
        </For>
        <div ref={messagesEndRef} />
      </div>

      <div class="sticky bottom-0 left-0 right-0 px-4 sm:px-6 md:px-8 py-3 sm:py-4 border-t bg-background/95 backdrop-blur-sm pb-safe">
        <form onSubmit={sendMessage} class="flex gap-2 sm:gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            class="input flex-1 text-sm sm:text-base py-2.5 sm:py-3 px-3 sm:px-4"
            value={input()}
            onInput={(e) => setInput(e.currentTarget.value)}
            placeholder="Faça uma pergunta sobre os dados..."
            disabled={isStreaming()}
          />
          <button
            type="submit"
            class="btn btn-primary px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-medium whitespace-nowrap"
            disabled={isStreaming() || !input()}
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
