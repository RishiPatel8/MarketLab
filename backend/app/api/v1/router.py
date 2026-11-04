from fastapi import APIRouter
from app.api.v1.endpoints import research, instruments, experiments, documents, internal, system, portfolios, strategies

api_router = APIRouter()

api_router.include_router(research.router, prefix="/research", tags=["Research"])
api_router.include_router(instruments.router, prefix="/instruments", tags=["Instruments & Market Data"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Strategy Lab & Experiments"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies & Quantitative Modeling"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["Virtual Portfolios & Simulation"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents & RAG"])
api_router.include_router(internal.router, prefix="/internal", tags=["Internal Automation"])
api_router.include_router(system.router, prefix="/system", tags=["System & Integrations"])
