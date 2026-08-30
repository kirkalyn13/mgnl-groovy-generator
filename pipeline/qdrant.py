import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.postprocessor.colbert_rerank import ColbertRerank
from config.logger import logger

# Setup envs
load_dotenv()
url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
llm_mode = os.getenv("LLM_MODE", "ollama")
collection_name = os.getenv("COLLECTION_NAME", "magnolia_groovies") + "_" + llm_mode

# Setup Client
def setup_client() -> AsyncQdrantClient:
    """Setup QDrant Client"""
    return QdrantClient(
        api_key = api_key,
        url=url
    )

# Setup Async Client
async def setup_aclient() -> AsyncQdrantClient:
    """Setup Async QDrant Client"""
    return AsyncQdrantClient(
        api_key = api_key,
        url=url
    )


async def init_vector_store():
    """Instantiate QDrant Vector Store"""
    logger.info("⚙️  Setting up vector store...")
    client = setup_client()
    aclient = await setup_aclient()

    logger.info(f"🧰 QDrant Client URL: {url}")
    logger.info(f"🧰 Collection Name: {collection_name}")

    # Create collection if it doesn't exist
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        logger.info(f"⚙️ Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=get_collection_size(llm_mode),        # nomic-embed-text dimension
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"✅ Collection '{collection_name}' created")

    # Create and return vector store
    return QdrantVectorStore(
        client=client,
        aclient=aclient,
        collection_name=collection_name,
    )

async def init_rag_engine(llm):
    """Instantiate Vector Store and Query Engine"""
    logger.info("⚙️  Setting up query engine...")
    vector_store = await init_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)

    # Similarity threshold — filters out low confidence results
    similarity_filter = SimilarityPostprocessor(similarity_cutoff=0.5)
    node_postprocessors = [similarity_filter]

    # Reranker — reorders top-k results by relevance (disabled on memory-constrained deploys)
    enable_rerank = os.getenv("ENABLE_RERANK", "true").lower() == "true"
    if enable_rerank:
        logger.info("🔀 Reranking enabled")
        reranker = ColbertRerank(top_n=3)
        node_postprocessors.append(reranker)
    else:
        logger.info("🔀 Reranking disabled")

    return {
        "llm": llm,
        "vector_store": vector_store,
        "query_engine": index.as_query_engine(
            similarity_top_k=10,
            node_postprocessors=node_postprocessors,
        )
    }

def get_collection_size(llm_mode: str):
    match llm_mode:
        case "ollama":
            return 768
        case "gemini":
            return 3072
        case _:
            return 768