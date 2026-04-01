#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
    print(
        "matplotlib is required for render_figure_from_layout.py. "
        "Install it first, for example: pip install matplotlib",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

from figure_checklist_report import build_report
from validate_color_and_labels import is_hex_color, load_layout, validate_colors_and_labels
from validate_figure_layout import canvas_size, normalized_box, validate_layout


DEFAULT_FORMATS = ("png", "pdf")
SUPPORTED_FORMATS = {"png", "pdf", "svg"}
DEFAULT_TEXT_COLOR = "#23313F"
DEFAULT_STROKE = "#31445A"
DEFAULT_FILL = "#ECEFF1"
DEFAULT_ARROW = "#455A64"


plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.bbox"] = "tight"


def load_palette(skill_root: Path, name: str) -> dict[str, str]:
    palette_path = skill_root.parent / "assets" / "palette-presets.json"
    payload = json.loads(palette_path.read_text(encoding="utf-8-sig"))
    palette = payload.get(name)
    if not isinstance(palette, dict):
        available = ", ".join(sorted(payload))
        raise ValueError(f"unknown palette '{name}'. Available palettes: {available}")
    return {str(key): str(value) for key, value in palette.items()}


def detect_palette_name(layout: dict[str, Any]) -> str:
    task_type = str(layout.get("task_type", "")).strip().lower()
    if task_type == "system":
        return "system_layers"
    if task_type == "data":
        return "data_contrast"
    return "semantic_blueprint"


def resolve_output_dir(layout: dict[str, Any], output_dir: Path | None) -> Path:
    if output_dir is not None:
        return output_dir
    task_name = str(layout.get("task_name", "")).strip() or "figure-task"
    return Path.cwd() / "outputs" / "figures" / task_name


def element_box(element: dict[str, Any], width: float, height: float) -> tuple[float, float, float, float]:
    x, y, w, h = normalized_box(element, width, height)
    return x, y, w, h


def element_center(element: dict[str, Any], width: float, height: float) -> tuple[float, float]:
    x, y, w, h = element_box(element, width, height)
    return x + w / 2.0, y + h / 2.0


def resolve_color(element: dict[str, Any], key: str, palette: dict[str, str], fallback: str) -> str:
    raw = str(element.get(key, "")).strip()
    if raw:
        return raw
    category = str(element.get("category", "")).strip()
    if category and category in palette and key == "fill":
        return palette[category]
    if key == "stroke" and "stroke" in palette:
        return palette["stroke"]
    if key == "color" and "arrow" in palette:
        return palette["arrow"]
    if key == "text_color" and "stroke" in palette:
        return palette["stroke"]
    return fallback


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def resolve_anchor_point(
    element: dict[str, Any],
    width: float,
    height: float,
    toward: tuple[float, float],
    explicit_anchor: str | None = None,
) -> tuple[float, float]:
    x, y, w, h = element_box(element, width, height)
    cx, cy = x + w / 2.0, y + h / 2.0
    anchor = (explicit_anchor or "").strip().lower()
    if anchor == "left":
        return x, cy
    if anchor == "right":
        return x + w, cy
    if anchor == "top":
        return cx, y
    if anchor == "bottom":
        return cx, y + h
    if anchor == "center":
        return cx, cy

    tx, ty = toward
    dx = tx - cx
    dy = ty - cy
    if abs(dx) >= abs(dy):
        return (x + w, cy) if dx >= 0 else (x, cy)
    return (cx, y + h) if dy >= 0 else (cx, y)


def wrap_label(label: str, width_fraction: float, base_chars: int = 28) -> str:
    if not label or "\n" in label:
        return label
    limit = max(10, int(base_chars * max(width_fraction, 0.08) / 0.18))
    wrapper = textwrap.TextWrapper(width=limit, break_long_words=False, break_on_hyphens=False)
    return wrapper.fill(label)


def fit_box_text(
    label: str,
    box_width: float,
    box_height: float,
    canvas_width: float,
    canvas_height: float,
    font_size: float,
    min_font_size: float = 9.0,
) -> tuple[str, float]:
    if not label:
        return "", font_size

    current_size = font_size
    width_px = box_width * canvas_width
    height_px = box_height * canvas_height
    while True:
        chars_per_line = max(6, int(width_px / max(current_size * 0.95, 1.0)))
        wrapper = textwrap.TextWrapper(
            width=chars_per_line,
            break_long_words=False,
            break_on_hyphens=False,
        )
        wrapped = wrapper.fill(label)
        line_count = len(wrapped.splitlines()) or 1
        max_lines = max(1, int(height_px / max(current_size * 1.35, 1.0)))
        longest_line = max(len(line) for line in wrapped.splitlines() or [""])
        estimated_line_width = longest_line * current_size * 0.9
        width_fits = estimated_line_width <= width_px * 0.84
        if (line_count <= max_lines and width_fits) or current_size <= min_font_size:
            return wrapped, current_size
        current_size -= 1.0


def draw_rect_like(
    ax: Any,
    element: dict[str, Any],
    width: float,
    height: float,
    palette: dict[str, str],
) -> None:
    x, y, w, h = element_box(element, width, height)
    fill = resolve_color(element, "fill", palette, DEFAULT_FILL)
    stroke = resolve_color(element, "stroke", palette, DEFAULT_STROKE)
    text_color = resolve_color(element, "text_color", palette, DEFAULT_TEXT_COLOR)
    linewidth = float(element.get("linewidth", 1.6))
    alpha = float(element.get("alpha", 1.0))
    rounding = float(element.get("rounding", 0.02))
    zorder = float(element.get("zorder", 2))
    shape = str(element.get("shape", "")).strip().lower()
    linestyle = str(element.get("linestyle", "-"))

    if shape == "circle":
        radius = min(w, h) / 2.0
        patch = Circle(
            (x + w / 2.0, y + h / 2.0),
            radius=radius,
            facecolor=fill,
            edgecolor=stroke,
            linewidth=linewidth,
            linestyle=linestyle,
            alpha=alpha,
            zorder=zorder,
        )
    elif shape == "rectangle":
        patch = Rectangle(
            (x, y),
            w,
            h,
            facecolor=fill,
            edgecolor=stroke,
            linewidth=linewidth,
            linestyle=linestyle,
            alpha=alpha,
            zorder=zorder,
        )
    else:
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0.005,rounding_size={rounding}",
            facecolor=fill,
            edgecolor=stroke,
            linewidth=linewidth,
            linestyle=linestyle,
            alpha=alpha,
            zorder=zorder,
        )
    ax.add_patch(patch)

    label = str(element.get("label", "")).strip()
    if label:
        font_size = float(element.get("font_size", 14))
        label, font_size = fit_box_text(label, w, h, width, height, font_size)
        ax.text(
            x + w / 2.0,
            y + h / 2.0,
            label,
            ha=str(element.get("align", "center")),
            va=str(element.get("valign", "center")),
            fontsize=font_size,
            fontweight=str(element.get("font_weight", "normal")),
            color=text_color,
            zorder=zorder + 0.5,
        )

    subtitle = str(element.get("subtitle", "")).strip()
    if subtitle:
        subtitle_text, subtitle_size = fit_box_text(
            subtitle,
            w * 0.92,
            max(h * 0.28, 0.035),
            width,
            height,
            max(8.0, float(element.get("font_size", 14)) - 2.5),
            min_font_size=8.0,
        )
        ax.text(
            x + w / 2.0,
            y + h - min(0.012, h * 0.18),
            subtitle_text,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontweight=str(element.get("subtitle_weight", "normal")),
            color=text_color,
            alpha=0.9,
            zorder=zorder + 0.5,
        )


def draw_text(ax: Any, element: dict[str, Any], width: float, height: float, palette: dict[str, str]) -> None:
    x = float(element.get("x", 0.0))
    y = float(element.get("y", 0.0))
    if max(abs(x), abs(y)) > 1.5:
        x /= width
        y /= height
    ax.text(
        clamp(x, 0.0, 1.0),
        clamp(y, 0.0, 1.0),
        str(element.get("label", "")),
        ha=str(element.get("align", "left")),
        va=str(element.get("valign", "center")),
        fontsize=float(element.get("font_size", 13)),
        fontweight=str(element.get("font_weight", "normal")),
        color=resolve_color(element, "text_color", palette, DEFAULT_TEXT_COLOR),
        alpha=float(element.get("alpha", 1.0)),
        zorder=float(element.get("zorder", 4)),
    )


def draw_arrow(
    ax: Any,
    element: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    width: float,
    height: float,
    palette: dict[str, str],
) -> None:
    source_id = str(element.get("from", "")).strip()
    target_id = str(element.get("to", "")).strip()
    if not source_id or not target_id:
        return
    if source_id not in nodes or target_id not in nodes:
        return

    source = nodes[source_id]
    target = nodes[target_id]
    target_center = element_center(target, width, height)
    source_center = element_center(source, width, height)
    start = resolve_anchor_point(source, width, height, target_center, element.get("start_anchor"))
    end = resolve_anchor_point(target, width, height, source_center, element.get("end_anchor"))
    color = resolve_color(element, "color", palette, DEFAULT_ARROW)

    arrow = FancyArrowPatch(
        start,
        end,
        connectionstyle=f"arc3,rad={float(element.get('curve', 0.0))}",
        arrowstyle=str(element.get("arrowstyle", "-|>")),
        mutation_scale=float(element.get("mutation_scale", 12)),
        linewidth=float(element.get("linewidth", 1.8)),
        linestyle=str(element.get("linestyle", "-")),
        color=color,
        alpha=float(element.get("alpha", 1.0)),
        zorder=float(element.get("zorder", 3)),
        shrinkA=float(element.get("shrink_a", 2.5)),
        shrinkB=float(element.get("shrink_b", 2.5)),
    )
    ax.add_patch(arrow)

    label = str(element.get("label", "")).strip()
    if label:
        mx = (start[0] + end[0]) / 2.0
        my = (start[1] + end[1]) / 2.0
        ax.text(
            mx,
            my - 0.015,
            label,
            ha="center",
            va="bottom",
            fontsize=float(element.get("font_size", 11)),
            fontweight=str(element.get("font_weight", "normal")),
            color=resolve_color(element, "text_color", palette, DEFAULT_TEXT_COLOR),
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "#FFFFFF",
                "edgecolor": "none",
                "alpha": 0.85,
            },
            zorder=float(element.get("zorder", 4)),
        )


def add_title(fig: Any, layout: dict[str, Any], palette: dict[str, str]) -> None:
    canvas = layout.get("canvas", {})
    title = str(canvas.get("title", "")).strip()
    if not title:
        return
    fig.text(
        0.5,
        0.985,
        title,
        ha="center",
        va="top",
        fontsize=float(canvas.get("title_font_size", 18)),
        color=str(canvas.get("title_color", palette.get("stroke", DEFAULT_TEXT_COLOR))),
        fontweight=str(canvas.get("title_weight", "semibold")),
    )


def add_legend(fig: Any, layout: dict[str, Any], palette: dict[str, str]) -> None:
    legend = layout.get("legend", [])
    if not legend:
        return
    handles = []
    labels = []
    for item in legend:
        color = str(item.get("color", "")).strip()
        if not is_hex_color(color):
            color = palette.get(str(item.get("category", "")).strip(), DEFAULT_FILL)
        patch = Rectangle((0, 0), 1, 1, facecolor=color, edgecolor=palette.get("stroke", DEFAULT_STROKE))
        handles.append(patch)
        labels.append(str(item.get("label", "")).strip() or str(item.get("category", "")).strip())
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=min(4, max(1, len(handles))),
        frameon=False,
        fontsize=10,
        handlelength=1.2,
        columnspacing=1.4,
    )


def render_layout(
    layout: dict[str, Any],
    output_dir: Path,
    formats: tuple[str, ...],
    dpi: int,
    palette_name: str | None = None,
) -> list[Path]:
    width_px, height_px = canvas_size(layout)
    palette = load_palette(Path(__file__).resolve().parent, palette_name or detect_palette_name(layout))
    canvas = layout.get("canvas", {})
    background = str(canvas.get("background", "#FFFFFF"))
    fig = plt.figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi, facecolor=background)
    ax = fig.add_axes([0.03, 0.07, 0.94, 0.84])
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(1.0, 0.0)
    ax.axis("off")
    ax.set_facecolor(background)

    elements = layout.get("elements", [])
    nodes = {
        str(element.get("id", "")): element
        for element in elements
        if str(element.get("type", "")).strip().lower() != "arrow"
    }

    non_arrows = sorted(
        (element for element in elements if str(element.get("type", "")).strip().lower() != "arrow"),
        key=lambda item: float(item.get("zorder", 2)),
    )
    arrows = sorted(
        (element for element in elements if str(element.get("type", "")).strip().lower() == "arrow"),
        key=lambda item: float(item.get("zorder", 3)),
    )

    for element in non_arrows:
        element_type = str(element.get("type", "box")).strip().lower()
        if element_type in {"box", "panel", "group", "icon", "node"}:
            draw_rect_like(ax, element, width_px, height_px, palette)
        elif element_type == "text":
            draw_text(ax, element, width_px, height_px, palette)

    for element in arrows:
        draw_arrow(ax, element, nodes, width_px, height_px, palette)

    add_title(fig, layout, palette)
    add_legend(fig, layout, palette)

    output_dir.mkdir(parents=True, exist_ok=True)
    basename = str(layout.get("task_name", "")).strip() or "figure"
    rendered_paths: list[Path] = []
    for fmt in formats:
        save_path = output_dir / f"{basename}.{fmt}"
        fig.savefig(save_path, dpi=dpi, facecolor=background)
        rendered_paths.append(save_path)
    plt.close(fig)
    return rendered_paths


def run_validation(layout: dict[str, Any], task_type: str, output_dir: Path) -> dict[str, Path]:
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    layout_report = validate_layout(layout)
    label_color_report = validate_colors_and_labels(layout)
    checklist_report = build_report(layout, task_type)
    geometry_path = reports_dir / "layout-validation.json"
    label_color_path = reports_dir / "color-and-label-validation.json"
    checklist_path = reports_dir / "figure-checklist-report.json"
    geometry_path.write_text(json.dumps(layout_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    label_color_path.write_text(json.dumps(label_color_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    checklist_path.write_text(json.dumps(checklist_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "layout_validation": geometry_path,
        "color_and_label_validation": label_color_path,
        "checklist_report": checklist_path,
    }


def parse_formats(value: str) -> tuple[str, ...]:
    formats = tuple(part.strip().lower() for part in value.split(",") if part.strip())
    if not formats:
        raise ValueError("at least one output format is required")
    invalid = sorted(set(formats) - SUPPORTED_FORMATS)
    if invalid:
        raise ValueError(f"unsupported format(s): {', '.join(invalid)}")
    return formats


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a publication-style figure from figure_layout.json")
    parser.add_argument("layout_json", type=Path, help="Path to figure_layout.json")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory for rendered files")
    parser.add_argument(
        "--formats",
        default="png,pdf",
        help="Comma-separated output formats. Supported: png,pdf,svg",
    )
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI for raster exports")
    parser.add_argument(
        "--palette",
        default=None,
        help="Optional palette override. Defaults to a palette inferred from task_type",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip writing validation reports before rendering",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Abort rendering if validation reports contain errors",
    )
    args = parser.parse_args()

    layout = load_layout(args.layout_json)
    formats = parse_formats(args.formats)
    output_dir = resolve_output_dir(layout, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    task_type = str(layout.get("task_type", "mixed")).strip().lower() or "mixed"
    report_paths: dict[str, Path] = {}
    if not args.skip_validation:
        report_paths = run_validation(layout, task_type, output_dir)
        checklist = json.loads(report_paths["checklist_report"].read_text(encoding="utf-8"))
        if args.strict and checklist.get("overall_status") != "pass":
            print(
                json.dumps(
                    {
                        "rendered": False,
                        "reason": "validation_failed",
                        "reports": {key: str(value) for key, value in report_paths.items()},
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            raise SystemExit(1)

    rendered = render_layout(layout, output_dir, formats, args.dpi, args.palette)
    print(
        json.dumps(
            {
                "rendered": True,
                "outputs": [str(path) for path in rendered],
                "reports": {key: str(value) for key, value in report_paths.items()},
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
