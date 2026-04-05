from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from config.init import init
from routers import register_routers
from config.settings import HOST, PORT
from config.logger import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
limiter = Limiter(key_func=get_remote_address)

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

# Init App
app = FastAPI(title="Magnolia Groovy Script Generator", lifespan=lifespan)

# Config Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
register_routers(app)

# Health Check
@app.get("/health")
def health():
    return {"status": "ok"}

# Runn Uvicorn server
if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)