from fastapi import FastAPI
from routers import health, generate, ingest, describe

def register_routers(app: FastAPI):
    """Register all defined Fast API routers here"""
    app.include_router(health.router)
    app.include_router(generate.router)
    app.include_router(ingest.router)
    app.include_router(describe.router)