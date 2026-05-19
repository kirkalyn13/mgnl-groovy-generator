from llama_index.core import SimpleDirectoryReader
from config.logger import logger
from config.settings import DEFAULT_DOCS_PATH, EXTENSIONS

def load_documents(path: str = DEFAULT_DOCS_PATH) -> list:
    """Load documents from the specified path."""
    logger.info(f"⚙️ Loading documents from {path}...")
    documents = SimpleDirectoryReader(path, required_exts=EXTENSIONS).load_data()
    logger.info(f"📄 Loaded {len(documents)} documents")
    return documents