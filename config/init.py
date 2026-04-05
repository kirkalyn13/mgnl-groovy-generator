from config.ollama import setup_ollama
from config.qdrant import init_rag_engine

def init() -> dict :
    print("🛠️ Running Setup...")
    setup_ollama()
    return init_rag_engine()