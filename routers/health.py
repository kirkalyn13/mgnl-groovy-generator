from routers.base import router

@router.get("/health")
def health():
    return {"status": "ok"}