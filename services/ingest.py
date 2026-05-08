import os
import nest_asyncio
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from config.logger import logger
from config.settings import DEFAULT_DOCS_PATH, EXTENSIONS

nest_asyncio.apply()

async def run_ingest(vector_store, path: str = DEFAULT_DOCS_PATH) -> int:
    """Run data ingest script to Qdrant cluster"""
    try:
        logger.info("🟢 Starting data ingestion.")

        # Load documents
        logger.info("⚙️ Loading data...")
        documents = SimpleDirectoryReader(path, required_exts=EXTENSIONS).load_data()

        # Pipeline — chunking + metadata extraction
        logger.info("⚙️ Running ingestion pipeline...")
        pipeline = IngestionPipeline(
            transformations=[
                # 1 — Chunk documents into nodes
                SentenceSplitter(
                    chunk_size=512,
                    chunk_overlap=64,
                ),
                # 2 — Extract metadata for filtering
                TitleExtractor(),
                Settings.embed_model
            ],
            vector_store=vector_store,
        )

        nodes = pipeline.run(documents=documents)
        logger.info(f"⚙️ Created {len(nodes)} nodes from documents")

        # Log metadata for verification
        for node in nodes[:3]:  # preview first 3
            logger.info(f"📋 Node metadata: {node.metadata}")

        file_count = sum(
            1 for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
            and any(f.endswith(ext) for ext in EXTENSIONS)
        )

        logger.info(f"✅ Ingested {file_count} file(s) → {len(nodes)} nodes to Qdrant!")
        return file_count

    except Exception as e:
        logger.error(f"‼️ Data ingestion failed: {e}")
        raise