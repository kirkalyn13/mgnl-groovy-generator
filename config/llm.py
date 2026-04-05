import os
from dotenv import load_dotenv
from config.logger import logger
from config.ollama import setup_ollama
from config.logger import logger

# Read preferred LLM mode from .env
load_dotenv()
llm_mode = os.getenv("LLM_MODE", "ollama")

def init_llm():
    """Initialized LLM used based on configured settings."""
    try:
        match llm_mode:
            case "ollama":
                setup_ollama()
            case _:
                setup_ollama()
                
        logger.info(f"🤖 Enabled LLM mode: {llm_mode}")
    except Exception as e:
        logger.error(f"‼️ Error encountered: {e}")
        raise