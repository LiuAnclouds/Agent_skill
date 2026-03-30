# Analysis Dimensions

## Use This File

Choose the dimensions that match the dataset. Do not force all of them on every task, but do not skip a relevant dimension because the first summary looked “good enough.”

## A. Base Structured-Data Dimensions

Check:

- schema and dtype
- categorical vs numeric role
- label distribution
- train/val/test split semantics
- missing-value encoding
- feature ranges and units
- outliers
- correlation and redundancy

Useful outputs:

- summary table
- per-feature quantiles
- histograms or CDFs
- correlation heatmap
- missingness table

## B. Missingness And Sentinel Values

Check:

- is missingness encoded as `NaN`, `-1`, `0`, or a special token?
- is missingness uniform across classes?
- does missingness change over time or between phases?
- do missing patterns appear in combinations?

Important interpretations:

- a missing marker can be a real predictive signal
- a large missingness shift can indicate distribution drift
- sentinel-heavy columns should not be blindly standardized without care

## C. Imbalance And Rare-Event Structure

Check:

- positive rate
- negative-positive ratio
- how positives distribute over time, groups, or graph neighborhoods
- whether positives are isolated or concentrated

Useful outputs:

- class distribution table
- positive-rate-by-window chart
- subgroup rarity analysis

## D. Long-Tail And Extreme Values

Check:

- whether a few samples dominate the upper tail
- whether means are much less stable than medians
- whether p95/p99 diverge sharply from the median

Useful outputs:

- CDF
- boxplot without fliers
- quantile table
- log-scale histogram when appropriate

## E. Correlation And Redundancy

Check:

- strongly correlated numeric columns
- repeated statistics in slightly different forms
- whether top “important” columns are near-duplicates

Useful outputs:

- correlation heatmap
- sorted top-correlation pairs

## F. Temporal Dimensions

Check:

- activity volume by day or window
- feature drift by time window
- whether validation should be chronological
- whether labels themselves shift over time

Useful outputs:

- activity curve
- windowed feature summaries
- time-based drift table

## G. Distribution Drift

Check:

- train vs validation drift
- phase1 vs phase2 drift
- missingness change and not just mean change
- whether drift appears in structure, time, or label context

Useful outputs:

- PSI table
- quantile shift table
- edge-type ratio comparison
- time-window comparison

## H. Graph-Structure Dimensions

Check:

- node and edge counts
- degree distribution
- indegree/outdegree asymmetry
- edge types
- relation patterns between node groups
- bridge roles and context nodes

Useful outputs:

- degree histograms
- indegree vs outdegree comparison
- endpoint-pair heatmap
- edge-type frequency table

## I. Dynamic-Graph Dimensions

Check:

- edge volume over time
- edge-type activation over time
- first active time
- last active time
- active span
- whether anomalous nodes are short-lived or late-appearing

Useful outputs:

- daily edge curve
- edge-type time heatmap
- first-active CDF
- active-span comparison

## J. Anomaly Detection And Anti-Fraud Dimensions

Check:

- rarity and skew
- whether anomalies are low-degree, high-degree, short-lived, or context-dependent
- whether anomaly signals live in node features, local structure, or temporal behavior
- whether background or unlabeled nodes carry essential context

Useful outputs:

- positive-vs-normal feature comparisons
- degree and directionality comparisons
- neighbor-context analysis
- lifecycle comparison

## Priority Rule

If the task is graph, dynamic graph, anomaly detection, or anti-fraud, prioritize:

1. imbalance
2. missingness
3. graph structure
4. temporal behavior
5. drift

Do not treat these as optional decorations.
