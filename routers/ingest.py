from routers.base import router, limiter
from fastapi import HTTPException, Request
from dtos.ingest import IngestRequest, IngestResponse
from services.ingest import run

@router.post("/v1/ingest", 
             response_model=IngestResponse,
             summary="Ingest Groovy scripts",
             description="Loads and embeds Groovy scripts from the data folder into Qdrant.")
@limiter.limit("1/second")
def generate(request: Request, body: IngestRequest):
    try:
        path = body.path
        vector_store = request.app.state.vector_store
        ingested_files = run(vector_store, path)
        response = f"Successfully ingested {ingested_files} documents."

        return IngestResponse(success=True, message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))