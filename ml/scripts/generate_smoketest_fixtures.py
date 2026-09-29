"""
Generate 10 synthetic MP4 fixtures for RealEyes pipeline smoke tests.

IMPORTANT:
    These files are NOT training or evaluation data.
    They exist only to verify manifest generation, grouping, splitting,
    and basic video readability.

Requirements:
    ffmpeg must be available on PATH.

Usage (from repo root RealEyes_Prod):
    python ml/scripts/generate_smoketest_fixtures.py
    python ml/scripts/generate_smoketest_fixtures.py --force
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
SMOKE_ROOT = ML_DIR / "data" / "samples" / "smoketest"
REAL_DIR = SMOKE_ROOT / "real"
FAKE_DIR = SMOKE_ROOT / "fake"


# ---------------------------------------------------------------------------
# Fixture plan: 5 source groups × (1 real + 1 fake) = 10 files
# ---------------------------------------------------------------------------

FIXTURES = [
    # source smoke_01
    ("smoke_01", "real", "smoke_01_real",   "0x1F4E79"),
    ("smoke_01", "fake", "smoke_01_fake_a", "0x8B1E1E"),
    # source smoke_02
    ("smoke_02", "real", "smoke_02_real",   "0x1F4E79"),
    ("smoke_02", "fake", "smoke_02_fake_a", "0x8B1E1E"),
    # source smoke_03
    ("smoke_03", "real", "smoke_03_real",   "0x1F4E79"),
    ("smoke_03", "fake", "smoke_03_fake_a", "0x8B1E1E"),
    # source smoke_04
    ("smoke_04", "real", "smoke_04_real",   "0x1F4E79"),
    ("smoke_04", "fake", "smoke_04_fake_a", "0x8B1E1E"),
    # source smoke_05
    ("smoke_05", "real", "smoke_05_real",   "0x1F4E79"),
    ("smoke_05", "fake", "smoke_05_fake_a", "0x8B1E1E"),
]


DURATION_SEC = 2
WIDTH = 320
HEIGHT = 240
FPS = 10


def require_ffmpeg() -> str:
    """Return path to ffmpeg, or exit with a clear error."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print(
            "ERROR: ffmpeg not found on PATH.\n"
            "Install it, then re-run this script.\n"
            "  Windows:  winget install ffmpeg\n"
            "  macOS:    brew install ffmpeg\n"
            "  Ubuntu:   sudo apt-get install -y ffmpeg\n"
            "  Colab:    !apt-get install -y ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)
    return ffmpeg


def build_ffmpeg_cmd(ffmpeg: str, out_path: Path, bg_color: str) -> list[str]:
    """
    Build an ffmpeg command that writes a short solid-color MP4.

    Uses lavfi color source without font or filterchain dependencies.
    No audio. yuv420p + +faststart for maximum OpenCV compatibility.
    """
    return [
        ffmpeg,
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s={WIDTH}x{HEIGHT}:d={DURATION_SEC}:r={FPS}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        str(out_path),
    ]


def generate_one(ffmpeg: str, role: str, stem: str, bg_color: str, force: bool) -> Path:
    out_dir = REAL_DIR if role == "real" else FAKE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.mp4"

    if out_path.exists() and not force:
        print(f"  skip (exists): {out_path.relative_to(ML_DIR)}")
        return out_path

    cmd = build_ffmpeg_cmd(ffmpeg, out_path, bg_color)
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
        print(f"ERROR generating {out_path.name}:\n{err}", file=sys.stderr)
        sys.exit(1)

    print(f"  wrote: {out_path.relative_to(ML_DIR)}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic MP4 fixtures for RealEyes smoke tests."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite fixtures even if they already exist.",
    )
    args = parser.parse_args()

    print("RealEyes smoke-test fixture generator")
    print("These files are SYNTHETIC FIXTURES ONLY — not ML training data.")
    print(f"Output root: {SMOKE_ROOT}")
    print()

    ffmpeg = require_ffmpeg()
    print(f"Using ffmpeg: {ffmpeg}")
    print()

    REAL_DIR.mkdir(parents=True, exist_ok=True)
    FAKE_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for source_id, role, stem, bg_color in FIXTURES:
        path = generate_one(ffmpeg, role, stem, bg_color, force=args.force)
        written.append((source_id, role, path))

    print()
    print(f"Done. {len(written)} fixtures ready under ml/data/samples/smoketest/")
    print("Grouping reminder:")
    for source_id, role, path in written:
        print(f"  {path.name:24s}  source_video_id={source_id:10s}  role={role}")
    print()
    print("Next: verify SmokeTestAdapter yields these 10 records.")


if __name__ == "__main__":
    main()