## Prompt para Correção de Bug de Renderização de Gráficos (Chat.tsx)

**Contexto:**
O agente de BI está falhando em exibir gráficos Plotly no frontend. O problema ocorre porque a lógica de processamento de eventos Server-Sent Events (SSE) no componente `Chat.tsx` está sobrescrevendo a propriedade `type` da mensagem, fazendo com que o componente de gráfico seja desmontado imediatamente após a chegada de qualquer chunk de texto subsequente.

**Análise Técnica:**
1.  Quando o backend envia um evento `type: 'chart'`, uma nova mensagem é criada com `type: 'chart'` (linha 273).
2.  O `currentMessageId` é atualizado para o ID desta nova mensagem.
3.  Quando o backend envia o próximo chunk de texto (que pode ser o texto final ou um espaço), o bloco `if (data.type === 'text')` é executado.
4.  Neste bloco, a propriedade `type` da mensagem é **hardcoded** para `'text'` (linha 261), sobrescrevendo o `type: 'chart'`.
5.  A condição de renderização do gráfico (`msg.type === 'chart'`) falha, e o gráfico desaparece.

**Arquivo a ser Corrigido:**
`frontend-solid/src/pages/Chat.tsx`

**Correção Proposta (Diff):**

O bloco de código a ser corrigido está em torno da linha 257, dentro da função `processUserMessage`.

```typescript
// Linhas 257-264 - CÓDIGO ATUAL COM BUG
          if (data.type === 'text') {
            setMessages(prev => prev.map(msg => {
              if (msg.id === currentMessageId) {
                const newText = msg.text + data.text;
                fullResponseContent = newText;
                return { ...msg, text: newText, type: 'text' }; // <-- BUG: Hardcoded 'type: "text"'
              }
              return msg;
            }));
          }

// Linhas 257-264 - CÓDIGO CORRIGIDO
          if (data.type === 'text') {
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
          }
```

**Instrução para o Agente:**
"Aplique a correção no arquivo `frontend-solid/src/pages/Chat.tsx` removendo a atribuição hardcoded `type: 'text'` dentro do bloco `if (data.type === 'text')` para garantir que mensagens de gráfico (`type: 'chart'`) e tabela (`type: 'table'`) preservem seu tipo ao receberem chunks de texto subsequentes."

**Recomendação Adicional (Opcional):**
Verificar se o `PlotlyChart.tsx` está usando `createEffect` com a dependência correta para garantir que o gráfico seja renderizado quando o `chartSpec` for atualizado. O uso de `chartSpec={() => msg.chart_spec}` em `Chat.tsx` e `createEffect(renderPlot)` em `PlotlyChart.tsx` (onde `renderPlot` depende de `props.chartSpec()`) sugere que a reatividade está correta, mas a correção do `type` é o problema principal.

---
**Prompt Final:**
```
No arquivo 'frontend-solid/src/pages/Chat.tsx', o processamento de eventos SSE está com um bug que impede a renderização de gráficos. Na função 'processUserMessage', dentro do 'eventSource.onmessage', o bloco 'if (data.type === 'text')' sobrescreve o tipo da mensagem para 'text' (linha 261), mesmo que a mensagem seja um gráfico ('chart').

**Ação:** Remova a atribuição hardcoded 'type: 'text'' na linha 261 para que o tipo original da mensagem (e.g., 'chart') seja preservado, permitindo que o componente PlotlyChart seja renderizado corretamente.

Código a ser alterado (aproximadamente linha 261):
De:
return { ...msg, text: newText, type: 'text' };

Para:
return { ...msg, text: newText };
```
