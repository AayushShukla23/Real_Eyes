from fastapi import APIRouter
from app.core.config import settings
from app.core.database import db_manager
from app.ml.model_loader import model_manager
from app.schemas.prediction import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model_loaded=model_manager.is_loaded,
        db_connected=db_manager.db is not None,
    )