"""
SSE Helper para EventSource
Gerencia conexões Server-Sent Events com reconexão automática
"""

export interface SSEOptions {
  onMessage: (data: any) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export function createSSEConnection(
  url: string,
  options: SSEOptions
): () => void {
  const eventSource = new EventSource(url);
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.error) {
        options.onError?.(new Error(data.error));
        eventSource.close();
        return;
      }
      
      if (data.done) {
        options.onComplete?.();
        eventSource.close();
        return;
      }
      
      options.onMessage(data);
    } catch (error) {
      options.onError?.(error as Error);
    }
  };
  
  eventSource.onerror = () => {
    options.onError?.(new Error('SSE connection failed'));
    eventSource.close();
  };
  
  // Retornar função de cleanup
  return () => eventSource.close();
}
