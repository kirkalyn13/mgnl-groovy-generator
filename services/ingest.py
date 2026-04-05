import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from config.ollama import setup_ollama
from config.logger import log

def run(vector_store) -> int:
    try:
        log.info("❕ Starting data ingestion.")
    
        # Setup models
        setup_ollama()

        # Load documents from /data
        log.info("⚙️ Loading data...")
        documents = SimpleDirectoryReader("./data").load_data()

        # Create index (this embeds + stores)
        log.info("⚙️ Embedding and storing data...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        log.info("✅ Data ingested into Qdrant!")

        file_count = sum(1 for f in os.listdir("./data") if os.path.isfile(os.path.join("./data", f)))
        return file_count
    except Exception as e:
        log.info(f"❗ Data ingested failed: {e}")