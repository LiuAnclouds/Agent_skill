# Module Guides Index

Use this file as the router into the detailed module-level explanations. Each linked guide expands one `experiment/` Python file with purpose, caller path, side effects, and top-level symbol notes.

- [experiment/eda/analysis.py](module-guide__experiment__eda__analysis.md): Run the reproducible EDA stack: overview, feature profile, graph statistics, temporal behavior, drift checks, and the recommended time-aware split.
- [experiment/eda/data_loader.py](module-guide__experiment__eda__data_loader.md): Resolve the XinYe dataset paths, flatten arrays, validate schema assumptions, and load one phase into a typed PhaseData container.
- [experiment/eda/run_eda.py](module-guide__experiment__eda__run_eda.md): CLI entrypoint for the EDA pipeline.
- [experiment/training/common.py](module-guide__experiment__training__common.md): Shared training utilities for paths, metrics, split loading, seeding, prediction saving, and device resolution.
- [experiment/training/features.py](module-guide__experiment__training__features.md): Offline feature-cache and graph-cache builder plus runtime FeatureStore and GraphCache readers.
- [experiment/training/gbdt_models.py](module-guide__experiment__training__gbdt_models.md): LightGBM baseline wrapper used by the unified training CLI.
- [experiment/training/gnn_models.py](module-guide__experiment__training__gnn_models.md): Graph sampling, relation-aware message passing layers, temporal encoders, training loop, logging, hard-negative mining, and GNN inference wrappers.
- [experiment/training/run_training.py](module-guide__experiment__training__run_training.md): Unified CLI for build_features, LightGBM / GNN training, and prediction blending.
- [experiment/training/run_xgb_covshift.py](module-guide__experiment__training__run_xgb_covshift.md): GPU XGBoost exploration script for covariate-shift weighting between time-split train and val distributions.
- [experiment/training/run_xgb_graphprop.py](module-guide__experiment__training__run_xgb_graphprop.md): GPU XGBoost exploration script for propagated graph features such as A*X and A^2*X style blocks.
- [experiment/training/run_xgb_relmean.py](module-guide__experiment__training__run_xgb_relmean.md): GPU XGBoost exploration script for relation-specific neighbor mean features.
