# Routing And Output Contract

## Task Routing

Route by requested figure intent, not by file type alone.

- System architecture branch:
  - “系统图”
  - “架构图”
  - “流程图”
  - “模块图”
  - “交互图”
  - “时序图”
  - “数据流图”
- Data figure branch:
  - “数据图”
  - “结果图”
  - “对比图”
  - “实验图”
  - “训练曲线”
  - “消融图”
  - “漂移图”
  - “分布图”
- Neural model branch:
  - “模型图”
  - “网络结构图”
  - “神经网络结构图”
  - “根据代码画模型”
  - “根据论文方法画模型”

Load multiple branches when the request mixes:

- system + model
- model + result figure
- system + data

## Internal Working Artifact

Create one internal planning artifact before validation. Use the lightest artifact that can still preserve the real figure semantics.

### Renderer-First Path: `figure_layout.json`

Use `figure_layout.json` for system diagrams, data figures, and simple model diagrams that fit the built-in renderer.

Recommended shape:

```json
{
  "task_name": "full-meanmax-model",
  "task_type": "model",
  "canvas": {
    "width": 1600,
    "height": 900,
    "title": "Figure 5 ..."
  },
  "elements": [
    {
      "id": "input_proj",
      "type": "box",
      "label": "Input Projection",
      "category": "encoder",
      "x": 0.40,
      "y": 0.20,
      "width": 0.18,
      "height": 0.10,
      "fill": "#DCEBFA",
      "stroke": "#31445A"
    },
    {
      "id": "arrow_1",
      "type": "arrow",
      "from": "input_proj",
      "to": "block_stack",
      "color": "#455A64"
    }
  ],
  "legend": [
    {
      "label": "Encoder",
      "category": "encoder",
      "color": "#DCEBFA"
    }
  ],
  "reading_order": ["seed_nodes", "sampler", "encoder", "fusion_head"]
}
```

Rules:

- Prefer normalized coordinates `0..1` for geometry.
- Use unique `id` values.
- Put arrows in `elements` with `type: "arrow"` and `from`/`to` references.
- Put meaningful `category` values on boxes when a legend or color family is used.
- Include `reading_order` when the reading path is not trivially left-to-right.

The first-pass renderer at `scripts/render_figure_from_layout.py` currently supports these element types directly:

- `box`
- `panel`
- `group`
- `node`
- `icon`
- `text`
- `arrow`

Recommended optional fields for better first-pass rendering:

- `subtitle` for secondary text inside a block
- `shape` with `circle`, `rectangle`, or default rounded rectangle
- `font_size`, `linewidth`, `alpha`, `zorder`
- `start_anchor` / `end_anchor` for arrow routing control
- `curve` for curved arrows

Recommended render command:

```bash
python scripts/render_figure_from_layout.py figure_layout.json --output-dir outputs/figures/<task-name>
```

### Native Python Path: `render_<task-name>_native.py`

Use a native Python script for advanced neural/model-heavy figures that require graph topology insets, tensor slices, embedded equations, panel-local `NetworkX` plots, or cross-panel residual pointers.

Rules:

- Start from `scripts/render_neural_model_v7_template.py` when the figure is publication-facing and model-heavy.
- Keep one function per major panel or stage instead of scattering geometry across the file.
- Centralize helper primitives for panel backgrounds, cross-panel arrows, and tensor blocks.
- Save exports into `outputs/figures/<task-name>/` unless the user specifies another path.

Recommended adaptation flow:

1. Copy or adapt `scripts/render_neural_model_v7_template.py` into the active workspace as `render_<task-name>_native.py`.
2. Rename panels and replace placeholder topology/tensor labels with the real model semantics.
3. Render once, inspect the output manually, refine, and export the final figure.

## Default Output

- Export `PNG + PDF`
- Export `SVG` only on explicit request
- If the user does not give a path, use `outputs/figures/<task-name>/`
- Keep the final figure clean; the internal JSON and validation outputs are not required to be user-facing
- When using the renderer, keep validation reports in `outputs/figures/<task-name>/reports/`

## Web Reference Trigger

Reference review is mandatory when any of the following is true:

- the task is a neural model figure
- the task is a paper-facing or thesis-facing system figure
- the user explicitly asks for “论文风格”, “顶刊风格”, “参考高质量图”, or equivalent

When reference review is triggered, use web search for visual inspiration and layout patterns, then refine the figure and validate again.
