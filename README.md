# AETHER: Hydrologically Informed Reliability Estimation & Selective Forecasting for Environmental Extremes

[![CI](https://github.com/placeholder-org/aether/actions/workflows/ci.yml/badge.svg)](https://github.com/placeholder-org/aether/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AETHER is an open research and engineering framework investigating whether **pre-outcome information** (predictive uncertainty representations, input-space out-of-distribution signals, and hydrologically informed domain diagnostics) can **predict streamflow forecast failure** before ground truth arrives, and whether the resulting reliability estimate enables **selective forecasting** during environmental extremes.

---

## 1. Scientific & Project Status

* **Current Phase:** Gate R0 Complete — Implementation Kickoff (Milestone 1.0 / MVP v0.1).
* **Research Status:** Conceptual research and hostile audits (Phase 0 through Phase 0.9) are complete. The experimental specification is frozen in [AETHER_Phase_1.0_Implementation_Freeze.md](AETHER_Phase_1.0_Implementation_Freeze.md).
* **Target Benchmark:** CAMELS-US v1.2 (531 non-impacted benchmark catchments).
* **Primary Objective:** Empirically test Hypothesis H1 (failure predictability) and Hypothesis H2 (incremental value of hydrological domain features).

---

## 2. Repository Architecture

```
aether/
├── configs/          # YAML configuration schemas and Pydantic validation models
├── data/             # CAMELS-US ingestion, basin registry, split manager
├── forecasting/      # Base EA-LSTM forecasting models & quantile heads
├── uncertainty/      # Conformalized Quantile Regression (CQR) engine
├── labels/           # Normalized Absolute Forecast Error (NAFE) labelers
├── features/         # Causal 21-feature extraction pipeline (Groups A-E)
├── reliability/      # LightGBM GBDT failure predictor & isotonic calibrator
├── selection/        # Selective action policies (RELEASE / ABSTAIN) & RC curves
├── evaluation/       # Clustered moving-block bootstrap statistical testing
├── utils/            # Logging, deterministic seeds, typing
└── experiments/      # Executable benchmark pipelines (Exp 001 - Exp 004)

tests/
├── unit/             # Isolated unit tests for configs, utilities, and models
├── data/             # Basin registry and dataset loader integrity checks
├── leakage/          # Automated 14-point causal filtration and split isolation tests
└── integration/      # End-to-end pipeline benchmark tests

docs/
├── reproducibility.md # Scientific reproducibility contract and metadata standards
└── decisions/        # Architectural Decision Records (ADRs)
```

---

## 3. Separation of Source Code and External Datasets

* **Source Code:** All data loaders, feature extractors, and split algorithms live in `aether/data/` and `aether/features/` and are tracked by Git.
* **Datasets (Raw & Processed):** Raw CAMELS-US files and generated Parquet feature tables are placed in `data/camels_us/` and `artifacts/`, which are explicitly excluded from Git tracking via `.gitignore`.

---

## 4. Quickstart & Environment Setup

AETHER uses [`uv`](https://github.com/astral-sh/uv) for fast, deterministic dependency management.

```bash
# Clone repository
git clone <repo-url>
cd Aether

# Create virtual environment
uv venv aethervenv

# Activate virtual environment
# Windows PowerShell:
.\aethervenv\Scripts\activate
# Linux/macOS:
source aethervenv/bin/activate

# Install AETHER in editable mode with development dependencies
uv pip install -e ".[dev]"
```

---

## 5. Running the Test Suite & Linting

```bash
# Run all unit tests
pytest -v

# Run the automated data leakage test suite
pytest tests/leakage/ -v

# Run Ruff linter and formatter checks
ruff check .
ruff format --check .
```

---

## 6. Contributor Workflow

Please review [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions (`feature/*`, `fix/*`, `exp/*`), commit conventions (Conventional Commits), and PR review guidelines for our three-person team.
