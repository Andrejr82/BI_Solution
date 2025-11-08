## Instruções rápidas para agentes de código (Copilot/AI)

Siga estas diretrizes específicas do repositório Agent_Solution_BI para ser produtivo rapidamente.

- Contexto rápido: este projeto é uma plataforma BI conversacional (Python 3.11+) com 3 interfaces (React, Streamlit e FastAPI). O backend principal está em `core/` e usa LangGraph para orquestração de workflows e adaptadores LLM em `core/llm_adapter.py`.

- Entradas/saídas esperadas: as interações do usuário viram mensagens LangChain → LangGraph orquestra nodes (ex.: `classify_intent`, `generate_parquet_query`, `execute_query`, `generate_plotly_spec`) → respostas formatadas (JSON + `plotly_spec`/`plotly_fig`). Veja `core/agent_state.py` para o shape do estado.

- Comandos úteis (Windows):
  - Criar/ativar venv: `python -m venv .venv` e ` .venv\Scripts\activate`
  - Instalar deps: `pip install -r requirements.txt`
  - Streamlit (dev/demo): `streamlit run streamlit_app.py` (entrada principal para protótipos)
  - API FastAPI: `uvicorn main:app --reload` ou `python main.py` (documentação em `/docs`)
  - Testes: `pytest` (config em `pytest.ini`)

- Padrões do projeto que o agente deve respeitar:
  - Use `ComponentFactory.get_llm_adapter()` / `ComponentFactory` para criar/adquirir adaptadores LLM (fallback automático Gemini → DeepSeek). Não instancie clientes LLM diretamente quando já houver factory.
  - Cache de respostas: `ResponseCache` é usado com TTL aumentado (6h). Ao propor mudanças, preserve o pattern de cache e o parâmetro `cache_context` usado em `core/llm_adapter.py`.
  - Lazy loading: imports pesados e configurações são carregados sob demanda; mantenha essa estratégia para reduzir tempo de inicialização e problemas em cloud.
  - Acesso a dados: use `ParquetAdapter`/`DirectQueryEngine`/`HybridQueryEngine` em `core/connectivity/` em vez de consultas ad-hoc dispersas.

- Tratamento de erros e fallback: observe os mecanismos de fallback implementados em `core/llm_adapter.py` (detecção de rate/quota e chamada a `ComponentFactory.set_gemini_unavailable(True)`). Ao alterar fluxos LLM, preserve a lógica de fallback e logging.

- Onde procurar exemplos concretos:
  - Fluxos LangGraph: `core/graph/` (nó `generate_parquet_query`, `execute_query`, `generate_plotly_spec`)
  - UI Streamlit: `streamlit_app.py` (estilo CSS, sessão, limpeza de cache automática)
  - Integração LLM: `core/llm_adapter.py` e `core/llm_base.py`
  - Estado do agente: `core/agent_state.py` (TypedDict com campos `messages`, `sql_query`, `plotly_spec`, `final_response`)

- Convenções de contribuição e estilo:
  - Seguir PEP8; projeto usa `ruff`/`black` no CI (ver `docs/` se necessário)
  - Testes unitários e mocks para adaptadores LLM e engines de consulta (persistência em `data/` para testes)

- Notas práticas ao gerar código:
  - Ao elaborar prompts ou mudanças de pré/ pós-processamento, cite os arquivos de template em `data/` (`data/*.json`) e preserve o formato de saída que alimenta `plotly_spec`.
  - Quando propor mudanças no cache, documente impacto em `core/utils/response_cache.py` e atualize TTLs com justificativa de custo/latência.

Se algo estiver faltando ou ambiguidades aparecerem (por exemplo, qual entrypoint FastAPI usar: `main.py` vs `api_server.py`), pergunte qual interface o time quer priorizar (Streamlit vs API vs React). Obrigado — me diga se prefere instruções mais curtas ou incluir exemplos de patches/PRs.
