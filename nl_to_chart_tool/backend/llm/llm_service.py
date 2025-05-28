from typing import Literal, Optional, Dict, Any
from .ollama_client import get_sql_from_ollama, DEFAULT_OLLAMA_MODEL
from .deepseek_client import get_sql_from_deepseek, DEFAULT_DEEPSEEK_MODEL
from .qwen_client import get_sql_from_qwen, DEFAULT_QWEN_MODEL

LlmType = Literal["ollama", "deepseek", "qwen"]
DEFAULT_LLM_PROVIDER: LlmType = "ollama"

LLM_CONFIG: Dict[LlmType, Dict[str, Any]] = {
    "ollama": {"default_model": DEFAULT_OLLAMA_MODEL, "endpoint": None},  # Default endpoint for ollama can be None
    "deepseek": {"default_model": DEFAULT_DEEPSEEK_MODEL, "api_key_env": "DEEPSEEK_API_KEY"},
    "qwen": {"default_model": DEFAULT_QWEN_MODEL, "api_key_env": "QWEN_API_KEY"},
}

async def get_sql_from_llm(
    natural_language_query: str,
    llm_provider: LlmType = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs: Any
) -> str:
    '''
    Routes the natural language query to the specified LLM provider to get a SQL query.
    '''
    print(f"Routing query to LLM provider: {llm_provider}")

    if llm_provider == "ollama":
        current_model = model_name or LLM_CONFIG["ollama"]["default_model"]
        # Use endpoint from kwargs if provided, else from LLM_CONFIG, else client's default (None)
        ollama_endpoint = kwargs.get("ollama_endpoint", LLM_CONFIG["ollama"].get("endpoint"))
        return await get_sql_from_ollama(
            natural_language_query,
            model=current_model,
            system_prompt=system_prompt,
            ollama_endpoint=ollama_endpoint # Pass None if not specified, client handles default
        )
    elif llm_provider == "deepseek":
        current_model = model_name or LLM_CONFIG["deepseek"]["default_model"]
        return await get_sql_from_deepseek(
            natural_language_query,
            api_key=api_key, # Client handles env var if api_key is None
            model=current_model,
            system_prompt=system_prompt
        )
    elif llm_provider == "qwen":
        current_model = model_name or LLM_CONFIG["qwen"]["default_model"]
        return await get_sql_from_qwen(
            natural_language_query,
            api_key=api_key, # Client handles env var if api_key is None
            model=current_model,
            system_prompt=system_prompt
        )
    else:
        # This case should ideally be caught by type checking LlmType
        valid_providers = ", ".join(LLM_CONFIG.keys())
        return f"Error: Unknown LLM provider '{llm_provider}'. Available providers are: {valid_providers}."

if __name__ == '__main__':
    import asyncio
    import os

    async def test_llm_service():
        test_nl_query = "Show me the total number of users."
        
        print("\n--- Testing Ollama ---")
        # Assuming Ollama is running and the default model (e.g., llama2) is available
        # To specify a different Ollama endpoint for testing:
        # ollama_sql = await get_sql_from_llm(test_nl_query, llm_provider="ollama", ollama_endpoint="http://custom.host:11434/api/generate")
        ollama_sql = await get_sql_from_llm(test_nl_query, llm_provider="ollama")
        print(f"Ollama generated SQL: {ollama_sql}")

        print("\n--- Testing DeepSeek ---")
        if os.getenv("DEEPSEEK_API_KEY"):
            deepseek_sql = await get_sql_from_llm(test_nl_query, llm_provider="deepseek")
            print(f"DeepSeek generated SQL: {deepseek_sql}")
        else:
            print("DEEPSEEK_API_KEY not set. Skipping DeepSeek test.")

        print("\n--- Testing Qwen ---")
        if os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"):
            qwen_sql = await get_sql_from_llm(test_nl_query, llm_provider="qwen")
            print(f"Qwen generated SQL: {qwen_sql}")
        else:
            print("QWEN_API_KEY/DASHSCOPE_API_KEY not set. Skipping Qwen test.")
        
        # Example of testing a non-default model for Ollama
        # print("\n--- Testing Ollama with non-default model (e.g., mistral) ---")
        # Make sure 'mistral' (or other model) is pulled: `ollama pull mistral`
        # ollama_mistral_sql = await get_sql_from_llm(test_nl_query, llm_provider="ollama", model_name="mistral")
        # print(f"Ollama (Mistral) generated SQL: {ollama_mistral_sql}")

    # To run this test (ensure relevant services/keys are set up):
    # 1. Navigate to the `nl_to_chart_tool/backend` directory.
    # 2. Set environment variables if needed (e.g., DEEPSEEK_API_KEY).
    # 3. Run the command: `python -m llm.llm_service`
    #
    # asyncio.run(test_llm_service()) # Commented out for worker execution
    pass
