from routers.base import router, QueryRequest, QueryResponse
from fastapi import HTTPException, Request
import services.ingest as ingest

@router.post("/ingest", response_model=QueryResponse)
def generate(request: Request, body: QueryRequest):
    try:
        vector_store = request.app.state.vector_store
        ingested_files = ingest.run(vector_store)
        response = f"Successfully ingested {ingested_files} documents."
        return QueryResponse(response=str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))