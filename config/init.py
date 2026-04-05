from config.ollama import setup_ollama
from config.qdrant import init_rag_engine
from config.logger import logger

def init() -> dict :
    """Run setup and config initializations e.g. LLM and RAG config"""
    logger.info("🛠️ Running Setup...")
    setup_ollama()
    return init_rag_engine()