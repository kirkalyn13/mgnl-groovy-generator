from routers.base import router, limiter
from dtos.generate import QueryRequest, QueryResponse
from fastapi import HTTPException, Request
from services.generate import run
from config.logger import logger

@router.post("/v1/generate",
             response_model=QueryResponse,
             summary="Generate Groovy scripts",
             description="Generate Groovy scripts based from the specified query.")
@limiter.limit("1/second")
def generate(request: Request, body: QueryRequest):
    try:
        result = run(body.query, body.workspaces, body.properties, request)
        return QueryResponse(
            success=True,
            query=body.query,
            script=result["script"],
            retries=result["retries"],
        )
    except ValueError as e:
        logger.warning(f"⚠️ {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"‼️ Failed to generate script: {e}")
        raise HTTPException(status_code=500, detail=str(e))