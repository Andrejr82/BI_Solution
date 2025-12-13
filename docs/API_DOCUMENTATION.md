# Documentação da API - Agent Solution BI

## Visão Geral

A API segue o padrão RESTful e utiliza JSON para troca de dados.
A autenticação é via Bearer Token (JWT).

**Base URL:** `/api/v1`

---

## 🔐 Autenticação

### Login (Token)
- **POST** `/auth/login`
- **Body:** `{"username": "user", "password": "pass"}`
- **Response:** `{"access_token": "...", "token_type": "bearer"}`

### Refresh Token
- **POST** `/auth/refresh`
- **Body:** `{"refresh_token": "..."}`
- **Response:** `{"access_token": "...", "refresh_token": "..."}`

---

## 💬 Chat BI (Agente)

### Chat Streaming (Principal)
- **GET** `/chat/stream`
- **Query Params:**
    - `q`: A pergunta do usuário (URL encoded).
    - `token`: O token de acesso JWT.
- **Response:** Server-Sent Events (SSE).
    - Evento `data`: JSON contendo fragmentos de texto, especificações de gráfico ou tabelas.
    - `{"type": "text", "text": "..."}`
    - `{"type": "chart", "chart_spec": {...}}`
    - `{"type": "table", "data": [...]}`
    - `{"type": "final", "done": true}`

### Enviar Feedback
- **POST** `/chat/feedback`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
    ```json
    {
      "response_id": "id_da_resposta",
      "feedback_type": "positive", // ou "negative"
      "comment": "Opcional"
    }
    ```

---

## 📊 Analytics

### KPIs (Indicadores Chave)
- **GET** `/analytics/kpis`
- **Query Params:** `days` (int, default 7).
- **Response:**
    ```json
    {
      "total_queries": 150,
      "total_errors": 2,
      "success_rate_feedback": 98.5,
      "cache_hit_rate": 45.0,
      "average_response_time_ms": "1200"
    }
    ```

### Tendência de Erros
- **GET** `/analytics/error-trend`
- **Query Params:** `days` (int, default 30).
- **Response:** Lista de objetos `{"date": "YYYY-MM-DD", "error_count": 0}`.

### Top Queries
- **GET** `/analytics/top-queries`
- **Query Params:** `days` (int, default 7), `limit` (int, default 10).
- **Response:** Lista de objetos `{"query": "texto da query", "count": 15}`.

---

## 📦 Transferências (UNE)

### Sugestões Automáticas
- **GET** `/transfers/suggestions`
- **Query Params:** `segmento` (opcional), `limit` (int).
- **Response:** Lista de sugestões de transferência baseadas em risco de ruptura.

### Validar Transferência
- **POST** `/transfers/validate`
- **Body:**
    ```json
    {
      "produto_id": 101,
      "une_origem": 1,
      "une_destino": 2,
      "quantidade": 10
    }
    ```
- **Response:** `{"status": "sucesso", "mensagem": "..."}`

### Criar Solicitação
- **POST** `/transfers`
- **Body:** Mesmo payload da validação.
- **Response:** `{"message": "Criado com sucesso", "transfer_id": "..."}`

### Relatório de Transferências
- **GET** `/transfers/report`
- **Query Params:** `start_date`, `end_date`.
- **Response:** Lista de todas as solicitações de transferência criadas.

---

## ⚠️ Rupturas

### Rupturas Críticas
- **GET** `/rupturas/critical`
- **Query Params:** `limit` (int).
- **Response:** Lista de produtos/UNEs com alto risco de ruptura iminente.
