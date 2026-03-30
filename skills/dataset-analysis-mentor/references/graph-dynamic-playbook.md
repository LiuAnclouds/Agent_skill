# Graph Dynamic Playbook

## Use This File

Read this file for graph data, dynamic graphs, anomaly detection, anti-fraud, or any task where unlabeled or background nodes may still carry context.

## Priority Order

1. label imbalance
2. graph connectivity
3. directionality
4. background-node bridge effects
5. temporal behavior
6. drift across windows or phases

## Graph Checks

Always check:

- node count and edge count
- directed vs undirected semantics
- edge type count and imbalance
- indegree, outdegree, total degree
- edge endpoint group patterns
- how much of the graph flows through background or unlabeled nodes

## Dynamic Checks

Always check:

- activity by day or time window
- edge-type activity over time
- first active time
- last active time
- active span
- whether anomalous nodes are late, short-lived, or bursty

## Anti-Fraud And Anomaly Questions

Ask:

- are suspicious nodes lower-degree or higher-degree than normal nodes?
- are they more passive or more active?
- do they appear briefly and disappear?
- do they rely on background nodes for connectivity?
- do feature-missing patterns correlate with suspicious labels?
- do signals survive across time windows or phases?

## Background Node Rule

Do not delete background nodes by default.

Keep them if:

- a large fraction of edges touches them
- a large fraction of labeled target nodes connects to them
- they preserve realistic connectivity

If considering removal, first quantify the damage to:

- edge coverage
- labeled-node neighborhood coverage
- graph component structure

## Validation Rule

If the graph is temporal or multi-phase, prefer time-aware validation over random splitting.

Explain the split using observed drift, not intuition alone.
