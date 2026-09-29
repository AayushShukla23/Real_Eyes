from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ModelMetadata(BaseModel):
    version: str
    architecture: str
    backbone: str


class PredictionResponse(BaseModel):
    report_id: str
    prediction: str          # "REAL" or "FAKE"
    confidence: float        # 0.0 to 1.0 scale
    raw_score: float         # Raw sigmoid output
    filename: str
    file_size_bytes: int
    model_metadata: ModelMetadata
    processing_time_ms: float
    frames_analyzed: int
    created_at: str


class ReportSummary(BaseModel):
    report_id: str
    filename: str
    prediction: str
    confidence: float
    created_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    db_connected: bool