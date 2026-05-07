from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    workspaces: list[str] = []
    properties: list[str] = []
    allow_modifications: bool = False
    session_id: str | None = None

class QueryResponse(BaseModel):
    success: bool
    query: str
    script: str
    retries: int
    message: str | None = None