from config.logger import logger
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.describe import TOOLS

def run(script_path: str) -> str:
    """Describe a Groovy script based on its path in Magnolia."""
    try:
        llm = ChatOllama(model="qwen3", temperature=0)
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