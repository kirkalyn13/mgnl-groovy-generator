import os
from config.logger import logger
from dotenv import load_dotenv
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from config.settings import REQUEST_TIMEOUT

# Load ollama env variables
load_dotenv()
base_url = os.getenv("OLLAMA_URL")
embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL")
llm = os.getenv("OLLAMA_LLM")

def setup_ollama():
    """Setup Ollama Configurations"""
    logger.info("⚙️ Setting up model...")
    logger.info(f"⚙️ LLM Base URL: {base_url}")

    # Configure Ollama models
    Settings.embed_model = OllamaEmbedding(
        model_name=embedding_model,
        base_url=base_url,
    )
    logger.info(f"🤖 Embedding Model: {embedding_model}")

    Settings.llm = Ollama(
        model=llm,
        base_url=base_url,
        request_timeout=REQUEST_TIMEOUT,
    )

    logger.info(f"🤖 Large Language Model: {llm}")

    return Settings.llm