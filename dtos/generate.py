from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    workspaces: list[str] = []
    properties: list[str] = []

class QueryResponse(BaseModel):
    success: bool
    query: str
    script: str
    retries: int
    message: str | None = None