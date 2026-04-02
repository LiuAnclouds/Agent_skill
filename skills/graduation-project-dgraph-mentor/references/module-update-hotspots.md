# Module Update Hotspots

Use this file when you already know the type of change you want to make but do not yet know which files to edit.

## If You Want To Add A New Dataset

- `experiment/eda/data_loader.py`: add filename resolution and validation logic.
- `experiment/eda/analysis.py`: make sure EDA and split logic still work on the new dataset.
- `references/dataset-profile.md`: the sync script will refresh counts once the loader can see the new data.

## If You Want To Add Or Change Features

- `experiment/training/features.py`: add feature construction, manifest spans, and any cache writes.
- `experiment/training/run_training.py`: expose the new feature usage if a model family or CLI flag needs to select it.
- Any probe script under `experiment/training/run_xgb_*.py` that should consume the new feature recipe.

## If You Want To Change The GNN Backbone

- `experiment/training/gnn_models.py`: message passing blocks, loss logic, batch construction, logging, and inference live here.
- `experiment/training/run_training.py`: model choices and CLI exposure live here.
- `experiment/training/README_gnn_models.md`: existing hand-written explanation may need updating if you want the manual docs to stay aligned.

## If You Want To Change Evaluation Or Metrics

- `experiment/training/common.py`: shared metric definitions.
- `experiment/training/run_training.py`: which metrics are surfaced into summaries.
- `experiment/training/gnn_models.py`: per-epoch logging and curve generation.

## If You Want Faster Iteration On New Ideas

- Prefer `run_xgb_graphprop.py`, `run_xgb_relmean.py`, and `run_xgb_covshift.py` before launching a very long GNN run.
