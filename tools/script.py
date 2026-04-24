import os
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from config.logger import logger
from config.settings import REQUEST_TIMEOUT

load_dotenv()
MAGNOLIA_URL = os.getenv("MAGNOLIA_SCRIPTS_REST_DELIVERY_URL")
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

TOOLS = [fetch_script]