---
name: dataset-analysis-mentor
description: 深度数据分析与结果讲解工作流。Use when Codex needs to do careful exploratory data analysis, uncover hidden statistics or distributions, interpret charts/tables/metrics, or produce a dataset analysis report with per-artifact explanations. Especially useful for structured data, graph data, dynamic graphs, anomaly detection, anti-fraud, time drift, missingness, long-tail behavior, and requests like “详细分析数据”, “做 EDA”, “解释这些图表”, “分析分布/漂移/缺失”, or “输出数据分析报告”.
---

# Dataset Analysis Mentor

## Overview

Deliver deep data analysis instead of shallow summary. Produce artifacts and explanations together. Reuse existing project analysis code when possible; fill the gaps with new analysis only where the current outputs are insufficient.

## Core Workflow

1. Read the dataset description, existing analysis outputs, and repository structure before proposing more work.
2. Build a data-grounded overview: size, schema, split logic, labels, class imbalance, missingness, time span, and obvious anomalies.
3. Expand the analysis along the relevant dimensions from [references/analysis-dimensions.md](references/analysis-dimensions.md).
4. For graph, temporal, anomaly-detection, or anti-fraud tasks, load [references/graph-dynamic-playbook.md](references/graph-dynamic-playbook.md) and prioritize structure, directionality, background nodes, temporal behavior, and drift.
5. Interpret every important chart, table, and metric using the contract in [references/artifact-explanation-contract.md](references/artifact-explanation-contract.md).
6. Write a main report and a per-artifact explanation file. Do not stop at isolated comments.
7. End with concrete modeling implications, risks, and next analysis steps.

## Output Contract

Always produce both outputs unless the user explicitly narrows the task:

- Main report: `reports/dataset-analysis-report.md`
- Per-artifact explanations: `reports/artifact-explanations.md`

If artifacts are numerous, also generate `reports/artifact-index.csv`, but never use it as a replacement for the Markdown explanations.

Use this default structure for the main report:

1. Data overview
2. Feature distributions and missingness
3. Structure or relation patterns
4. Time behavior and drift
5. Risks and modeling implications
6. Artifact reading order

## Artifact Explanation Rules

For every important artifact, explain all five items:

1. 作用
2. 怎么看
3. 本项目中的实际现象
4. 建模/实验启发
5. 风险与补充检查

Do not say only “the chart shows a difference.” State what is different, where the difference lies, whether the signal is stable, and what decision it should affect.

For terminology such as CDF, long-tail, PSI, quantiles, indegree, outdegree, total degree, and active span, use the fixed explanations in [references/metric-glossary.md](references/metric-glossary.md).

## Resource Map

- Read [references/analysis-workflow.md](references/analysis-workflow.md) for the full step order and stop conditions.
- Read [references/analysis-dimensions.md](references/analysis-dimensions.md) to choose the relevant analysis dimensions.
- Read [references/artifact-explanation-contract.md](references/artifact-explanation-contract.md) before writing artifact explanations.
- Read [references/metric-glossary.md](references/metric-glossary.md) when metrics need precise explanation.
- Read [references/graph-dynamic-playbook.md](references/graph-dynamic-playbook.md) for graph and dynamic-graph tasks.
- Read [references/case-study-dgraph.md](references/case-study-dgraph.md) for the current DGraph anti-fraud case and reference implementation mapping.
- Read [references/report-template.md](references/report-template.md) before drafting the final report.

Use the helper scripts only as scaffolding:

- `scripts/init_analysis_bundle.py`: create the default `reports/` bundle from templates.
- `scripts/build_artifact_manifest.py`: scan an artifact directory and build a manifest.
- `scripts/init_artifact_explanations.py`: turn a manifest into a Markdown explanation skeleton.

Use the templates in `assets/` as starting points, not as final deliverables.

## Quality Bar

- Prefer evidence over adjectives.
- Explain hidden behavior, not just visible charts.
- Continue digging when you see high missingness, strong imbalance, long-tail, or drift.
- Separate “what the data says” from “what you infer for modeling.”
- For graph and temporal tasks, explicitly check directionality, background-node bridge effects, time-window drift, and whether validation should be time-aware.
