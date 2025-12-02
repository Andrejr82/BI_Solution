import { createSignal, createEffect, onCleanup, For } from 'solid-js';
import auth from '@/store/auth';
import { Typewriter } from '@/components';

// Interface para mensagem
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
  timestamp: number;
}

export default function Chat() {
  const [messages, setMessages] = createSignal<Message[]>([
    { id: '0', role: 'assistant', text: 'Olá! Sou seu assistente de BI. Pergunte sobre vendas, produtos ou estoque.', timestamp: Date.now() }
  ]);
  const [input, setInput] = createSignal('');
  const [isStreaming, setIsStreaming] = createSignal(false);
  let messagesEndRef: HTMLDivElement | undefined;

  // Auto-scroll
  createEffect(() => {
    messages();
    if (messagesEndRef) {
      messagesEndRef.scrollIntoView({ behavior: 'smooth' });
    }
  });

  const sendMessage = async (e: Event) => {
    e.preventDefault();
    if (!input() || isStreaming()) return;

    const userText = input();
    setInput('');
    
    // Validar autenticação
    const token = auth.token();
    if (!token) {
      console.error('❌ Token não encontrado');
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: 'assistant', 
        text: '[Erro: Você não está autenticado. Por favor, faça login novamente.]', 
        timestamp: Date.now() 
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }
    
    // Adiciona mensagem do usuário
    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: userText, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setIsStreaming(true);

    // Prepara mensagem do assistente
    const assistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', text: '', timestamp: Date.now() }]);

    try {
      // Conexão SSE Real com Backend
      console.log('📡 Iniciando SSE com token:', token.substring(0, 20) + '...');
      const eventSource = new EventSource(`/api/v1/chat/stream?q=${encodeURIComponent(userText)}&token=${token}`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.done) {
            console.log('✅ Stream concluído');
            eventSource.close();
            setIsStreaming(false);
            return;
          }

          if (data.text) {
            setMessages(prev => prev.map(msg => 
              msg.id === assistantId ? { ...msg, text: msg.text + data.text } : msg
            ));
          }
          
          if (data.error) {
            console.error('❌ Erro do servidor:', data.error);
            setMessages(prev => prev.map(msg => 
              msg.id === assistantId ? { ...msg, text: msg.text + "\n[Erro: " + data.error + "]" } : msg
            ));
            eventSource.close();
            setIsStreaming(false);
          }

        } catch (err) {
          console.error("❌ SSE Parse Error", err);
        }
      };

      eventSource.onerror = (err) => {
        console.error("❌ EventSource failed:", err);
        eventSource.close();
        setIsStreaming(false);
        setMessages(prev => prev.map(msg => 
           msg.id === assistantId ? { ...msg, text: msg.text + "\n⚠️ Erro de conexão com o servidor." } : msg
        ));
      };

    } catch (err) {
      console.error("❌ Chat error:", err);
      setIsStreaming(false);
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId ? { ...msg, text: "\n❌ Erro ao processar mensagem." } : msg
      ));
    }
  };

  return (
    <div class="flex flex-col h-full max-w-4xl mx-auto">
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <For each={messages()}>
          {(msg) => (
            <div class={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                class={`max-w-[80%] rounded-lg p-4 text-sm leading-relaxed shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card border text-card-foreground'
                }`}
              >
                {/* Usar Typewriter apenas para mensagens do assistente que estão sendo recebidas */}
                {msg.role === 'assistant' && isStreaming() && msg.id === messages()[messages().length - 1].id ? (
                  <Typewriter
                    text={msg.text}
                    speed={15}
                  />
                ) : (
                  <span style={{"white-space": "pre-wrap"}}>{msg.text}</span>
                )}
              </div>
            </div>
          )}
        </For>
        <div ref={messagesEndRef} />
      </div>

      <div class="p-4 border-t bg-background/50 backdrop-blur">
        <form onSubmit={sendMessage} class="flex gap-2">
          <input
            type="text"
            class="input flex-1"
            value={input()}
            onInput={(e) => setInput(e.currentTarget.value)}
            placeholder="Faça uma pergunta sobre os dados..."
            disabled={isStreaming()}
          />
          <button type="submit" class="btn btn-primary" disabled={isStreaming() || !input()}>
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
