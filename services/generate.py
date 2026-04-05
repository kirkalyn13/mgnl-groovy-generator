from fastapi import Request
from config.logger import logger
from config.settings import UNWANTED_RESPONSE_KEYWORDS, MAX_RETRIES

# Run generate script query
def run(query: str, request: Request) -> {str, str}:
    try:
        logger.info(f"💬 Query: {query}")
        query_engine = request.app.state.query_engine
        prompt = f"""
        You are a Magnolia CMS Groovy script generator.
        Return ONLY the raw Groovy script with no explanations, no markdown, no code blocks.
        
        Request: {query}
        """

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔃 Generating script (attempt {attempt}/{MAX_RETRIES})")
            response = str(query_engine.query(prompt)).strip()

            if not contains_unwanted(response):
                logger.info("✅ Script generated successfully")
                return { "script": response, "retries": attempt - 1 }
            logger.warning(f"⚠️ Unwanted content detected on attempt {attempt}, retrying...")

        logger.error("‼️ Max retries reached, response still contains unwanted content")
        raise ValueError("Failed to generate a clean script after max retries")

    except Exception as e:
        logger.error(f"‼️ Failed to generate script: {e}")
        raise

# Validate response if it contains unwanted keywords
# Keywords are usually edit syntax
def contains_unwanted(text: str) -> bool:
    return any(word in text.lower() for word in UNWANTED_RESPONSE_KEYWORDS)