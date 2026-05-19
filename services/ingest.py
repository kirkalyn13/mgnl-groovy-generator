import os
from pipeline.loader import load_documents
from pipeline.validator import validate_documents
from pipeline.enricher import add_metadata
from pipeline.pipeline import run_pipeline
from config.logger import logger
from config.settings import DEFAULT_DOCS_PATH, EXTENSIONS


async def run_ingest(vector_store, path: str = DEFAULT_DOCS_PATH) -> int:
    """Orchestrate the RAG ingestion pipeline."""
    try:
        logger.info("🟢 Starting data ingestion.")

        documents = load_documents(path)
        documents = validate_documents(documents)

        if not documents:
            raise ValueError("‼️ No valid documents found for ingestion.")

        documents = add_metadata(documents)
        nodes = await run_pipeline(documents, vector_store)

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