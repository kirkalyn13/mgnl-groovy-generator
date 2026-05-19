from config.logger import logger
from config.settings import MIN_DOC_LENGTH

def validate_documents(documents: list) -> list:
    """Filter out empty or invalid documents."""
    valid = []
    for doc in documents:
        if not doc.text or len(doc.text.strip()) < MIN_DOC_LENGTH:
            logger.warning(f"⚠️ Skipping invalid document: {doc.metadata.get('file_name')}")
            continue
        valid.append(doc)
    logger.info(f"✅ {len(valid)}/{len(documents)} documents passed validation")
    return valid