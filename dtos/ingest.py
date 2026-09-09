from pydantic import BaseModel

class IngestRequest(BaseModel):
    path: str
    source: str | None = None

class IngestResponse(BaseModel):
    success: bool
    message: str | None = None
