import asyncio
import click

from config.init import init
from services.ingest import run_ingest

@click.command()
@click.option(
    "--path",
    default="./docs",
    help="Document path"
)
def ingest(path):
    """Run RAG ingest pipeline via CLI"""
    async def _run():
        print("💻 Triggered data ingestion via CLI")
        qdrant = await init()
        count = await run_ingest(qdrant["vector_store"])

        print(f"✅ Successfully ingested {count} nodes via CLI run.")

    asyncio.run(_run())


if __name__ == "__main__":
    ingest()