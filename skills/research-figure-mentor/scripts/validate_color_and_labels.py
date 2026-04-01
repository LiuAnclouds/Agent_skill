#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def load_layout(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def is_hex_color(value: str) -> bool:
    return bool(HEX_COLOR_RE.match(value))


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    clean = value.lstrip("#")
    if len(clean) == 8:
        clean = clean[:6]
    return tuple(int(clean[idx : idx + 2], 16) / 255.0 for idx in (0, 2, 4))


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float:
    fg = relative_luminance(hex_to_rgb(foreground))
    bg = relative_luminance(hex_to_rgb(background))
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return (lighter + 0.05) / (darker + 0.05)


def validate_colors_and_labels(layout: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    elements = layout.get("elements", [])
    legend = layout.get("legend", [])
    label_to_ids: dict[str, list[str]] = {}
    category_to_fill: dict[str, str] = {}
    distinct_fills: set[str] = set()

    for idx, element in enumerate(elements):
        element_id = str(element.get("id", f"element_{idx}"))
        label = str(element.get("label", "")).strip()
        if label:
            label_to_ids.setdefault(label, []).append(element_id)

        for key in ("fill", "stroke", "color", "text_color"):
            value = element.get(key)
            if value is None:
                continue
            value = str(value)
            if not is_hex_color(value):
                errors.append(f"{element_id} has invalid {key}: {value}")
            if key == "fill":
                distinct_fills.add(value)

        fill = element.get("fill")
        text_color = element.get("text_color")
        if fill and text_color and is_hex_color(str(fill)) and is_hex_color(str(text_color)):
            if contrast_ratio(str(text_color), str(fill)) < 3.0:
                warnings.append(f"{element_id} may have low text/background contrast")

        category = str(element.get("category", "")).strip()
        fill_value = str(element.get("fill", "")).strip()
        if category and fill_value:
            existing = category_to_fill.get(category)
            if existing is None:
                category_to_fill[category] = fill_value
            elif existing != fill_value:
                warnings.append(f"category {category} uses inconsistent fill colors")

    for label, ids in label_to_ids.items():
        if len(ids) > 1:
            warnings.append(f"duplicate visible label '{label}' used by: {', '.join(ids)}")

    legend_labels: set[str] = set()
    legend_colors: dict[str, str] = {}
    for item in legend:
        label = str(item.get("label", "")).strip()
        color = str(item.get("color", "")).strip()
        if label in legend_labels:
            errors.append(f"duplicate legend label: {label}")
        legend_labels.add(label)
        if color and not is_hex_color(color):
            errors.append(f"legend item {label or '<empty>'} has invalid color: {color}")
        if color:
            mapped = legend_colors.get(color)
            if mapped is not None and mapped != label:
                warnings.append(f"legend color {color} is reused by both '{mapped}' and '{label}'")
            legend_colors[color] = label

    if len(distinct_fills) > 8:
        warnings.append(f"too many distinct fill colors ({len(distinct_fills)}); simplify the palette")

    passed = not errors
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "distinct_fill_colors": len(distinct_fills),
            "legend_items": len(legend),
            "labeled_elements": len(label_to_ids),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate figure color usage and label consistency.")
    parser.add_argument("layout_json", type=Path, help="Path to figure_layout.json")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    result = validate_colors_and_labels(load_layout(args.layout_json))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
