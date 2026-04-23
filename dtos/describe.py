from pydantic import BaseModel

class DescribeResponse(BaseModel):
    success: bool
    path: str
    description: str