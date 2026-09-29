"""
Leakage-safe group splitting for RealEyes dataset manifests.

Reads manifest.csv and outputs splits.csv containing:
    video_id,source_video_id,split

Leakage-control invariant:
    All records sharing the same `source_video_id` MUST be assigned
    to the same split (train, val, or test). Zero overlap of source
    groups across splits is permitted.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import numpy as np

from ml.data.manifest import load_manifest


logger = logging.getLogger(__name__)

DEFAULT_RATIOS: Tuple[float, float, float] = (0.70, 0.15, 0.15)  # train, val, test
VALID_SPLITS: Set[str] = {"train", "val", "test"}


@dataclass(frozen=True)
class SplitResult:
    """Summary of split generation."""

    splits_path: Path
    total_videos: int
    total_sources: int
    train_videos: int
    val_videos: int
    test_videos: int
    train_sources: int
    val_sources: int
    test_sources: int
    strategy: str
    seed: int


def group_split_manifest(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    ratios: Tuple[float, float, float] = DEFAULT_RATIOS,
    seed: int = 42,
    strategy: str = "group_random",
    splits_filename: str = "splits.csv",
) -> SplitResult:
    """
    Perform a leakage-safe group split on a dataset manifest.

    Args:
        manifest_path: Path to manifest.csv.
        output_dir: Directory where splits.csv will be written.
        ratios: Tuple of (train_ratio, val_ratio, test_ratio). Must sum to 1.0.
        seed: Random seed for group shuffling.
        strategy: Splitting strategy ("group_random").
        splits_filename: Name of the output CSV file.

    Returns:
        SplitResult dataclass summarizing counts per split.

    Raises:
        ValueError, FileNotFoundError on invalid input or leakage assertion failure.
    """
    manifest_file = Path(manifest_path)
    rows = load_manifest(manifest_file)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    _validate_ratios(ratios)

    if strategy != "group_random":
        raise ValueError(f"Unsupported splitting strategy: {strategy!r}. Supported: 'group_random'")

    # Group video_ids by source_video_id
    source_to_videos: Dict[str, List[str]] = {}
    for r in rows:
        src = r["source_video_id"]
        source_to_videos.setdefault(src, []).append(r["video_id"])

    unique_sources = sorted(source_to_videos.keys())
    num_sources = len(unique_sources)

    if num_sources == 0:
        raise ValueError(f"No source groups found in manifest: {manifest_file}")

    # Partition source groups deterministically
    train_srcs, val_srcs, test_srcs = _partition_groups_random(
        unique_sources, ratios, seed
    )

    # Map videos to assigned splits
    video_to_split: Dict[str, str] = {}
    for src in train_srcs:
        for vid in source_to_videos[src]:
            video_to_split[vid] = "train"
    for src in val_srcs:
        for vid in source_to_videos[src]:
            video_to_split[vid] = "val"
    for src in test_srcs:
        for vid in source_to_videos[src]:
            video_to_split[vid] = "test"

    # Enforce strict zero-leakage invariant assertions
    _assert_no_group_leakage(train_srcs, val_srcs, test_srcs)
    _assert_all_videos_assigned(rows, video_to_split)

    # Write splits.csv
    splits_path = out_dir / splits_filename
    _write_splits_csv(splits_path, rows, video_to_split)

    # Calculate summaries
    train_vids = sum(len(source_to_videos[s]) for s in train_srcs)
    val_vids = sum(len(source_to_videos[s]) for s in val_srcs)
    test_vids = sum(len(source_to_videos[s]) for s in test_srcs)

    logger.info(
        "Generated splits (%s, seed=%d): train=%d vids (%d srcs), val=%d vids (%d srcs), test=%d vids (%d srcs)",
        strategy,
        seed,
        train_vids,
        len(train_srcs),
        val_vids,
        len(val_srcs),
        test_vids,
        len(test_srcs),
    )

    return SplitResult(
        splits_path=splits_path,
        total_videos=len(rows),
        total_sources=num_sources,
        train_videos=train_vids,
        val_videos=val_vids,
        test_videos=test_vids,
        train_sources=len(train_srcs),
        val_sources=len(val_srcs),
        test_sources=len(test_srcs),
        strategy=strategy,
        seed=seed,
    )


def load_splits(splits_path: str | Path) -> Dict[str, str]:
    """
    Load splits.csv into a mapping of video_id -> split_name.
    """
    path = Path(splits_path)
    if not path.exists():
        raise FileNotFoundError(f"Splits file not found: {path}")

    mapping: Dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "video_id" not in reader.fieldnames or "split" not in reader.fieldnames:
            raise ValueError(f"Splits file schema invalid: {path}")

        for i, row in enumerate(reader, start=2):
            vid = (row.get("video_id") or "").strip()
            split = (row.get("split") or "").strip()

            if not vid or not split:
                raise ValueError(f"Line {i}: empty video_id or split in {path}")
            if split not in VALID_SPLITS:
                raise ValueError(f"Line {i}: invalid split name {split!r} in {path}")
            if vid in mapping:
                raise ValueError(f"Line {i}: duplicate video_id {vid!r} in {path}")

            mapping[vid] = split

    return mapping


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _validate_ratios(ratios: Tuple[float, float, float]) -> None:
    if len(ratios) != 3:
        raise ValueError(f"ratios must be a tuple of 3 floats (train, val, test), got {ratios!r}")
    if any(r < 0.0 for r in ratios):
        raise ValueError(f"ratios cannot be negative, got {ratios!r}")

    total = sum(ratios)
    if abs(total - 1.0) > 1e-5:
        raise ValueError(f"ratios must sum to 1.0, got sum({ratios!r}) = {total:.6f}")


def _partition_groups_random(
    sources: List[str], ratios: Tuple[float, float, float], seed: int
) -> Tuple[Set[str], Set[str], Set[str]]:
    """Partition source IDs deterministically into 3 sets using a NumPy RNG."""
    rng = np.random.default_rng(seed)
    shuffled = [str(s) for s in rng.permutation(sources)]
    n = len(shuffled)

    train_r, val_r, _ = ratios

    # Compute group counts
    n_train = int(round(n * train_r))
    n_val = int(round(n * val_r))

    # Guard edge cases for very small numbers of source groups (e.g., smoke-test fixture)
    if n >= 3:
        n_train = max(1, n_train)
        n_val = max(1, n_val)
        if n_train + n_val >= n:
            n_train = n - 2
            n_val = 1

    train_set = set(shuffled[:n_train])
    val_set = set(shuffled[n_train : n_train + n_val])
    test_set = set(shuffled[n_train + n_val :])

    return train_set, val_set, test_set


def _assert_no_group_leakage(
    train_srcs: Set[str], val_srcs: Set[str], test_srcs: Set[str]
) -> None:
    """Hard assertion that source IDs do not overlap across splits."""
    tv_overlap = train_srcs & val_srcs
    tt_overlap = train_srcs & test_srcs
    vt_overlap = val_srcs & test_srcs

    if tv_overlap or tt_overlap or vt_overlap:
        raise ValueError(
            f"LEAKAGE ASSERTION FAILED:\n"
            f"  Train/Val overlap: {tv_overlap}\n"
            f"  Train/Test overlap: {tt_overlap}\n"
            f"  Val/Test overlap: {vt_overlap}"
        )


def _assert_all_videos_assigned(
    rows: Sequence[dict], video_to_split: Dict[str, str]
) -> None:
    manifest_vids = {r["video_id"] for r in rows}
    assigned_vids = set(video_to_split.keys())

    missing = manifest_vids - assigned_vids
    if missing:
        raise ValueError(f"Unassigned video_ids during splitting: {missing}")


def _write_splits_csv(
    path: Path, rows: Sequence[dict], video_to_split: Dict[str, str]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "source_video_id", "split"])
        writer.writeheader()
        for r in rows:
            vid = r["video_id"]
            writer.writerow(
                {
                    "video_id": vid,
                    "source_video_id": r["source_video_id"],
                    "split": video_to_split[vid],
                }
            )