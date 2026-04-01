#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_color_and_labels import load_layout, validate_colors_and_labels
from validate_figure_layout import validate_layout


MANUAL_ITEMS = {
    "common": [
        "title matches the actual figure purpose",
        "main story is obvious at first glance",
        "labels are readable at export size",
        "colors encode semantics instead of decoration",
        "second-pass refinement did not introduce semantic drift",
    ],
    "system": [
        "system boundary and main runtime flow are clear",
        "optional paths are visually weaker than the main path",
    ],
    "data": [
        "the strongest contrast is visually dominant",
        "the chart supports one clear conclusion",
    ],
    "model": [
        "the figure is faithful to the real forward path",
        "repeated blocks and branch fusion are represented correctly",
    ],
}


def build_report(layout: dict[str, Any], task_type: str) -> dict[str, Any]:
    layout_result = validate_layout(layout)
    color_result = validate_colors_and_labels(layout)
    auto_errors = layout_result["errors"] + color_result["errors"]
    auto_warnings = layout_result["warnings"] + color_result["warnings"]
    manual = MANUAL_ITEMS["common"] + MANUAL_ITEMS.get(task_type, [])
    overall = "pass" if not auto_errors else "fail"

    return {
        "overall_status": overall,
        "task_type": task_type,
        "automatic_checks": {
            "layout": layout_result,
            "colors_and_labels": color_result,
        },
        "manual_review_required": manual,
        "summary": {
            "error_count": len(auto_errors),
            "warning_count": len(auto_warnings),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate figure validation results into one report.")
    parser.add_argument("layout_json", type=Path, help="Path to figure_layout.json")
    parser.add_argument(
        "--task-type",
        choices=("system", "data", "model", "mixed"),
        default="mixed",
        help="Primary figure task type",
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    report = build_report(load_layout(args.layout_json), args.task_type)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    sys.exit(0 if report["overall_status"] == "pass" else 1)


if __name__ == "__main__":
    main()
