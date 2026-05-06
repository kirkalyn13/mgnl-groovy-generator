from langfuse.llama_index import LlamaIndexInstrumentor
from config.logger import logger

def init_langfuse():
    """Initialize LangFuse"""
    logger.info("⚙️ Initializing Langfuse...")
    LlamaIndexInstrumentor().start()
    logger.info("✅ Langfuse initialized")