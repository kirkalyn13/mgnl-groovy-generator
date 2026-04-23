from fastapi import HTTPException, Request
from routers.base import router, limiter
from config.settings import RATE_LIMIT
from dtos.describe import DescribeResponse
from services.describe import run
from config.logger import logger

@router.get("/v1/describe/{script_path:path}",
    response_model=DescribeResponse,
    summary="*Experimental* Describe an existing Groovy script from a Magnolia instance",
    description="Returns a natural language description of a Groovy script at the given path.",
)
@limiter.limit(RATE_LIMIT)
def describe(request: Request, script_path: str):
    try:
        result = run(request, script_path)
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