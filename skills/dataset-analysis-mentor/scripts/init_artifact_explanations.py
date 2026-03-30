#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


HEADER = "# 产物逐项讲解\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown explanation skeleton from an artifact manifest."
    )
    parser.add_argument("manifest_csv", type=Path, help="Manifest CSV path.")
    parser.add_argument("output_md", type=Path, help="Markdown output path.")
    return parser.parse_args()


def build_section(relative_path: str, artifact_type: str) -> str:
    return (
        f"\n## `{relative_path}`\n\n"
        f"- artifact_type: `{artifact_type}`\n\n"
        "### 作用\n\n"
        "### 怎么看\n\n"
        "### 本项目中的实际现象\n\n"
        "### 建模/实验启发\n\n"
        "### 风险与补充检查\n"
    )


def main() -> None:
    args = parse_args()
    with args.manifest_csv.open("r", encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))

    parts = [HEADER]
    for row in rows:
        parts.append(build_section(row["relative_path"], row["artifact_type"]))

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")
    print(f"[OK] Wrote {args.output_md} for {len(rows)} artifacts")


if __name__ == "__main__":
    main()
