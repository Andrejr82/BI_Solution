'use client';

import { useState, useRef, useEffect } from 'react';
import { createSSEConnection } from '@/lib/api/sse';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Loader2 } from 'lucide-react';
import { ChatMessage } from '@/components/chat/ChatMessage';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentMessageRef = useRef<HTMLDivElement>(null);
  const cleanupRef = useRef<(() => void) | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);

  const sendMessage = (query: string) => {
    if (isStreaming) return;

    // Adicionar mensagem do usuário
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Criar mensagem vazia para streaming
    const assistantId = crypto.randomUUID();
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    setIsStreaming(true);
    let buffer = '';
    let lastUpdate = Date.now();

    // Conectar SSE
    const cleanup = createSSEConnection(
      `/api/v1/chat/stream?q=${encodeURIComponent(query)}`,
      {
        onMessage: (data) => {
          buffer += data.text;

          // Atualizar DOM diretamente (performance)
          const now = Date.now();
          if (now - lastUpdate > 50) {
            // Throttle: 50ms
            if (currentMessageRef.current) {
              currentMessageRef.current.textContent = buffer;
            }
            lastUpdate = now;
          }
        },
        onComplete: () => {
          // Sincronizar com React state
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, content: buffer, isStreaming: false }
                : msg
            )
          );
          setIsStreaming(false);
          cleanupRef.current = null;
        },
        onError: (error) => {
          console.error('SSE Error:', error);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? {
                    ...msg,
                    content: `❌ Erro: ${error.message}`,
                    isStreaming: false,
                  }
                : msg
            )
          );
          setIsStreaming(false);
        },
      }
    );

    cleanupRef.current = cleanup;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    sendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Chat BI com IA</h1>
        <p className="text-muted-foreground">
          Faça perguntas sobre seus dados em linguagem natural
        </p>
      </div>

      {/* Messages area */}
      <Card className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center">
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  Bem-vindo ao Chat BI! 👋
                </p>
                <p className="text-sm text-muted-foreground">
                  Comece fazendo uma pergunta sobre seus dados
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                messageRef={
                  message.isStreaming ? currentMessageRef : undefined
                }
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </Card>

      {/* Indicador de streaming */}
      {isStreaming && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>IA está digitando...</span>
        </div>
      )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua pergunta sobre os dados..."
          disabled={isStreaming}
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={isStreaming || !input.trim()}
          size="icon"
        >
          {isStreaming ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </form>
    </div>
  );
}
