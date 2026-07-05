from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="GridMind AI",
    description="The Intelligence Layer for Power Infrastructure",
    version="0.1.0"
)

app.include_router(router)