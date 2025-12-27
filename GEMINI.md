# Agent Solution BI Project Overview

This document provides an overview of the Agent Solution BI project. It reflects the current system status as of December 2025, following a migration to SolidJS and a modernized build system.

## Project Purpose

The Agent Solution BI project is a full-stack application that provides a conversational Business Intelligence interface powered by Gemini technology. It allows users to interact with analytical datasets using natural language queries, receiving responses and data visualizations.

## Technologies Used

*   **Frontend**: SolidJS with Vite and TailwindCSS (located in `frontend-solid`).
*   **Backend**: FastAPI with Python 3.11+.
*   **Database/Storage**:
    *   **Authentication**: Hybrid system using Supabase (primary) with a Parquet file fallback (`users.parquet`) for local/offline development.
    *   **Business Data**: SQL Server (structured data) and Parquet files (analytical data).
*   **Language Model**: Google Gemini 3.0 Flash.
*   **Orchestration**: Node.js scripts (`npm run dev`) and `concurrently` for managing processes.

## Architecture

The project follows a full-stack architecture:
*   **Frontend (`frontend-solid`)**: Built with SolidJS for high performance. It communicates with the backend via REST API calls.
*   **Backend (`backend`)**: A FastAPI application handling business logic, data processing, and LLM integration. It supports a "lazy loading" architecture to prevent crashes if external services (like Supabase or SQL Server) are unavailable.
*   **Data Layer**:
    *   **SQL Server**: Used for production data (can be disabled via `USE_SQL_SERVER=false`).
    *   **Parquet**: Used for high-performance analytical data and as a fallback for authentication.
    *   **Supabase**: Managed service for authentication and user profiles.

## Development Environment Setup

### Prerequisites

*   **Python**: 3.11+
*   **Node.js**: 18+ (20+ recommended)
*   **Package Managers**: `npm` and `pnpm` (for frontend).

### Initial Setup

1.  **Install Root Dependencies:**
    ```bash
    npm install
    ```

2.  **Environment Configuration:**
    *   Ensure `backend/.env` exists (created automatically by validation scripts if missing).
    *   **Critical**: Add your `GEMINI_API_KEY` to `backend/.env`.

3.  **Install Sub-project Dependencies:**
    ```bash
    # Installs both backend (pip) and frontend (pnpm) dependencies
    npm run install
    ```
    *Alternatively:*
    *   Backend: `npm run install:backend`
    *   Frontend: `npm run install:frontend`

## Building and Running the Application

The project now uses standard `npm` scripts for orchestration.

### Start All Services (Recommended)
```bash
npm run dev
```
This command:
1.  Cleans ports 8000 and 3000.
2.  Starts the FastAPI backend (port 8000).
3.  Starts the SolidJS frontend (port 3000).
4.  Displays combined logs in the terminal.

### Start Individually
*   **Backend only**: `npm run dev:backend`
*   **Frontend only**: `npm run dev:frontend`

### Other Useful Commands
*   **Clean Ports**: `npm run clean:ports` (Kills processes on 8000/3000)
*   **Health Check**: `curl http://localhost:8000/health`

## Documentation References

For detailed information, refer to:
*   **`README_NEW_SYSTEM.md`**: Quick start guide and system overview.
*   **`MIGRATION_GUIDE.md`**: Details on the migration from `run.py`/React to `npm`/SolidJS.
*   **`SYSTEM_STATUS.md`**: Current operational status and certification.

## Development Conventions

*   **Frontend**: SolidJS components, TailwindCSS for styling.
*   **Backend**: Python FastAPI, strictly typed (Pydantic).
*   **Testing**:
    *   Backend: `pytest` (in `backend/tests`).
    *   Frontend: `vitest` (configured in `frontend-solid`).