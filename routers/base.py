from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

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