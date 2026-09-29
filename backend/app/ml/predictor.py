import time
import numpy as np
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import logger
from app.ml.model_loader import model_manager
from app.ml.frame_extractor import extract_frames


def predict_video(video_path: str) -> Dict[str, Any]:
    """Run deepfake detection on a video file."""
    start_time = time.time()

    # Step 1: Extract frames
    t0 = time.time()
    frames = extract_frames(video_path)
    num_frames = len(frames)
    logger.info(f"Frame extraction time: {time.time() - t0:.3f}s")

    # Step 2: Memory-efficient feature extraction
    t0 = time.time()

    if model_manager.feature_extractor is not None:
        feature_list = []

        # Process one frame at a time to reduce peak memory usage
        for i, frame in enumerate(frames):
            frame_tensor = np.expand_dims(
                frame.astype(np.float32),
                axis=0
            )

            feature = model_manager.feature_extractor(
                frame_tensor,
                training=False
            ).numpy()

            feature_list.append(feature[0])

            # Release temporary tensors immediately
            del frame_tensor
            del feature

        features = np.asarray(feature_list, dtype=np.float32)

    else:
        # Dummy features if model file is missing
        features = np.random.randn(
            num_frames,
            settings.NUM_FEATURES
        ).astype(np.float32)

    logger.info(
        f"Feature extraction time: {time.time() - t0:.3f}s"
    )

    # Step 3: Pad/truncate to fixed sequence length & create mask
    seq_features = np.zeros(
        (
            1,
            settings.MAX_SEQ_LENGTH,
            settings.NUM_FEATURES
        ),
        dtype=np.float32
    )

    seq_mask = np.zeros(
        (
            1,
            settings.MAX_SEQ_LENGTH
        ),
        dtype=bool
    )

    length = min(
        num_frames,
        settings.MAX_SEQ_LENGTH
    )

    seq_features[0, :length, :] = features[:length]
    seq_mask[0, :length] = True

    # Step 4: Temporal classification
    t0 = time.time()

    if model_manager.model is not None:
        raw_score = float(
            model_manager.model.predict(
                [seq_features, seq_mask],
                verbose=0
            )[0][0]
        )
    else:
        # Dummy score if model file is missing
        raw_score = float(
            np.random.uniform(0.1, 0.9)
        )

    logger.info(
        f"Model inference time: {time.time() - t0:.3f}s"
    )

    # Step 5: Format output
    total_time = (time.time() - start_time) * 1000
    is_fake = raw_score > 0.5

    return {
        "prediction": "FAKE" if is_fake else "REAL",
        "confidence": round(
            raw_score if is_fake else 1.0 - raw_score,
            4
        ),
        "raw_score": round(raw_score, 4),
        "model_metadata": {
            "version": settings.APP_VERSION,
            "architecture": "InceptionV3 + GRU",
            "backbone": "InceptionV3 (ImageNet)"
        },
        "processing_time_ms": round(total_time, 2),
        "frames_analyzed": num_frames,
    }