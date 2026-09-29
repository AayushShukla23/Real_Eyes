from pydantic import BaseModel


class ModelMetadata(BaseModel):
    version: str
    architecture: str
    backbone: str


class PredictionResponse(BaseModel):
    prediction: str          # "REAL" or "FAKE"
    confidence: float        # 0.0 to 1.0 scale
    raw_score: float         # Raw sigmoid output
    model_metadata: ModelMetadata
    processing_time_ms: float
    frames_analyzed: int


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool