# ADR-001: Formulation of Hydrologically Informed Reliability & Selective Action

* **Status:** ACCEPTED
* **Date:** 2026-08-27
* **Authors:** AETHER Research & Engineering Team
* **Supersedes:** Phase 0.0–0.5 "Physics-Guided Recursive Self-Verification"

---

## 1. Context & Problem Statement
The original AETHER concept proposed a multi-iteration recursive refinement loop where predictions were repeatedly checked against mass conservation residuals. Hostile audits (Phase 0.5 & Phase 0.9) revealed that:
1. Catchment-scale mass balance residuals are circular at daily event scales because subterranean storage change $\Delta S$ is unobserved.
2. Recursive refinement loops lack descent/convergence guarantees and risk amplifying errors during unseen hydrological regimes.
3. Conformal nonconformity scores cannot be computed at inference time without ground truth.

A reformulated, mathematically rigorous architecture is required to test whether pre-outcome signals can predict forecast failure and enable selective action.

---

## 2. Decision
We freeze the following architectural decisions for AETHER Milestone 1.0:
1. **Core Problem:** Pre-outcome failure prediction ($R_t = \hat{P}(F_t = 1 \mid \mathcal{I}_t)$) and selective forecasting ($\text{RELEASE}$ vs $\text{ABSTAIN}$).
2. **Dataset:** CAMELS-US v1.2, evaluated on the 531 benchmark non-impacted basins.
3. **Base Forecaster:** NeuralHydrology Entity-Aware LSTM (EA-LSTM) with 365-day lookback and 1-day lead time.
4. **Uncertainty Engine:** Conformalized Quantile Regression (CQR, nominal 90% coverage) + 5-seed deep ensemble spread.
5. **Reliability Estimator:** LightGBM GBDT with 5-fold block cross-fitting and out-of-fold Isotonic probability calibration trained on the Calibration split (`2005–2010`).
6. **Primary Failure Label:** Normalized Absolute Forecast Error ($\text{NAFE} > 1.0$).
7. **Temporal Partitioning:** Train (`1980–2000`), Validation (`2000–2005`), Calibration (`2005–2010`), Test (`2010–2018`) with 366-day embargo buffers.

---

## 3. Alternatives Considered
* **Recursive Refinement Loops:** Rejected due to lack of convergence guarantees and risk of error amplification.
* **LLM-Based Critique Agents (e.g. HydroAgent):** Rejected as non-deterministic and ungrounded in physical conservation laws.
* **Naive DeLong Testing:** Rejected due to high type-I error rates under spatiotemporally autocorrelated streamflow.

---

## 4. Scientific & Engineering Consequences
* **Positive:** Every component is mathematically well-posed, computationally efficient, and verifiable with standard statistical metrics (AUROC, AUPRC, Brier, AURC).
* **Trade-offs:** Requires strict 4-way temporal data management and 5-fold cross-fitting on calibration data.

---

## 5. Reproducibility & Leakage Impact
* Calibration split is completely segregated from the base model training and the held-out test set.
* Features satisfy strict temporal causality: $X_t \in \mathcal{I}_t$ with target $Q_{t+1}$ evaluated strictly ex-post.
