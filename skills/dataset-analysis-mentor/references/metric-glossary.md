# Metric Glossary

## CDF

CDF means cumulative distribution function.

Read it as:

- x-axis: feature value
- y-axis: proportion of samples with value less than or equal to x

Use it to explain:

- threshold behavior
- median shifts
- whether one class stays systematically left or right of another
- whether differences happen near sentinel values such as `-1`

## Long-Tail

Long-tail means:

- most samples stay in a low range
- a small fraction extends to very large values

Explain it with:

- median vs p95 or p99
- CDF
- boxplot
- log-scale histogram if needed

## Long-Tail Effect

Long-tail effect means a few extreme samples can strongly affect:

- the mean
- scaling
- model fit
- visual interpretation

If the tail is important, do not rely on mean alone.

## PSI

PSI means Population Stability Index.

Use it to describe distribution drift between two groups or two time periods.

Interpret cautiously:

- near 0: low drift
- around 0.1: meaningful drift worth attention
- larger values: stronger drift

Always pair PSI with:

- missingness shift
- median shift
- mean shift

## Quantiles

Quantiles summarize position in the distribution.

Important ones:

- median or q50: typical center
- q75: upper-middle range
- p95 or q95: heavy-tail start
- p99: extreme tail

## Indegree

Number of incoming edges for a node.

Use it to describe how much a node is pointed to or contacted by others.

## Outdegree

Number of outgoing edges for a node.

Use it to describe how much a node actively points to or contacts others.

## Total Degree

`indegree + outdegree`

Use it as the overall connectivity level, but do not confuse it with directionality.

## Density In Histograms

When a chart says density, it usually means normalized frequency, not graph density.

Use that explanation when comparing classes with very different sample counts.

## First Active Time

Earliest time at which a node appears in any edge.

Use it to discuss arrival timing.

## Last Active Time

Latest time at which a node appears in any edge.

Use it to discuss persistence or late activity.

## Active Span

`last_active - first_active`

Use it to describe the lifecycle length of a node.

If anomalies have a very small active span, say they are short-lived or bursty rather than only saying “they are different.”
