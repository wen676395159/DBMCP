import httpx
import os
import json
from typing import Optional
from backend.core.config import get_api_key, get_llm_setting # New import

QWEN_API_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
FALLBACK_QWEN_MODEL = "qwen-turbo"
DEFAULT_QWEN_MODEL = get_llm_setting('qwen', 'default_model', FALLBACK_QWEN_MODEL)

async def get_sql_from_qwen(
    natural_language_query: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None, # Changed to Optional
    api_endpoint: str = QWEN_API_ENDPOINT,
    system_prompt: Optional[str] = None
) -> str:
    '''
    Sends a natural language query to the Qwen API and expects a SQL query in return.
    '''
    effective_api_key = api_key
    if not effective_api_key:
        effective_api_key = get_api_key("QWEN") # Get from config file
    
    if not effective_api_key: # Fallback to environment variable
        effective_api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        if effective_api_key:
            print("Qwen API Key found in environment variables (QWEN_API_KEY/DASHSCOPE_API_KEY). Consider moving to config.ini.")

    if not effective_api_key:
        return "Error: QWEN_API_KEY (or DASHSCOPE_API_KEY) not found in config file or environment variables."

    effective_model = model if model is not None else DEFAULT_QWEN_MODEL

    if not system_prompt:
        # Qwen models often use <|system|>, <|user|>, <|assistant|> roles
        system_prompt = "You are an AI assistant that translates natural language queries into SQL. Given the following natural language query, please return ONLY the SQL query. Do not include any other text, explanation, or markdown formatting. The SQL should be directly executable."


    headers = {
        "Authorization": f"Bearer {effective_api_key}", # MODIFIED
        "Content-Type": "application/json",
        # "X-DashScope-SSE": "enable", # For streaming, not used here
    }

    # Qwen's input format might be slightly different, often involving an 'input' and 'parameters' field.
    # The 'messages' structure is also common for chat-tuned models.
    payload = {
        "model": effective_model, # MODIFIED
        "input": {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_language_query}
            ]
        },
        "parameters": {
            # "result_format": "message", # to get a structured message response
            # "temperature": 0.1, # Optional: for more deterministic output
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Sending query to Qwen ({effective_model} at {api_endpoint}): {natural_language_query}") # MODIFIED
            response = await client.post(api_endpoint, json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()

            # Extract the SQL query from the response
            # Based on DashScope Qwen API docs, content is in response.output.choices[0].message.content or response.output.text
            sql_query = "" # Initialize sql_query
            if response_data.get("output"):
                output_data = response_data["output"]
                if output_data.get("choices") and output_data["choices"][0].get("message"):
                    sql_query = output_data["choices"][0]["message"].get("content", "").strip()
                elif output_data.get("text"): # Fallback for simpler text completion models
                    sql_query = output_data.get("text", "").strip()
                else:
                    # Check for error messages from the API if content is not where expected
                    if response_data.get("code") and response_data.get("message"):
                         return f"Error from Qwen API (in output processing): {response_data['code']} - {response_data['message']}"
                    return "Error: Could not extract content from Qwen response output."
            else:
                # Check for error messages from the API at the top level
                if response_data.get("code") and response_data.get("message"):
                    return f"Error from Qwen API: {response_data['code']} - {response_data['message']}"
                return "Error: Could not extract output field from Qwen response."


            if not sql_query:
                # This condition might be hit if the specific extraction logic above failed or returned empty
                # and no prior error was returned.
                return "Error: LLM returned an empty response or content extraction failed."

            # Clean-up potential markdown code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query[len("```sql"):].strip()
            if sql_query.startswith("```"):
                sql_query = sql_query[len("```"):].strip()
            if sql_query.endswith("```"):
                sql_query = sql_query[:-len("```")].strip()
            
            print(f"Received SQL from Qwen: {sql_query}")
            return sql_query

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "message" in error_json: # DashScope errors often have a "message" field
                    error_detail = error_json["message"]
                elif "Message" in error_json: # Sometimes it's capitalized
                     error_detail = error_json["Message"]
                elif "code" in error_json and "message" in error_json: # Another common error format
                    error_detail = f"{error_json['code']}: {error_json['message']}"
            except json.JSONDecodeError:
                pass # Use raw text if not JSON
            error_message = f"Error connecting to Qwen API: HTTP {e.response.status_code} - {error_detail}"
            print(error_message)
            return f"Error: Could not get SQL from Qwen. Status: {e.response.status_code}, Detail: {error_detail}"
        except httpx.RequestError as e:
            error_message = f"Error connecting to Qwen API: {str(e)}"
            print(error_message)
            return "Error: Could not connect to Qwen API."
        except json.JSONDecodeError:
            error_message = "Error: Could not decode JSON response from Qwen API."
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred while querying Qwen API: {str(e)}"
            print(error_message)
            return "Error: An unexpected error occurred with Qwen API."

if __name__ == '__main__':
    import asyncio

    async def test_qwen():
        print(f"Qwen Client using Default Model: {DEFAULT_QWEN_MODEL}")
        # Ensure QWEN_API_KEY (or DASHSCOPE_API_KEY) environment variable is set OR in config.ini
        # For example: export QWEN_API_KEY='your_api_key_here'
        # The function get_sql_from_qwen will now try to fetch API key from config first,
        # then environment variables.

        test_query_1 = "List all departments with more than 50 employees."
        print(f"Testing Qwen with query: '{test_query_1}'")
        sql_1 = await get_sql_from_qwen(test_query_1)
        print(f"Generated SQL: {sql_1}\n")

        test_query_2 = "Find the top 3 products by sales revenue in the last month."
        print(f"Testing Qwen with query: '{test_query_2}'")
        sql_2 = await get_sql_from_qwen(test_query_2)
        print(f"Generated SQL: {sql_2}\n")

    # To run this test (ensure QWEN_API_KEY/DASHSCOPE_API_KEY is set in config.ini or environment):
    # 1. Navigate to the `nl_to_chart_tool/backend` directory.
    # 2. Set the QWEN_API_KEY environment variable.
    # 3. Run the command: `python -m llm.qwen_client`
    #
    # asyncio.run(test_qwen()) # Commented out for worker execution
    pass
