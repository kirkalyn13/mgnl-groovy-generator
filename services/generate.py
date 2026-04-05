import string
from fastapi import Request
from config.logger import log

def run(query: string, request: Request) -> string:
    try:
        log.info("💬 Query: {query}")
        query_engine = request.app.state.query_engine
        prompt = f"""
        You are a Magnolia CMS Groovy script generator.
        Return ONLY the raw Groovy script with no explanations, no markdown, no code blocks.
        
        Request: {query}
        """

        log.info("🔃 Generating Script")
        response = query_engine.query(prompt)

        return str(response).strip()
    except Exception as e:
        log.error(f"‼️ Failed to generate script: {e}")