# Migration Plan – Caçulinha Data Analyzer (removing Streamlit)

## 🎯 Goal
Replace the **Streamlit** UI with a **single FastAPI service** that exposes all existing backend functionality (LLM, data adapter, authentication) and archive every Streamlit‑related artifact. The result is a clean, container‑ready API that can be consumed by any frontend (React, Vue, mobile, etc.).

---
## 📂 Project structure after migration
```
Agent_Solution_BI/
│   README.md                # Updated with FastAPI instructions
│   MIGRATION_PLAN.md        # This detailed plan (you are reading it)
│   caculinha_backend.py     # FastAPI entry point (already created)
│   archive_streamlit.bat    # Script that moves Streamlit files to archive/
│   copy_to_caculinha_agente.bat  # Helper script (unchanged)
│
├─ archive_streamlit/        # <-- all Streamlit UI files go here (history kept)
│   ├─ streamlit_app.py
│   └─ ui/ …
│
├─ core/                     # Existing backend modules (unchanged)
│   ├─ llm_service.py
│   ├─ connectivity/
│   └─ …
│
├─ data/                     # Data sources (Parquet, SQL configs)
│   └─ …
│
└─ tests/                    # Unit / integration tests (reuse existing)
```
---
## 🛠️ Detailed Steps

### 1️⃣ Create FastAPI entry point (already done)
- File: **`caculinha_backend.py`** – provides the following endpoints:
  - `GET /health` – simple health‑check.
  - `POST /auth/login` – forwards to `core.auth.login`.
  - `POST /chat` – forwards prompt to `LLMService`; supports `stream=true` for chunked responses.
  - `GET /data/status` – returns the status of `HybridDataAdapter` (source, fallback, connection health).
  - `GET /session/expired` – checks session expiration via `core.auth`.
- All imports are resolved by adding the project root to `sys.path`.
- Singleton instances (`llm_service`, `data_adapter`) guarantee one‑time initialization and keep the existing caching logic.

### 2️⃣ Archive the old Streamlit UI
Create **`archive_streamlit.bat`** (if not already present) with the following content:
```bat
@echo off
rem ------------------------------------------------------------
rem Move all Streamlit‑related files to an archive folder
rem ------------------------------------------------------------

set "PROJECT_ROOT=%~dp0"
set "ARCHIVE_DIR=%PROJECT_ROOT%archive_streamlit"

rem Create archive folder if it does not exist
if not exist "%ARCHIVE_DIR%" (
    mkdir "%ARCHIVE_DIR%"
)

rem List of items to move – adjust if you add more UI files later
set "ITEMS=streamlit_app.py ui load_optimized_css.css"

for %%I in (%ITEMS%) do (
    if exist "%PROJECT_ROOT%%%I" (
        echo Moving %%I to %ARCHIVE_DIR%
        move "%PROJECT_ROOT%%%I" "%ARCHIVE_DIR%" >nul
    )
)

echo ------------------------------------------------------------
echo Archive completed. Verify %ARCHIVE_DIR%
pause
```
Run the script **once** after confirming the FastAPI service works. It will keep a copy of the UI for historical reference.

### 3️⃣ Install dependencies
```bash
cd C:\Users\André\Documents\Agent_Solution_BI
# FastAPI and uvicorn are already in requirements.txt, but ensure they are installed
pip install -r requirements.txt
```
If you prefer an isolated environment:
```bash
python -m venv .venv
.venv\Scripts\activate   # on Windows
pip install -r requirements.txt
```

### 4️⃣ Run the server locally
```bash
uvicorn caculinha_backend:app --reload
```
- The server starts on `http://127.0.0.1:8000`.
- Swagger UI is automatically available at `http://127.0.0.1:8000/docs` – you can test all endpoints interactively.

### 5️⃣ Verify functionality (manual checklist)
| Check | Command / Action | Expected result |
|-------|------------------|-----------------|
| Health | `curl http://127.0.0.1:8000/health` | `{"status":"ok"}` |
| Auth login | `curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"pwd\"}" http://127.0.0.1:8000/auth/login` | JSON with login status (or 401). |
| Chat (non‑stream) | `curl -X POST -H "Content-Type: application/json" -d "{\"prompt\":\"Qual foi a venda total no último mês?\"}" http://127.0.0.1:8000/chat` | `{"response": "..."}` containing LLM answer. |
| Chat (stream) | `curl -N -X POST -H "Content-Type: application/json" -d "{\"prompt\":\"Mostre o ranking de vendas.\",\"stream\":true}" http://127.0.0.1:8000/chat` | Text chunks printed progressively. |
| Data status | `curl http://127.0.0.1:8000/data/status` | JSON with `current_source`, `sql_available`, etc. |
| Session expired | `curl http://127.0.0.1:8000/session/expired` | `{"expired": false}` (or true). |

Run the existing **pytest** suite to ensure nothing broke:
```bash
pytest tests
```
All tests should pass; if any fail, adjust imports or mock external services accordingly.

### 6️⃣ Update documentation (`README.md`)
Replace the old Streamlit start‑up section with:
```markdown
## Running the API
```bash
uvicorn caculinha_backend:app --reload
```
The API is documented at `http://localhost:8000/docs`.
```
Add a short paragraph explaining that the UI has been archived and that any new frontend should consume the FastAPI endpoints.

### 7️⃣ Optional enhancements (future work)
- **CORS** – add `CORSMiddleware` if the frontend lives on another domain.
- **Response caching** – integrate `fastapi-cache` or `functools.lru_cache` for frequently asked queries.
- **Health‑check extensions** – ping Gemini API key validity and DB connectivity.
- **Dockerisation** – create a `Dockerfile` that copies the project, installs deps, and runs `uvicorn`. Example:
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "caculinha_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```
- **CI/CD** – add a GitHub Actions workflow that runs tests and builds the Docker image on push.

---
## 📦 Deliverables
- `caculinha_backend.py` – FastAPI service (already present).
- `archive_streamlit.bat` – script to move Streamlit files to `archive_streamlit/`.
- Updated `README.md` with FastAPI instructions.
- `MIGRATION_PLAN.md` – this detailed document (now expanded).
- Optional: Dockerfile, GitHub Actions workflow (can be added later).

---
*All Streamlit‑specific code is now safely archived; the project can be deployed as a standard API.*
