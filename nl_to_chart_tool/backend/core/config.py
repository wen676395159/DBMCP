import configparser
import os
from typing import Optional

# Path to the configuration file
# Assumes config.ini is in the same directory as this script (core)
# For robustness, construct path relative to this file's location or project root
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, '..', 'config.ini') # Place config.ini in backend/
CONFIG_FILE_PATH = os.path.abspath(os.path.join(CONFIG_DIR, '..', 'config.ini'))


# Initialize the config parser
config = configparser.ConfigParser()

# Load the configuration file if it exists
if os.path.exists(CONFIG_FILE_PATH):
    config.read(CONFIG_FILE_PATH)
    # print(f"Configuration file loaded from {CONFIG_FILE_PATH}")
else:
    # print(f"Warning: Configuration file {CONFIG_FILE_PATH} not found. Using defaults or environment variables where applicable.")
    # You might want to raise an error or handle this more gracefully depending on requirements
    pass

def get_api_key(service_name: str) -> Optional[str]:
    '''
    Retrieves an API key from the configuration file.
    Example section in config.ini:
    [api_keys]
    deepseek_api_key = YOUR_KEY_HERE
    qwen_api_key = YOUR_KEY_HERE
    '''
    try:
        return config.get('api_keys', f'{service_name.lower()}_api_key', fallback=None)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return None

def get_llm_setting(llm_provider: str, setting_name: str, default: Optional[str] = None) -> Optional[str]:
    '''
    Retrieves a specific LLM setting from the config file.
    Example section in config.ini:
    [ollama_settings]
    default_model = llama3
    endpoint = http://localhost:11435

    [deepseek_settings]
    default_model = deepseek-coder
    '''
    try:
        return config.get(f'{llm_provider.lower()}_settings', setting_name, fallback=default)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default

# --- Example Usage (for testing this module directly) ---
if __name__ == '__main__':
    print(f"Attempting to load config from: {CONFIG_FILE_PATH}")
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"IMPORTANT: Create a 'config.ini' file in the '{os.path.dirname(CONFIG_FILE_PATH)}' directory for testing.")
        print("Example 'config.ini':")
        print("""
[api_keys]
deepseek_api_key = YOUR_DEEPSEEK_KEY
qwen_api_key = YOUR_QWEN_KEY

[ollama_settings]
default_model = llama2
# endpoint = http://localhost:11434

[deepseek_settings]
default_model = deepseek-coder

[qwen_settings]
default_model = qwen-turbo
        """)
    else:
        print("config.ini found.")

    print(f"DeepSeek API Key: {get_api_key('DEEPSEEK')}")
    print(f"Qwen API Key: {get_api_key('QWEN')}")
    print(f"Ollama Default Model: {get_llm_setting('ollama', 'default_model', 'default_ollama_model_here')}")
    print(f"Ollama Endpoint: {get_llm_setting('ollama', 'endpoint')}") # Will be None if not set
    print(f"DeepSeek Default Model: {get_llm_setting('deepseek', 'default_model', 'default_deepseek_model_here')}")
