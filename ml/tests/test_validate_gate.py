"""Validator must catch deliberate source leakage."""

from __future__ import annotations

import csv
from pathlib import Path

from ml.data.adapters.smoketest import SmokeTestAdapter
from ml.data.manifest import build_manifest, load_manifest
from ml.data.split import group_split_manifest, load_splits
from ml.data.validate import validate_manifest_and_splits


def test_validator_detects_forced_leakage(smoke_root: Path, output_dir: Path, repo_root: Path):
    adapter = SmokeTestAdapter(str(smoke_root))
    man = build_manifest(adapter, output_dir, path_root=repo_root)
    split_res = group_split_manifest(man.manifest_path, output_dir, seed=42)

    # Sanity: clean splits pass
    clean = validate_manifest_and_splits(man.manifest_path, split_res.splits_path)
    assert clean.ok

    rows = load_manifest(man.manifest_path)
    split_map = load_splits(split_res.splits_path)

    # Pick a source that has both a real and fake row; move one video to another split.
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source_video_id"], []).append(r["video_id"])

    target_src, vids = next(iter(by_src.items()))
    assert len(vids) >= 2
    victim = vids[0]
    original = split_map[victim]
    forced = "test" if original != "test" else "train"
    split_map[victim] = forced

    poisoned = output_dir / "splits_poisoned.csv"
    with poisoned.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["video_id", "source_video_id", "split"])
        w.writeheader()
        src_by_vid = {r["video_id"]: r["source_video_id"] for r in rows}
        for vid, sp in split_map.items():
            w.writerow(
                {
                    "video_id": vid,
                    "source_video_id": src_by_vid[vid],
                    "split": sp,
                }
            )

    report = validate_manifest_and_splits(man.manifest_path, poisoned)
    assert report.ok is False
    assert any("LEAKAGE" in e for e in report.errors)