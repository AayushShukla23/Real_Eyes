"""
Build a dataset-agnostic manifest from any DatasetAdapter.

Outputs:
    manifest.csv
        video_id,path,dataset,label,source_video_id,manipulation_type

    manifest_extra.jsonl   (optional, only if any record has non-empty extra)
        {"video_id": "...", "extra": {...}}

Rules:
    - Fail loudly on duplicate video_id or duplicate path.
    - Fail loudly if adapter yields zero records.
    - Preserve VideoRecord contract; do not reinterpret labels/source IDs.
    - Prefer portable POSIX relative paths.
    - Path existence checks use the SAME root used for normalization.
    - Never treat smoke-test fixtures as real ML evaluation data.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

from ml.data.adapters.base import DatasetAdapter, VideoRecord


logger = logging.getLogger(__name__)

MANIFEST_COLUMNS: Sequence[str] = (
    "video_id",
    "path",
    "dataset",
    "label",
    "source_video_id",
    "manipulation_type",
)


@dataclass(frozen=True)
class ManifestResult:
    """Summary returned after a successful manifest build."""

    manifest_path: Path
    extra_path: Optional[Path]
    num_records: int
    num_real: int
    num_fake: int
    num_source_groups: int
    datasets: Tuple[str, ...]


def build_manifest(
    adapter: DatasetAdapter,
    output_dir: str | Path,
    *,
    path_root: str | Path | None = None,
    require_files_exist: bool = True,
    manifest_filename: str = "manifest.csv",
    extra_filename: str = "manifest_extra.jsonl",
) -> ManifestResult:
    """
    Materialize all records from `adapter` into validated manifest files.

    Args:
        adapter: Any DatasetAdapter implementation.
        output_dir: Directory where manifest files are written.
        path_root: Root used to compute relative paths AND to validate
            relative path existence. Defaults to CWD.
        require_files_exist: If True, every record.path must exist on disk
            when resolved with path_root semantics.
        manifest_filename: Name of the main CSV file.
        extra_filename: Name of the side-car JSONL file for record.extra.

    Returns:
        ManifestResult with paths and basic counts.

    Raises:
        ValueError, FileNotFoundError on any integrity violation.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    root = Path(path_root).resolve() if path_root is not None else Path.cwd().resolve()

    records = list(adapter.iter_videos())
    if not records:
        raise ValueError(
            f"Adapter '{adapter.name}' yielded zero records from root_dir={adapter.root_dir!r}."
        )

    if any(r.dataset == "smoketest" for r in records):
        logger.warning(
            "Smoke-test fixtures detected in manifest build. "
            "These are pipeline fixtures ONLY and must never be used for "
            "training metrics or evaluation claims."
        )

    # Normalize first (portable path strings), then validate using SAME root.
    normalized = [_normalize_record_path(r, root) for r in records]
    _validate_records(
        normalized,
        path_root=root,
        require_files_exist=require_files_exist,
    )

    manifest_path = out_dir / manifest_filename
    _write_manifest_csv(manifest_path, normalized)

    extra_path: Optional[Path] = None
    if any(r.extra for r in normalized):
        extra_path = out_dir / extra_filename
        _write_extra_jsonl(extra_path, normalized)

    num_real = sum(1 for r in normalized if r.label == 0)
    num_fake = sum(1 for r in normalized if r.label == 1)
    num_groups = len({r.source_video_id for r in normalized})
    datasets = tuple(sorted({r.dataset for r in normalized}))

    logger.info(
        "Wrote manifest: %s | rows=%d real=%d fake=%d sources=%d datasets=%s",
        manifest_path.as_posix(),
        len(normalized),
        num_real,
        num_fake,
        num_groups,
        list(datasets),
    )

    return ManifestResult(
        manifest_path=manifest_path,
        extra_path=extra_path,
        num_records=len(normalized),
        num_real=num_real,
        num_fake=num_fake,
        num_source_groups=num_groups,
        datasets=datasets,
    )


def load_manifest(manifest_path: str | Path) -> List[dict]:
    """
    Load manifest.csv into a list of plain dict rows.

    Notes:
        - label is returned as int
        - empty manipulation_type becomes None
    """
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    rows: List[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Manifest has no header: {path}")

        missing = [c for c in MANIFEST_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Manifest schema missing columns {missing}. Found={list(reader.fieldnames)}"
            )

        seen_ids: Set[str] = set()
        for i, row in enumerate(reader, start=2):  # header is line 1
            video_id = (row.get("video_id") or "").strip()
            if not video_id:
                raise ValueError(f"Line {i}: empty video_id")
            if video_id in seen_ids:
                raise ValueError(f"Line {i}: duplicate video_id={video_id!r}")
            seen_ids.add(video_id)

            try:
                label = int(row["label"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Line {i}: invalid label={row.get('label')!r}") from exc
            if label not in (0, 1):
                raise ValueError(f"Line {i}: label must be 0 or 1, got {label}")

            source_video_id = (row.get("source_video_id") or "").strip()
            if not source_video_id:
                raise ValueError(f"Line {i}: empty source_video_id for video_id={video_id!r}")

            manipulation = (row.get("manipulation_type") or "").strip()
            manipulation_type: Optional[str] = manipulation if manipulation else None

            # Enforce the same REAL/FAKE manipulation rule on load.
            if label == 0 and manipulation_type is not None:
                raise ValueError(
                    f"Line {i}: REAL video_id={video_id!r} must have empty manipulation_type"
                )
            if label == 1 and manipulation_type is None:
                raise ValueError(
                    f"Line {i}: FAKE video_id={video_id!r} must have non-empty manipulation_type"
                )

            rows.append(
                {
                    "video_id": video_id,
                    "path": (row.get("path") or "").strip(),
                    "dataset": (row.get("dataset") or "").strip(),
                    "label": label,
                    "source_video_id": source_video_id,
                    "manipulation_type": manipulation_type,
                }
            )

    if not rows:
        raise ValueError(f"Manifest is empty: {path}")

    return rows


def resolve_manifest_path(path_str: str, path_root: str | Path | None = None) -> Path:
    """
    Resolve a path string from the manifest using path_root semantics.

    Order:
        1. If absolute, use as-is.
        2. Try path_root / relative.
        3. Try CWD / relative.
        4. Return path_root-joined path even if missing (caller decides).
    """
    root = Path(path_root).resolve() if path_root is not None else Path.cwd().resolve()
    p = Path(path_str)

    if p.is_absolute():
        return p

    candidate_root = (root / p).resolve()
    if candidate_root.exists():
        return candidate_root

    candidate_cwd = (Path.cwd() / p).resolve()
    if candidate_cwd.exists():
        return candidate_cwd

    # Prefer path_root semantics when nothing exists yet / for error messages.
    return candidate_root


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize_record_path(record: VideoRecord, path_root: Path) -> VideoRecord:
    """
    Return a new VideoRecord with path rewritten to a portable POSIX string.

    Prefer path relative to path_root. Fall back to absolute POSIX path.
    """
    raw = Path(record.path)
    abs_path = raw if raw.is_absolute() else (Path.cwd() / raw)
    abs_path = abs_path.resolve()

    try:
        portable = abs_path.relative_to(path_root).as_posix()
    except ValueError:
        portable = abs_path.as_posix()

    return VideoRecord(
        video_id=record.video_id,
        path=portable,
        dataset=record.dataset,
        label=record.label,
        source_video_id=record.source_video_id,
        manipulation_type=record.manipulation_type,
        extra=dict(record.extra),
    )


def _validate_records(
    records: Sequence[VideoRecord],
    *,
    path_root: Path,
    require_files_exist: bool,
) -> None:
    """
    Validate record integrity.

    Existence checks resolve relative paths against the SAME path_root used
    during normalization.
    """
    seen_ids: Set[str] = set()
    seen_paths: Set[str] = set()

    for r in records:
        if r.video_id in seen_ids:
            raise ValueError(f"Duplicate video_id in adapter output: {r.video_id!r}")
        seen_ids.add(r.video_id)

        if r.path in seen_paths:
            raise ValueError(
                f"Duplicate path in adapter output: {r.path!r} (video_id={r.video_id!r})"
            )
        seen_paths.add(r.path)

        if not r.source_video_id.strip():
            raise ValueError(f"Empty source_video_id for video_id={r.video_id!r}")

        if require_files_exist:
            resolved = resolve_manifest_path(r.path, path_root=path_root)
            if not resolved.exists():
                raise FileNotFoundError(
                    f"Video file does not exist for video_id={r.video_id!r}: "
                    f"stored={r.path!r}, resolved={resolved.as_posix()!r}, "
                    f"path_root={path_root.as_posix()!r}"
                )


def _write_manifest_csv(path: Path, records: Sequence[VideoRecord]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(MANIFEST_COLUMNS))
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "video_id": r.video_id,
                    "path": r.path,
                    "dataset": r.dataset,
                    "label": r.label,
                    "source_video_id": r.source_video_id,
                    # REAL → empty cell; FAKE → concrete manipulation family
                    "manipulation_type": r.manipulation_type or "",
                }
            )


def _write_extra_jsonl(path: Path, records: Sequence[VideoRecord]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            if not r.extra:
                continue
            payload = {"video_id": r.video_id, "extra": r.extra}
            f.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + "\n")