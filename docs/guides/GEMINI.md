# Project Overview

This project, **Agent BI**, is a conversational business intelligence platform. It allows users to interact with business data using natural language. The application is built with Python, using Streamlit for the frontend and FastAPI for the backend. It integrates with Large Language Models (LLMs) like Gemini and DeepSeek, and it can connect to SQL Server databases and Parquet files.

The application is modular, with a clear separation between the business logic, user interface, and backend. The core of the application is a conversational agent that can answer questions, generate charts, and provide data insights.

## Building and Running

To build and run this project, follow these steps:

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the environment variables:**
    Copy the `.env.example` file to a new file named `.env` and fill in the required credentials for the LLMs and the SQL Server database.

4.  **Run the application:**
    ```bash
    streamlit run streamlit_app.py
    ```
    The application will be available at `http://localhost:8501`.

## Development Conventions

*   **Modular Architecture:** The project follows a modular architecture, with code organized into `core`, `data`, `pages`, `scripts`, and `tests` directories.
*   **Dependency Management:** The project uses `pip-compile` to manage dependencies. The `requirements.in` file lists the direct dependencies, and the `requirements.txt` file is generated from it.
*   **Testing:** The project has a suite of automated tests using `pytest`. The tests are located in the `tests` directory and can be run with the following command:
    ```bash
    pytest tests/test_direct_queries.py -v
    ```
*   **Conversational Agent:** The core of the application is a conversational agent built with `langchain` and `langgraph`. The agent's logic is defined in `core/graph/graph_builder.py` and `core/agents/bi_agent_nodes.py`.
*   **Frontend:** The user interface is built with `streamlit`. The main application file is `streamlit_app.py`, and additional pages are located in the `pages` directory.
*   **Data Handling:** The application can read data from both SQL Server and Parquet files. The `core/connectivity` directory contains the adapters for connecting to these data sources.
