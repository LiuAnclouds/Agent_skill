# Module Guide: `experiment/eda/data_loader.py`

## Purpose

Resolve the XinYe dataset paths, flatten arrays, validate schema assumptions, and load one phase into a typed PhaseData container.

## When To Read This File

Read this file first when dataset paths change or when the repository needs to support more datasets.

## Upstream Callers / Entrypoints


## Downstream Consumers / Artifacts

- experiment/eda/analysis.py
- experiment/training/features.py
- experiment/training/common.py

## Main Outputs Or Side Effects

- Validated PhaseData objects in memory

## Common Edit Hotspots

- Add new dataset filename conventions here.
- Relax or extend schema validation here if later datasets differ from XinYe DGraph.

## Top-Level Symbols

### `PhaseData`

- Kind: `class`
- Lines: `24-41`
- Role: Immutable in-memory bundle for one dataset phase, including node features, labels, edges, timestamps, and official train/test node ids.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `num_nodes(self) -> int` lines `36-37`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `num_edges(self) -> int` lines `40-41`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.

### `resolve_dataset_path(phase: str, repo_root: Path | None = None) -> Path`

- Kind: `function`
- Lines: `44-61`
- Role: Find the canonical npz file for a named phase under the current dataset layout.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_flatten_array(values: np.ndarray, dtype: np.dtype | None = None) -> np.ndarray`

- Kind: `function`
- Lines: `64-68`
- Role: Flatten label or mask arrays to one dimension and optionally cast dtype.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_validate_phase_data(data: PhaseData) -> None`

- Kind: `function`
- Lines: `71-100`
- Role: Assert that the loaded phase matches the expected DGraph schema and label assumptions.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `load_phase(phase: str, repo_root: Path | None = None) -> PhaseData`

- Kind: `function`
- Lines: `103-119`
- Role: Load one dataset phase from disk and return a validated PhaseData object.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

