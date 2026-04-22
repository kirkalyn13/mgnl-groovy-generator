import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from config.settings import TOP_K_SIMILARITY
from config.logger import logger

# Setup envs
load_dotenv()
url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME", "magnolia_groovies")

# Setup Client
def setup_client() -> QdrantClient:
    """Setup QDrant Client"""
    return QdrantClient(
        url = url,
        api_key = api_key,
    )


def init_vector_store():
    """Instantiate QDrant Vector Store"""
    logger.info("⚙️  Setting up vector store...")
    client = setup_client()

    logger.info(f"🧰 QDrant Client URL: {url}")
    logger.info(f"🧰 Collection Name: {collection_name}")

    # Create and return vector store
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
    )

def init_rag_engine(llm):
    """Instantiate Vector Store and Query Engine"""
    logger.info("⚙️  Setting up query engine...")

    vector_store = init_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    return {
        "vector_store": vector_store,
        "query_engine": index.as_query_engine(similarity_top_k=TOP_K_SIMILARITY),
        "llm": llm
    }