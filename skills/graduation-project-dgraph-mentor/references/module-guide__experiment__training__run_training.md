# Module Guide: `experiment/training/run_training.py`

## Purpose

Unified CLI for build_features, LightGBM / GNN training, and prediction blending.

## When To Read This File

Read this file when the user-facing training CLI changes, when a new model family is added to the main benchmark path, or when summary outputs need to change consistently.

## Upstream Callers / Entrypoints

- shell / terminal

## Downstream Consumers / Artifacts

- experiment/training/features.py
- experiment/training/gbdt_models.py
- experiment/training/gnn_models.py
- experiment/outputs/training/models/

## Main Outputs Or Side Effects

- Unified build/train/blend command surface and summary.json files

## Common Edit Hotspots

- Add CLI flags here for new model families or new training options.
- Keep summary structure stable if downstream comparison scripts depend on it.

## Top-Level Symbols

### `_path_repr(path: Path) -> str`

- Kind: `function`
- Lines: `54-58`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `61-405`
- Role: Parse the unified CLI for feature building, tabular/GNN training, and blending.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_model_run_dir(outdir: Path, model_name: str, run_name: str) -> Path`

- Kind: `function`
- Lines: `408-409`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_load_labels_for_splits(split) -> tuple[np.ndarray, np.ndarray]`

- Kind: `function`
- Lines: `412-418`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_prepare_split_ids(args: argparse.Namespace)`

- Kind: `function`
- Lines: `421-426`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_graph_model_config(args: argparse.Namespace) -> GraphModelConfig`

- Kind: `function`
- Lines: `429-466`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_save_average_predictions(run_dir: Path, split_name: str, node_ids: np.ndarray, labels: np.ndarray, predictions: list[np.ndarray]) -> Path`

- Kind: `function`
- Lines: `469-479`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `_benchmark_summary_path(outdir: Path, run_name: str) -> Path`

- Kind: `function`
- Lines: `482-483`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_promotion_decision(model_name: str, run_name: str, outdir: Path, summary_payload: dict[str, Any]) -> dict[str, Any]`

- Kind: `function`
- Lines: `486-519`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `run_build_features(args: argparse.Namespace) -> None`

- Kind: `function`
- Lines: `522-530`
- Role: Launch the offline feature and graph-cache build.
- How to use: This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically.
- Side effects / outputs: Typically triggers most of the file's intended side effects, including artifact writes or model execution.

### `run_train_lightgbm(args: argparse.Namespace) -> None`

- Kind: `function`
- Lines: `533-663`
- Role: Train tabular baselines on the recommended split and write per-seed plus averaged predictions.
- How to use: This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically.
- Side effects / outputs: Typically triggers most of the file's intended side effects, including artifact writes or model execution.

### `_make_graph_contexts(feature_dir: Path, model_name: str, extra_groups: list[str] | None = None, feature_normalizer_state = None, phase1_known_label_codes: np.ndarray | None = None, phase2_known_label_codes: np.ndarray | None = None) -> tuple[GraphPhaseContext, GraphPhaseContext]`

- Kind: `function`
- Lines: `666-694`
- Role: Open feature stores, graph caches, and labels for both phases.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `run_train_graph(args: argparse.Namespace) -> None`

- Kind: `function`
- Lines: `697-904`
- Role: Train GNN models, evaluate on phase1 val and phase2 external, and write logs / curves / summaries.
- How to use: This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically.
- Side effects / outputs: Typically triggers most of the file's intended side effects, including artifact writes or model execution.

### `_load_prediction_bundle(path: Path) -> dict[str, np.ndarray]`

- Kind: `function`
- Lines: `907-913`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_logit(probability: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `916-918`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_resolve_prediction_path(model_run_dir: Path, split_name: str) -> Path`

- Kind: `function`
- Lines: `921-932`
- Role: Inference helper that converts a fitted model into fraud probabilities or scores.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `run_blend(args: argparse.Namespace) -> None`

- Kind: `function`
- Lines: `935-1020`
- Role: Blend multiple saved model runs through logistic stacking on validation logits.
- How to use: This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically.
- Side effects / outputs: Typically triggers most of the file's intended side effects, including artifact writes or model execution.

### `main() -> None`

- Kind: `function`
- Lines: `1023-1037`
- Role: Top-level dispatcher for the unified training CLI.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

