from config.llm import init_llm
from config.qdrant import init_rag_engine
from config.logger import logger

def init() -> dict :
    """Run setup and config initializations e.g. LLM and RAG config"""
    logger.info("🛠️ Running Setup...")
    init_llm()
    return init_rag_engine()