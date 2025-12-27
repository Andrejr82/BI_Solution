# Relatório Context7: Análise de Performance do Chat

Este relatório apresenta uma análise técnica da latência percebida no ChatBI, seguindo a metodologia Context7 de diagnóstico e arquitetura.

## 1. Sumário Executivo
A "lentidão" percebida pelo usuário (frequentemente >4 segundos) não se deve a gargalos de processamento de dados, mas sim ao modelo de **execução síncrona e bloqueante** do backend, que não fornece feedback visual durante o processo de raciocínio e execução de ferramentas.

## 2. Diagnóstico Técnico

### 2.1. Bloqueio na Orquestração (`chat.py`)
O endpoint de chat, embora definido como um streaming (`/stream`), executa a lógica do agente de forma atômica e bloqueante:

```python
# backend/app/api/v1/endpoints/chat.py
# Linha ~142
agent_response = await asyncio.to_thread(caculinha_bi_agent.run, ...)
```

O uso de `asyncio.to_thread` em cima do método síncrono `run` faz com que o servidor processe **todo** o ciclo (Pensamento LLM → Execução Ferramenta → Pensamento Final) antes de enviar o primeiro byte de resposta para o frontend.

### 2.2. Ciclo de Vida da Requisição (Onde está o tempo?)
Para uma consulta típica ("Qual a venda de Tecidos?"):

1.  **Request Frontend**: Usuário envia pergunta.
2.  **LLM Call 1 (Router)**: O Gemini analisa a pergunta e decide chamar `consultar_dados_flexivel`. (~1.5s - SILÊNCIO)
3.  **Tool Execution**: O backend carrega o Parquet via DuckDB e filtra. (~0.5s - SILÊNCIO)
4.  **LLM Call 2 (Analysis)**: O Gemini recebe os dados JSON e escreve a resposta final. (~2.0s - SILÊNCIO)
5.  **Response**: O texto final é enviado de uma vez (simulando streaming).

**Tempo Total de "Tela Congelada": ~4.0 segundos.**

### 2.3. Otimização de Dados (DuckDB)
Analisamos o adaptador de dados (`duckdb_adapter.py`) e a ferramenta (`flexible_query_tool.py`). Eles estão **bem otimizados**, utilizando *Predicate Pushdown* para não carregar arquivos inteiros em memória. O problema **não** está na velocidade do banco de dados.

## 3. Recomendações (Plano de Ação)

Para resolver a percepção de lentidão, devemos adotar o padrão **"Streaming Tool Use"**:

### 3.1. Backend: Migrar para `run_async`
O agente `CaculinhaBIAgent` já possui um método `run_async` com suporte a callback `on_progress`.

**Ação Necessária**:
Alterar `chat.py` para usar `run_async` e injetar eventos SSE intermediários:

```python
async def on_progress(event):
    if event["type"] == "tool_progress":
        yield f"data: {json.dumps({'type': 'status', 'text': f'Executando: {event['tool']}...'})}\\n\\n"

await caculinha_bi_agent.run_async(..., on_progress=on_progress)
```

### 3.2. Frontend: Feedback Visual
Atualizar `Chat.tsx` para reagir a eventos do tipo `status`. Em vez de mostrar apenas "Digitando...", mostrar o que o sistema está fazendo ("Consultando estoque...", "Gerando gráfico...").

### 3.3. Streaming Real de Tokens
Atualmente, o texto final é gerado completo e depois "fatiado" para parecer streaming.
**Melhoria**: Integrar streaming nativo do Gemini (parameter `stream=True`) para que o texto comece a aparecer assim que o LLM começar a escrever a resposta final.

## 4. Conclusão
A arquitetura atual é funcional mas peca em UX por ser "caixa preta" durante o processamento. A implementação do feedback de progresso (tool usage streaming) transformará a espera de 5 segundos em uma experiência interativa, eliminando a sensação de travamento.
