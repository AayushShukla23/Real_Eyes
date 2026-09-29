"""Same seed must produce identical split assignments."""

from __future__ import annotations

from pathlib import Path

from ml.data.adapters.smoketest import SmokeTestAdapter
from ml.data.manifest import build_manifest
from ml.data.split import group_split_manifest, load_splits


def test_split_is_deterministic_for_seed(smoke_root: Path, output_dir: Path, repo_root: Path):
    """
    Correctness invariant:
        same manifest + same seed => identical video_id -> split mapping.

    We do NOT assert that different seeds must differ. With only 5 source
    groups, different seeds can collide; that is not a failure of the splitter.
    """
    adapter = SmokeTestAdapter(str(smoke_root))
    man = build_manifest(adapter, output_dir, path_root=repo_root)

    out1 = output_dir / "run1"
    out2 = output_dir / "run2"
    out1.mkdir()
    out2.mkdir()

    s1 = group_split_manifest(man.manifest_path, out1, seed=42)
    s2 = group_split_manifest(man.manifest_path, out2, seed=42)

    m1 = load_splits(s1.splits_path)
    m2 = load_splits(s2.splits_path)

    assert m1 == m2
    assert set(m1.values()).issubset({"train", "val", "test"})
    assert len(m1) == man.num_records