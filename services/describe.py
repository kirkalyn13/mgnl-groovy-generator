import os
from dotenv import load_dotenv
from config.logger import logger
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.script import TOOLS
from langfuse.llama_index import LlamaIndexInstrumentor

load_dotenv()
TOOL_LLM = os.getenv("TOOL_CALL_LLM", "qwen3.5")
instrumentor = LlamaIndexInstrumentor()

def run_describe(script_path: str) -> str:
    """Describe a Groovy script based on its path in Magnolia."""
    with instrumentor.observe(
        user_id="api-user",
        session_id=script_path[:20],
        tags=["generate", "groovy"]
    ):
        try:
            llm = ChatOllama(model=TOOL_LLM, temperature=0)
            messages = [{"role": "user", "content": f"Fetch and explain the Groovy script at path: {script_path}"}]

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