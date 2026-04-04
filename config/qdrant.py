import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore

# Setup client
load_dotenv()
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
collection_name = os.getenv("COLLECTION_NAME", "magnolia_groovies")

def get_vector_store():
    print("⚙️ Setting up vector store...")

    # Create and return vector store
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
    )