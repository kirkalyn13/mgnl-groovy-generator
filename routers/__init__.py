from fastapi import FastAPI
from routers import generate, ingest

def register_routers(app: FastAPI):
    """Register all defined Fast API routers here"""
    app.include_router(generate.router)
    app.include_router(ingest.router)