# Artifact Explanation Contract

## Purpose

Every important output file or chart must have a readable explanation. Do not leave the user with raw figures.

## Required Blocks

For each artifact, write exactly these blocks in order:

### 1. 作用

State what the artifact measures and why it exists.

### 2. 怎么看

Explain axes, groups, colors, table fields, and the correct reading order.

### 3. 本项目中的实际现象

State the concrete pattern visible in this dataset. Use numbers when available.

### 4. 建模/实验启发

Translate the observation into a modeling or evaluation decision.

### 5. 风险与补充检查

State what this artifact does not prove, what could be misleading, and what follow-up analysis is still needed.

## Writing Rules

- Prefer concrete statements over generic phrases.
- Mention the actual artifact filename.
- Mention the exact statistic or pattern that matters.
- Separate observation from inference.
- Do not write empty formalities such as “this is useful for analysis.”

## Good Pattern

Observation:

- `x6` has a much higher `-1` ratio in fraud than in normal samples.

Model implication:

- keep the raw value and add a missing-indicator feature

Risk:

- verify whether the effect stays stable across time windows

## Bad Pattern

- “The chart shows a difference.”
- “This may help modeling.”
- “Need more analysis.” without naming the missing analysis
