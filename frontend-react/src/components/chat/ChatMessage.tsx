'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
  messageRef?: React.RefObject<HTMLDivElement | null>;
}

export function ChatMessage({ message, messageRef }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-4 rounded-lg p-4',
        isUser ? 'bg-muted/50' : 'bg-card'
      )}
    >
      {/* Avatar */}
      <Avatar className={cn('h-8 w-8', isUser ? 'bg-blue-600' : 'bg-purple-600')}>
        <AvatarFallback className="text-white">
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      {/* Message content */}
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">
            {isUser ? 'Você' : 'Assistente BI'}
          </span>
          <span className="text-xs text-muted-foreground">
            {message.timestamp.toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        <div className="prose prose-sm max-w-none dark:prose-invert">
          {message.isStreaming ? (
            // Usar ref para updates diretos no DOM durante streaming
            <div ref={messageRef} className="streaming-text whitespace-pre-wrap" />
          ) : (
            // Renderização normal do React após streaming completo
            <ReactMarkdown
              components={{
                code(props) {
                  const { children, className, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      className="rounded-md"
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code
                      className="rounded bg-muted px-1 py-0.5 font-mono text-sm"
                      {...rest}
                    >
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}

          {message.isStreaming && (
            <span className="inline-block h-4 w-1 animate-pulse bg-primary" />
          )}
        </div>
      </div>
    </div>
  );
}
