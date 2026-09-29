from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.database import db_manager
from app.ml.model_loader import model_manager
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await db_manager.connect()

    try:
        model_manager.load()
    except Exception as e:
        logger.error(f"Model load failed: {e}. Running in DUMMY mode.")

    yield

    # --- SHUTDOWN ---
    await db_manager.disconnect()
    logger.info("Shutting down RealEyes backend.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Deepfake Video Detection API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "RealEyes Deepfake Detection API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }