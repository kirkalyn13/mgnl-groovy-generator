import os
import httpx
from fastapi import Request
from dotenv import load_dotenv
from ollama import chat
from config.logger import logger
from config.settings import REQUEST_TIMEOUT

load_dotenv()
MAGNOLIA_URL = os.getenv("MAGNOLIA_SCRIPTS_REST_DELIVERY_URL")
LLM = os.getenv("TOOL_CALL_LLM", "qwen3")
MAGNOLIA_USERNAME = os.getenv("MAGNOLIA_USERNAME", "superuser")
MAGNOLIA_PASSWORD = os.getenv("MAGNOLIA_PASSWORD", "superuser")

def fetch_script(script_path: str) -> str:
    """Fetch a Groovy script from the Magnolia REST delivery API.

    Args:
        script_path: The relative path to the script node in Magnolia e.g. my-script

    Returns:
        A dict containing the script text and raw response.
    """
    endpoint = f"{MAGNOLIA_URL}/{script_path}"
    logger.info(f"🌐 Fetching script from: {endpoint}")

    response = httpx.get(endpoint, timeout=REQUEST_TIMEOUT, auth=(MAGNOLIA_USERNAME, MAGNOLIA_PASSWORD))

    if response.status_code == 404:
        raise FileNotFoundError(f"Script not found at path: {script_path}")

    if response.status_code != 200:
        raise Exception(f"Failed to fetch script: {response.status_code} — {response.text}")

    data = response.json()
    text = data.get("text")

    if not text:
        raise ValueError(f"No 'text' field found in response for path: {script_path}")

    return text


def run(request: Request, script_path: str) -> str:
    """Describe a Groovy script based on its path in Magnolia."""
    messages = [{"role": "user", "content": f"Fetch and explain the Groovy script at path: {script_path}"}]

    response = chat(model=LLM, messages=messages, tools=[fetch_script], think=True)
    messages.append(response.message)

    if response.message.tool_calls:
        call = response.message.tool_calls[0]
        logger.info(f"🔧 Tool called: {call.function.name} with args: {call.function.arguments}")

        try:
            result = fetch_script(**call.function.arguments)
        except Exception as e:
            logger.error(f"‼️ Tool execution failed: {e}")
            raise

        messages.append({
            "role": "tool",
            "tool_name": call.function.name,
            "content": result
        })

        final_response = chat(model=LLM, messages=messages, think=True)

        return final_response.message.content

    return response.message.content