'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessageMutation = useMutation({
    mutationFn: async (query: string) => {
      // Adicionar mensagem do usuário
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Adicionar mensagem de resposta vazia (para streaming)
      const assistantMessageId = (Date.now() + 1).toString();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Simular streaming (será substituído por API real)
      const response = await apiClient.post<{ response: string }>(
        '/api/chat',
        { query }
      );

      // Atualizar com resposta completa
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, content: response.response, isStreaming: false }
            : msg
        )
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sendMessageMutation.isPending) return;

    sendMessageMutation.mutate(input.trim());
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
              <ChatMessage key={message.id} message={message} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </Card>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua pergunta sobre os dados..."
          disabled={sendMessageMutation.isPending}
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={sendMessageMutation.isPending || !input.trim()}
          size="icon"
        >
          {sendMessageMutation.isPending ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </form>
    </div>
  );
}
