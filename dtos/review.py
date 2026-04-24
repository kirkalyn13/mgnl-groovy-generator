from pydantic import BaseModel

class ReviewResponse(BaseModel):
    success: bool
    path: str
    review: str