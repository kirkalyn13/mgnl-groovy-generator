from pydantic import BaseModel

class IngestRequest(BaseModel):
    path: str

class IngestResponse(BaseModel):
    success: bool
    message: str | None = None
