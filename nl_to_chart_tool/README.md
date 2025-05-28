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
# LLM API keys and local Ollama setup are now managed via config.ini (see LLM Configuration section)
- Database instances (MySQL, PostgreSQL, etc. - for future phases)

## LLM Configuration

This tool supports multiple Large Language Models (LLMs) for translating natural language to SQL. Configuration for API keys and LLM-specific settings is managed via a configuration file.

1.  **Locate the Example Configuration File:**
    In the `nl_to_chart_tool/backend/` directory, you will find a file named `config.example.ini`.

2.  **Create Your Configuration File:**
    Make a copy of `config.example.ini` and rename it to `config.ini` in the *same directory* (`nl_to_chart_tool/backend/config.ini`).

    ```bash
    cp nl_to_chart_tool/backend/config.example.ini nl_to_chart_tool/backend/config.ini
    ```

3.  **Edit `config.ini`:**
    Open `nl_to_chart_tool/backend/config.ini` with a text editor and fill in your API keys and desired settings under the appropriate sections.

    **Example Sections in `config.ini`:**

    *   **`[api_keys]`**:
        *   `deepseek_api_key = YOUR_DEEPSEEK_API_KEY_HERE`
        *   `qwen_api_key = YOUR_QWEN_API_KEY_HERE` (This is for Alibaba Cloud DashScope Qwen models)

    *   **`[ollama_settings]`**:
        *   `default_model = llama2` (Specify the default Ollama model you have pulled, e.g., `llama3`, `mistral`)
        *   `endpoint = http://localhost:11434` (If your Ollama service runs on a different address/port)
        Ensure your Ollama service is running and the specified model is available (e.g., `ollama pull llama2`).

    *   **`[deepseek_settings]`**:
        *   `default_model = deepseek-coder` (Default model for DeepSeek)

    *   **`[qwen_settings]`**:
        *   `default_model = qwen-turbo` (Default model for Qwen)

    **Important:** The `config.ini` file contains sensitive API keys and should *not* be committed to version control. It should be automatically ignored by Git if a `.gitignore` file is set up correctly (see next step).

4.  **API Usage:**
    The backend API endpoint `POST /api/query` uses these LLM services. You can specify the desired LLM provider in the JSON payload:
    ```json
    {
      "natural_language_query": "your query here",
      "llm_provider": "ollama" // or "deepseek", "qwen"
      // "model_name": "specific-model-if-not-default" // Optional, overrides default from config.ini
    }
    ```
    If `llm_provider` is omitted, it defaults to the one specified as `DEFAULT_LLM_PROVIDER` in the code (currently "ollama"). The system will use the API keys and default models specified in your `config.ini`.

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
