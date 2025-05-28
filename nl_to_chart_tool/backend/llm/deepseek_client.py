import httpx
import os
import json
from typing import Optional

# DeepSeek API Configuration
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_DEEPSEEK_MODEL = "deepseek-coder" # Or "deepseek-chat" - choose the one more suitable for SQL generation

async def get_sql_from_deepseek(
    natural_language_query: str,
    api_key: Optional[str] = None,
    model: str = DEFAULT_DEEPSEEK_MODEL,
    api_endpoint: str = DEEPSEEK_API_ENDPOINT,
    system_prompt: Optional[str] = None
) -> str:
    '''
    Sends a natural language query to the DeepSeek API and expects a SQL query in return.
    '''
    if api_key is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "Error: DEEPSEEK_API_KEY environment variable not set."

    if not system_prompt:
        system_prompt = "You are an AI assistant that translates natural language queries into SQL. Given the following natural language query, please return ONLY the SQL query. Do not include any other text, explanation, or markdown formatting. The SQL should be directly executable."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_query},
        ],
        "stream": False,
        # "temperature": 0.1, # Optional: Adjust for more deterministic output
        # "max_tokens": 500,  # Optional: Limit response length
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Sending query to DeepSeek ({model} at {api_endpoint}): {natural_language_query}")
            response = await client.post(api_endpoint, json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            
            # Extract the SQL query from the response
            # Based on DeepSeek API docs, content is in response.choices[0].message.content
            if response_data.get("choices") and response_data["choices"][0].get("message"):
                sql_query = response_data["choices"][0]["message"].get("content", "").strip()
            else:
                return "Error: Could not extract content from DeepSeek response."

            if not sql_query:
                return "Error: LLM returned an empty response."

            # Clean-up potential markdown code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query[len("```sql"):].strip()
            if sql_query.startswith("```"):
                sql_query = sql_query[len("```"):].strip()
            if sql_query.endswith("```"):
                sql_query = sql_query[:-len("```")].strip()

            print(f"Received SQL from DeepSeek: {sql_query}")
            return sql_query

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json and "message" in error_json["error"]:
                    error_detail = error_json["error"]["message"]
            except json.JSONDecodeError:
                pass # Use raw text if not JSON
            error_message = f"Error connecting to DeepSeek API: HTTP {e.response.status_code} - {error_detail}"
            print(error_message)
            return f"Error: Could not get SQL from DeepSeek. Status: {e.response.status_code}"
        except httpx.RequestError as e:
            error_message = f"Error connecting to DeepSeek API: {str(e)}"
            print(error_message)
            return "Error: Could not connect to DeepSeek API."
        except json.JSONDecodeError:
            error_message = "Error: Could not decode JSON response from DeepSeek API."
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred while querying DeepSeek API: {str(e)}"
            print(error_message)
            return "Error: An unexpected error occurred with DeepSeek API."

if __name__ == '__main__':
    import asyncio

    async def test_deepseek():
        # Ensure DEEPSEEK_API_KEY environment variable is set before running
        # For example: export DEEPSEEK_API_KEY='your_api_key_here'
        api_key_present = os.getenv("DEEPSEEK_API_KEY")
        if not api_key_present:
            print("DEEPSEEK_API_KEY not found in environment. Skipping test.")
            print("Please set it: export DEEPSEEK_API_KEY='your_actual_api_key'")
            return

        print(f"Using DeepSeek model: {DEFAULT_DEEPSEEK_MODEL}")
        test_query_1 = "Show me all users from the database named 'employees' who are older than 30."
        print(f"Testing DeepSeek with query: '{test_query_1}'")
        sql_1 = await get_sql_from_deepseek(test_query_1)
        print(f"Generated SQL: {sql_1}\n")

        test_query_2 = "What is the average salary for software engineers?"
        print(f"Testing DeepSeek with query: '{test_query_2}'")
        sql_2 = await get_sql_from_deepseek(test_query_2)
        print(f"Generated SQL: {sql_2}\n")
    
    # To run this test (ensure DEEPSEEK_API_KEY is set):
    # 1. Navigate to the `nl_to_chart_tool/backend` directory.
    # 2. Set the DEEPSEEK_API_KEY environment variable.
    # 3. Run the command: `python -m llm.deepseek_client`
    #
    # asyncio.run(test_deepseek()) # Commented out for worker execution
    pass
