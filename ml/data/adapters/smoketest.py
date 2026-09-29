"""
Smoke-test dataset adapter.

Reads the synthetic fixtures under ml/data/samples/smoketest/ and yields
VideoRecord objects for pipeline verification ONLY.

These fixtures are NOT training or evaluation data.
Never report ML metrics from this adapter's outputs.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Set

from ml.data.adapters.base import DatasetAdapter, VideoRecord


# Filename contracts for the synthetic fixtures.
REAL_PATTERN = re.compile(r"^(smoke_\d+)_real\.mp4$", re.IGNORECASE)
FAKE_PATTERN = re.compile(r"^(smoke_\d+)_fake_[a-z]\.mp4$", re.IGNORECASE)

# Non-video files allowed to exist in the fixture tree without causing failure.
ALLOWED_NON_VIDEO_NAMES = {
    "readme.md",
    ".gitkeep",
    "thumbs.db",
    "desktop.ini",
}


class SmokeTestAdapter(DatasetAdapter):
    """
    Adapter for the synthetic smoke-test fixture set.

    Expected layout:

        <root_dir>/
          real/
            smoke_01_real.mp4
            ...
          fake/
            smoke_01_fake_a.mp4
            ...

    Grouping rule (encoded in filenames):
        smoke_01_real.mp4   -> source_video_id = smoke_01
        smoke_01_fake_a.mp4 -> source_video_id = smoke_01
    """

    name = "smoketest"

    def __init__(self, root_dir: str) -> None:
        super().__init__(root_dir)
        self._root = Path(root_dir).expanduser().resolve()
        self._real_dir = self._root / "real"
        self._fake_dir = self._root / "fake"

    def iter_videos(self) -> Iterator[VideoRecord]:
        self._assert_layout()

        records: List[VideoRecord] = []
        records.extend(self._collect_real_records())
        records.extend(self._collect_fake_records())

        if not records:
            raise FileNotFoundError(
                f"No smoke-test videos found under {self._root}. "
                f"Run: python ml/scripts/generate_smoketest_fixtures.py"
            )

        self._assert_source_pairs(records)

        # Deterministic order for stable manifests/tests.
        records.sort(key=lambda r: r.video_id)

        for record in records:
            yield record

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assert_layout(self) -> None:
        if not self._root.exists():
            raise FileNotFoundError(
                f"Smoke-test root does not exist: {self._root}. "
                f"Run the fixture generator first."
            )
        if not self._real_dir.is_dir():
            raise FileNotFoundError(
                f"Missing required folder: {self._real_dir}"
            )
        if not self._fake_dir.is_dir():
            raise FileNotFoundError(
                f"Missing required folder: {self._fake_dir}"
            )

    def _collect_real_records(self) -> List[VideoRecord]:
        records: List[VideoRecord] = []

        for path in sorted(self._real_dir.iterdir()):
            if not path.is_file():
                continue
            if path.name.lower() in ALLOWED_NON_VIDEO_NAMES:
                continue
            if path.suffix.lower() != ".mp4":
                raise ValueError(
                    f"Unexpected non-MP4 file in smoke-test real/: {path.name}"
                )

            match = REAL_PATTERN.match(path.name)
            if not match:
                raise ValueError(
                    f"Unexpected real fixture filename: {path.name}. "
                    f"Expected pattern smoke_XX_real.mp4"
                )

            source_video_id = match.group(1)
            video_id = path.stem  # e.g. smoke_01_real

            records.append(
                VideoRecord(
                    video_id=video_id,
                    path=self._to_portable_path(path),
                    dataset=self.name,
                    label=0,  # REAL
                    source_video_id=source_video_id,
                    manipulation_type=None,
                    extra={
                        "fixture": True,
                        "synthetic": True,
                        "role": "real",
                    },
                )
            )

        return records

    def _collect_fake_records(self) -> List[VideoRecord]:
        records: List[VideoRecord] = []

        for path in sorted(self._fake_dir.iterdir()):
            if not path.is_file():
                continue
            if path.name.lower() in ALLOWED_NON_VIDEO_NAMES:
                continue
            if path.suffix.lower() != ".mp4":
                raise ValueError(
                    f"Unexpected non-MP4 file in smoke-test fake/: {path.name}"
                )

            match = FAKE_PATTERN.match(path.name)
            if not match:
                raise ValueError(
                    f"Unexpected fake fixture filename: {path.name}. "
                    f"Expected pattern smoke_XX_fake_a.mp4"
                )

            source_video_id = match.group(1)
            video_id = path.stem  # e.g. smoke_01_fake_a

            records.append(
                VideoRecord(
                    video_id=video_id,
                    path=self._to_portable_path(path),
                    dataset=self.name,
                    label=1,  # FAKE
                    source_video_id=source_video_id,
                    manipulation_type="synthetic_dummy",
                    extra={
                        "fixture": True,
                        "synthetic": True,
                        "role": "fake",
                    },
                )
            )

        return records

    def _assert_source_pairs(self, records: List[VideoRecord]) -> None:
        """
        Smoke-test specific integrity check:
        every source_video_id must appear as both REAL and FAKE.
        """
        real_sources: Set[str] = set()
        fake_sources: Set[str] = set()

        for r in records:
            if r.label == 0:
                real_sources.add(r.source_video_id)
            else:
                fake_sources.add(r.source_video_id)

        missing_fakes = sorted(real_sources - fake_sources)
        missing_reals = sorted(fake_sources - real_sources)

        if missing_fakes or missing_reals:
            parts = []
            if missing_fakes:
                parts.append(f"real sources missing fake pair: {missing_fakes}")
            if missing_reals:
                parts.append(f"fake sources missing real pair: {missing_reals}")
            raise ValueError(
                "Smoke-test fixture pairing invalid. " + " | ".join(parts)
            )

    def _to_portable_path(self, path: Path) -> str:
        """
        Prefer a relative POSIX-style path for manifest portability.
        Fall back to absolute POSIX path if relative conversion fails.
        """
        try:
            # Relative to current working directory when possible.
            rel = path.resolve().relative_to(Path.cwd().resolve())
            return rel.as_posix()
        except ValueError:
            return path.resolve().as_posix()