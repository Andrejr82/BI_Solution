# Diagrama Visual da Arquitetura do Sistema

Este documento apresenta a visão visual da arquitetura do sistema Agent Solution BI, detalhando os microserviços, agentes e fluxos de dados.

## Visão Geral (C4 Container Diagram)

```mermaid
C4Container
    title Diagrama de Conteîneres - Sistema de BI Agent Solution

    Person(user, "Usuário", "Usuário de Negócios acessando Dashboards")

    Container_Boundary(frontend, "Frontend Logic (SolidJS)") {
        Container(web_app, "Aplicação Web", "SolidJS, Vite, Tailwind", "Interface SPA reativa, Chat UI, Dashboards")
        Container(auth_store, "Auth Store", "Solid Signals", "Gerenciamento de Estado de Sessão")
    }

    Container_Boundary(backend, "Backend Logic (FastAPI)") {
        Container(api, "API Gateway", "FastAPI", "Endpoints REST, SSE para Chat, Auth Middleware")
        
        Container_Boundary(agents, "Sistema de Agentes (Core)") {
            Component(router, "Caculinha BI Agent", "Router Principal", "Interpreta intenção e delega")
            Component(code_gen, "Code Gen Agent", "Especialista Python", "Gera código para análise de dados")
            Component(product_agent, "Product Agent", "Especialista de Produto", "Análise de Mix, Rupturas e Estoque")
            Component(multi_step, "Multi-Step Agent", "Orquestrador", "Resolve tarefas complexas em etapas")
            Component(rag, "RAG System", "FAISS/Embeddings", "Recuperação de Queries e Contexto")
        }

        Container(data_layer, "Hybrid Data Adapter", "Python Class", "Abstração de acesso a dados (SQL/Parquet)")
    }

    System_Ext(gemini, "Google Gemini API", "LLM Service", "Motor de Inteligência (Flash 3.0)")
    
    Container_Boundary(persistence, "Persistência de Dados") {
        SystemDb(supabase, "Supabase", "PostgreSQL", "Autenticação e Perfis")
        SystemDb(sqlserver, "SQL Server", "Relacional", "ERP, Vendas, Estoque (Produção)")
        SystemDb(parquet, "Parquet Files", "Arquivo Local", "Dados Analíticos (Performance/Offline)")
        SystemDb(vector_db, "Vector Store", "FAISS", "Índice de Embeddings para RAG")
    }

    Rel(user, web_app, "Interage", "HTTPS")
    Rel(web_app, api, "Requisições API", "JSON/SSE")
    
    Rel(api, router, "Envia Prompt")
    Rel(router, gemini, "Decide Roteamento")
    
    Rel(router, code_gen, "Delega Análise Ad-hoc")
    Rel(router, product_agent, "Delega Perguntas de Produto")
    Rel(router, multi_step, "Delega Tarefas Complexas")
    
    Rel(code_gen, gemini, "Gera Código")
    Rel(product_agent, gemini, "Analisa Contexto")
    
    Rel(code_gen, data_layer, "Executa Query (Polars)")
    Rel(product_agent, data_layer, "Consulta Dados")
    
    Rel(rag, vector_db, "Busca Similaridade")
    Rel(agents, rag, "Enriquece Contexto")

    Rel(data_layer, supabase, "Auth/User Profile")
    Rel(data_layer, sqlserver, "SQL Queries")
    Rel(data_layer, parquet, "Leitura Otimizada")

    UpdateElementStyle(user, $fontColor="white", $bgColor="#0d6efd", $borderColor="#0d6efd")
    UpdateElementStyle(web_app, $fontColor="white", $bgColor="#198754", $borderColor="#198754")
    UpdateElementStyle(api, $fontColor="white", $bgColor="#dc3545", $borderColor="#dc3545")
    UpdateElementStyle(gemini, $fontColor="white", $bgColor="#6610f2", $borderColor="#6610f2")

```

## Legenda Técnica

### Agentes
*   **Caculinha BI Agent**: O "recepcionista". Recebe a pergunta do usuário, consulta o histórico e decide qual especialista acionar.
*   **Code Gen Agent**: O "engenheiro de dados". Escreve e executa código Python (focado na biblioteca Polars) para responder perguntas inéditas sobre os dados. Possui mecanismo de "Self-Healing" para corrigir erros de código automaticamente.
*   **Product Agent**: O "especialista de varejo". Entende profundamente sobre SKUs, categorias, marcas e problemas específicos como ruptura de estoque. Faz uso de prompts especializados para extrair filtros complexos.
*   **Multi-Step Agent**: O "gerente de projeto". Quebra perguntas complexas (ex: "Compare as vendas de hoje com a média do mês passado e identifique as 3 piores lojas") em sub-tarefas executáveis. Utiliza lógica de grafo (LangGraph) para loops de execução e validação.

### Camada de Dados Híbrida
O sistema opera em modo híbrido para garantir resiliência e performance:
1.  **Parquet**: Usado preferencialmente para consultas analíticas pesadas (OLAP), pois é muito mais rápido que consultas SQL tradicionais para grandes volumes de dados locais.
2.  **SQL Server**: Fonte da verdade (OLTP). Usado quando dados em tempo real são necessários ou para escrita.
3.  **Supabase**: Gerencia identidades, garantindo que usuários só vejam dados permitidos (Row Level Security implementado na aplicação via `DataScopeService`).

### RAG (Retrieval Augmented Generation)
O sistema utiliza embeddings para encontrar perguntas similares feitas no passado. Se um usuário pergunta algo que já foi respondido com sucesso (e o código SQL/Python gerado foi validado), o sistema reutiliza a solução anterior em vez de gerar do zero.
