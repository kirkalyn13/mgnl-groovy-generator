from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    workspaces: list[str] = []
    properties: list[str] = []

class QueryResponse(BaseModel):
    query: str
    response: str
    retries: int
    message: str | None = None