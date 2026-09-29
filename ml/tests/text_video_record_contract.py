"""Unit tests for VideoRecord validation contract."""

from __future__ import annotations

import pytest

from ml.data.adapters.base import VideoRecord


def test_valid_real_record():
    r = VideoRecord(
        video_id="x_real",
        path="some/path.mp4",
        dataset="smoketest",
        label=0,
        source_video_id="x",
        manipulation_type=None,
    )
    assert r.label == 0
    assert r.manipulation_type is None


def test_valid_fake_record():
    r = VideoRecord(
        video_id="x_fake",
        path="some/path.mp4",
        dataset="smoketest",
        label=1,
        source_video_id="x",
        manipulation_type="synthetic_dummy",
    )
    assert r.label == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"video_id": "", "path": "p.mp4", "dataset": "d", "label": 0, "source_video_id": "s"},
        {"video_id": "v", "path": "", "dataset": "d", "label": 0, "source_video_id": "s"},
        {"video_id": "v", "path": "p.mp4", "dataset": "", "label": 0, "source_video_id": "s"},
        {"video_id": "v", "path": "p.mp4", "dataset": "d", "label": 2, "source_video_id": "s"},
        {"video_id": "v", "path": "p.mp4", "dataset": "d", "label": 0, "source_video_id": ""},
        {
            "video_id": "v",
            "path": "p.mp4",
            "dataset": "d",
            "label": 0,
            "source_video_id": "s",
            "manipulation_type": "nope",  # REAL cannot have manipulation
        },
        {
            "video_id": "v",
            "path": "p.mp4",
            "dataset": "d",
            "label": 1,
            "source_video_id": "s",
            "manipulation_type": None,  # FAKE must have manipulation
        },
    ],
)
def test_invalid_records_fail_loudly(kwargs):
    with pytest.raises(ValueError):
        VideoRecord(**kwargs)