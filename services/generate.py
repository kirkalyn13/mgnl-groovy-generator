import re
import json
from fastapi import Request
from langfuse import get_client
from config import langfuse
from config.logger import logger
from config.settings import MAX_RETRIES
from config.session import USING_REDIS, create_session, get_session, add_to_session, format_history

def run_generate(request: Request, query: str, workspaces: list[str], properties: list[str], allow_modifications: bool, session_id=None) -> dict:
    """Run LLM-assisted groovy script generation"""
    try:
        logger.info(f"💬 Query: {query}")
        llm = request.app.state.llm
        query_engine = request.app.state.query_engine
        sessions = request.app.state.sessions

        # Create new session if none provided or not found
        if not session_id or not get_session(sessions, session_id):
            session_id, _ = create_session()
            if not USING_REDIS:
                sessions[session_id] = get_session(sessions, session_id) or _

        session = get_session(sessions, session_id)
        history = format_history(session)

        # Step 1 — Validate request
        logger.info("🔎 Validating request...")
        validation = validate_request(query, llm)
        logger.info(f"🔎 Validation result: {validation}")

        if not validation.get("is_groovy_request"):
            raise ValueError(f"Not a Groovy request: {validation.get('reason')}")

        if not validation.get("is_read_only") and allow_modifications != True:
            raise ValueError(f"Modification request blocked: {validation.get('reason')}")

        # Step 2 — Retrieve context
        logger.info("🔍 Retrieving context from Qdrant...")
        context = str(query_engine.query(query))

        # Step 3 — Generate script with retries
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔃 Generating script (attempt {attempt}/{MAX_RETRIES})")

            result = generate_script(query, workspaces, properties, context, llm, history)
            script = clean_script(result.get("script", ""))

            if not result.get("is_valid_groovy"):
                logger.warning(f"⚠️ LLM flagged output as invalid Groovy on attempt {attempt}, retrying...")
                continue

            if not result.get("is_safe"):
                logger.warning(f"⚠️ LLM flagged script as unsafe on attempt {attempt}, retrying...")
                continue

            logger.info("✅ Script generated successfully")

            # Store on success
            add_to_session(sessions, session_id, query, script)

            return {
                "script": script,
                "retries": attempt - 1,
                "session_id": session_id
            }

        raise ValueError("Failed to generate a valid script after max retries.")

    except Exception as e:
        logger.error(f"‼️ Failed to generate script: {e}")
        raise


def clean_script(response: str) -> str:
    """Remove markdown code blocks from response."""
    return re.sub(r"^```[\w]*\n?|```$", "", response.strip(), flags=re.MULTILINE).strip()

def validate_request(query: str, llm) -> dict:
    """Use LLM to validate if the request is a safe, read-only Groovy request."""
    with get_client().start_as_current_observation(as_type="span", name="validate_request"):
        prompt = f"""
        You are a validator for a Magnolia CMS Groovy script generator.
        Respond ONLY with a JSON object, no explanation, no markdown.

        Assess the following request and return this exact structure:
        {{
            "is_groovy_request": true or false,
            "is_read_only": true or false,
            "reason": "brief explanation"
        }}

        Guidelines for is_read_only:
        - TRUE: fetch, get, pull, retrieve, list, show, display, find, search, query, read, check, view
        - FALSE: update, edit, modify, delete, remove, drop, create, insert, write, save, publish

        Request: {query}
        """
        response = str(llm.complete(prompt)).strip()
        clean = re.sub(r"^```[\w]*\n?|```$", "", response, flags=re.MULTILINE).strip()
        return json.loads(clean)

def generate_script(query: str, workspaces: list[str], properties: list[str], context: str, llm, history="") -> dict:
    """Use LLM to generate a Groovy script and validate the output."""
    with get_client().start_as_current_observation(as_type="span", name="generate_script"):
        workspaces_clause = f"\nTarget Magnolia workspaces: {', '.join(workspaces)}." if workspaces else ""
        properties_clause = f"\nThe script must include the following properties: {', '.join(properties)}." if properties else ""
        history_clause = f"\n{history}" if history else ""

        prompt = f"""
        You are a Magnolia CMS Groovy script generator.
        Respond ONLY with a JSON object, no explanation, no markdown.

        Generate a Groovy script and return this exact structure:
        {{
            "script": "the raw Groovy script here",
            "is_valid_groovy": true or false,
            "is_safe": true or false
        }}

        Rules:
        - script must be raw Groovy only, no markdown, no code blocks
        - is_valid_groovy must be true if the script is valid Groovy
        - is_safe must be false if the script contains Runtime.exec, System.exit, File.delete, or shell commands
        {workspaces_clause}
        {properties_clause}

        {history_clause}
        Request: {query}
        Context from examples: {context}
        """
        response = str(llm.complete(prompt)).strip()
        clean = re.sub(r"^```[\w]*\n?|```$", "", response, flags=re.MULTILINE).strip()
        return json.loads(clean)