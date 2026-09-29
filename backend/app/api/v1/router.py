from fastapi import APIRouter
from app.api.v1.endpoints import health, predict, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predict.router, tags=["Prediction"])
api_router.include_router(reports.router, tags=["Reports"])