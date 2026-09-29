"""Pytest path bootstrap and shared fixtures for RealEyes ML Phase 2 tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ml/tests/conftest.py -> parents[0]=tests, [1]=ml, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SMOKE_ROOT = REPO_ROOT / "ml" / "data" / "samples" / "smoketest"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def smoke_root() -> Path:
    real_dir = SMOKE_ROOT / "real"
    fake_dir = SMOKE_ROOT / "fake"

    if not real_dir.is_dir() or not fake_dir.is_dir():
        pytest.fail(
            f"Smoke-test fixtures missing under {SMOKE_ROOT}. "
            f"Run: python ml/scripts/generate_smoketest_fixtures.py"
        )

    real_n = len(list(real_dir.glob("*.mp4")))
    fake_n = len(list(fake_dir.glob("*.mp4")))
    if real_n != 5 or fake_n != 5:
        pytest.fail(
            f"Expected 5 real + 5 fake mp4 fixtures, found real={real_n} fake={fake_n}. "
            f"Re-run: python ml/scripts/generate_smoketest_fixtures.py --force"
        )

    return SMOKE_ROOT


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    """Per-test isolated output directory."""
    d = tmp_path / "outputs"
    d.mkdir(parents=True, exist_ok=True)
    return d