import os
from dotenv import load_dotenv
from config.logger import logger
from config.ollama import setup_ollama
from config.gemini import setup_gemini
from config.logger import logger

# Read preferred LLM mode from .env
load_dotenv()
llm_mode = os.getenv("LLM_MODE", "ollama")

def init_llm():
    """Initialized LLM used based on configured settings."""
    logger.info(f"🤖 Enabled LLM mode: {llm_mode}")
    try:
        match llm_mode:
            case "ollama":
                return setup_ollama()
            case "gemini":
                return setup_gemini()
            # To add a new provider (e.g. OpenAI):
            # 1. Create config/openai.py with a setup_openai() function
            #    mirroring setup_ollama()/setup_gemini()
            # 2. Add a case "openai": return setup_openai()
            # 3. Ensure Qdrant collection suffix + embedding dims
            #    are handled for the new mode (see COLLECTION_NAME logic)
            case _:
                return setup_ollama()
    except Exception as e:
        logger.error(f"‼️ Error encountered: {e}")
        raise