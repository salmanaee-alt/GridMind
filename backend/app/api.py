from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {
        "project": "GridMind AI",
        "status": "running"
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }