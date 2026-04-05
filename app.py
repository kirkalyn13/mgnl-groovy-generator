from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from config.init import init
from routers import generate
from config.settings import HOST, PORT
from config.logger import logger

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs once when the app starts
    qdrant = init()
    app.state.vector_store = qdrant["vector_store"]
    app.state.query_engine = qdrant["query_engine"]

    logger.info("✅ RAG engine ready")
    yield

    # Shutdown: clean up if needed
    logger.info("👋 Shutting down")

app = FastAPI(title="Magnolia Groovy Script Generator", lifespan=lifespan)
app.include_router(generate.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)