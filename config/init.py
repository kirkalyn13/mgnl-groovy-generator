from config.qdrant import init_rag_engine
from config.llm import init_llm
from config.logger import logger

def init() -> dict :
    """Run setup and config initializations e.g. LLM and RAG config"""
    logger.info("🛠️ Running Setup...")
    llm = init_llm()
    return init_rag_engine(llm)