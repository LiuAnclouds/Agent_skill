# Data Figure Playbook

## Goal

Make the chart carry one clear claim. A good data figure lets the reader see the intended contrast in seconds.

## Pick The Figure By Claim

- Distribution shift:
  - histogram with aligned bins
  - ECDF
  - violin/boxplot for compact comparison
- Class imbalance:
  - stacked bars
  - percentage bars
- Time drift:
  - line plot with moving average
  - multi-panel phase comparison
- Ranking or contribution:
  - sorted horizontal bars
- Correlation or interaction:
  - heatmap
- Ablation or experiment table-to-figure:
  - grouped bars
  - dot plot
  - slope chart
- Training stability:
  - line plot with smoothing and milestone annotation

## Contrast-First Rules

- Prefer fewer series with stronger annotation over many weak series.
- Sort categories when ranking matters.
- Mark thresholds, best values, large deltas, or phase boundaries when they support the claim.
- If a chart needs a paragraph to explain the basic difference, redesign the chart.

## Title And Annotation

- Prefer titles that communicate the main finding when the figure is paper-facing.
- Annotate the most important points directly on the figure when possible.
- Keep annotations short and attached to the correct local feature.

## Color Rules

- Use color to encode comparison groups, not decoration.
- Keep baseline/comparison colors stable across a figure set.
- Avoid gradients unless the data is continuous and the scale matters.
- If there are more than 6 categories, reconsider the figure design before adding more colors.

## Common Failure Modes

- mixing unrelated metrics on one axis
- unsorted bars hiding the real ranking
- equal visual weight for primary and secondary signals
- legends far away from the actual traces
- archive-style figures with too many panels for the intended conclusion
