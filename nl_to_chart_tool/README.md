# Natural Language to Chart Tool

This project aims to create a tool that allows users to input natural language queries, which are then parsed by a Large Language Model (LLM) to generate SQL queries. These SQL queries are executed against a configured database, and the results are visualized as statistical charts.

## Current Status

This is the initial setup of the project. It includes:
- A basic Python FastAPI backend structure.
- A basic Vue3 frontend structure.
- A mock API endpoint that simulates returning chart data.
- Placeholder frontend components for query input and chart display.

## Project Structure

```
nl_to_chart_tool/
├── backend/        # Python FastAPI backend
│   ├── api/        # API endpoint definitions
│   ├── core/       # Core logic, parsing, etc.
│   ├── db/         # Database integration modules
│   ├── llm/        # LLM integration modules
│   ├── main.py     # FastAPI application entry point
│   └── requirements.txt
├── frontend/       # Vue3 frontend
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/ # Vue components
│   │   ├── App.vue     # Main App component
│   │   └── main.js     # Vue app entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 18+ (which includes npm) or Yarn
- An LLM API key or local Ollama setup (for future phases)
- Database instances (MySQL, PostgreSQL, etc. - for future phases)

## Running the Application (Current State)

### Backend

1.  Navigate to the backend directory:
    ```bash
    cd nl_to_chart_tool/backend
    ```
2.  Create a virtual environment and activate it (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the FastAPI development server:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend API will be available at `http://localhost:8000`. You can access the root endpoint at `http://localhost:8000/` and the API docs at `http://localhost:8000/docs`.

### Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd nl_to_chart_tool/frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    # OR if you prefer yarn
    # yarn install
    ```
3.  Run the Vue3 development server:
    ```bash
    npm run dev
    # OR if you prefer yarn
    # yarn dev
    ```
    The frontend application will be available at `http://localhost:5173` (or another port if 5173 is busy, check your console output).

## Next Steps

The following phases will involve:
1.  Integrating actual LLM services (Ollama, DeepSeek, Qwen).
2.  Implementing database connectors (MySQL, PostgreSQL, KingbaseES, DM8).
3.  Connecting the frontend to the backend for real data flow.
4.  Developing chart generation and display capabilities.
5.  Adding comprehensive error handling, configuration, and testing.
```
