import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from config.logger import logger
from config.settings import DEFAULT_DOCS_PATH, EXTENSIONS

def run_ingest(vector_store, path: str = DEFAULT_DOCS_PATH) -> int:
    """Run data ingest script to Qdrant cluster"""
    try:
        logger.info("🟢 Starting data ingestion.")

        # Load documents from /data
        logger.info("⚙️ Loading data...")
        documents = SimpleDirectoryReader(path, required_exts=EXTENSIONS).load_data()

        # Create index (this embeds + stores)
        logger.info("⚙️ Embedding and storing data...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        file_count = sum(1 for f in os.listdir("./data") if os.path.isfile(os.path.join("./data", f)) and any(f.endswith(ext) for ext in EXTENSIONS))

        logger.info(f"✅ Ingested {file_count} file(s) to Qdrant!")

        return file_count
    except Exception as e:
        logger.error(f"‼️ Data ingestion failed: {e}")
        raise