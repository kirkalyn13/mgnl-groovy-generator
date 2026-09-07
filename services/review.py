import os
from fastapi import Request
from dotenv import load_dotenv
from langfuse import get_client
from config.logger import logger
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.script import TOOLS

load_dotenv()
REVIEW_LLM = os.getenv("GEN_AI_MODEL", "mistral")
TOOL_LLM = os.getenv("TOOL_CALL_MODEL", "qwen3.5")
CONTEXT_QUERY = (
    "Magnolia CMS Groovy script examples with documented use cases, "
    "best practices, and common pitfalls, used as reference material "
    "for reviewing and critiquing similar scripts"
)

def run_review(request: Request, script_path: str) -> str:
    """Review a Groovy script based on its path in Magnolia."""
    with get_client().start_as_current_observation(as_type="span", name="review_script"):
        try:
            logger.info(f"💬 Reviewing groovy script from path: {script_path}")

            query_engine = request.app.state.query_engine
            tool_llm = ChatOllama(model=TOOL_LLM, temperature=0)
            review_llm = ChatOllama(model=REVIEW_LLM, temperature=0)

            # Fetch Script
            logger.info("🔧 Fetching script via tool agent...")
            tool_agent = create_agent(model=tool_llm, tools=TOOLS)
            fetch_response = tool_agent.invoke({
                "messages": [{"role": "user", "content": f"Fetch the Groovy script at path: {script_path}"}]
            })
            script = fetch_response["messages"][-1].content
            logger.info("✅ Script fetched successfully")

            # Review Script
            logger.info("🔍 Reviewing script...")
            context = str(query_engine.query(CONTEXT_QUERY))
            review_prompt = f"""
            You are a code reviewer for a Magnolia CMS Groovy script.
            Review the following script and suggest optimizations, improvements,
            and any potential issues. Only respond with the code review details.

            Script:
            {script}

            Context for reference scripts: {context}
            """
            review_response = review_llm.invoke(review_prompt)
            logger.info("✅ Script reviewed successfully")

            return review_response.content

        except Exception as e:
            logger.error(f"‼️ Review execution failed: {e}")
            raise