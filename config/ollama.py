import os
from dotenv import load_dotenv
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from config.settings import REQUEST_TIMEOUT

# Load ollama env variables
load_dotenv()
base_url = os.getenv("OLLAMA_URL")
model_name = os.getenv("OLLAMA_EMBEDDING_MODEL")
model = os.getenv("OLLAMA_LLM")


def setup_ollama():
    print("⚙️ Setting up model...")

    # Configure Ollama models
    Settings.embed_model = OllamaEmbedding(
        model_name=model_name,
        base_url=base_url,
    )
    Settings.llm = Ollama(
        model=model,
        base_url=base_url,
        request_timeout=REQUEST_TIMEOUT,
    )