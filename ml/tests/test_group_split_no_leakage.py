"""Leakage-safe split tests on smoke fixtures (mechanics only)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ml.data.adapters.smoketest import SmokeTestAdapter
from ml.data.manifest import build_manifest, load_manifest
from ml.data.split import group_split_manifest, load_splits
from ml.data.validate import validate_manifest_and_splits


def test_group_split_zero_source_leakage(smoke_root: Path, output_dir: Path, repo_root: Path):
    adapter = SmokeTestAdapter(str(smoke_root))
    man = build_manifest(adapter, output_dir, path_root=repo_root, require_files_exist=True)
    split_res = group_split_manifest(man.manifest_path, output_dir, seed=42)

    assert split_res.total_videos == 10
    assert split_res.total_sources == 5
    assert split_res.train_sources + split_res.val_sources + split_res.test_sources == 5

    rows = load_manifest(man.manifest_path)
    split_map = load_splits(split_res.splits_path)

    source_to_splits = defaultdict(set)
    for r in rows:
        source_to_splits[r["source_video_id"]].add(split_map[r["video_id"]])

    for src, splits in source_to_splits.items():
        assert len(splits) == 1, f"LEAKAGE: source {src} in splits {splits}"

    report = validate_manifest_and_splits(man.manifest_path, split_res.splits_path)
    assert report.ok, report.errors