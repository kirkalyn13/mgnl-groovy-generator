from fastapi import APIRouter
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class BaseResponse(BaseModel):
    success: bool
    message: str | None = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    retries: int
    message: str | None = None