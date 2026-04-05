from routers.base import router, QueryRequest, QueryResponse, limiter
from fastapi import HTTPException, Request
from services.generate import run


@router.post("/generate", response_model=QueryResponse)
@limiter.limit("1/second")
def generate(request: Request, body: QueryRequest):
    try:
        query = body.query

        if (validate_query(query) == False):
            raise HTTPException(status_code=400, detail="Modification scripts are not allowed.")

        result = run(body.query, request)

        return QueryResponse(
            success=True,
            query=query,
            response=result["script"],
            retries=result["retries"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Validate if edit keywords are mentioned  
def validate_query(query: str) -> bool:
    edit_keywords = ["edit", "change", "modify", "update"]
    return not any(word in query for word in edit_keywords)
