import os
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, KeywordExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.llms.ollama import Ollama
from config.logger import logger

# Ingestion is done from local files decoupling it from Gemini or external API usage
# This approach should be enough since ingestion is done from local files for this setup
extraction_llm = Ollama(model="mistral", base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"), request_timeout=60)

async def run_pipeline(documents: list, vector_store) -> list:
    """Assemble and run the ingestion pipeline."""
    logger.info("⚙️ Running ingestion pipeline...")
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=64),
            TitleExtractor(llm=extraction_llm),
            KeywordExtractor(keywords=10, llm=extraction_llm),
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