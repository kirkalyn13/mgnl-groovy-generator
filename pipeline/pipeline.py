from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, KeywordExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from config.logger import logger

async def run_pipeline(documents: list, vector_store) -> list:
    """Assemble and run the ingestion pipeline."""
    logger.info("⚙️ Running ingestion pipeline...")
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=64),
            TitleExtractor(),
            KeywordExtractor(keywords=10),
            Settings.embed_model,
        ],
        vector_store=vector_store,
        docstore=SimpleDocumentStore(),
        docstore_strategy="upserts_and_delete",
    )

    nodes = await pipeline.arun(documents=documents)
    logger.info(f"⚙️ Created {len(nodes)} nodes")

    for node in nodes[:3]:
        logger.info(f"📋 Node metadata: {node.metadata}")

    return nodes