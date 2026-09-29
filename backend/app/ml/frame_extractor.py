import cv2
import numpy as np
from typing import Tuple

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import VideoProcessingError


def crop_center_square(frame: np.ndarray) -> np.ndarray:
    """Crop the center square from a frame, preserving aspect ratio."""
    y, x = frame.shape[0:2]
    min_dim = min(y, x)
    start_x = (x // 2) - (min_dim // 2)
    start_y = (y // 2) - (min_dim // 2)
    return frame[start_y : start_y + min_dim, start_x : start_x + min_dim]


def extract_frames(video_path: str) -> np.ndarray:
    """
    Extract frames from a video file.
    IMPORTANT: Crop FIRST (preserve aspect ratio), THEN resize.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise VideoProcessingError(f"Cannot open video: {video_path}")

    frames = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # CORRECT ORDER: Crop first, then resize
            frame = crop_center_square(frame)
            frame = cv2.resize(frame, (settings.IMG_SIZE, settings.IMG_SIZE))

            # Convert BGR (OpenCV default) to RGB
            frame = frame[:, :, [2, 1, 0]]
            frames.append(frame)

            if len(frames) >= settings.MAX_SEQ_LENGTH:
                break
    finally:
        cap.release()

    if len(frames) == 0:
        raise VideoProcessingError("No frames could be extracted from video.")

    logger.info(f"Extracted {len(frames)} frames from video.")
    return np.array(frames)