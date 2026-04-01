---
name: research-figure-mentor
description: Publication-grade figure workflow for system architecture diagrams, data analysis figures, and neural network model diagrams. Use when Codex needs to draw or refine system diagrams, architecture diagrams, flowcharts, data comparison charts, EDA figures, experiment/result figures, or code-faithful neural model figures; trigger for requests like “画系统图”, “画架构图”, “画流程图”, “画数据图”, “做论文风格图表”, “根据代码画模型图”, “按代码画网络结构图”, “优化图布局/配色/箭头/文字位置”, or tasks requiring two-pass validation and reference-driven refinement against strong paper-quality visuals.
---

# Research Figure Mentor

## Overview

Create figures that are both faithful to the source material and strong enough for papers, theses, midterm reviews, and technical presentations. Prefer a code/data/system-grounded workflow over aesthetic guesswork.

Read [references/routing-and-output-contract.md](references/routing-and-output-contract.md) first. Then load only the branch references needed for the current request.

## Routing

Route the task into one or more branches before drawing anything.

- Load [references/system-architecture-playbook.md](references/system-architecture-playbook.md) for system architecture, workflow, sequence, interaction, or dataflow diagrams.
- Load [references/data-figure-playbook.md](references/data-figure-playbook.md) for EDA, result comparison, drift, distribution, ranking, correlation, or experiment charts.
- Load [references/neural-model-figure-playbook.md](references/neural-model-figure-playbook.md) for model structure figures built from code or paper method descriptions.
- Load [references/native-neural-v7-template.md](references/native-neural-v7-template.md) when a neural/model figure needs native Python rendering with `matplotlib.patches` + `NetworkX`, especially for graph topology insets, tensor slices, equations, or dense multi-panel academic layouts.
- Load [references/dynamic-graph-anomaly-figure-patterns.md](references/dynamic-graph-anomaly-figure-patterns.md) when the figure is about dynamic graphs, relation graphs, anomaly detection, subgraph reasoning, or when the user explicitly wants node-edge evolution shown across panels.
- Always load [references/visual-style-guide.md](references/visual-style-guide.md) before final layout decisions.
- Always load [references/validation-checklist.md](references/validation-checklist.md) before final export.
- Load [references/reference-review-playbook.md](references/reference-review-playbook.md) when the task is model-heavy, paper-facing, architecture-heavy, or explicitly asks for top-tier visual quality.

If one request spans multiple figure types, keep one shared figure story but apply every relevant branch workflow. Do not split into separate external skills.

## Core Workflow

1. Identify the exact figure objective before choosing a layout.
2. Inspect the real source material first.
   - For system figures: read the description, entrypoints, modules, interfaces, and control/data flow.
   - For data figures: read tables, CSV/JSON artifacts, EDA outputs, metrics, and experiment summaries.
   - For model figures: read the code path, forward path, tensor flow, branches, skips, heads, and configuration switches.
3. Decide the figure family only after understanding the object.
4. Draft one internal planning artifact before rendering:
   - `figure_layout.json` for renderer-first system/data/simple model figures.
   - a native Python scaffold based on `scripts/render_neural_model_v7_template.py` for dense neural/model figures that need the v7-style publication layout.
5. Produce the first figure draft with the matching scaffold:
   - `scripts/render_figure_from_layout.py` for the JSON path.
   - `scripts/render_neural_model_v7_template.py` as the starting template for the native Python path.
6. Run the first validation pass:
   - JSON path: `scripts/validate_figure_layout.py`, `scripts/validate_color_and_labels.py`, `scripts/figure_checklist_report.py`
   - native Python path: render once at target size, then inspect bounds, overlaps, arrow routing, label fit, and color semantics with [references/validation-checklist.md](references/validation-checklist.md)
7. If the task is high-stakes or paper-facing, perform the reference-review step and refine the draft.
8. Run the second validation pass after refinement.
9. Export the final figure.

Never start from a decorative sketch and backfill semantics afterward.

## Branch Rules

### System Architecture Figures

- Extract system boundary, major modules, external dependencies, input/output, primary flow, optional flow, and failure path.
- Choose the diagram type that best matches the job:
  - module architecture for layers and subsystems
  - flowchart for execution steps
  - sequence/interaction diagram for role coordination
  - dataflow diagram for data movement
- Keep the main path visually dominant.
- Align peer modules and standardize arrow direction.
- Normalize names; do not mix colloquial labels and code identifiers without reason.
- For large systems, prefer one overview figure plus one detailed figure instead of one overloaded figure.

### Data Analysis Figures

- Decide what the chart must prove before choosing the chart type.
- Prefer contrast-first chart forms:
  - comparative bars
  - dual-phase line plots
  - heatmaps
  - ranked horizontal bars
  - small multiples
- Make the title conclusion-oriented when appropriate.
- Highlight thresholds, abnormal points, phase boundaries, top-k items, or large deltas when they help the main reading.
- Avoid archive-style “everything at once” plots for paper-facing requests. Prefer selective, conclusion-carrying figures.

### Neural Network Model Figures

- Read the model code thoroughly before drawing.
- Reconstruct the exact execution path: input branches, encoder backbone, normalization/residual blocks, pooling/fusion/JK paths, and output heads.
- **Advanced Rendering Paradigm (Critical for Publication-Grade Graphics)**:
  - **Basic Flowcharts**: Use the default `figure_layout.json` scaffold *only* for highly abstracted, high-level schematic box-and-arrow system charts.
  - **Academic / Neural Style (Preferred State-of-the-Art)**: When tasks demand top-tier academic figures (e.g., explicit graph topologies, 3D tensor block slices, complex mathematical notation, cross-layer residual pointers), **DO NOT force the drawing into the rigid `figure_layout.json` coordinates**. Instead, dynamically author a robust, native Python script leveraging `matplotlib.patches` (for layered bounding boxes, spatial coordinates, 3D matrix visualization) and `NetworkX` (for accurate subgraph topology/fanout representation).
  - For advanced neural/model-heavy figures, start from the native v7-style scaffold at `scripts/render_neural_model_v7_template.py` instead of squeezing the design into JSON.
  - Represent dataset/sampling stages precisely with visual node-edge connected topologies (e.g., gold center nodes with multi-hop colored neighbors) rather than text boxes.
  - Draw embedded representations and feature paths as layered 3D matrices/tensors to evoke standard Deep Learning visualization vernacular.
  - Integrate concise Math/LaTeX formulations directly onto algorithmic blocks (e.g., $h_v^{(l+1)} = \operatorname{FFN}(\dots)$, $\otimes$, $\oplus$).
- Prefer a rigorous spatial grouping that makes input domains, encoding layers, and fusion projections distinct and strictly non-overlapping.
- First guarantee absolute faithfulness to the real source code, then stylize the resulting graphical density and color palettes (using sophisticated hues) to match top CV/NLP/Graph conferences.

## Validation And Reference Review

Two validation passes are mandatory.

- First pass: catch overflow, overlap, dangling arrows, invalid bounds, color inconsistency, unreadable legend usage, and obvious layout drift.
- Reference-review pass: inspect strong external examples when the task is paper-facing, architecture-heavy, or model-heavy.
- Second pass: confirm that the refined version is still faithful and did not introduce new layout or semantic errors.

Use the validation scripts on `figure_layout.json` when the renderer-first path is used. For native Python neural figures, the validation surface is the render script plus the checklist-driven manual pass; do not force the figure back into JSON just to satisfy the renderer.

## Render Scaffold

Use `scripts/render_figure_from_layout.py` when the task needs a reproducible first-pass figure from a validated layout spec.

- The renderer accepts `figure_layout.json` and exports `PNG + PDF` by default.
- Add `--formats png,pdf,svg` only when the user explicitly wants `SVG`.
- The renderer also writes validation reports unless `--skip-validation` is used.
- Use `--strict` when the draft must fail fast on layout or label errors instead of exporting anyway.
- Reuse [assets/example-figure-layout.json](assets/example-figure-layout.json) as a smoke-test fixture or a starting schema example when helpful.

For dense neural/model figures that need code-faithful topologies, tensor blocks, or equation-rich panels, start from `scripts/render_neural_model_v7_template.py`.

- Keep the four-stage narrative only if it matches the real model; rename, remove, or add panels based on the source code.
- Preserve the helper primitives such as `draw_section_bg`, `draw_flow_arrow`, and `draw_tensor` so the layout stays visually consistent while semantics change.
- Move the adapted native script into the active workspace when the task becomes task-specific or needs local assets.

## Output Contract

- Default export: `PNG + PDF`
- Add `SVG` only if the user explicitly asks for it.
- If the user does not specify an output path, default to `outputs/figures/<task-name>/` inside the active workspace.
- Unless the user narrows the request, aim for figures that are ready for papers, theses, midterm reviews, and slides.
