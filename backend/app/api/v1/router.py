from fastapi import APIRouter
from app.api.v1.endpoints import research, instruments, experiments, documents, internal

api_router = APIRouter()

api_router.include_router(research.router, prefix="/research", tags=["Research"])
api_router.include_router(instruments.router, prefix="/instruments", tags=["Instruments & Market Data"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Strategy Lab & Experiments"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents & RAG"])
api_router.include_router(internal.router, prefix="/internal", tags=["Internal Automation"])
