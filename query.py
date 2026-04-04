from llama_index.core import VectorStoreIndex
from config.qdrant import get_vector_store
from config.ollama import setup_ollama
from config.settings import TOP_K_SIMILARITY

SAMPLE_QUERY = "Generate a Magnolia Groovy script to review user details"

def query():
    # Configure Ollama models
    setup_ollama()

    # Load index
    vector_store=get_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)

    # Create query engine (top-k = 3)
    query_engine = index.as_query_engine(similarity_top_k=TOP_K_SIMILARITY)

    response = query_engine.query(SAMPLE_QUERY)

    print("\n=== RESPONSE ===\n")
    print(response)

query()