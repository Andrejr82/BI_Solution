# Agent Solution BI Project Overview

This document provides an overview of the Agent Solution BI project, its architecture, how to set up the development environment, and how to build/run the application.

## Project Purpose

The Agent Solution BI project is a full-stack application that provides a conversational Business Intelligence interface powered by Gemini technology. It allows users to interact with analytical datasets using natural language queries, receiving responses and data visualizations.

## Technologies Used

*   **Frontend**: React (Next.js) with TypeScript, using Axios for API communication.
*   **Backend**: FastAPI with Python, Pydantic for data validation, and SQLAlchemy for database interaction.
*   **Database**: SQL Server for authentication and metadata, and Parquet files for main analytical data.
*   **Language Model**: Google Gemini 2.5 Flash.

## Architecture

The project follows a full-stack architecture with a clear separation of concerns:
*   **Frontend**: Built with React (Next.js), responsible for the user interface and interaction. It communicates with the backend via REST API calls.
*   **Backend**: Implemented using FastAPI, handling business logic, data processing, database interactions, and integration with the Gemini language model.
*   **Data Storage**: Utilizes SQL Server for structured data (authentication, metadata) and Parquet files for high-performance analytical data.

## Development Environment Setup

### Prerequisites

*   Python 3.11+
*   Node.js 20+
*   SQL Server with the "ODBC Driver 17 for SQL Server" installed.

### Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage backend dependencies.

1.  **Create the virtual environment:**
    ```bash
    python -m venv .venv
    ```
2.  **Activate the virtual environment:**
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **macOS and Linux:**
        ```bash
        source .venv/bin/activate
        ```

### Dependency Installation

1.  **Backend Dependencies:**
    With the virtual environment active, navigate to the `backend` directory and install:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Frontend Dependencies:**
    Navigate to the `frontend-react` directory and install:
    ```bash
    pnpm install
    ```

### Important: DATABASE_URL Environment Variable

A known issue involves the `DATABASE_URL` environment variable. Ensure it is *not* set in your terminal session to prevent conflicts with SQLite configurations.

*   **Check (Windows PowerShell):**
    ```powershell
    $env:DATABASE_URL
    ```
*   **Clear for current session (Windows PowerShell):**
    ```powershell
    $env:DATABASE_URL = ""
    # Or more explicitly:
    Remove-Item Env:DATABASE_URL
    ```
*   **To remove permanently (Windows, requires admin):**
    ```powershell
    [System.Environment]::SetEnvironmentVariable("DATABASE_URL", $null, "Machine")
    ```
    *Restart your terminal after permanent removal.*

## Configuration

1.  **Backend Configuration:**
    *   Navigate to the `backend` folder.
    *   Create a `.env` file (e.g., copy from `.env.example`).
    *   Ensure `USE_SQL_SERVER=True` is set in this `.env` file.
    *   Verify that `DATABASE_URL` in `backend/app/config/settings.py` points correctly to your SQL Server instance with the right credentials.

## Building and Running the Application

The project provides a convenience script `run.bat` (for Windows) to start both the backend and frontend.

1.  **From the project root directory, execute:**
    ```bash
    run.bat
    ```

This script performs the following actions:
*   Checks dependencies.
*   Clears processes on port 8000.
*   Starts the FastAPI backend on port 8000.
*   Starts the React frontend on port 3000.
*   Opens the browser automatically to `http://localhost:3000`.

## Development Conventions

*   **Code Formatting**: While specific tools aren't explicitly detailed in the main `README`, the presence of `.prettierrc` in `frontend-react` suggests Prettier is used for frontend code formatting. For Python backend, common practices like `black` or `ruff format` are likely followed, though not explicitly stated.
*   **Testing**: The project includes a `backend/tests` directory and `frontend-react/jest.config.ts`, indicating a commitment to testing. The `README` also mentions a TODO for "more integration tests," suggesting an ongoing effort in this area.
