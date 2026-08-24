import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers.base import router, limiter
from routers import health, scripts
from config.auth import verify_api_key


@pytest.fixture
def client():
    limiter.enabled = False
    app = FastAPI()
    app.include_router(router)
    app.state.vector_store = None
    app.dependency_overrides[verify_api_key] = lambda: True
    return TestClient(app)