#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".csv",
    ".json",
    ".md",
    ".pdf",
    ".npy",
}


def artifact_type_for_suffix(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".svg"}:
        return "image"
    if suffix in {".csv", ".json", ".npy"}:
        return "data"
    if suffix == ".md":
        return "report"
    if suffix == ".pdf":
        return "document"
    return "other"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan an artifact directory and emit a manifest CSV."
    )
    parser.add_argument("artifacts_dir", type=Path, help="Directory to scan.")
    parser.add_argument("output_csv", type=Path, help="Manifest output CSV path.")
    parser.add_argument(
        "--extensions",
        default=",".join(sorted(DEFAULT_SUFFIXES)),
        help="Comma-separated suffix allowlist.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to skip. Repeatable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.artifacts_dir.resolve()
    suffixes = {
        value.strip().lower()
        for value in args.extensions.split(",")
        if value.strip()
    }
    excludes = set(args.exclude_dir)

    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in excludes for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffixes and suffix not in suffixes:
            continue
        rel = path.relative_to(root)
        rows.append(
            {
                "relative_path": rel.as_posix(),
                "artifact_type": artifact_type_for_suffix(suffix),
                "extension": suffix,
                "size_bytes": path.stat().st_size,
                "directory": rel.parent.as_posix() if rel.parent != Path(".") else ".",
                "stem": path.stem,
            }
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "relative_path",
                "artifact_type",
                "extension",
                "size_bytes",
                "directory",
                "stem",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Wrote {args.output_csv} with {len(rows)} rows")


if __name__ == "__main__":
    main()
