from datetime import datetime
from config.logger import logger

def add_metadata(documents: list) -> list:
    """Enrich documents with custom metadata fields."""
    for doc in documents:
        filename = doc.metadata.get("file_name", "")
        doc.metadata.update({
            "file_type": ".groovy",
            "source": "magnolia_cms",
            "ingested_at": str(datetime.utcnow()),
            "script_name": filename.replace(".groovy", ""),
        })
        doc.excluded_embed_metadata_keys = ["ingested_at", "source"]
        doc.excluded_llm_metadata_keys = ["ingested_at"]
    logger.info(f"✅ Metadata enriched for {len(documents)} documents")
    return documents