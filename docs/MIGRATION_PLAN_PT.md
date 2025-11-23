# Plano de Migração – Caçulinha Data Analyzer (removendo Streamlit)

## 🎯 Objetivo
Substituir a interface **Streamlit** por um **serviço FastAPI único** que exponha todas as funcionalidades existentes do backend (LLM, adaptador de dados, autenticação) e arquivar todos os artefatos relacionados ao Streamlit. O resultado será uma API limpa, pronta para contêiner, consumível por qualquer frontend (React, Vue, mobile, etc.).

---
## 📂 Estrutura do projeto após a migração
```
Agent_Solution_BI/
│   README.md                # Atualizado com instruções do FastAPI
│   MIGRATION_PLAN.md        # Plano detalhado (original em inglês)
│   MIGRATION_PLAN_PT.md     # Plano traduzido (este arquivo)
│   caculinha_backend.py     # Entrada FastAPI (já criada)
│   archive_streamlit.bat    # Script que move arquivos Streamlit para archive/
│   copy_to_caculinha_agente.bat  # Script auxiliar (inalterado)
│
├─ archive_streamlit/        # <-- todos os arquivos UI do Streamlit vão aqui (histórico mantido)
│   ├─ streamlit_app.py
│   └─ ui/ …
│
├─ core/                     # Módulos backend existentes (inalterados)
│   ├─ llm_service.py
│   ├─ connectivity/
│   └─ …
│
├─ data/                     # Fontes de dados (Parquet, configurações SQL)
│   └─ …
│
└─ tests/                    # Testes unitários / de integração (reutilizados)
```
---
## 🛠️ Passos Detalhados

### 1️⃣ Criar entrada FastAPI (já feito)
- Arquivo: **`caculinha_backend.py`** – fornece os seguintes endpoints:
  - `GET /health` – verificação simples de saúde.
  - `POST /auth/login` – encaminha para `core.auth.login`.
  - `POST /chat` – encaminha o prompt para `LLMService`; suporta `stream=true` para respostas em chunks.
  - `GET /data/status` – devolve o status do `HybridDataAdapter` (fonte, fallback, saúde da conexão).
  - `GET /session/expired` – verifica expiração da sessão via `core.auth`.
- Todos os imports são resolvidos adicionando a raiz do projeto ao `sys.path`.
- Instâncias singleton (`llm_service`, `data_adapter`) garantem inicialização única e preservam a lógica de cache existente.

### 2️⃣ Arquivar a UI antiga do Streamlit
Crie **`archive_streamlit.bat`** (se ainda não existir) com o seguinte conteúdo:
```bat
@echo off
rem ------------------------------------------------------------
rem Mover todos os arquivos relacionados ao Streamlit para uma pasta de arquivo
rem ------------------------------------------------------------

set "PROJECT_ROOT=%~dp0"
set "ARCHIVE_DIR=%PROJECT_ROOT%archive_streamlit"

rem Criar pasta de arquivo se não existir
if not exist "%ARCHIVE_DIR%" (
    mkdir "%ARCHIVE_DIR%"
)

rem Lista de itens a mover – ajuste caso adicione mais arquivos UI no futuro
set "ITEMS=streamlit_app.py ui load_optimized_css.css"

for %%I in (%ITEMS%) do (
    if exist "%PROJECT_ROOT%%%I" (
        echo Movendo %%I para %ARCHIVE_DIR%
        move "%PROJECT_ROOT%%%I" "%ARCHIVE_DIR%" >nul
    )
)

echo ------------------------------------------------------------
echo Arquivamento concluído. Verifique %ARCHIVE_DIR%
pause
```
Execute o script **uma única vez** após confirmar que o serviço FastAPI funciona. Ele manterá uma cópia da UI para referência histórica.

### 3️⃣ Instalar dependências
```bash
cd C:\Users\André\Documents\Agent_Solution_BI
# FastAPI e uvicorn já estão no requirements.txt, mas garanta que estejam instalados
pip install -r requirements.txt
```
Caso prefira um ambiente isolado:
```bash
python -m venv .venv
.venv\Scripts\activate   # no Windows
pip install -r requirements.txt
```

### 4️⃣ Executar o servidor localmente
```bash
uvicorn caculinha_backend:app --reload
```
- O servidor inicia em `http://127.0.0.1:8000`.
- A UI Swagger está disponível em `http://127.0.0.1:8000/docs`, permitindo testar interativamente todos os endpoints.

### 5️⃣ Verificar funcionalidade (checklist manual)
| Verificação | Comando / Ação | Resultado esperado |
|-------------|----------------|--------------------|
| Saúde | `curl http://127.0.0.1:8000/health` | `{\"status\":\"ok\"}` |
| Login | `curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"pwd\"}" http://127.0.0.1:8000/auth/login` | JSON com status de login (ou 401) |
| Chat (não‑stream) | `curl -X POST -H "Content-Type: application/json" -d "{\"prompt\":\"Qual foi a venda total no último mês?\"}" http://127.0.0.1:8000/chat` | `{\"response\": \"...\"}` contendo a resposta do LLM |
| Chat (stream) | `curl -N -X POST -H "Content-Type: application/json" -d "{\"prompt\":\"Mostre o ranking de vendas.\",\"stream\":true}" http://127.0.0.1:8000/chat` | Chunks de texto impressos progressivamente |
| Status dos dados | `curl http://127.0.0.1:8000/data/status` | JSON com `current_source`, `sql_available`, etc. |
| Sessão expirada | `curl http://127.0.0.1:8000/session/expired` | `{\"expired\": false}` (ou true) |

Execute a suíte de testes existente (**pytest**) para garantir que nada quebrou:
```bash
pytest tests
```
Todos os testes devem passar; caso algum falhe, ajuste imports ou faça mocks dos serviços externos conforme necessário.

### 6️⃣ Atualizar a documentação (`README.md`)
Substitua a seção antiga de início do Streamlit por:
```markdown
## Executando a API
```bash
uvicorn caculinha_backend:app --reload
```
A API está documentada em `http://localhost:8000/docs`.
```
Adicione um breve parágrafo explicando que a UI foi arquivada e que qualquer novo frontend deve consumir os endpoints FastAPI.

### 7️⃣ Melhorias opcionais (trabalho futuro)
- **CORS** – adicionar `CORSMiddleware` se o frontend estiver em outro domínio.
- **Cache de respostas** – integrar `fastapi-cache` ou `functools.lru_cache` para consultas frequentes.
- **Checks de saúde avançados** – validar a chave Gemini e a conectividade ao banco.
- **Dockerização** – criar um `Dockerfile` que copie o projeto, instale dependências e execute `uvicorn`. Exemplo:
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "caculinha_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```
- **CI/CD** – adicionar workflow GitHub Actions que execute testes e construa a imagem Docker a cada push.

---
## 📦 Entregáveis
- `caculinha_backend.py` – serviço FastAPI (já presente).
- `archive_streamlit.bat` – script que move arquivos Streamlit para `archive_streamlit/`.
- `README.md` atualizado com instruções do FastAPI.
- `MIGRATION_PLAN_PT.md` – este documento detalhado em português.
- Opcional: Dockerfile, workflow GitHub Actions (poderão ser adicionados posteriormente).

---
## 📊 Diagrama de fluxo das mudanças
```mermaid
flowchart TD
    A[Criar FastAPI (caculinha_backend.py)] --> B[Arquivar UI Streamlit (archive_streamlit.bat)]
    B --> C[Instalar dependências]
    C --> D[Executar servidor (uvicorn)]
    D --> E[Verificar endpoints]
    E --> F[Atualizar README]
    F --> G[Melhorias opcionais (CORS, cache, Docker, CI/CD)]
```
---
*Todo o código Streamlit foi arquivado; o projeto está pronto para ser implantado como uma API padrão.*
