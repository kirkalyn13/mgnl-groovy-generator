import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.postprocessor.colbert_rerank import ColbertRerank
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

    # Create collection if it doesn't exist
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        logger.info(f"⚙️ Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,        # nomic-embed-text dimension
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"✅ Collection '{collection_name}' created")

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

    # Reranker — reorders top-k results by relevance
    reranker = ColbertRerank(top_n=3)

    # Similarity threshold — filters out low confidence results
    similarity_filter = SimilarityPostprocessor(similarity_cutoff=0.5)

    return {
        "llm": llm,
        "vector_store": vector_store,
        "query_engine": index.as_query_engine(
            similarity_top_k=10,        # fetch more candidates for reranker to work with
            node_postprocessors=[
                similarity_filter,      # filter low confidence first
                reranker,               # then rerank remaining
            ]       
        )
    }