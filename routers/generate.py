from routers.base import router, limiter
from dtos.generate import QueryRequest, QueryResponse
from fastapi import HTTPException, Request
from services.generate import run
from config.logger import logger
from config.settings import EDIT_KEYWORDS, GROOVY_REQUEST_KEYWORDS, GROOVY_KEYWORDS

@router.post("/generate",
             response_model=QueryResponse,
             summary="Generate Groovy scripts",
             description="Generate Groovy scripts based from the specified query.")
@limiter.limit("1/second")
def generate(request: Request, body: QueryRequest):
    try:
        query = body.query

        # Input guard rails
        if not is_groovy_request(query):
            logger.warning(f"⚠️ Blocked non-Groovy request: {query}")
            raise HTTPException(status_code=400, detail="Only Magnolia CMS Groovy script requests are allowed.")
        
        if not is_read_only(query):
            logger.warning(f"⚠️ Blocked modification query: {query}")
            raise HTTPException(status_code=400, detail="Modification scripts are not allowed.")

        result = run(query, request)
        script = result["script"]

        # Output guard rails
        if not is_groovy_script(script):
            logger.warning(f"⚠️ Response does not appear to be a Groovy script")
            raise HTTPException(status_code=500, detail="Generated output is not a valid Groovy script.")

        if not is_safe_script(script):
            logger.warning(f"⚠️ Dangerous script detected, blocking response")
            raise HTTPException(status_code=500, detail="Generated script contains unsafe operations.")

        return QueryResponse(
            success=True,
            query=query,
            response=script,
            retries=result["retries"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"‼️ Failed to generate script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def is_groovy_request(query: str) -> bool:
    """Block queries that are not related to Groovy script generation."""
    return any(word in query.lower() for word in GROOVY_REQUEST_KEYWORDS)
 
def is_read_only(query: str) -> bool:
    """Block queries that attempt to modify data."""
    return not any(word in query.lower() for word in EDIT_KEYWORDS)

def is_groovy_script(response: str) -> bool:
    """Ensure the response looks like an actual Groovy script."""
    return any(word in response for word in GROOVY_KEYWORDS)

def is_safe_script(response: str) -> bool:
    """Block scripts that contain dangerous operations."""
    dangerous = ["Runtime.exec", "ProcessBuilder", "System.exit", "File.delete", "DROP", "rm -rf"]
    return not any(word in response for word in dangerous)