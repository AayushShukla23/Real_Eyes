from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RealEyes"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
        # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "realeyes_db"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Model
    MODEL_PATH: str = "./models/Deepfake_Detection_Model1.keras"
    IMG_SIZE: int = 224
    MAX_SEQ_LENGTH: int = 20
    NUM_FEATURES: int = 2048

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: str = "mp4,avi,mov,mkv"

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()