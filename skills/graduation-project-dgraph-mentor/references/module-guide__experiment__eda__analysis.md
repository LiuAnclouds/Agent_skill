# Module Guide: `experiment/eda/analysis.py`

## Purpose

Run the reproducible EDA stack: overview, feature profile, graph statistics, temporal behavior, drift checks, and the recommended time-aware split.

## When To Read This File

Read this file when you need to understand where the recommended train/val split comes from, why the current validation regime is time-aware, or how the generated EDA artifacts are produced.

## Upstream Callers / Entrypoints

- experiment/eda/run_eda.py

## Downstream Consumers / Artifacts

- experiment/outputs/eda/*.json / *.csv / *.md
- experiment/training/common.py::load_experiment_split
- experiment/training/features.py temporal feature construction

## Main Outputs Or Side Effects

- dataset_summary.json
- feature_profile.csv
- graph_profile.csv
- temporal_profile.csv
- drift_summary.md
- recommended_split.json

## Common Edit Hotspots

- Modify split strategy here if the project changes its validation philosophy.
- Adjust temporal windows, drift metrics, or artifact set here when EDA requirements expand.

## Top-Level Symbols

### `configure_matplotlib() -> None`

- Kind: `function`
- Lines: `25-33`
- Role: Set a font stack that can render Chinese labels in generated plots and keep minus signs readable.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `ensure_dir(path: Path) -> Path`

- Kind: `function`
- Lines: `36-38`
- Role: Create an artifact directory if missing and return the same path for chained writes.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `write_csv(path: Path, rows: list[dict[str, Any]]) -> None`

- Kind: `function`
- Lines: `41-56`
- Role: Write a list of dict rows into a UTF-8 CSV artifact with stable field ordering.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `write_json(path: Path, payload: dict[str, Any]) -> None`

- Kind: `function`
- Lines: `59-64`
- Role: Persist a JSON summary artifact for later reuse by training or reporting code.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `write_square_csv(path: Path, headers: list[str], matrix: np.ndarray) -> None`

- Kind: `function`
- Lines: `67-73`
- Role: Write a square matrix such as a correlation or PSI-style table with row and column headers.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `label_name(label: int) -> str`

- Kind: `function`
- Lines: `76-77`
- Role: Map numeric dataset labels to readable names like normal, fraud, and background classes.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `quantile_row(prefix: str, values: np.ndarray) -> dict[str, float]`

- Kind: `function`
- Lines: `80-86`
- Role: Convert one numeric vector into a prefixed quantile-stat dict row for CSV summaries.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `basic_stats(values: np.ndarray) -> dict[str, float]`

- Kind: `function`
- Lines: `89-97`
- Role: Return a compact statistics dict used inside EDA summaries.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `sample_values(values: np.ndarray, seed: int, max_size: int = PLOT_SAMPLE_SIZE) -> np.ndarray`

- Kind: `function`
- Lines: `100-105`
- Role: Downsample large vectors for plotting so EDA remains tractable on million-scale data.
- How to use: Use this to build a local sampled subset or subgraph instead of materializing the full graph structure.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `plot_empirical_cdf(ax: plt.Axes, values: np.ndarray, label: str, color: str) -> None`

- Kind: `function`
- Lines: `108-114`
- Role: Draw an empirical CDF curve on an existing matplotlib axis.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `build_time_windows(values: np.ndarray, n_windows: int = TIME_WINDOW_COUNT) -> list[dict[str, Any]]`

- Kind: `function`
- Lines: `117-139`
- Role: Split a time-like vector into quantile-based windows for later temporal summaries.
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `build_phase_output_dir(outdir: Path, phase: str) -> Path`

- Kind: `function`
- Lines: `142-143`
- Role: Create the output subdirectory for a specific phase under the EDA output root.
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `get_train_target(data: PhaseData) -> tuple[np.ndarray, np.ndarray]`

- Kind: `function`
- Lines: `146-148`
- Role: Return the official supervised node ids and labels for one dataset phase.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `analyze_overview(data: PhaseData, outdir: Path) -> dict[str, Any]`

- Kind: `function`
- Lines: `151-198`
- Role: Produce the high-level size, label, edge-type, and train/test distribution summary for one phase.
- How to use: Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload.
- Side effects / outputs: Usually writes plots / tables and returns a structured summary for the phase being analyzed.

### `analyze_features(data: PhaseData, outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]`

- Kind: `function`
- Lines: `201-457`
- Role: Profile raw feature distributions, missingness, normal-vs-fraud gaps, and per-group missing patterns.
- How to use: Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload.
- Side effects / outputs: Usually writes plots / tables and returns a structured summary for the phase being analyzed.

### `compute_degree_arrays(data: PhaseData) -> tuple[np.ndarray, np.ndarray, np.ndarray]`

- Kind: `function`
- Lines: `460-466`
- Role: Compute indegree, outdegree, and total degree arrays from the raw edge list.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `compute_temporal_core(data: PhaseData) -> dict[str, np.ndarray]`

- Kind: `function`
- Lines: `469-492`
- Role: Compute first_active, last_active, and active_span arrays used throughout EDA and feature building.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `analyze_graph(data: PhaseData, outdir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]`

- Kind: `function`
- Lines: `495-724`
- Role: Profile graph structure, background-node effects, degree patterns, and edge-type behavior.
- How to use: Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload.
- Side effects / outputs: Usually writes plots / tables and returns a structured summary for the phase being analyzed.

### `analyze_temporal(data: PhaseData, outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, np.ndarray]]`

- Kind: `function`
- Lines: `727-828`
- Role: Profile node activity over time, time windows, and train-class temporal behavior.
- How to use: Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload.
- Side effects / outputs: Usually writes plots / tables and returns a structured summary for the phase being analyzed.

### `_psi(reference: np.ndarray, current: np.ndarray, bins: np.ndarray) -> float`

- Kind: `function`
- Lines: `831-839`
- Role: Compute a population stability style drift score between reference and current distributions.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_drift_bins(values: np.ndarray, n_bins: int = DRIFT_BIN_COUNT) -> np.ndarray`

- Kind: `function`
- Lines: `842-853`
- Role: Create quantile-based bins for drift calculations.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `analyze_drift(outdir: Path) -> tuple[list[dict[str, Any]], str]`

- Kind: `function`
- Lines: `856-946`
- Role: Compare phase1 and phase2 feature drift and write a drift summary report.
- How to use: Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload.
- Side effects / outputs: Usually writes plots / tables and returns a structured summary for the phase being analyzed.

### `build_recommended_split(outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> dict[str, Any]`

- Kind: `function`
- Lines: `949-1022`
- Role: Create the project's leakage-safe time-aware phase1 train/val split and phase2 external evaluation ids.
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `run_eda(phases: list[str], analyses: list[str], outdir: Path) -> dict[str, Any]`

- Kind: `function`
- Lines: `1025-1090`
- Role: Execute the requested EDA stages, aggregate summaries, and persist the full artifact bundle.
- How to use: This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically.
- Side effects / outputs: Typically triggers most of the file's intended side effects, including artifact writes or model execution.

