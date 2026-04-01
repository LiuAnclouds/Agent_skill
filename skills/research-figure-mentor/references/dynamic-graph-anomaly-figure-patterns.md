# Dynamic Graph Anomaly Figure Patterns

## Goal

Make dynamic graph anomaly figures readable as an algorithmic story, not just as a collection of tensor boxes with decorative node-edge snippets.

This reference is for model figures where node roles, edge types, temporal context, local subgraphs, and anomaly evidence all matter.

## Core Principle

If the model reasons over a local subgraph, the figure should also reason over a local subgraph.

That usually means one recurring subgraph should appear across multiple panels and visibly evolve as the computation progresses.

## Recommended Multi-Panel Story

Use this when the real code path supports it:

1. sampled subgraph or temporal neighborhood
2. edge-aware encoding on the same subgraph
3. gated or attention-weighted message passing on the same subgraph
4. anomaly evidence concentration and final readout on the same subgraph

The repeated graph should not be pixel-identical every time. It should preserve node roles and rough anchors while changing edge appearance or node styling to reflect the algorithmic stage.

## Panel-Specific Patterns

### Embedding Panel

- Keep the tensor blocks for node projection, relation embedding, time encoding, and edge fusion.
- Add one large graph area instead of several tiny disconnected graph icons.
- Show at least one raw subgraph view and one encoded-edge view if space allows.
- Use short callouts from `Relation Emb`, `Time MLP`, or `E_emb` into the graph view.

- Keep one dominant `edge_emb` story in Panel B: `relation embedding + time encoding -> concat -> edge embedding` should read as a single pipeline before any auxiliary graph annotations.
- If the encoded subgraph in Panel B reuses `edge_emb`, show that as one secondary arrow only; do not fan multiple arrows out of the same operator unless each arrow has a clearly distinct semantic purpose.
- Keep the `Concat` operator away from tensor faces and branch arrows. If it starts covering the edge embedding tensor or the time branch path, move it upward or sideways before shrinking labels.
- Bottom raw/encoded subgraph cards in Panel B should remain calmer than the operator stack above them: enlarge the cards and legend area before adding extra explanatory labels between them.

### Core Message-Passing Panel

- Keep the model-specific formulas and update blocks.
- Put the main graph near the message/gate equations, not far away as decoration.
- Use edge width, saturation, or glow to represent gate strength or attention weight.
- A small before/after inset is useful when the difference between candidate edges and retained edges is semantically important.

### Readout Panel

- Do not end with a tiny generic star graph unless the real model truly operates like that.
- Show the final anomaly target together with supporting or risky neighbors.
- Use heterogeneous edge colors for relation families and stronger edges where evidence is concentrated.
- Make it visually obvious that the score comes from node representation, edge evidence, and subgraph statistics together.

## Visual Semantics

- Node color should encode role, not decoration.
  - target node
  - core neighbors
  - context neighbors
  - bridge or risky nodes
  - anomaly target or highlighted result node
- Edge color should encode relation family or direction.
- Edge width, opacity, or secondary overlay can encode recency, gate strength, or contribution strength.
- If one panel shows encoded nodes instead of raw nodes, add a subtle visual upgrade such as an outer ring or embedded core to distinguish the stage.

## Layout Rules

- If graph semantics are the main missing element, widen the canvas or reallocate panel widths before reducing graph detail.
- Preserve the overall visual family even when the canvas changes:
  - same background colors
  - same title system
  - same tensor style
  - same reading order
- Keep recurring subgraph node anchors fixed manually whenever panel-to-panel continuity matters.
- Leave explicit whitespace zones for callouts and formulas so graph edges do not run through text.

## Failure Modes To Avoid

- decorative graph snippets with no clear computational meaning
- unrelated graph topology in each panel when the figure is supposed to tell one continuous local-subgraph story
- inconsistent node-color semantics across panels
- a dense graph that hides the model math instead of clarifying it
- a final anomaly panel that marks a red node without showing what evidence made it anomalous

