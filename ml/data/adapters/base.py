"""
Dataset adapter interface for RealEyes ML pipeline.

Every dataset (smoke-test, FaceForensics++, Celeb-DF v2, future additions)
is exposed to the rest of the pipeline through a `DatasetAdapter` that yields
`VideoRecord` objects. The manifest builder, splitter, feature extractor, and
trainer never need to know which dataset they are operating on.

Leakage-control invariant:
    Every derivative of the same physical source clip MUST share the same
    `source_video_id`. This field is the sole key used by the group-safe
    splitter. If a dataset cannot reliably provide it, the adapter must
    refuse to yield the record rather than guess.

Label convention (project-wide):
    0 = REAL
    1 = FAKE
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, Optional


VALID_LABELS = (0, 1)


@dataclass(frozen=True)
class VideoRecord:
    """
    Immutable description of a single physical video file.

    Fields:
        video_id:          Unique, stable identifier across the whole project.
                           Must be unique within a dataset. Enforced by the
                           manifest builder.
        path:              Path to the video file on disk. Stored as a string
                           so the manifest stays portable across OSes; the
                           manifest builder normalizes to POSIX relative paths.
        dataset:           Short dataset tag, e.g. "smoketest", "ff++", "celebdf".
        label:             0 = REAL, 1 = FAKE. No other values allowed.
        source_video_id:   Grouping key for leakage-safe splitting. Two records
                           share this value iff they were derived from the same
                           physical source clip (or one was derived from the other).
                           Must be a non-empty string.
        manipulation_type: For fakes, name of the manipulation family
                           (e.g. "deepfakes", "face2face"). For reals, must be None.
        extra:             Dataset-specific metadata (e.g. FF++ compression level,
                           Celeb-DF identity pair). Never written to the main
                           manifest.csv; serialized separately to manifest_extra.jsonl.
    """

    video_id: str
    path: str
    dataset: str
    label: int
    source_video_id: str
    manipulation_type: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate at construction so bad records never enter the pipeline.
        if not isinstance(self.video_id, str) or not self.video_id.strip():
            raise ValueError(f"video_id must be a non-empty string, got: {self.video_id!r}")

        if not isinstance(self.path, str) or not self.path.strip():
            raise ValueError(f"path must be a non-empty string, got: {self.path!r}")

        if not isinstance(self.dataset, str) or not self.dataset.strip():
            raise ValueError(f"dataset must be a non-empty string, got: {self.dataset!r}")

        if self.label not in VALID_LABELS:
            raise ValueError(
                f"label must be 0 (REAL) or 1 (FAKE), got: {self.label!r} "
                f"for video_id={self.video_id!r}"
            )

        if not isinstance(self.source_video_id, str) or not self.source_video_id.strip():
            raise ValueError(
                f"source_video_id must be a non-empty string (leakage-control key), "
                f"got: {self.source_video_id!r} for video_id={self.video_id!r}"
            )

        # Real videos must not carry a manipulation type. Fakes must.
        if self.label == 0 and self.manipulation_type is not None:
            raise ValueError(
                f"REAL video must have manipulation_type=None, "
                f"got: {self.manipulation_type!r} for video_id={self.video_id!r}"
            )
        if self.label == 1 and (
            self.manipulation_type is None or not str(self.manipulation_type).strip()
        ):
            raise ValueError(
                f"FAKE video must have a non-empty manipulation_type, "
                f"got: {self.manipulation_type!r} for video_id={self.video_id!r}"
            )


class DatasetAdapter(ABC):
    """
    Abstract base class every dataset must implement.

    Concrete adapters know how to walk their own on-disk layout and how to
    derive `source_video_id` from that dataset's metadata. Nothing else in
    the ML pipeline needs to know those details.

    Contract:
        - `name` is a stable short tag used throughout the pipeline.
        - `root_dir` is the absolute or relative path to the dataset root
          on the current machine.
        - `iter_videos()` yields one VideoRecord per physical video file.
          It must be safe to iterate multiple times.
    """

    #: Short, stable dataset tag. Subclasses set this as a class attribute.
    name: str = ""

    def __init__(self, root_dir: str) -> None:
        if not isinstance(root_dir, str) or not root_dir.strip():
            raise ValueError(f"root_dir must be a non-empty string, got: {root_dir!r}")
        if not self.name:
            raise ValueError(
                f"{type(self).__name__} must set a non-empty class attribute `name`."
            )
        self.root_dir = root_dir

    @abstractmethod
    def iter_videos(self) -> Iterator[VideoRecord]:
        """
        Yield one VideoRecord per physical video in the dataset.

        Implementations MUST:
            - Populate `source_video_id` from the dataset's own metadata.
              Never invent it. Never guess. Fail loudly if the dataset
              layout does not allow reliable grouping.
            - Yield records with unique `video_id` values.
            - Set `dataset` to `self.name`.

        This method may be called multiple times and must produce the same
        set of records each time.
        """
        raise NotImplementedError