import os
from config.logger import logger
from dotenv import load_dotenv
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from config.settings import REQUEST_TIMEOUT

# Load Gemini env variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2-preview")
llm = os.getenv("GEMINI_LLM", "gemini-2.5-flash")

def setup_gemini():
    """Setup Gemini Configurations"""
    logger.info("⚙️ Setting up model...")
    logger.info(f"⚙️ Gemini Model: {llm}")

    # Configure Gemini models
    Settings.embed_model = GoogleGenAIEmbedding(
        model_name=embedding_model,
        api_key=api_key,
    )
    logger.info(f"🤖 Embedding Model: {embedding_model}")

    Settings.llm = GoogleGenAI(
        model=llm,
        api_key=api_key,
        request_timeout=REQUEST_TIMEOUT,
    )

    logger.info(f"🤖 Large Language Model: {llm}")

    return Settings.llm