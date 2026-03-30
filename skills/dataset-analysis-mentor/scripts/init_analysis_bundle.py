#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a report bundle for dataset analysis outputs."
    )
    parser.add_argument(
        "target_root",
        type=Path,
        help="Project directory where the reports folder should be created.",
    )
    parser.add_argument(
        "--report-dir",
        default="reports",
        help="Relative report directory under target_root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files.",
    )
    return parser.parse_args()


def copy_template(src: Path, dst: Path, force: bool) -> None:
    if dst.exists() and not force:
        print(f"[SKIP] {dst} already exists")
        return
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[OK] Wrote {dst}")


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    assets_dir = skill_root / "assets"
    target_root = args.target_root.resolve()
    report_dir = target_root / args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    copy_template(
        assets_dir / "dataset-analysis-report-template.md",
        report_dir / "dataset-analysis-report.md",
        force=args.force,
    )
    copy_template(
        assets_dir / "artifact-explanation-template.md",
        report_dir / "artifact-explanations.md",
        force=args.force,
    )

    artifact_index = report_dir / "artifact-index.csv"
    if not artifact_index.exists() or args.force:
        artifact_index.write_text(
            "relative_path,artifact_type,extension,size_bytes,directory,stem\n",
            encoding="utf-8",
        )
        print(f"[OK] Wrote {artifact_index}")
    else:
        print(f"[SKIP] {artifact_index} already exists")


if __name__ == "__main__":
    main()
