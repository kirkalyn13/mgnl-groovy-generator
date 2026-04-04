from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from config.ollama import setup_ollama
from config.qdrant import get_vector_store

def ingest():
    print("❕ Starting data ingestion.")
    
    # Setup models
    setup_ollama()

    # Load documents from /data
    print("⚙️ Loading data...")
    documents = SimpleDirectoryReader("./data").load_data()

    # Create index (this embeds + stores)
    print("⚙️ Embedding and storing data...")
    vector_store=get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )

    print("✅ Data ingested into Qdrant!")

ingest()