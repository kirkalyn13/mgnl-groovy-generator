import os
import httpx
from dotenv import load_dotenv
from config.logger import logger
from config.settings import REQUEST_TIMEOUT
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

load_dotenv()
MAGNOLIA_URL = os.getenv("MAGNOLIA_SCRIPTS_REST_DELIVERY_URL")
LLM = os.getenv("TOOL_CALL_LLM", "qwen3")
MAGNOLIA_USERNAME = os.getenv("MAGNOLIA_USERNAME", "superuser")
MAGNOLIA_PASSWORD = os.getenv("MAGNOLIA_PASSWORD", "superuser")


@tool
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

def run(script_path: str) -> str:
    """Describe a Groovy script based on its path in Magnolia."""
    try:
        llm = ChatOllama(model="qwen3", temperature=0)
        messages = [{"role": "user", "content": f"Fetch and explain the Groovy script at path: {script_path}"}]

        agent = create_agent(
            model=llm,
            tools=[fetch_script]
        )

        logger.info(f"💬 Describe groovy script from path {script_path}")
        response = agent.invoke({"messages": messages})

        return response["messages"][-1].content
    except Exception as e:
        logger.error(f"‼️ Describe execution failed: {e}")
        raise