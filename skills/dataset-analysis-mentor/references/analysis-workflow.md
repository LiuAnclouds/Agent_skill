# Analysis Workflow

## Goal

Turn a dataset or an existing artifact directory into:

- a deep main report
- a per-artifact explanation file

Do not stop at one-pass EDA if important risks remain unexplained.

## Full Order

1. Ground in reality
2. Build a global summary
3. Expand along relevant dimensions
4. Interpret artifacts one by one
5. Recover modeling implications
6. Close with risks and next steps

## 1. Ground In Reality

Read before asking:

- dataset files or manifests
- train/val/test split logic
- label semantics
- existing scripts or notebooks
- existing output artifacts

Confirm:

- shape and schema
- label space
- whether the task is classification, anomaly detection, link prediction, ranking, or regression
- whether there is time, graph structure, groups, or hierarchy

## 2. Build A Global Summary

Always start with:

- sample count
- feature count
- label distribution
- split sizes
- obvious missing-value encodings
- time span if present
- graph size if present

Stop and correct assumptions early if the dataset structure contradicts the prompt.

## 3. Expand Along Relevant Dimensions

Pick dimensions from [analysis-dimensions.md](analysis-dimensions.md).

Minimum expectation:

- structured data: feature distribution, missingness, imbalance, drift, correlation
- graph data: degree, edge type, relation pattern, bridge nodes, directionality
- temporal data: activity curve, time windows, drift, leakage risk
- anomaly or anti-fraud: rarity, concentration, lifecycle, context dependence

## 4. Interpret Artifacts One By One

For every important artifact, answer:

1. What is this artifact measuring?
2. How should it be read?
3. What concrete phenomenon is visible?
4. What does that imply for modeling or validation?
5. What could be misleading or still missing?

Use the fixed five-block contract from [artifact-explanation-contract.md](artifact-explanation-contract.md).

## 5. Recover Modeling Implications

Translate observations into decisions:

- feature treatment
- missing-value encoding
- class imbalance handling
- graph context retention
- time-aware split choice
- drift-aware evaluation

Prefer actionable recommendations over generic statements.

## 6. Stop Conditions

The analysis is not complete until:

- the main report exists
- the per-artifact explanation file exists
- major risks have explicit explanations
- the next modeling step is informed by the analysis

Keep drilling if any of these remain unclear:

- strong class imbalance
- very high missingness
- long-tail behavior
- large train-test or phase drift
- graph background nodes that dominate connectivity
- time-window effects that can invalidate random splitting
