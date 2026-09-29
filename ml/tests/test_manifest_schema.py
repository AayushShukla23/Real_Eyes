"""Manifest builder schema and integrity tests (smoke fixtures only)."""

from __future__ import annotations

from pathlib import Path

from ml.data.adapters.smoketest import SmokeTestAdapter
from ml.data.manifest import MANIFEST_COLUMNS, build_manifest, load_manifest


def test_build_manifest_smoke_schema(smoke_root: Path, output_dir: Path, repo_root: Path):
    adapter = SmokeTestAdapter(str(smoke_root))
    result = build_manifest(
        adapter,
        output_dir,
        path_root=repo_root,
        require_files_exist=True,
    )

    assert result.num_records == 10
    assert result.num_real == 5
    assert result.num_fake == 5
    assert result.num_source_groups == 5
    assert result.datasets == ("smoketest",)
    assert result.manifest_path.exists()
    assert result.extra_path is not None and result.extra_path.exists()

    rows = load_manifest(result.manifest_path)
    assert len(rows) == 10
    assert set(rows[0].keys()) >= set(MANIFEST_COLUMNS)

    # Every source appears as real+fake pair in smoke fixtures
    from collections import defaultdict

    by_src = defaultdict(set)
    for r in rows:
        by_src[r["source_video_id"]].add(r["label"])
    for src, labels in by_src.items():
        assert labels == {0, 1}, f"source {src} labels={labels}"