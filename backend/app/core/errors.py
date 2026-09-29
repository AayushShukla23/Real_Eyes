from fastapi import HTTPException, status


class VideoValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class ModelInferenceError(HTTPException):
    def __init__(self, detail: str = "Model inference failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class VideoProcessingError(HTTPException):
    def __init__(self, detail: str = "Video processing failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )