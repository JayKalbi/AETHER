# AETHER Scientific Reproducibility Contract

**Document Version:** 1.0.0  
**Scope:** All computational experiments, benchmark suites, and publication artifacts.

---

## 1. Core Reproducibility Principle

Every scientific result, figure, metric, and decision table published by AETHER must be **deterministically reproducible** from:
1. **The Codebase:** Fixed Git commit SHA.
2. **The Configuration:** A self-contained YAML configuration file.
3. **The Documented Dataset:** Specific versioned dataset and basin registry.
4. **The Pinned Environment:** Locked Python environment (`uv.lock` / `pyproject.toml`).

---

## 2. Mandatory Experiment Metadata Log

Every experiment run must automatically record and persist an `experiment_meta.json` artifact containing:

| Metadata Field | Type | Description |
|:---|:---|:---|
| `experiment_id` | String | Unique run identifier (e.g., `EXP001_FAILURE_BENCHMARK_v1`) |
| `git_commit_sha` | String | Complete 40-character Git commit hash (must not be dirty for official runs) |
| `git_branch` | String | Active Git branch name |
| `config_path` | String | Relative path to the executed YAML configuration |
| `config_hash` | String | SHA-256 hash of the exact configuration file contents |
| `dataset_name` | String | Dataset identifier (e.g., `CAMELS-US`) |
| `dataset_version` | String | Dataset release version (`v1.2`) |
| `basin_registry_hash` | String | SHA-256 hash of `camels_us_benchmark_531.json` |
| `temporal_split_definition` | Object | Exact date bounds for Train, Val, Cal, Test |
| `random_seeds` | Object | Master global seed, PyTorch seed, NumPy seed, LightGBM seed |
| `python_version` | String | Full sys.version string (e.g., `3.12.10`) |
| `platform_info` | Object | OS, CPU architecture, CUDA version, GPU device name |
| `dependencies` | Object | Exact installed package versions (Torch, LightGBM, Scikit-learn, etc.) |
| `start_time_utc` | String | ISO-8601 execution start timestamp |
| `end_time_utc` | String | ISO-8601 execution completion timestamp |

---

## 3. Determinism & Randomness Contract

* **Random Number Generation:** All pseudo-randomness must be governed by `aether.utils.seed.set_global_seed(seed)`.
* **PyTorch Backend:** Deterministic algorithms are enforced:
  ```python
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  torch.use_deterministic_algorithms(True)
  ```
* **Ensemble Seeds:** When training deep ensembles, seeds must be explicitly enumerated in the configuration (e.g., `[101, 102, 103, 104, 105]`) rather than randomly sampled at runtime.

---

## 4. Split and Data Isolation Contract

* **Normalization Statistics:** Catchment mean streamflow $\bar{Q}_b$, standard deviation $\sigma_{Q, b}$, and Daymet climate statistics $(\mu, \sigma)$ must be computed strictly on `TRAIN` (`1980-10-01` to `2000-09-30`).
* **Threshold Selection:** Quantiles for failure labeling ($Q_{95, b}$) must be derived strictly from `TRAIN`.
* **Reliability Calibration:** Probability calibration and decision threshold tuning ($\tau$) must be performed strictly within `CAL` (`2005-10-01` to `2010-09-30`) using 5-fold cross-fitting.
* **Test Isolation:** The `TEST` partition (`2010-10-01` to `2018-09-30`) is strictly evaluated on frozen checkpoints.

---

## 5. Artifact Storage Standards

All experiment outputs must be structured deterministically under `artifacts/<experiment_id>/`:
```
artifacts/<experiment_id>/
├── experiment_meta.json      # Complete provenance metadata
├── config_frozen.yaml        # Copy of the exact config used
├── metrics/
│   ├── summary_metrics.json  # CONUS-wide aggregate metrics (AUROC, AUPRC, Brier, AURC)
│   ├── basin_metrics.parquet # Per-basin evaluation breakdown
│   └── bootstrap_cis.json    # Clustered block bootstrap confidence intervals
├── predictions/
│   ├── cal_oof_preds.parquet # Out-of-fold predictions on calibration split
│   └── test_preds.parquet    # Test set predictions, intervals, and reliability scores
└── plots/
    ├── roc_pr_curves.png     # ROC and Precision-Recall plots
    ├── reliability_diag.png  # Calibration reliability diagrams
    └── risk_coverage.png     # Selective risk-coverage trajectories
```
