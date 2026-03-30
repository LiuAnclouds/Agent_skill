# DGraph Case Study

## Purpose

Use this file as a concrete example of how the skill should reason in a real graph anti-fraud project.

## Reference Project

Current reference implementation path:

- `F:/Codes/毕设/动态图异常检测/experiment/eda/analysis.py`
- `F:/Codes/毕设/动态图异常检测/experiment/eda/data_loader.py`
- `F:/Codes/毕设/动态图异常检测/experiment/eda/run_eda.py`

Current reference outputs:

- `F:/Codes/毕设/动态图异常检测/experiment/outputs/eda/`

## What This Example Demonstrates

- high class imbalance
- heavy sentinel-value usage such as `-1`
- graph background nodes that dominate connectivity
- directionality differences between fraud and normal nodes
- dynamic-graph behavior and phase drift
- the need for both a main report and per-artifact explanations

## How To Reuse The Example

Do not copy project-specific logic into a new task blindly.

Reuse the reasoning pattern:

1. identify task type and split semantics
2. quantify missingness and class imbalance
3. quantify graph directionality and bridge effects
4. quantify temporal behavior and drift
5. explain each artifact in modeling terms

## Mapping Example

Example artifact-to-meaning mappings from the DGraph project:

- `feature_neg1_ratio.png`: sentinel-value concentration
- `feature_top_gap_hist.png`: single-feature separability
- `degree_direction.png`: indegree vs outdegree asymmetry
- `graph_structure.png`: total-degree contrast and endpoint-pair structure
- `temporal_patterns.png`: edge activity and lifecycle behavior
- `feature_drift.csv`: cross-phase feature drift

Use these as examples of explanation style, not as a fixed list for all projects.
