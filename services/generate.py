import re
from fastapi import Request
from config.logger import logger
from config.settings import UNWANTED_RESPONSE_KEYWORDS, MAX_RETRIES

def run(query: str, workspaces: list[str], properties: list[str], request: Request) -> {str, str}:
    """Run generate script query to Qdrant cluster"""
    try:
        logger.info(f"💬 Query: {query}")
        query_engine = request.app.state.query_engine

        workspaces_clause = (
        f"\nThe script must query the data from the following workspaces: {', '.join(workspaces)}."
        if workspaces else ""
        )

        properties_clause = (
        f"\nThe script must include the following properties: {', '.join(properties)}."
        if properties else ""
        )
        
        prompt = f"""
        You are a Magnolia CMS Groovy script generator.
        Return ONLY the raw Groovy script with no explanations, no markdown, no code blocks.
        {workspaces_clause}
        {properties_clause}

        Request: {query}
        """

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔃 Generating script (attempt {attempt}/{MAX_RETRIES})")
            response = str(query_engine.query(prompt)).strip()

            if not contains_unwanted(response):
                logger.info("✅ Script generated successfully")
                return { "script": clean_script(response), "retries": attempt - 1 }
            logger.warning(f"⚠️ Unwanted content detected on attempt {attempt}, retrying...")

        logger.error("‼️ Max retries reached, response still contains unwanted content")
        raise ValueError("Failed to generate a clean script after max retries")

    except Exception as e:
        logger.error(f"‼️ Failed to generate script: {e}")
        raise

def contains_unwanted(text: str) -> bool:
    """Validate response if it contains unwanted keywords e.g edit keywords"""
    return any(word in text.lower() for word in UNWANTED_RESPONSE_KEYWORDS)

def clean_script(response: str) -> str:
    """Remove markdown code blocks from response."""
    return re.sub(r"^```[\w]*\n?|```$", "", response.strip(), flags=re.MULTILINE).strip()