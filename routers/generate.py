import string

from routers.base import router, QueryRequest, QueryResponse
from fastapi import HTTPException, Request
from services.generate import run

@router.post("/generate", response_model=QueryResponse)
def generate(request: Request, body: QueryRequest):
    try:
        query = body.query

        if (validate_query(query) == False):
            raise HTTPException(status_code=400, detail="Modification scripts are not allowed.")

        response = run(body.query, request)
        return QueryResponse(response=str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Validate if edit keywords are mentioned  
def validate_query(query: string) -> bool:
    edit_keywords = ["edit", "change", "modify", "update"]
    return not any(word in query for word in edit_keywords)
