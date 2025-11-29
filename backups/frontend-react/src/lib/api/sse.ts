/**
 * SSE Helper para EventSource
 * Gerencia conexões Server-Sent Events com reconexão automática
 */

export interface SSEOptions {
  onMessage: (data: any) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export function createSSEConnection(
  url: string,
  options: SSEOptions
): () => void {
  console.log('[SSE] Creating connection to:', url);
  
  const eventSource = new EventSource(url);
  let messageCount = 0;
  
  eventSource.onopen = () => {
    console.log('[SSE] Connection opened successfully');
  };
  
  eventSource.onmessage = (event) => {
    messageCount++;
    console.log(`[SSE] Message #${messageCount} received:`, event.data);
    
    try {
      const data = JSON.parse(event.data);
      
      if (data.error) {
        console.error('[SSE] Error in data:', data.error);
        options.onError?.(new Error(data.error));
        eventSource.close();
        return;
      }
      
      if (data.done) {
        console.log('[SSE] Stream completed, closing connection');
        options.onComplete?.();
        eventSource.close();
        return;
      }
      
      options.onMessage(data);
    } catch (error) {
      console.error('[SSE] Parse error:', error);
      options.onError?.(error as Error);
      eventSource.close();
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('[SSE] Connection error:', error);
    console.error('[SSE] ReadyState:', eventSource.readyState);
    console.error('[SSE] URL:', url);
    
    // Verificar se recebeu alguma mensagem antes do erro
    if (messageCount === 0) {
      console.error('[SSE] No messages received before error - possible auth or network issue');
    }
    
    options.onError?.(new Error('SSE connection failed'));
    eventSource.close();
  };
  
  // Retornar função de cleanup
  return () => {
    console.log('[SSE] Cleanup called, closing connection');
    eventSource.close();
  };
}
