# 🔍 GAPS IDENTIFICADOS - Melhorias Críticas Faltantes

**Data:** 26/11/2025  
**Fonte:** Context7.com + Pesquisa 2025

---

## ⚠️ GAPS CRÍTICOS ENCONTRADOS

### 1. **Falta de `Last-Event-ID` no SSE (Reconexão Inteligente)**

**Problema:** A TASK atual não implementa `Last-Event-ID` para reconexão SSE.

**Impacto:** Se conexão cair, usuário perde mensagens ou recebe duplicadas.

**Solução:**

**Backend:**
```python
@router.get("/chat/stream")
async def stream_chat(q: str, request: Request):
    # ✅ ADICIONAR: Suporte a Last-Event-ID
    last_event_id = request.headers.get("Last-Event-ID")
    
    async def event_generator():
        event_counter = int(last_event_id) if last_event_id else 0
        
        async for chunk in llm_service.stream_response(q):
            event_counter += 1
            # ✅ Incluir ID em cada evento
            yield f"id: {event_counter}\n"
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        
        yield f"id: {event_counter + 1}\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
```

**Frontend:**
```typescript
// ✅ EventSource automaticamente envia Last-Event-ID
const eventSource = new EventSource(url);

// Reconexão automática com resumo
eventSource.onerror = () => {
  // EventSource reconecta automaticamente
  // e envia Last-Event-ID header
  console.log('Reconectando...');
};
```

**Adicionar na TASK:** Sprint 1, Dia 2

---

### 2. **Falta de React Compiler (`use cache`) - Next.js 16**

**Problema:** TASK não menciona `"use cache"` directive do Next.js 16.

**Impacto:** Perde 30-40% de performance potencial em RSC.

**Solução:**

```typescript
// ✅ ADICIONAR: use cache directive
'use cache';

export default async function DashboardPage() {
  // Esta função será cacheada automaticamente
  const metrics = await fetchMetrics();
  
  return <MetricsCards data={metrics} />;
}
```

**Configuração:**
```typescript
// next.config.ts
export default {
  experimental: {
    dynamicIO: true,  // ✅ Habilitar caching dinâmico
  },
};
```

**Adicionar na TASK:** Sprint 3, Dia 2

---

### 3. **Falta de Prevenção de "Async Waterfalls" em RSC**

**Problema:** TASK não alerta sobre fetches sequenciais (waterfall).

**Impacto:** Queries sequenciais podem adicionar 2-5s de latência.

**Solução:**

**❌ ERRADO (Waterfall):**
```typescript
export default async function Page() {
  const user = await fetchUser();        // 500ms
  const posts = await fetchPosts(user);  // 500ms
  const comments = await fetchComments(posts); // 500ms
  // Total: 1500ms
}
```

**✅ CORRETO (Paralelo):**
```typescript
export default async function Page() {
  const [user, posts, comments] = await Promise.all([
    fetchUser(),
    fetchPosts(),
    fetchComments(),
  ]);
  // Total: 500ms (paralelo)
}
```

**Adicionar na TASK:** Sprint 3, Dia 1 (Seção de avisos)

---

## 📝 OUTRAS MELHORIAS MENORES

### 4. **HTTP/2 Push para SSE**
- Configurar servidor para HTTP/2
- Melhora multiplexing de SSE
- Adicionar em: Sprint 1, Dia 5 (opcional)

### 5. **Gzip Compression para SSE**
```python
# Backend
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
    headers={
        "Content-Encoding": "gzip",  # ✅ Adicionar
    }
)
```

### 6. **React 19 `useOptimistic` para ChatBI**
```typescript
// Feedback instantâneo antes da resposta
const [optimisticMessages, addOptimistic] = useOptimistic(
  messages,
  (state, newMessage) => [...state, newMessage]
);

function sendMessage(text: string) {
  // ✅ UI atualiza instantaneamente
  addOptimistic({ role: 'user', content: text });
  
  // Depois faz request real
  streamChatResponse(text);
}
```

---

## ✅ PRIORIZAÇÃO

### CRÍTICO (Adicionar AGORA):
1. ✅ Last-Event-ID (Sprint 1)
2. ✅ `use cache` directive (Sprint 3)
3. ✅ Prevenção de waterfalls (Sprint 3)

### IMPORTANTE (Adicionar se houver tempo):
4. HTTP/2 para SSE
5. Gzip compression
6. `useOptimistic` hook

---

**Ação:** Atualizar TASK_FRONTEND_OPTIMIZATION.md com estes 3 gaps críticos.
