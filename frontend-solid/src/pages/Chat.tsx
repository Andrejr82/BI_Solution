import { createSignal, createEffect, onCleanup, onMount, For, Show } from 'solid-js';
import auth from '@/store/auth';
import { Typewriter, TypingIndicator } from '@/components';
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

// Configurar marked para renderizar tabelas corretamente
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown (suporta tabelas)
  breaks: true, // Quebras de linha automáticas
});

// Helper para renderizar Markdown
const renderMarkdown = (text: string): string => {
  try {
    return marked.parse(text) as string;
  } catch (e) {
    console.error('Erro ao renderizar Markdown:', e);
    return text;
  }
};

// Interface para mensagem - Atualizada para suportar estrutura JSON do backend
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
  timestamp: number;
  type?: 'text' | 'chart' | 'table' | 'final' | 'error'; // Tipo da resposta do assistente
  chart_spec?: any; // Especificação JSON do Plotly
  data?: any[]; // Dados tabulares
  response_id?: string; // ID da resposta para feedback
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
  let messagesEndRef: HTMLDivElement | undefined;

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

  // Auto-scroll - melhorado para garantir que sempre role até o final
  createEffect(() => {
    messages(); // Re-run effect when messages change

    // Usar setTimeout para garantir que o DOM foi atualizado
    setTimeout(() => {
      if (messagesEndRef) {
        messagesEndRef.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    }, 100);
  });

  // Cleanup on unmount
  onCleanup(() => {
    const es = currentEventSource();
    if (es) {
      es.close();
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

    // Prepara mensagem do assistente - agora com suporte a tipos e dados
    const assistantId = (Date.now() + 1).toString();
    const newMessage: Message = { id: assistantId, role: 'assistant', text: '', timestamp: Date.now(), type: 'text' };
    setMessages(prev => [...prev, newMessage]);

    try {
      // Conexão SSE Real com Backend
      console.log('📡 Iniciando SSE com token:', token.substring(0, 20) + '...', 'Session:', sessionId());
      const eventSource = new EventSource(`/api/v1/chat/stream?q=${encodeURIComponent(userText)}&token=${encodeURIComponent(token)}&session_id=${sessionId()}`);
      setCurrentEventSource(eventSource);

      let fullResponseContent = ''; // Para acumular texto e gerar response_id
      let currentMessageId = assistantId;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Desativa o indicador assim que receber qualquer dado
          if (isWaitingForResponse()) {
            setIsWaitingForResponse(false);
          }

          if (data.done) {
            console.log('✅ Stream concluído');
            eventSource.close();
            setCurrentEventSource(null);
            setIsStreaming(false);
            setIsWaitingForResponse(false);
            // Finaliza a mensagem do assistente, adicionando o response_id
            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, response_id: fullResponseContent ? btoa(fullResponseContent).substring(0, 16) : undefined } : msg
            ));
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
            const statusMsg = statusMap[data.tool] || `Executando: ${data.tool}...`;
            setCurrentStatus(statusMsg);
          } else if (data.type === 'text') {
            setCurrentStatus(''); // Limpa status ao começar a receber texto
            setMessages(prev => prev.map(msg => {
              if (msg.id === currentMessageId) {
                const newText = msg.text + data.text;
                fullResponseContent = newText;
                // CORREÇÃO CRÍTICA: Não sobrescrever o 'type' da mensagem.
                // Se a mensagem já é um 'chart' ou 'table', o tipo deve ser preservado.
                return { ...msg, text: newText };
              }
              return msg;
            }));
          } else if (data.type === 'chart' && data.chart_spec) {
            // Adiciona um novo bloco de mensagem para o gráfico
            const chartMsgId = (Date.now() + 2).toString();
            setMessages(prev => [...prev, {
              id: chartMsgId,
              role: 'assistant',
              text: 'Aqui está o gráfico que você pediu:',
              timestamp: Date.now(),
              type: 'chart',
              chart_spec: data.chart_spec,
              response_id: btoa(JSON.stringify(data.chart_spec)).substring(0, 16) // ID baseado no spec do gráfico
            }]);
            currentMessageId = chartMsgId; // O feedback será para este novo elemento
          } else if (data.type === 'table' && data.data) {
            // Adiciona um novo bloco de mensagem para a tabela
            const tableMsgId = (Date.now() + 3).toString();
            setMessages(prev => [...prev, {
              id: tableMsgId,
              role: 'assistant',
              text: 'Aqui estão os dados tabulares:',
              timestamp: Date.now(),
              type: 'table',
              data: data.data,
              response_id: btoa(JSON.stringify(data.data)).substring(0, 16) // ID baseado nos dados
            }]);
            currentMessageId = tableMsgId; // O feedback será para este novo elemento
          }
          else if (data.type === 'final' && data.text) {
            // Tratamento para mensagem final, se houver
            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, text: msg.text + data.text, type: 'text' } : msg
            ));
          }

          if (data.error) {
            console.error('❌ Erro do servidor:', data.error);
            setMessages(prev => prev.map(msg =>
              msg.id === currentMessageId ? { ...msg, text: msg.text + "\n[Erro: " + (data.details ? JSON.stringify(data.details) : data.error) + "]", type: 'error' } : msg
            ));
            eventSource.close();
            setCurrentEventSource(null);
            setIsStreaming(false);
            setIsWaitingForResponse(false);
          }

        } catch (err) {
          console.error("❌ SSE Parse Error", err);
        }
      };

      eventSource.onerror = (err) => {
        console.error("❌ EventSource failed:", err);
        eventSource.close();
        setCurrentEventSource(null);
        setIsStreaming(false);
        setIsWaitingForResponse(false);
        setCurrentStatus('');
        setMessages(prev => prev.map(msg =>
          msg.id === currentMessageId ? { ...msg, text: msg.text + "\n⚠️ Erro de conexão com o servidor.", type: 'error' } : msg
        ));
      };

    } catch (err) {
      console.error("❌ Chat error:", err);
      setIsStreaming(false);
      setIsWaitingForResponse(false);
      setMessages(prev => prev.map(msg =>
        msg.id === assistantId ? { ...msg, text: "\n❌ Erro ao processar mensagem.", type: 'error' } : msg
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
      {/* Header with actions */}
      <div class="flex items-center justify-between px-6 py-4 border-b bg-background/50 backdrop-blur">
        <h2 class="text-lg font-semibold">Chat BI</h2>
        <div class="flex items-center gap-2">
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

      <div class="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        <For each={messages()}>
          {(msg, index) => (
            <div class={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                class={`max-w-[90%] rounded-lg p-4 text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                  ? 'bg-primary/10 border border-primary/20 text-foreground'
                  : 'bg-card border text-card-foreground'
                  }`}
              >
                <Show when={msg.role === 'assistant' && msg.type === 'chart' && msg.chart_spec}>
                  <PlotlyChart chartSpec={() => msg.chart_spec} />
                </Show>
                <Show when={msg.role === 'assistant' && msg.type === 'table' && msg.data}>
                  <DataTable data={() => msg.data} caption={msg.text} />
                </Show>
                <Show when={msg.role === 'assistant' && msg.type === 'text'}>
                  <Show
                    when={isWaitingForResponse() && msg.id === messages()[messages().length - 1].id}
                    fallback={
                      <div
                        class="markdown-body"
                        innerHTML={renderMarkdown(msg.text + (isStreaming() && msg.id === messages()[messages().length - 1].id ? ' ▍' : ''))}
                      />
                    }
                  >
                    <div class="flex flex-col gap-2">
                      <Show when={currentStatus()}>
                        <div class="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-primary/10 border border-primary/20 text-primary animate-pulse mb-2">
                          <div class="w-2 h-2 rounded-full bg-primary animate-ping" />
                          {currentStatus()}
                        </div>
                      </Show>
                      <TypingIndicator />
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
                  <span class="text-red-500 font-bold whitespace-pre-wrap">{msg.text}</span>
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

      <div class="px-8 py-4 border-t bg-background/50 backdrop-blur">
        <form onSubmit={sendMessage} class="flex gap-3">
          <input
            type="text"
            class="input flex-1 text-base py-3"
            value={input()}
            onInput={(e) => setInput(e.currentTarget.value)}
            placeholder="Faça uma pergunta sobre os dados..."
            disabled={isStreaming()}
          />
          <button type="submit" class="btn btn-primary px-6 py-3 text-base font-medium" disabled={isStreaming() || !input()}>
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
