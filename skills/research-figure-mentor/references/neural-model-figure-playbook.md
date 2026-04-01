# Neural Model Figure Playbook

## Goal

Draw the model that actually exists in code or method description, then improve readability until it looks publication-grade.

## Mandatory Read-First Steps

Before drawing, reconstruct the real model path:

1. Find the model entrypoint and main class.
2. Trace the forward path.
3. Identify every input branch.
4. Identify repeated blocks and stack depth.
5. Identify residual, normalization, dropout, FFN, pooling, fusion, JK/skip, and output heads.
6. Distinguish fixed structure from configuration switches.

Do not infer structure from class names alone.

## Visual Decomposition

Prefer these sections in order:

- inputs
- preprocessing or projection
- backbone or block stack
- branch-specific processing
- pooling or aggregation
- fusion
- prediction head

For graph models, also make explicit:

- node path
- edge path
- subgraph/global context path
- fusion points

## Simplification Rules

- Collapse repeated identical blocks into `×L` or `×N` notation only after confirming repetition is faithful.
- Do not collapse branches that differ semantically.
- Do not remove a branch or skip path that changes the interpretation of the model.

## Style Rules

- Use one stable color family per functional role:
  - inputs
  - encoders
  - pooling/fusion
  - outputs
- Put fusion points where branch convergence is visually obvious.
- Keep arrows mostly monotonic left-to-right or top-to-bottom.
- Keep labels short and local; move formulas or long notes into side notes.

## Native Python V7 Template Path

Use the native v7-style path when the figure needs more than a clean box-arrow schematic:

- graph topology insets
- 3D tensor or memory blocks
- math formulas embedded directly in the blocks
- multiple semantically distinct panels with cross-panel connectors

Start from [native-neural-v7-template.md](native-neural-v7-template.md) and `../scripts/render_neural_model_v7_template.py`.

Map the real model into the v7 panel story only if it is faithful:

- panel A: context, sampling, or graph construction
- panel B: feature access, projection, or embedding
- panel C: the core encoder/message-passing block
- panel D: fusion, pooling, readout, and prediction

If the real model differs, change the panel meaning rather than forcing a fake match.

## Dynamic Graph And Anomaly Figure Lessons

When the figure is about dynamic graph anomaly detection, relation graphs, or subgraph reasoning, load [dynamic-graph-anomaly-figure-patterns.md](dynamic-graph-anomaly-figure-patterns.md) and follow these rules:

- Do not use decorative mini-graphs that have no algorithmic role.
- Reuse one main local subgraph across multiple panels when the story is edge encoding -> message gating -> anomaly inference.
- In the embedding panel, connect relation/time/tensor blocks back to a graph view with short callouts so the reader sees that edge attributes are attached to real edges, not abstract boxes.
- In the core block panel, show candidate edges versus retained edges after gating or attention; a before/after inset is often clearer than extra formulas alone.
- In the readout panel, show how node representation, edge evidence, and subgraph statistics jointly support the anomaly score; avoid ending with a tiny decorative star graph.
- If graphs become too cramped, increase the canvas or reallocate panel widths before shrinking the graph semantics away.
- Keep node-role colors and anchor positions stable across panels whenever the figure claims a continuous subgraph evolution.

## Fidelity Rules

- If code and paper disagree, prefer code when the user asks for a code-based figure.
- If the model has optional configuration branches, state whether the figure shows:
  - the active configuration
  - the configurable superset
- Do not make a paper-pretty figure that lies about the real model.
