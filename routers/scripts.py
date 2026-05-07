from config.auth import verify_api_key
from config.settings import RATE_LIMIT
from fastapi import HTTPException, Request, Depends
from routers.base import router, limiter
from dtos.generate import QueryRequest, QueryResponse
from dtos.ingest import IngestRequest, IngestResponse
from dtos.review import ReviewResponse
from dtos.describe import DescribeResponse
from services.generate import run_generate
from services.ingest import run_ingest
from services.review import run_review
from services.describe import run_describe
from config.logger import logger

@router.post("/v1/scripts/generate",
    response_model=QueryResponse,
    summary="Generate Groovy scripts",
    description="Generate Groovy scripts based from the specified query.",
    dependencies=[Depends(verify_api_key)])
@limiter.limit(RATE_LIMIT)
def generate(request: Request, body: QueryRequest):
    """Router for script generation"""
    try:
        result = run_generate(request, body.query, body.workspaces, body.properties, body.allow_modifications)
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
    
@router.post("/v1/scripts/ingest", 
    response_model=IngestResponse,
    summary="Ingest Groovy scripts",
    description="Loads and embeds Groovy scripts from the data folder into Qdrant.",
    dependencies=[Depends(verify_api_key)])
@limiter.limit(RATE_LIMIT)
def ingest(request: Request, body: IngestRequest):
    """Router for scripts document ingestion"""
    try:
        path = body.path
        vector_store = request.app.state.vector_store
        ingested_files = run_ingest(vector_store, path)
        response = f"Successfully ingested {ingested_files} documents."

        return IngestResponse(success=True, message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/v1/scripts/review/{script_path:path}",
    response_model=ReviewResponse,
    summary="Review an existing Groovy script from a Magnolia instance",
    description="Returns a natural language code review of a Groovy script at the given path.",
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit(RATE_LIMIT)
def review(request: Request, script_path: str):
    """Router for script review"""
    try:
        result = run_review(script_path)
        return ReviewResponse(
            success=True,
            path=script_path,
            review=result
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"‼️ Failed to review script: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/v1/scripts/describe/{script_path:path}",
    response_model=DescribeResponse,
    summary="Describe an existing Groovy script from a Magnolia instance",
    description="Returns a natural language description of a Groovy script at the given path.",
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit(RATE_LIMIT)
def describe(request: Request, script_path: str):
    """Router for script description"""
    try:
        result = run_describe(script_path)
        return DescribeResponse(
            success=True,
            path=script_path,
            description=result
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"‼️ Failed to describe script: {e}")
        raise HTTPException(status_code=500, detail=str(e))