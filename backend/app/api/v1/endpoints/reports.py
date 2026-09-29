from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from app.core.database import db_manager
from app.schemas.prediction import ReportSummary

router = APIRouter()


@router.get("/reports", response_model=List[ReportSummary])
async def get_recent_reports(limit: int = 20):
    """Fetch recent report summaries for the frontend sidebar."""
    if db_manager.db is None:
        return []

    try:
        cursor = db_manager.db["reports"].find(
            {},
            {"_id": 0, "report_id": 1, "filename": 1, "prediction": 1, "confidence": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit)

        reports = await cursor.to_list(length=limit)
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}"
        )


@router.get("/reports/seed")
async def seed_sample_reports():
    """Seed 3 pre-computed sample reports into MongoDB if the collection is empty."""
    if db_manager.db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    count = await db_manager.db["reports"].count_documents({})
    if count > 0:
        return {"message": f"Database already contains {count} reports. Skipping seed."}

    samples = [
        {
            "report_id": "rep_sample_01",
            "prediction": "FAKE",
            "confidence": 0.942,
            "raw_score": 0.942,
            "filename": "celeb_df_swap_01.mp4",
            "file_size_bytes": 12480000,
            "model_metadata": {
                "version": "1.0.0",
                "architecture": "InceptionV3 + GRU",
                "backbone": "InceptionV3 (ImageNet)"
            },
            "processing_time_ms": 1840.5,
            "frames_analyzed": 20,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "report_id": "rep_sample_02",
            "prediction": "REAL",
            "confidence": 0.918,
            "raw_score": 0.082,
            "filename": "news_broadcast_uncut.mp4",
            "file_size_bytes": 18900000,
            "model_metadata": {
                "version": "1.0.0",
                "architecture": "InceptionV3 + GRU",
                "backbone": "InceptionV3 (ImageNet)"
            },
            "processing_time_ms": 1620.1,
            "frames_analyzed": 20,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "report_id": "rep_sample_03",
            "prediction": "FAKE",
            "confidence": 0.784,
            "raw_score": 0.784,
            "filename": "tiktok_lip_sync_deepfake.mp4",
            "file_size_bytes": 8300000,
            "model_metadata": {
                "version": "1.0.0",
                "architecture": "InceptionV3 + GRU",
                "backbone": "InceptionV3 (ImageNet)"
            },
            "processing_time_ms": 1410.8,
            "frames_analyzed": 20,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    await db_manager.db["reports"].insert_many(samples)
    return {"message": "Successfully seeded 3 sample reports into MongoDB Atlas!"}


@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_report_by_id(report_id: str):
    """Fetch a complete detailed report by its unique ID."""
    if db_manager.db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    report = await db_manager.db["reports"].find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_44_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found."
        )

    return report