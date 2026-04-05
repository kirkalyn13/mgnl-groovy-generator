from routers.base import router, QueryRequest, QueryResponse
from fastapi import HTTPException, Request

@router.post("/generate", response_model=QueryResponse)
def generate(request: Request, body: QueryRequest):
    try:
        query_engine = request.app.state.query_engine
        response = query_engine.query(body.query)
        return QueryResponse(response=str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))