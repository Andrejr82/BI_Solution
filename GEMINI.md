# Agent Solution BI - Lojas Caçula (Context7 Edition)

This `GEMINI.md` file provides essential context for the "Agent Solution BI" project, a high-performance Business Intelligence platform integrated with Generative AI (Google Gemini).

## 🌍 Project Overview

**Agent Solution BI** is a strategic decision platform designed for retail management (Lojas Caçula). It transforms millions of sales and inventory records into immediate action plans using a hybrid architecture of Generative AI and columnar data processing.

### Key Technologies
*   **AI/LLM:** Google Gemini 2.5 Flash-Lite (Primary), Llama-3 (Secondary/Groq).
*   **Backend:** Python 3.11+, FastAPI.
*   **Data Engine:** DuckDB 1.1+ (Analytical SQL), Polars (DataFrames), Apache Parquet (Storage).
*   **Frontend:** SolidJS (Reactive UI), Tailwind CSS.
*   **Architecture:** Hybrid (SQL Server + Parquet Fallback), RAG (Retrieval-Augmented Generation).

### Core Features
*   **Conversational BI:** Natural language queries ("How are sales in store 1685?").
*   **Context7 Ultimate:** Advanced system prompt framework for natural, narrative-driven data storytelling (no raw JSON output).
*   **Self-Aware Data Agent:** Dynamic schema injection allowing the LLM to inspect available columns at runtime.
*   **Universal Charting:** `gerar_grafico_universal_v2` tool for on-demand visualization.

## 📂 Directory Structure

```text
C:\Agente_BI\BI_Solution\
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/              # API Endpoints (v1)
│   │   ├── core/             # Core Logic (Agents, Tools, Config)
│   │   │   ├── agents/       # AI Agents (CaculinhaBIAgent, MasterPrompt)
│   │   │   └── tools/        # BI Tools (Charts, Data Query)
│   │   └── services/         # Business Services
│   ├── data/                 # Data Storage (Parquet, Cache)
│   ├── main.py               # Application Entry Point
│   └── .env                  # Environment Variables (API Keys, Config)
├── frontend-solid/           # SolidJS Frontend
│   ├── src/                  # Source Code
│   ├── package.json          # Dependencies
│   └── vite.config.ts        # Build Configuration
├── docs/                     # Project Documentation
├── scripts/                  # Utility Scripts
├── START_LOCAL_DEV.bat       # Windows Local Start Script
└── README.md                 # Project Overview
```

## 🚀 Building and Running

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   Google Gemini API Key (configured in `backend/.env`)

### Local Development (Windows)
The recommended way to start the project without Docker is using the batch script:

```bat
START_LOCAL_DEV.bat
```

**Manual Start:**

1.  **Backend:**
    ```bash
    cd backend
    # Ensure venv is active if used
    python main.py
    ```
    *Runs on:* `http://localhost:8000` (Docs: `/docs`)

2.  **Frontend:**
    ```bash
    cd frontend-solid
    npm install  # First time only
    npm run dev
    ```
    *Runs on:* `http://localhost:3000`

## 🛠️ Development Conventions

### AI & Prompt Engineering
*   **System Prompt:** Located in `backend/app/core/agents/master_prompt.py`. It follows the "Context7 Ultimate" standard.
*   **Context7 Rules:**
    1.  **Narrative First:** Responses must be natural text, not raw data dumps.
    2.  **No JSON:** Never expose JSON structures to the end-user.
    3.  **Visuals:** Prioritize chart generation (`gerar_grafico_universal_v2`) for visual requests.
    4.  **Self-Correction:** Use `consultar_dicionario_dados` if unsure about the schema.

### Backend (Python)
*   **Style:** Follows PEP 8.
*   **Dependency Management:** `backend/requirements.txt`.
*   **Testing:** `pytest` is used. Key tests are in `backend/tests/` and `backend/verify_gemini_env.py`.

### Frontend (SolidJS)
*   **State Management:** Solid Signals and Stores.
*   **Styling:** Tailwind CSS.

## 🔑 Key Configuration Files
*   `backend/.env`: Critical configuration (LLM provider, API keys, database paths).
*   `backend/app/core/agents/master_prompt.py`: The "brain" of the agent (System Prompt).
*   `backend/app/core/agents/caculinha_bi_agent.py`: Agent logic and tool binding.

## 📝 Recent Context & Updates
*   **LLM Model:** Updated to `gemini-2.5-flash-lite`.
*   **Authentication:** Fixed API Key issues in `.env`.
*   **Prompting:** Updated `master_prompt.py` to "Context7 Ultimate".
*   **Tooling:** Validated connection with `backend/verify_gemini_env.py`.
