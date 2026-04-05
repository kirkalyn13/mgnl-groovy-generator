from fastapi import FastAPI
from routers import generate, ingest

# Include all routers here
def register_routers(app: FastAPI):
    app.include_router(generate.router)
    app.include_router(ingest.router)