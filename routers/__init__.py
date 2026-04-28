from fastapi import FastAPI
from routers import scripts

def register_routers(app: FastAPI):
    """Register all defined Fast API routers here"""
    app.include_router(scripts.router)
