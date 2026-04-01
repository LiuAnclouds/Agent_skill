#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from pathlib import Path
from typing import Any


NON_ARROW_TYPES = {"box", "text", "group", "icon", "panel", "node"}


def load_layout(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canvas_size(layout: dict[str, Any]) -> tuple[float, float]:
    canvas = layout.get("canvas", {})
    width = float(canvas.get("width", 1.0))
    height = float(canvas.get("height", 1.0))
    if width <= 0 or height <= 0:
        raise ValueError("canvas width/height must be positive.")
    return width, height


def normalized_box(element: dict[str, Any], width: float, height: float) -> tuple[float, float, float, float]:
    x = float(element.get("x", 0.0))
    y = float(element.get("y", 0.0))
    w = float(element.get("width", 0.0))
    h = float(element.get("height", 0.0))
    if max(abs(x), abs(y), abs(w), abs(h)) > 1.5:
        return x / width, y / height, w / width, h / height
    return x, y, w, h


def box_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    return ix * iy


def estimated_label_capacity(element: dict[str, Any], width: float, height: float) -> int:
    _, _, w, h = normalized_box(element, width, height)
    w_px = w * width
    h_px = h * height
    font_size = float(element.get("font_size", 18))
    chars_per_line = max(1, int(w_px / max(font_size * 0.65, 1.0)))
    lines = max(1, int(h_px / max(font_size * 1.5, 1.0)))
    return chars_per_line * lines


def validate_layout(layout: dict[str, Any]) -> dict[str, Any]:
    width, height = canvas_size(layout)
    elements = layout.get("elements", [])
    errors: list[str] = []
    warnings: list[str] = []
    stats = {
        "element_count": len(elements),
        "node_count": 0,
        "arrow_count": 0,
    }

    by_id: dict[str, dict[str, Any]] = {}
    node_boxes: list[tuple[str, tuple[float, float, float, float], dict[str, Any]]] = []

    for idx, element in enumerate(elements):
        element_id = str(element.get("id", "")).strip()
        if not element_id:
            errors.append(f"element[{idx}] is missing id")
            continue
        if element_id in by_id:
            errors.append(f"duplicate element id: {element_id}")
            continue
        by_id[element_id] = element
        element_type = str(element.get("type", "box")).strip().lower()
        if element_type == "arrow":
            stats["arrow_count"] += 1
        else:
            stats["node_count"] += 1

        if element_type in NON_ARROW_TYPES:
            box = normalized_box(element, width, height)
            x, y, w, h = box
            node_boxes.append((element_id, box, element))
            if w <= 0 or h <= 0:
                errors.append(f"{element_id} has non-positive width/height")
            if x < 0 or y < 0 or x + w > 1 or y + h > 1:
                errors.append(f"{element_id} exceeds canvas bounds")

            label = str(element.get("label", "")).strip()
            if label:
                capacity = estimated_label_capacity(element, width, height)
                if len(label.replace("\n", "")) > capacity:
                    warnings.append(f"{element_id} label may overflow its box")

    for left, right in combinations(node_boxes, 2):
        left_id, left_box, left_meta = left
        right_id, right_box, right_meta = right
        if left_meta.get("allow_overlap") or right_meta.get("allow_overlap"):
            continue
        overlap = box_overlap(left_box, right_box)
        if overlap > 0.0:
            errors.append(f"{left_id} overlaps with {right_id}")

    for element in elements:
        if str(element.get("type", "")).lower() != "arrow":
            continue
        from_id = element.get("from")
        to_id = element.get("to")
        if not from_id or not to_id:
            errors.append(f"{element.get('id', 'arrow')} is missing from/to reference")
            continue
        if from_id not in by_id:
            errors.append(f"{element.get('id', 'arrow')} references missing source: {from_id}")
        if to_id not in by_id:
            errors.append(f"{element.get('id', 'arrow')} references missing target: {to_id}")
        if from_id == to_id:
            warnings.append(f"{element.get('id', 'arrow')} loops to the same element")

    reading_order = layout.get("reading_order", [])
    if reading_order:
        seen = set()
        for item in reading_order:
            if item in seen:
                errors.append(f"reading_order contains duplicate id: {item}")
            seen.add(item)
            if item not in by_id:
                errors.append(f"reading_order references missing id: {item}")

    passed = not errors
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate figure layout geometry and connectivity.")
    parser.add_argument("layout_json", type=Path, help="Path to figure_layout.json")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    result = validate_layout(load_layout(args.layout_json))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
