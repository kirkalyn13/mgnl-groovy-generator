import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from config.settings import TOP_K_SIMILARITY

# Setup envs
load_dotenv()
url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME", "magnolia_groovies")

# Setup Client
def setup_client() -> QdrantClient:
    return QdrantClient(
        url = url,
        api_key = api_key,
    )

# Instantiate Vector Store
def get_vector_store():
    print("⚙️  Setting up vector store...")
    client = setup_client()

    print(f"🧰 QDrant Client URL: {url}")
    print(f"🧰 Collection Name: {collection_name}")

    # Create and return vector store
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
    )

# Instantiate Query Engine
def get_query_engine():
    print("⚙️  Setting up query engine...")

    vector_store = get_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    return index.as_query_engine(similarity_top_k=TOP_K_SIMILARITY)