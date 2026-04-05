import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from config.ollama import setup_ollama
from config.logger import logger

DEFAULT_PATH = "./data"

def run(vector_store, path: str = DEFAULT_PATH) -> int:
    """Run data ingest script to Qdrant cluster"""
    try:
        logger.info("❕ Starting data ingestion.")
    
        # Setup models
        setup_ollama()

        # Load documents from /data
        logger.info("⚙️ Loading data...")
        documents = SimpleDirectoryReader(path).load_data()

        # Create index (this embeds + stores)
        logger.info("⚙️ Embedding and storing data...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        logger.info("✅ Data ingested into Qdrant!")

        file_count = sum(1 for f in os.listdir("./data") if os.path.isfile(os.path.join("./data", f)))
        return file_count
    except Exception as e:
        logger.error(f"‼️ Data ingestion failed: {e}")
        raise