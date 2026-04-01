# Optimization Goals

## Main Goal

- Primary internal target: push phase1_val_auc to at least 0.82 without any data leakage.
- Keep phase2_external_auc as the robustness check; improving val while collapsing external generalization is not acceptable.
- Use GPU in the Graph conda environment for heavy experiments. The user explicitly requested GPU rather than CPU training.
- Current evidence suggests the hard temporal split is the main bottleneck: phase1 train nodes are much earlier than phase1 val nodes, so distribution shift is severe.

Current best recorded validation AUC is `0.789248` from `experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json`; external AUC is `0.790223`.

## Open Optimization Directions

- Improve time-aware sampling or time-conditioned feature engineering without leaking future information.
- Strengthen relation-aware modeling instead of global averaging. The current simple relation-mean probe was too weak, but more selective relation features remain open.
- Keep exploring GPU tabular models and graph-tabular hybrids because they are faster to iterate than long GNN runs.
- Revisit backbone updates such as stronger temporal GAT / Transformer-style modules once a faster feature or sampling baseline is stable.
- Consider calibrated ensembling or stacking only after a clearly stronger single-run validation model appears.
- Prepare the data-loading layer for future additional datasets; the current repository still assumes only the XinYe DGraph phase1/phase2 layout.

## Current Bottleneck Interpretation

- The project is not obviously failing to fit. Instead, it quickly saturates under a severe time-shifted validation regime.
- Simple extra tabular features and naive graph propagation improved little; relation-specific averaging and covariate-shift weighting were not enough in their current forms.
- This means future work should focus on stronger temporal / relation inductive bias, better sampling, or cleaner graph-tabular hybridization rather than only longer training.
