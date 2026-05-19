from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.ingest import run_ingest
from config.logger import logger
from config.settings import SCHEDULE_HOURS

def run_pipeline_scheduler(vector_store):
    """Run RAG Pipeline job scheduler"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_ingest,
        "interval",
        hours=SCHEDULE_HOURS,
        args=[vector_store],
        id="ingest_job",
    )
    scheduler.start()
    logger.info(f"⏰ RAG Pipeline schedule set every {SCHEDULE_HOURS} hrs")
