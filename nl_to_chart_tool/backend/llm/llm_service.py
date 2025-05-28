from typing import Literal, Optional, Dict, Any
# Client imports remain the same
from .ollama_client import get_sql_from_ollama 
from .deepseek_client import get_sql_from_deepseek
from .qwen_client import get_sql_from_qwen

# New import for config
from backend.core.config import get_llm_setting #, get_api_key # get_api_key is not used directly here

LlmType = Literal["ollama", "deepseek", "qwen"]
DEFAULT_LLM_PROVIDER: LlmType = "ollama" # Default provider if none specified in request

# LLM_CONFIG now sources default models from config.ini, with hardcoded fallbacks
LLM_CONFIG: Dict[LlmType, Dict[str, Any]] = {
    "ollama": {
        "default_model": get_llm_setting('ollama', 'default_model', 'llama2'),
        # Ollama endpoint is handled by ollama_client now, based on its own config or defaults
    },
    "deepseek": {
        "default_model": get_llm_setting('deepseek', 'default_model', 'deepseek-coder'),
        # Deepseek API key is handled by deepseek_client now
    },
    "qwen": {
        "default_model": get_llm_setting('qwen', 'default_model', 'qwen-turbo'),
        # Qwen API key is handled by qwen_client now
    },
}

async def get_sql_from_llm(
    natural_language_query: str,
    llm_provider: LlmType = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None, # User can specify a model to override default
    api_key: Optional[str] = None, # User can pass API key directly (client will prioritize this)
    system_prompt: Optional[str] = None,
    **kwargs: Any # For provider-specific arguments like ollama_endpoint
) -> str:
    print(f"LLM Service routing query to provider: {llm_provider}")

    # Determine the model to be used:
    # 1. User-specified model_name
    # 2. Default model from LLM_CONFIG (which is sourced from config.ini or fallback)
    effective_model_name = model_name
    if not effective_model_name and llm_provider in LLM_CONFIG:
        effective_model_name = LLM_CONFIG[llm_provider].get("default_model")
    
    # Note: If effective_model_name is still None (e.g. provider not in LLM_CONFIG),
    # the individual client modules will use their own internal default models.

    if llm_provider == "ollama":
        return await get_sql_from_ollama(
            natural_language_query,
            model=effective_model_name, # Pass the determined model
            system_prompt=system_prompt,
            ollama_endpoint=kwargs.get("ollama_endpoint") # Pass through if provided
        )
    elif llm_provider == "deepseek":
        return await get_sql_from_deepseek(
            natural_language_query,
            api_key=api_key, # Pass through API key (client handles config/env if None)
            model=effective_model_name, # Pass the determined model
            system_prompt=system_prompt
        )
    elif llm_provider == "qwen":
        return await get_sql_from_qwen(
            natural_language_query,
            api_key=api_key, # Pass through API key (client handles config/env if None)
            model=effective_model_name, # Pass the determined model
            system_prompt=system_prompt
        )
    else:
        # This path should ideally not be hit if LlmType is used correctly
        valid_providers = ", ".join(LLM_CONFIG.keys())
        return f"Error: Unknown LLM provider '{llm_provider}'. Available providers are: {valid_providers}."

if __name__ == '__main__':
    import asyncio
    import os # os is used by clients, but good for tests too
    # We need get_api_key from config for the test setup to check if keys are present
    from backend.core.config import get_api_key as config_get_api_key 

    async def test_llm_service():
        print("Testing LLM Service (defaults will be loaded from config.ini where available)")
        test_nl_query = "Show me the total number of users."
        
        print(f"\n--- Testing Ollama (model: {LLM_CONFIG['ollama']['default_model']}) ---")
        ollama_sql = await get_sql_from_llm(test_nl_query, llm_provider="ollama")
        print(f"Ollama generated SQL: {ollama_sql}")

        print(f"\n--- Testing DeepSeek (model: {LLM_CONFIG['deepseek']['default_model']}) ---")
        # Check if API key is likely configured (either in config.ini or environment)
        # The deepseek_client itself will perform the actual check. This is for the test runner.
        if config_get_api_key('DEEPSEEK') or os.getenv("DEEPSEEK_API_KEY"):
            deepseek_sql = await get_sql_from_llm(test_nl_query, llm_provider="deepseek")
            print(f"DeepSeek generated SQL: {deepseek_sql}")
        else:
            print("DeepSeek API Key not configured in config.ini or env. Skipping DeepSeek test in llm_service.")

        print(f"\n--- Testing Qwen (model: {LLM_CONFIG['qwen']['default_model']}) ---")
        # Check if API key is likely configured
        if config_get_api_key('QWEN') or os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"):
            qwen_sql = await get_sql_from_llm(test_nl_query, llm_provider="qwen")
            print(f"Qwen generated SQL: {qwen_sql}")
        else:
            print("Qwen API Key not configured in config.ini or env. Skipping Qwen test in llm_service.")
        
        # Example of overriding model for a specific call
        print(f"\n--- Testing Ollama with overridden model ('mistral', if different from default) ---")
        # This assumes 'mistral' is available in your Ollama setup
        # And that 'mistral' is different from the configured default for ollama
        ollama_mistral_sql = await get_sql_from_llm(test_nl_query, llm_provider="ollama", model_name="mistral")
        print(f"Ollama (mistral) generated SQL: {ollama_mistral_sql}")

    # To run this test:
    # 1. Make sure you have a `config.ini` in the `nl_to_chart_tool/backend/` directory,
    #    or relevant environment variables set for API keys if not using config.ini for keys.
    # 2. Navigate to the `nl_to_chart_tool/backend` directory.
    # 3. Run: `python -m llm.llm_service`
    #
    # asyncio.run(test_llm_service()) # Commented out for worker execution
    pass
