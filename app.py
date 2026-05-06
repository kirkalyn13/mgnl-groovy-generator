from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.init import init
from config.langfuse import init_langfuse
from config.openapi import custom_openapi
from routers import register_routers
from config.settings import HOST, PORT, ALLOWED_ORIGINS
from config.logger import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs once when the app starts
    init_langfuse()
    qdrant = init()

    app.state.vector_store = qdrant["vector_store"]
    app.state.query_engine = qdrant["query_engine"]
    app.state.llm = qdrant["llm"]

    logger.info("✅ RAG engine ready")
    yield
 
    # Shutdown: clean up if needed
    logger.info("👋 Shutting down")

# Init App
app = FastAPI(title="Magnolia Groovy Script Generator", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# OpenAPI config
app.openapi = lambda: custom_openapi(app)

# Register routers
register_routers(app)

# Runn Uvicorn server
if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)