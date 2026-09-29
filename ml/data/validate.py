"""
Validate RealEyes manifest + splits integrity and leakage safety.

Primary invariant:
    All rows sharing the same source_video_id must map to exactly one split.

Usage (library):
    from ml.data.validate import validate_manifest_and_splits
    report = validate_manifest_and_splits("manifest.csv", "splits.csv")

Usage (CLI, from repo root with PYTHONPATH=.):
    python -m ml.data.validate ^
      --manifest ml/data/outputs/smoketest/manifest.csv ^
      --splits ml/data/outputs/smoketest/splits.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ml.data.manifest import load_manifest
from ml.data.split import VALID_SPLITS, load_splits


logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Structured result of validation."""

    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    num_videos: int = 0
    num_sources: int = 0
    split_video_counts: Dict[str, int] = field(default_factory=dict)
    split_source_counts: Dict[str, int] = field(default_factory=dict)
    split_class_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def raise_if_failed(self) -> None:
        if not self.ok:
            joined = "\n".join(f"  - {e}" for e in self.errors)
            raise ValueError(f"Validation failed:\n{joined}")


def validate_manifest_and_splits(
    manifest_path: str | Path,
    splits_path: str | Path,
    *,
    allow_empty_split: bool = True,
) -> ValidationReport:
    """
    Validate manifest/splits consistency and zero source-group leakage.

    Args:
        manifest_path: Path to manifest.csv
        splits_path: Path to splits.csv
        allow_empty_split: If False, empty train/val/test is an error.
            Default True so tiny smoke fixtures can still pass mechanics
            checks if a split is empty (we still emit a warning).

    Returns:
        ValidationReport (ok=False with errors listed on failure)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # --- Load ---------------------------------------------------------------
    try:
        manifest_rows = load_manifest(manifest_path)
    except Exception as exc:
        return ValidationReport(ok=False, errors=[f"Failed to load manifest: {exc}"])

    try:
        split_map = load_splits(splits_path)
    except Exception as exc:
        return ValidationReport(ok=False, errors=[f"Failed to load splits: {exc}"])

    if any(r.get("dataset") == "smoketest" for r in manifest_rows):
        warnings.append(
            "Smoke-test fixtures detected. Valid for pipeline mechanics only; "
            "never report ML metrics from this dataset."
        )

    manifest_ids = {r["video_id"] for r in manifest_rows}
    split_ids = set(split_map.keys())

    # --- Completeness -------------------------------------------------------
    missing_in_splits = sorted(manifest_ids - split_ids)
    if missing_in_splits:
        errors.append(
            f"{len(missing_in_splits)} manifest video_id(s) missing from splits "
            f"(examples: {missing_in_splits[:5]})"
        )

    extra_in_splits = sorted(split_ids - manifest_ids)
    if extra_in_splits:
        errors.append(
            f"{len(extra_in_splits)} splits video_id(s) not present in manifest "
            f"(examples: {extra_in_splits[:5]})"
        )

    # --- Join rows that exist in both --------------------------------------
    by_id = {r["video_id"]: r for r in manifest_rows}
    joined: List[dict] = []
    for vid, split in split_map.items():
        if vid not in by_id:
            continue  # already reported as extra
        if split not in VALID_SPLITS:
            errors.append(f"Invalid split label for video_id={vid!r}: {split!r}")
            continue
        row = dict(by_id[vid])
        row["split"] = split
        joined.append(row)

    # --- Leakage invariant --------------------------------------------------
    source_to_splits: Dict[str, Set[str]] = defaultdict(set)
    source_to_videos: Dict[str, List[str]] = defaultdict(list)

    for row in joined:
        src = row["source_video_id"]
        source_to_splits[src].add(row["split"])
        source_to_videos[src].append(row["video_id"])

    leaking_sources = {
        src: sorted(splits)
        for src, splits in source_to_splits.items()
        if len(splits) > 1
    }
    if leaking_sources:
        # Show a compact but actionable error
        examples = list(leaking_sources.items())[:5]
        detail = "; ".join(
            f"{src} -> {spls} (videos={source_to_videos[src][:4]})"
            for src, spls in examples
        )
        errors.append(
            f"LEAKAGE: {len(leaking_sources)} source_video_id(s) appear in multiple splits. "
            f"Examples: {detail}"
        )

    # --- Counts -------------------------------------------------------------
    split_video_counts = {s: 0 for s in ("train", "val", "test")}
    split_source_counts = {s: 0 for s in ("train", "val", "test")}
    split_class_counts = {
        s: {"real": 0, "fake": 0} for s in ("train", "val", "test")
    }

    sources_per_split: Dict[str, Set[str]] = {
        s: set() for s in ("train", "val", "test")
    }

    for row in joined:
        sp = row["split"]
        if sp not in split_video_counts:
            continue
        split_video_counts[sp] += 1
        sources_per_split[sp].add(row["source_video_id"])
        if row["label"] == 0:
            split_class_counts[sp]["real"] += 1
        else:
            split_class_counts[sp]["fake"] += 1

    for sp in ("train", "val", "test"):
        split_source_counts[sp] = len(sources_per_split[sp])
        if split_video_counts[sp] == 0:
            msg = f"Split '{sp}' has 0 videos."
            if allow_empty_split:
                warnings.append(msg)
            else:
                errors.append(msg)

    report = ValidationReport(
        ok=(len(errors) == 0),
        errors=errors,
        warnings=warnings,
        num_videos=len(joined),
        num_sources=len(source_to_splits),
        split_video_counts=split_video_counts,
        split_source_counts=split_source_counts,
        split_class_counts=split_class_counts,
    )

    # Log human-readable summary
    for w in warnings:
        logger.warning(w)
    if report.ok:
        logger.info(
            "Validation PASSED | videos=%d sources=%d | "
            "train=%d (src=%d, real=%d, fake=%d) | "
            "val=%d (src=%d, real=%d, fake=%d) | "
            "test=%d (src=%d, real=%d, fake=%d)",
            report.num_videos,
            report.num_sources,
            split_video_counts["train"],
            split_source_counts["train"],
            split_class_counts["train"]["real"],
            split_class_counts["train"]["fake"],
            split_video_counts["val"],
            split_source_counts["val"],
            split_class_counts["val"]["real"],
            split_class_counts["val"]["fake"],
            split_video_counts["test"],
            split_source_counts["test"],
            split_class_counts["test"]["real"],
            split_class_counts["test"]["fake"],
        )
    else:
        for e in errors:
            logger.error(e)

    return report


def _build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate RealEyes manifest/splits leakage safety and integrity."
    )
    p.add_argument("--manifest", required=True, help="Path to manifest.csv")
    p.add_argument("--splits", required=True, help="Path to splits.csv")
    p.add_argument(
        "--strict-empty-splits",
        action="store_true",
        help="Treat empty train/val/test as errors (default: warnings).",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    args = _build_cli().parse_args(argv)

    report = validate_manifest_and_splits(
        args.manifest,
        args.splits,
        allow_empty_split=not args.strict_empty_splits,
    )

    if report.ok:
        print("OK: validation passed")
        print(f"  videos={report.num_videos} sources={report.num_sources}")
        print(f"  split_video_counts={report.split_video_counts}")
        print(f"  split_source_counts={report.split_source_counts}")
        print(f"  split_class_counts={report.split_class_counts}")
        if report.warnings:
            print("  warnings:")
            for w in report.warnings:
                print(f"    - {w}")
        return 0

    print("FAIL: validation errors:")
    for e in report.errors:
        print(f"  - {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())