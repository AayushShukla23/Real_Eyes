import anyio
import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File

from app.core.logging import logger
from app.core.database import db_manager
from app.schemas.prediction import PredictionResponse
from app.services.video_service import validate_and_save_upload, cleanup_temp_file
from app.ml.predictor import predict_video

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict_deepfake(file: UploadFile = File(...)):
    """
    Accept a video, run deepfake detection, save report to MongoDB Atlas, and return response.
    """
    temp_path = None

    try:
        # Step 1: Validate and save temp file
        temp_path = await validate_and_save_upload(file)
        file_size = os.path.getsize(temp_path)

        # Step 2: Run inference in threadpool
        logger.info(f"Starting inference for: {file.filename}")
        ml_result = await anyio.to_thread.run_sync(predict_video, temp_path)

        # Step 3: Package full report document
        report_id = f"rep_{uuid.uuid4().hex[:10]}"
        created_at = datetime.now(timezone.utc).isoformat()

        report_document = {
            "report_id": report_id,
            "filename": file.filename or "uploaded_video.mp4",
            "file_size_bytes": file_size,
            "prediction": ml_result["prediction"],
            "confidence": ml_result["confidence"],
            "raw_score": ml_result["raw_score"],
            "model_metadata": ml_result["model_metadata"],
            "processing_time_ms": ml_result["processing_time_ms"],
            "frames_analyzed": ml_result["frames_analyzed"],
            "created_at": created_at,
        }

        # Step 4: Persist to MongoDB Atlas
        if db_manager.db is not None:
            try:
                await db_manager.db["reports"].insert_one(dict(report_document))
                logger.info(f"Saved report {report_id} to MongoDB Atlas.")
            except Exception as db_err:
                logger.error(f"Failed to save report to Mongo: {db_err}")

        return PredictionResponse(**report_document)

    finally:
        if temp_path:
            cleanup_temp_file(temp_path)