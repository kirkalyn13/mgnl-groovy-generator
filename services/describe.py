import os
from fastapi import Request
from dotenv import load_dotenv
from langfuse import get_client
from config.logger import logger
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.script import TOOLS

load_dotenv()
TOOL_LLM = os.getenv("TOOL_CALL_MODEL", "qwen3.5")
CONTEXT_QUERY = (
    "Magnolia CMS Groovy script examples paired with clear descriptions "
    "of their purpose, functionality, and use case, for generating "
    "human-readable explanations of similar scripts"
)

def run_describe(request: Request, script_path: str) -> str:
    """Describe a Groovy script based on its path in Magnolia."""
    with get_client().start_as_current_observation(as_type="span", name="describe_script"):
        try:
            query_engine = request.app.state.query_engine
            llm = ChatOllama(model=TOOL_LLM, temperature=0)

            context = str(query_engine.query(CONTEXT_QUERY))
            messages = [{"role": "user", "content": f""""
            Fetch and explain the Groovy script at path: {script_path}
            
            Context from reference scripts: {context}
            """}]

            agent = create_agent(
                model=llm,
                tools=TOOLS
            )

            logger.info(f"💬 Describe groovy script from path {script_path}")
            response = agent.invoke({"messages": messages})

            return response["messages"][-1].content
        except Exception as e:
            logger.error(f"‼️ Describe execution failed: {e}")
            raise