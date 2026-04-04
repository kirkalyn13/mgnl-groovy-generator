import string

from llama_index.core import VectorStoreIndex
from config.qdrant import get_query_engine
from config.ollama import setup_ollama


SAMPLE_QUERY = "Generate a Magnolia Groovy script to review user details. Return only the script and nothing else."

def query(prompt: string) -> string:
    # Configure Ollama models
    setup_ollama()

    # Create query engine (top-k = 3)
    query_engine = get_query_engine()

    response = query_engine.query(SAMPLE_QUERY)

    print("\n=== RESPONSE ===\n")
    print(response)

query(SAMPLE_QUERY)