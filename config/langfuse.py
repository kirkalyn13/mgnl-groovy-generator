import os
from langfuse import get_client
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from config.logger import logger

langfuse = None

def init_langfuse():
    global langfuse
    logger.info("⚙️ Initializing Langfuse...")
    
    # Must be set before instrumentation
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-...")
    os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-...")
    os.environ.setdefault("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

    langfuse = get_client()

    if not langfuse.auth_check():
        logger.error("❌ Langfuse authentication failed")
        return

    LlamaIndexInstrumentor().instrument()
    logger.info("✅ Langfuse initialized")