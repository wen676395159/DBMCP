import httpx
import json
from typing import Optional
from backend.core.config import get_llm_setting # New import

# Default Ollama API endpoint - used if not in config and not passed as arg
FALLBACK_OLLAMA_API_ENDPOINT = "http://localhost:11434/api/generate"
# Default model to use if not specified - used if not in config and not passed as arg
FALLBACK_OLLAMA_MODEL = "llama2"

# Get settings from config, with fallbacks
OLLAMA_API_ENDPOINT = get_llm_setting('ollama', 'endpoint', FALLBACK_OLLAMA_API_ENDPOINT)
DEFAULT_OLLAMA_MODEL = get_llm_setting('ollama', 'default_model', FALLBACK_OLLAMA_MODEL)

async def get_sql_from_ollama(
    natural_language_query: str,
    model: Optional[str] = None, # Changed to Optional
    ollama_endpoint: Optional[str] = None, # Changed to Optional
    system_prompt: Optional[str] = None
) -> str:
    '''
    Sends a natural language query to an Ollama instance and expects a SQL query in return.
    '''
    # Determine model and endpoint: argument > config > fallback
    effective_model = model if model is not None else DEFAULT_OLLAMA_MODEL
    effective_endpoint = ollama_endpoint if ollama_endpoint is not None else OLLAMA_API_ENDPOINT
    
    if not system_prompt:
        system_prompt = "You are an AI assistant that translates natural language queries into SQL. Given the following natural language query, please return ONLY the SQL query. Do not include any other text, explanation, or markdown formatting. The SQL should be directly executable."

    payload = {
        "model": effective_model,
        "prompt": natural_language_query,
        "system": system_prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Sending query to Ollama ({effective_model} at {effective_endpoint}): {natural_language_query}") # MODIFIED
            response = await client.post(effective_endpoint, json=payload) # MODIFIED
            response.raise_for_status()

            response_data = response.json()
            sql_query = response_data.get("response", "").strip()

            if not sql_query:
                return "Error: LLM returned an empty response."
            
            # Clean-up potential markdown code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query[len("```sql"):].strip()
            if sql_query.startswith("```"):
                sql_query = sql_query[len("```"):].strip()
            if sql_query.endswith("```"):
                sql_query = sql_query[:-len("```")].strip()
            
            print(f"Received SQL from Ollama: {sql_query}")
            return sql_query

        except httpx.HTTPStatusError as e:
            error_message = f"Error connecting to Ollama: HTTP {e.response.status_code} - {e.response.text}"
            print(error_message)
            return f"Error: Could not get SQL from Ollama. Status: {e.response.status_code}"
        except httpx.RequestError as e:
            error_message = f"Error connecting to Ollama: {str(e)}"
            print(error_message)
            return "Error: Could not connect to Ollama service. Is it running?"
        except json.JSONDecodeError:
            error_message = "Error: Could not decode JSON response from Ollama."
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred while querying Ollama: {str(e)}"
            print(error_message)
            return "Error: An unexpected error occurred with Ollama."

if __name__ == '__main__':
    import asyncio

    async def test_ollama():
        # Ensure Ollama server is running and has the specified model
        # e.g., run: ollama pull llama2
        # e.g., run: ollama pull mistral
        print(f"Ollama Client using Endpoint: {OLLAMA_API_ENDPOINT}, Default Model: {DEFAULT_OLLAMA_MODEL}")
        test_query_1 = "Show me all customers from Boston"
        print(f"Testing Ollama with query: '{test_query_1}' (using default model from config or fallback)")
        sql_1 = await get_sql_from_ollama(test_query_1)
        print(f"Generated SQL: {sql_1}\n")

        test_query_2 = "List all products in the 'Electronics' category"
        # Example using a different model if available, e.g., "mistral"
        # sql_2 = await get_sql_from_ollama(test_query_2, model="mistral") 
        print(f"Testing Ollama with query: '{test_query_2}' (explicitly using model 'llama2' if different from default, else default)")
        # To test with a specific model if it's different from default, pass it.
        # Otherwise, it uses the DEFAULT_OLLAMA_MODEL (from config or fallback)
        sql_2 = await get_sql_from_ollama(test_query_2, model="llama2") 
        print(f"Generated SQL: {sql_2}\n")

        test_query_3 = "What is the total number of orders placed last month?"
        print(f"Testing Ollama with query: '{test_query_3}' (using default model from config or fallback)")
        sql_3 = await get_sql_from_ollama(test_query_3)
        print(f"Generated SQL: {sql_3}\n")

    # To run this test (ensure Ollama is running and configured):
    # 1. Navigate to the `nl_to_chart_tool/backend` directory.
    # 2. Run the command: `python -m llm.ollama_client`
    #
    # If you want to run it in an interactive Python session:
    # import asyncio
    # from llm.ollama_client import get_sql_from_ollama
    # asyncio.run(get_sql_from_ollama("your query here"))

    # The following line is commented out to prevent issues with the worker's execution context.
    # The user can uncomment it or use the instructions above for manual testing.
    # asyncio.run(test_ollama())
    pass
