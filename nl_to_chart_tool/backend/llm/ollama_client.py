import httpx
import json
from typing import Optional

# Default Ollama API endpoint
OLLAMA_API_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "llama2"

async def get_sql_from_ollama(
    natural_language_query: str,
    model: str = DEFAULT_OLLAMA_MODEL,
    ollama_endpoint: str = OLLAMA_API_ENDPOINT,
    system_prompt: Optional[str] = None
) -> str:
    '''
    Sends a natural language query to an Ollama instance and expects a SQL query in return.
    '''
    if not system_prompt:
        system_prompt = "You are an AI assistant that translates natural language queries into SQL. Given the following natural language query, please return ONLY the SQL query. Do not include any other text, explanation, or markdown formatting. The SQL should be directly executable."

    payload = {
        "model": model,
        "prompt": natural_language_query,
        "system": system_prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Sending query to Ollama ({model} at {ollama_endpoint}): {natural_language_query}")
            response = await client.post(ollama_endpoint, json=payload)
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
        test_query_1 = "Show me all customers from Boston"
        print(f"Testing Ollama (model: {DEFAULT_OLLAMA_MODEL}) with query: '{test_query_1}'")
        sql_1 = await get_sql_from_ollama(test_query_1)
        print(f"Generated SQL: {sql_1}\n")

        test_query_2 = "List all products in the 'Electronics' category"
        # Example using a different model if available, e.g., "mistral"
        # sql_2 = await get_sql_from_ollama(test_query_2, model="mistral") 
        sql_2 = await get_sql_from_ollama(test_query_2) # Defaulting to llama2 for this example
        print(f"Testing Ollama (model: {DEFAULT_OLLAMA_MODEL}) with query: '{test_query_2}'")
        print(f"Generated SQL: {sql_2}\n")

        test_query_3 = "What is the total number of orders placed last month?"
        print(f"Testing Ollama (model: {DEFAULT_OLLAMA_MODEL}) with query: '{test_query_3}'")
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
