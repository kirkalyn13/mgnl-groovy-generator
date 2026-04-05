import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from config.ollama import setup_ollama

def run(vector_store) -> int:
    try:
        print("❕ Starting data ingestion.")
    
        # Setup models
        setup_ollama()

        # Load documents from /data
        print("⚙️ Loading data...")
        documents = SimpleDirectoryReader("./data").load_data()

        # Create index (this embeds + stores)
        print("⚙️ Embedding and storing data...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        print("✅ Data ingested into Qdrant!")

        file_count = sum(1 for f in os.listdir("./data") if os.path.isfile(os.path.join("./data", f)))
        return file_count
    except Exception as e:
        print(f"❗ Data ingested failed: {e}")