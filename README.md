# AETHER: Hydrologically Informed Reliability Estimation & Selective Forecasting for Environmental Extremes

[![CI](https://github.com/placeholder-org/aether/actions/workflows/ci.yml/badge.svg)](https://github.com/placeholder-org/aether/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AETHER** is an open-source, reproducible, model-agnostic reliability and selective decision framework for hydrological forecasting.

---

## 1. Central Scientific Question

A conventional forecasting pipeline issues predictions and acts upon them without knowing whether the model has entered a failure mode:

```text
Hydrological data ──► Forecast Model ──► Forecast ──► Act unconditionally
```

AETHER introduces a pre-outcome reliability and selective decision layer:

```text
Hydrological data
      ↓
Forecast Model ──► Forecast
                         │
                         ▼
             ┌─────────────────────────┐
             │         AETHER          │
             │                         │
             │ Pre-Outcome Reliability │
             │ & Selective Estimation  │
             └───────────┬─────────────┘
                         │
                         ▼
                  Decision Policy
                 ↙       ↓       ↘
             RELEASE   REFINE   ABSTAIN
```

Its central research question is:

> **"Can we predict whether a hydrological forecast is likely to fail before the ground-truth outcome becomes available, and use that reliability estimate to make calibrated accept/refine/abstain decisions?"**

---

## 2. What AETHER Is NOT

To maintain clear scientific boundaries, AETHER is explicitly **not**:

- **Not another flood-prediction model:** The objective is not to design a new rainfall-runoff architecture.
- **Not another LSTM/Transformer forecaster:** AETHER wraps around existing forecasting models in a model-agnostic manner.
- **Not a generic uncertainty estimation library:** Uncertainty representations (such as conformal intervals or ensemble spread) serve strictly as pre-outcome features rather than the end product.
- **Not a dashboard project:** Visualization tools support the research; they do not substitute for validated scientific methods.
- **Not an ad-hoc collection of hydrology notebooks:** The repository is an auditable, test-driven research engineering framework.

---

## 3. Documentation Hierarchy & Governance

The repository maintains an explicit separation of roles across its documentation:

```text
docs/
├── AETHER_RESEARCH_NORTH_STAR.md          # Canonical scientific vision & standing decision guide
├── AETHER_Phase_1.0_Implementation_Freeze.md # Phase 1.0 experimental specification & contracts
├── reproducibility.md                     # Provenance logging, seed policies & split invariants
├── decisions/                             # Architectural Decision Records (ADRs)
│   ├── README.md                          # ADR lifecycle rules & index
│   ├── template.md                        # Standard decision template
│   └── ADR-001-reliability-framework-architecture.md
└── research/                              # Historical research & hostile audit archive
    ├── aether_research_audit.md           # Phase 0 literature audit & product definition
    ├── aether_hostile_review.md           # Phase 0.5 hostile scientific review & red-team
    ├── AETHER_Research_Audit_Product_Definition.pdf
    ├── AETHER_Phase_0.5_Hostile_Review.pdf
    ├── Response from Hostile Audit till phase 0.5.docx
    ├── Response from Hostile Audit till phase 0.5.pdf
    └── Response from Hostile Audit till phase 0.75.pdf
```

### Documentation Roles

* **Canonical Research Direction:** [docs/AETHER_RESEARCH_NORTH_STAR.md](docs/AETHER_RESEARCH_NORTH_STAR.md)
  *The primary research reference.* Sets the ultimate scientific standards, hypothesis falsification requirements, and decision rules. Check this document before implementing features, altering baseline suites, or claiming novelty.
* **Implementation Specification:** [docs/AETHER_Phase_1.0_Implementation_Freeze.md](docs/AETHER_Phase_1.0_Implementation_Freeze.md)
  *The frozen Phase 1.0 contract.* Defines the operational baseline (EA-LSTM, CAMELS-US 531 basins, CQR uncertainty, LightGBM reliability estimator, NAFE failure label, and 4-way temporal partitioning).
* **Reproducibility Contract:** [docs/reproducibility.md](docs/reproducibility.md)
  *The experimental replication standard.* Defines mandatory `experiment_meta.json` logging, seed control, and artifact structures.
* **Architectural Decision Records:** [docs/decisions/](docs/decisions/)
  *Immutable design logs.* Documents significant technical and scientific pivots, beginning with [ADR-001](docs/decisions/ADR-001-reliability-framework-architecture.md).
* **Historical Research & Audit Archive:** [docs/research/](docs/research/)
  *Auditable research record.* Contains Phase 0–0.9 conceptual audits, hostile red-team reviews, and responses that led to the current formulation.

---

## 4. Current Development Roadmap (Phase 1.0 Foundation)

Milestone 1.0 follows a rigorous, sequential execution plan:

- [x] **R1.1 — CAMELS-US benchmark basin registry:** Canonical 531-basin registry and manifest verification.
- [x] **R1.2 — CAMELS-US raw data loader:** Offline, unit-preserving parser for Daymet forcing, USGS streamflow, and catchment attributes.
- [ ] **R1.3 — CAMELS-US Daymet forcing schema validation:** Structural schema and boundary validation for meteorological inputs. *(NEXT)*
- [ ] **R1.4 — CAMELS-US discharge conversion validation:** Area-normalized discharge conversion ($cfs \to mm/\text{day}$).
- [ ] **R1.5 — CAMELS-US missing-data quality control:** Streamflow QC masking and missing-rate filtering protocols.
- [ ] **R1.6 — Leakage-safe temporal split manager:** Non-overlapping receptive fields across Train (`1980–2000`), Val (`2000–2005`), Cal (`2005–2010`), and Test (`2010–2018`).
- [ ] **R1.7 — 366-day lookback buffer enforcement:** History buffer prepending without label evaluation contamination.
- [ ] **R1.8 — Automated CAMELS-US data leakage test suite:** 14-point automated test suite guarding against temporal, spatial, and feature leakage.
- [ ] **R1.9 — CAMELS-US provenance and reproducibility documentation:** Full audit trial and end-to-end data pipeline verification.

---

## 5. Repository Architecture

```text
aether/
├── configs/          # YAML configuration schemas and validation models
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
```

---

## 6. Quickstart & Environment Setup

AETHER uses [`uv`](https://github.com/astral-sh/uv) for fast, deterministic dependency management.

```bash
# Clone repository
git clone https://github.com/JayKalbi/AETHER.git
cd Aether

# Create virtual environment
uv venv aethervenv

# Activate virtual environment
# Windows PowerShell:
.\aethervenv\Scripts\activate
# Linux/macOS:
source aethervenv/bin/activate

# Install locked dependencies into environment
uv sync --locked --dev
```

---

## 7. Running Verification & Tests

```bash
# Run all unit and data loader tests
uv run pytest -v

# Run Ruff linter and formatter checks
uv run ruff check .
uv run ruff format --check .
```

---

## 8. Contributor Workflow

Please review [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions (`feature/*`, `fix/*`, `docs/*`, `exp/*`), Conventional Commits formatting, and pull request requirements.
