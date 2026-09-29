import os
import numpy as np
from app.core.config import settings
from app.core.logging import logger


class ModelManager:
    """
    Singleton manager for the deepfake detection model.
    Loads the model once at startup and reuses it for all predictions.
    """
    def __init__(self):
        self._model = None
        self._feature_extractor = None
        self._is_loaded = False

    def load(self) -> None:
        """Load model and feature extractor into memory."""
        if self._is_loaded:
            return

        logger.info("Loading deepfake detection model...")

        try:
            import tensorflow as tf
            
            # Suppress TF info logs to keep terminal clean
            if not settings.DEBUG:
                tf.get_logger().setLevel("ERROR")
                os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

            # Load the classification model (GRU)
            if os.path.exists(settings.MODEL_PATH):
                self._model = tf.keras.models.load_model(
    settings.MODEL_PATH,
    compile=False
)
                logger.info(f"Model loaded from {settings.MODEL_PATH}")
            else:
                logger.warning(
                    f"Model file not found at {settings.MODEL_PATH}. "
                    "Running in DUMMY mode for development."
                )

            # Build the InceptionV3 feature extractor (Frozen)
            self._feature_extractor = self._build_feature_extractor(tf)
            self._is_loaded = True
            logger.info("Model and feature extractor ready.")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._is_loaded = False
            raise

    def _build_feature_extractor(self, tf):
        """Build InceptionV3 feature extractor."""
        base_model = tf.keras.applications.InceptionV3(
            weights="imagenet",
            include_top=False,
            pooling="avg",
            input_shape=(settings.IMG_SIZE, settings.IMG_SIZE, 3),
        )
        preprocess_input = tf.keras.applications.inception_v3.preprocess_input

        inputs = tf.keras.Input((settings.IMG_SIZE, settings.IMG_SIZE, 3))
        preprocessed = preprocess_input(inputs)
        outputs = base_model(preprocessed)

        return tf.keras.Model(inputs, outputs, name="feature_extractor")

    @property
    def model(self):
        return self._model

    @property
    def feature_extractor(self):
        return self._feature_extractor

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


# Global singleton instance
model_manager = ModelManager()