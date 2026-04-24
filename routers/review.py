from fastapi import HTTPException, Request
from routers.base import router, limiter
from config.settings import RATE_LIMIT
from dtos.review import ReviewResponse
from services.review import run
from config.logger import logger

@router.get("/v1/review/{script_path:path}",
    response_model=ReviewResponse,
    summary="Review an existing Groovy script from a Magnolia instance",
    description="Returns a natural language code review of a Groovy script at the given path.",
)
@limiter.limit(RATE_LIMIT)
def describe(request: Request, script_path: str):
    try:
        result = run(script_path)
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