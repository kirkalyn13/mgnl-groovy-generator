from datetime import datetime

from llama_index.core import Document, SimpleDirectoryReader
from config.logger import logger
from config.settings import DEFAULT_DOCS_PATH, EXTENSIONS

def load_documents(path: str = DEFAULT_DOCS_PATH) -> list:
    """Load documents from the specified path."""
    logger.info(f"⚙️ Loading documents from {path}...")
    documents = SimpleDirectoryReader(path, required_exts=EXTENSIONS).load_data()
    logger.info(f"📄 Loaded {len(documents)} documents")
    return documents

def convert_to_document(data: list):
    """Convert raw Magnolia script dicts into llama_index Document objects."""
    documents = []
    for item in data:
        filename = item.get("@name", "")
        doc = Document(
            text=item.get("text", ""),
            metadata={
                "file_name": filename,
                "file_type": ".groovy",
                "source": "magnolia_cms",
                "ingested_at": str(datetime.utcnow()),
                "script_name": filename.replace(".groovy", ""),
            },
            excluded_embed_metadata_keys=["ingested_at", "source"],
            excluded_llm_metadata_keys=["ingested_at"],
        )
        documents.append(doc)
    return documents