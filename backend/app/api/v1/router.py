from fastapi import APIRouter
from backend.app.api.v1.routes.businesses import router as businesses_router
from backend.app.api.v1.routes.health import router as health_router
from backend.app.api.v1.review_sessions import router as review_sessions_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(businesses_router)
api_router.include_router(review_sessions_router)
