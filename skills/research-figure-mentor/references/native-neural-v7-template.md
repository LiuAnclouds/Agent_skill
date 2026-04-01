# Native Neural V7 Template

## Goal

Use the `dev_model_v7.py` drawing style as the default native Python template for publication-grade neural and graph model figures.

This path is for figures that are too semantically rich for a plain `figure_layout.json` box-arrow render.

## When To Use It

Choose the v7 template when the figure needs any of the following:

- explicit graph topology or ego-graph insets
- dense multi-panel storytelling across the full model pipeline
- 3D tensor or memory blocks instead of flat rectangles
- short math formulas embedded directly into blocks
- cross-panel residual, skip, or fusion cues that need figure-level routing

## Canonical V7 Panel Story

The v7 template uses four horizontally aligned panels with figure-level arrows between them:

1. context or sampling
2. feature access or embedding
3. the core encoder / message-passing block
4. fusion, readout, and prediction

Only keep this exact story if it matches the real model. Otherwise:

- rename panels
- drop absent branches
- add missing stages
- mark repeated layers as `xL` only when the repetition is real

## Helper Primitives To Preserve

Keep these helper primitives so every adapted figure still feels structurally coherent:

- `draw_section_bg(ax, title, color)`
- `draw_flow_arrow(fig, x_start, x_end, y)`
- `draw_tensor(ax, x, y, width, height, color, label, depth, ...)`

The point is not to preserve the original labels. The point is to preserve the visual grammar:

- section backgrounds define semantic stages
- figure-level arrows define the global reading order
- tensor blocks distinguish raw features, learned embeddings, and fused representations

## Panel-Level Mapping Rules

### Panel A: Context / Sampling

Use `NetworkX` inset plots for:

- dynamic graph context
- ego-graph extraction
- temporal neighborhood sampling
- attention neighborhood snapshots

Prefer real node-edge motifs over text-only boxes.

### Panel B: Feature Access / Embedding

Use 3D tensor blocks and short operator labels for:

- raw node or edge features
- feature store / cache / memory bank
- linear projection, embedding, time encoding, or modality encoding
- concatenation or additive fusion before the backbone

### Panel C: Core Block

Reserve the largest panel for the actual computation:

- message functions
- gates or attention weights
- aggregation
- residuals
- normalization
- FFN or update rules

Put the most model-specific formula directly on this panel.

### Panel D: Fusion / Readout

End with the model outputs:

- JK or multi-layer fusion
- pooling
- graph or subgraph statistics
- classification / regression head
- final score or logits

## Layout Constraints From V7

- Build the canvas with explicit `fig.add_axes(...)` panel coordinates.
- Keep cross-panel arrows in figure coordinates, not local axis coordinates.
- Use one stable semantic palette for node, edge, time, fusion, and output families.
- Leave visible whitespace between the super-title, panel headers, inset plots, and formulas.
- Keep labels short enough to fit inside their blocks after export at paper scale.

## Experience Sync: Dynamic Graph Anomaly Figures

This template was validated on a dynamic graph anomaly architecture figure where the first version was technically correct but visually weak because the graph motifs in panels B/C/D were too sparse and decorative.

Carry forward these concrete lessons:

- Graphs in panels B/C/D must explain the algorithm, not merely decorate it.
- Panel B works better when it shows the same sampled local subgraph twice: once as the raw typed-temporal structure and once as the edge-aware encoded structure.
- Panel C works better when the main subgraph keeps the same node anchors as panel B, while a small inset contrasts candidate edges versus retained edges after gating.
- Panel D should end with an anomaly-evidence subgraph, not a tiny generic network icon; use bridge nodes, heterogeneous edge colors, and evidence concentration around the target node.
- Keep the visual family stable by preserving the original panel backgrounds, tensor boxes, and reading order even when the canvas and panel widths are adjusted.
- Prefer fixed manual anchors for the recurring subgraph so repeated renders do not drift.
- When adding graph detail, free space by widening the figure or redistributing panel widths instead of compressing labels or graph topology.

- Panel B improves when the operator chain is visually hierarchical: relation branch and time branch first, one small concat operator second, one unambiguous `edge_emb` tensor third.
- If `edge_emb` is consumed both by Panel C and by a Panel B encoded-subgraph inset, keep the arrow to the next panel as the primary continuation and the inset arrow as a smaller semantic side-route.
- Avoid turning Panel B into a local flowchart. Prefer one main downward/forward pipeline plus at most one auxiliary curved arrow into the encoded subgraph card.
- In Panel C, the `before/after gating` inset should live in the whitespace between message and gate blocks. If it touches branch arrows, the residual frame, or the central operator, shift it slightly left/down and reduce it before compressing labels.
- When a review says a panel feels "乱" or arrows feel "乱指", treat that as a layout bug, not a styling preference. Remove ambiguous arrow fans first, then re-add only the arrows that explain a unique computation step.

## Template Entry Point

Start from `../scripts/render_neural_model_v7_template.py`.

Adaptation order:

1. change the title and output path
2. rename panel titles to match the real pipeline
3. replace placeholder topology insets with task-faithful ones
4. replace tensor labels and formulas with the real operators from code
5. render, inspect, and refine

Do not keep any placeholder branch that does not exist in the real model.

