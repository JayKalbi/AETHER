# AETHER — Phase 0.5: Hostile Research-Gap Validation & Scientific Red-Team

**Date:** August 12, 2026  
**Status:** Hostile Review Complete  
**Previous Verdict:** Conditional Approval (Phase 0)  
**This Verdict:** OUTCOME B — MANDATORY REFORMULATION (see Section 17)

---

# PHASE 0 — RECONSTRUCTION OF PREVIOUS CLAIMS

| # | Previous Claim | Evidence Given | Confidence | Potential Weakness |
|---|---------------|----------------|:----------:|-------------------|
| 1 | **Research gap**: "Conformal-prediction-gated recursive physics-guided correction for flood forecasts is genuinely underexplored" | Searched ~20 queries across hydrology and ML venues; no exact match found | Medium | Searched for exact terminology, not conceptual equivalents; may have missed adjacent formulations in PDE solving, surrogate modeling, and power systems |
| 2 | **Novelty**: Combining {conformal prediction} ∩ {physics consistency} ∩ {recursive correction} ∩ {flood forecasting} is unstudied | Novelty matrix showing no system covers all four | Medium | Each component exists independently; combination may be incremental, not novel |
| 3 | **Closest competitors**: HydroAgent (LLM-based, no formal UQ), WaveAgent (coastal, no CP), dPL (training-time only) | Web searches, summaries | Low-Medium | Did not read primary HydroAgent or WaveAgent papers; relied on summaries |
| 4 | **Conformal prediction role**: Use nonconformity scores as gating signal for correction | Stated without mathematical verification | Low | Did not verify whether nonconformity scores can be computed at inference time without ground truth |
| 5 | **Physics-consistency diagnostics**: "No standardized diagnostic exists" | Assertion without systematic literature review | Low | Did not search for PIR, water balance residuals, or signature-based evaluation |
| 6 | **Recursive correction**: Physics-guided correction module triggered by verification gate | Architectural diagram only; no mathematical analysis | Low | No convergence analysis, no analysis of whether recursion is necessary vs. one-shot correction |
| 7 | **Mathematical guarantees**: "Provable coverage guarantees" from conformal prediction | Stated as a design goal | Very Low | Did not analyze whether coverage survives the correction loop |
| 8 | **Product differentiation**: "Verified, trustworthy forecasts" that no existing system provides | Competitive comparison table | Medium | "Trustworthiness" was never mathematically defined |
| 9 | **Publication potential**: WRR/HESS, 7/10 likelihood | Assessment based on gap analysis | Medium | Did not simulate actual reviewer objections |

> [!CAUTION]
> **Claims 4, 5, 6, and 7 were made without mathematical verification.** This is the most serious failure of the Phase 0 report. A research proposal that claims "provable guarantees" without checking whether the mathematics works is scientifically irresponsible.

---

# PHASE 1 — FRESH LITERATURE VERIFICATION

## Critical Papers Discovered That Were Missed in Phase 0

### 1. CP-PRE: Conformal Prediction with Physics Residual Error
- **Citation:** Gopakumar et al., "Calibrated Physics-Informed Uncertainty Quantification," ICML 2024/2025
- **Status:** Peer-reviewed (ICML)
- **What it does:** Uses **physics residual errors as nonconformity scores** in a conformal prediction framework. Provides data-free, model-agnostic uncertainty quantification for neural PDE solvers by checking how well predictions obey governing physical laws.
- **Why it threatens AETHER:** This is almost exactly what AETHER proposes — using physics residuals within a CP framework to assess prediction reliability. CP-PRE was published at ICML and is open-source.
- **AETHER implication:** AETHER cannot claim "physics-aware conformal prediction" as novel. CP-PRE already does this.

### 2. PhysicsCorrect
- **Citation:** Published ~2025, AAAI
- **Status:** Peer-reviewed
- **What it does:** Inference-time physics-based correction of neural PDE solvers using linearized PDE residual minimization. No retraining required. Uses Jacobian caching for efficiency.
- **Why it threatens AETHER:** This is inference-time physics-guided correction — one of AETHER's core components.

### 3. Selective Conformal Risk Control (SCRC)
- **Citation:** 2025–2026 (arXiv/conference)
- **Status:** Preprint / Under review
- **What it does:** Formalizes the exact "gate → control" pipeline AETHER proposes: Stage 1 filters low-confidence inputs (abstention/gating), Stage 2 applies conformal risk control to accepted predictions. Two variants (SCRC-T with exact finite-sample guarantees, SCRC-I with PAC guarantees).
- **Why it threatens AETHER:** SCRC is the mathematically rigorous version of AETHER's proposed gating mechanism, already formalized.

### 4. Selective Learning for Deep Time Series Forecasting
- **Citation:** NeurIPS 2025
- **Status:** Peer-reviewed
- **What it does:** Uses dual-mask mechanism (uncertainty mask + anomaly mask) to filter unreliable timesteps in deep time-series forecasting. Demonstrated MSE reductions across Informer, TimesNet, iTransformer.
- **Why it threatens AETHER:** Selective prediction in time-series forecasting is already published at NeurIPS.

### 5. Hydrological Forecast Post-Processing (Existing Practice)
- **Citation:** Multiple review papers (2024–2025); WMO Guidelines on Verification of Hydrological Forecasts (2025 update)
- **Status:** Established practice
- **What it does:** "Inference-time correction" of hydrological forecasts is universally known as **post-processing** or **Model Output Statistics (MOS)**. Deep learning LSTMs/CNNs are already used operationally for this. Test-Time Adaptation frameworks (e.g., Morphing-Flow) explicitly adapt to non-stationary flood events without retraining.
- **Why it threatens AETHER:** AETHER's "inference-time correction" may be viewed as rebranding standard post-processing.

### 6. Physical Inconsistency Ratio (PIR) and Signature-Based Evaluation
- **Citation:** Established hydrology literature; recent applications in GNN-based streamflow papers (2024–2026)
- **Status:** Established practice
- **What it does:** PIR quantifies mass/conservation-law violations. Hydrological signatures (flow duration curves, recession analysis, baseflow index) evaluate physical plausibility. KGE decomposition (Gupta et al., 2009) diagnoses model errors into bias, variability, and correlation.
- **Why it threatens AETHER:** AETHER's claim that "no standardized physics-consistency diagnostic exists" is **false**.

### 7. Autocorrelated Multi-step Conformal Prediction (AcMCP) for Hydrology
- **Citation:** 2025, Monash University
- **Status:** Published
- **What it does:** Generates efficient prediction intervals for streamflow by accounting for serial correlation in forecast errors.
- **Why it matters:** Demonstrates that advanced conformal prediction methods for hydrology are actively being developed by multiple groups.

---

# PHASE 2 — ATTACKING THE NOVELTY CLAIM

## The Claim Under Attack

> "Using conformal prediction as a formal verification mechanism that gates recursive physics-guided correction of flood forecasts is genuinely underexplored."

## Systematic Search Results

I searched the following term combinations (search evidence documented in scratch files):

| Search Terms | Result |
|-------------|--------|
| conformal prediction + physics + correction | **CP-PRE (ICML)** uses physics residuals as CP nonconformity scores |
| conformal prediction + gating + abstention | **SCRC (2025–2026)** formalizes selective conformal risk control with abstention |
| conformal prediction + hydrology + streamflow | **STACI, AcMCP, HopCPT** — active research area with multiple papers |
| physics residual + correction + inference time | **PhysicsCorrect (AAAI), SCaSML (ICLR)** — established practice |
| selective prediction + time series | **NeurIPS 2025** — dual-mask selective learning |
| forecast post-processing + machine learning + hydrology | **Standard practice** — called MOS/bias correction |
| physics consistency diagnostic + hydrology | **PIR, signatures, water balance** — established |
| uncertainty-triggered correction + forecasting | **Morphing-Flow (TTA)** — adapts at test time for extremes |

## Verdict on Novelty Claim

> [!WARNING]
> **The claim that this intersection is "genuinely underexplored" is FALSE.**
>
> - Physics residuals as CP nonconformity scores: **CP-PRE (ICML)**
> - Conformal prediction for gating/abstention: **SCRC (2025–2026)**
> - Conformal prediction in hydrology: **STACI, AcMCP, HopCPT**
> - Inference-time physics correction: **PhysicsCorrect, SCaSML**
> - Post-processing of flood forecasts: **Standard practice**
> - Physics-consistency diagnostics: **PIR, hydrological signatures**
>
> The remaining novelty is: **applying an SCRC-like selective-prediction framework to hydrological time-series forecasting while using domain-specific physics residuals as the nonconformity/gating signal.** This is an incremental domain application, not a methodological innovation.

---

# PHASE 3 — DEEP COMPETITOR ANALYSIS

| System | Year | Venue | Domain | Verification | UQ | Correction | Recursive | Train/Inference | Guarantees | Threat |
|--------|------|-------|--------|:------------:|:--:|:----------:|:---------:|:---------------:|:----------:|:------:|
| **CP-PRE** | 2024–2025 | ICML | PDE solving | Physics residual as CP score | ✅ CP | ❌ | ❌ | Inference | Marginal coverage | 🔴 HIGH |
| **PhysicsCorrect** | 2025 | AAAI | PDE solving | PDE residual | ❌ | ✅ Physics | ✅ (iterative) | Inference | None (heuristic) | 🔴 HIGH |
| **SCaSML** | 2025–2026 | ICLR | PDE solving | Defect PDE | ❌ | ✅ Stochastic | ❌ (one-shot) | Inference | Error bounds | 🔴 HIGH |
| **SCRC** | 2025–2026 | Preprint | General ML | Selective gate | ✅ CRC | ❌ | ❌ | Calibration | PAC / finite-sample | 🔴 HIGH |
| **STACI** | 2024 | ICLR | Hydrology | Topology-aware CP | ✅ CP | ❌ | ❌ | Calibration | Marginal coverage | 🟡 MODERATE |
| **HydroAgent** | 2026 | arXiv | Hydrology | LLM skill critique | ❌ | ✅ LLM-driven | ✅ | Inference | None | 🟡 MODERATE |
| **WaveAgent** | 2025–2026 | Ocean Eng. | Coastal waves | Physics rules | ❌ | ✅ Model switch | ✅ | Inference | None | 🟡 MODERATE |
| **AQUAH** | 2025–2026 | Preprint | Hydrology | Workflow | ❌ | ❌ | ❌ | Setup-time | None | 🟢 LOW |
| **Forecast post-processing** | Decades | Multiple | Hydrology | Ex-post metrics | Varies | ✅ Bias correction | ❌ | Inference | None | 🟡 MODERATE |
| **Selective Learning** | 2025 | NeurIPS | Time-series | Dual-mask | Residual entropy | ❌ (masking) | ❌ | Training | None | 🟡 MODERATE |

**Most dangerous combination:** CP-PRE (physics-aware CP) + PhysicsCorrect (inference-time correction) + SCRC (formal gating). Together, these three papers from top ML venues cover nearly everything AETHER proposed.

---

# PHASE 4 — ATTACKING THE CONFORMAL PREDICTION LOGIC

## Question 1: Can we compute a nonconformity score at inference time?

> [!CAUTION]
> **NO. This is a fundamental statistical error in the Phase 0 proposal.**

In split conformal prediction, the nonconformity score $s(x, y) = |y - \hat{f}(x)|$ requires the **true value $y$**. At inference time, $y$ is the future discharge — which is **unknown**. 

What conformal prediction actually provides at inference time is a **prediction set/interval**: the set of all $y$ values whose nonconformity score would be below the calibrated threshold $\hat{q}$. For regression with absolute residual scores: $C(x) = [\hat{f}(x) - \hat{q}, \hat{f}(x) + \hat{q}]$.

**You get the interval, not a score for the point prediction.** The Phase 0 architecture's Step 4 ("If the conformal nonconformity score is high, send to correction") is statistically ill-posed.

### What CAN be used as a gating signal:
- **Interval width**: Wide interval → high uncertainty. Valid heuristic but not a "nonconformity score."
- **Normalized interval width**: $w(x) = \mu(C(x)) / \hat{f}(x)$. Relative uncertainty.
- **A learned confidence score**: Separate model predicting expected error. Not conformal.
- **Physics residual** (with caveats — see Phase 5).

## Question 2: Can interval width serve as a reliability signal?

**Yes, with limitations.** Wide intervals indicate the model is uncertain in regions similar to those seen in calibration. However:
- Width ≠ error. A wide interval may still contain an accurate point prediction.
- Under distribution shift, width may be miscalibrated.
- Width reflects calibration-set uncertainty, not necessarily the uncertainty of the specific test instance.

## Question 3: Can CP be used to gate correction without destroying coverage?

> [!CAUTION]
> **Using the CP interval to decide whether to correct the prediction, and then claiming the resulting system has coverage guarantees, is mathematically invalid.**

The coverage guarantee $P(Y \in C(X)) \geq 1-\alpha$ holds for the **original** prediction. If you:
1. Compute $C(x)$ for $\hat{f}(x)$
2. Decide $\hat{f}(x)$ needs correction based on $C(x)$
3. Produce a corrected $\hat{f}'(x)$

Then $C(x)$ was computed for $\hat{f}(x)$, not $\hat{f}'(x)$. The interval is invalid for the corrected prediction.

## Question 4: Does coverage survive correction?

**No.** The correction creates a new prediction function $\hat{f}'$ whose residual distribution differs from the calibration residuals of $\hat{f}$. Exchangeability is violated. The coverage guarantee is destroyed.

## Question 5: Can the pipeline be conformalized end-to-end?

**Yes, but this eliminates the recursive architecture.** The valid approaches:

1. **Treat the entire pipeline as a black box**: Base model + correction = single function $g(x)$. Calibrate CP on $g(x)$ using a held-out set. This works but means:
   - CP is computed AFTER correction, not used to GATE correction
   - The "conformal verification gate" concept disappears
   - This is just standard CP on a post-processed model

2. **Use ACI (Gibbs & Candès)**: Wrap the entire pipeline with online conformal prediction. ACI adjusts $\alpha_t$ based on past coverage. This handles distribution shift but:
   - Cannot be used INSIDE the correction loop
   - Requires observing $y_t$ to update (delayed feedback)
   - Valid only around the pipeline's final output

3. **Use Conformal Risk Control**: Calibrate a gating threshold on a held-out set such that the expected risk (e.g., expected error) of the final system output is controlled. This is the **most principled approach** but:
   - Requires defining "risk" precisely
   - Requires sample splitting for the gating threshold calibration
   - Does not provide per-prediction coverage — provides average risk control

4. **SCRC framework**: Use selective conformal risk control. Gate first, then conformalize the selected predictions. Requires:
   - SCRC-T: joint thresholding over calibration + test (expensive, needs test set)
   - SCRC-I: calibration-only (PAC guarantees, slightly conservative)

> [!IMPORTANT]
> **The mathematically valid design is: correct first (unconditionally or based on a heuristic), THEN conformalize the final output.** Not: conformalize → gate → correct → re-conformalize. The latter is statistically invalid.

---

# PHASE 5 — ATTACKING THE PHYSICS-CONSISTENCY SCORE

## A. Mass Balance

The water balance equation: $\Delta S = P - ET - Q$

At prediction time:
- $P$ (precipitation): **Known** (observed or NWP forecast)
- $ET$ (evapotranspiration): **Estimated** (Penman-Monteith or model output — itself uncertain)
- $Q$ (discharge): **This is the prediction** $\hat{Q}$ — what we're trying to verify
- $\Delta S$ (storage change): **UNKNOWN** — unobservable without GRACE or dense soil moisture networks

> [!CAUTION]
> **The mass-balance check is circular.** Computing $R = P - \hat{ET} - \hat{Q}$ gives you an estimate of $\Delta \hat{S}$, not a verification of $\hat{Q}$.
>
> You cannot determine whether a nonzero residual is due to:
> 1. Error in $\hat{Q}$ (what you want to detect)
> 2. Error in $\hat{ET}$ (uncertain estimate)
> 3. Real storage change $\Delta S$ (physically valid, especially during floods)
>
> **During flood events — the exact scenario AETHER targets — $\Delta S$ is maximally non-zero.** Rapid soil saturation, reservoir filling, and groundwater recharge make $\Delta S$ large and variable. Assuming $\Delta S \approx 0$ is physically wrong.

### Partial Mitigation
Over **long time periods** (seasonal, annual), $\Delta S \approx 0$ is more defensible. But AETHER targets **event-scale** (hours to days) forecasting, where this assumption fails.

Could use **GRACE/GRACE-FO** for $\Delta S$? Only at monthly, ~300km resolution. Useless for event-scale, basin-scale verification.

## B. Rainfall-Runoff Consistency

The runoff coefficient $C = Q/P$ should be $\in [0, 1]$ for any physically valid prediction. This IS a valid check:
- $\hat{Q} > P$: Physically impossible (more water leaving than entering) → flag
- $\hat{Q} < 0$: Physically impossible → flag

**But this is trivial.** Any reasonable neural network will rarely violate these bounds. The PIR (Physical Inconsistency Ratio) already measures this and is used in the literature.

## C. Temporal Consistency

A physically valid hydrograph should:
- Not have discontinuous jumps (except in flash floods)
- Follow recession curve physics (exponential decay during baseflow)
- Have rising limbs that are physically plausible given upstream precipitation

**This is valid but hard to formalize.** What constitutes an "impossible" rate of change depends on basin characteristics. A universal threshold would be arbitrary.

## D. Spatial Consistency

> [!WARNING]
> **Not applicable to AETHER's base architecture.** If the model predicts scalar discharge at a single gauge, there is no spatial dimension to check consistency across.

Spatial consistency requires either:
- Multi-gauge predictions (upstream → downstream mass balance)
- Gridded predictions (which AETHER does not propose)

## E. Physical Plausibility vs. Accuracy

**These are fundamentally different properties.**

- A prediction can be physically plausible but highly inaccurate (e.g., predicting baseflow during a major flood — physically possible, just wrong)
- A prediction can be physically implausible but accidentally accurate (rare but possible with extreme event extrapolation)

The relationship between physical plausibility and accuracy is an **empirical question**, not a logical necessity. If AETHER cannot demonstrate a strong correlation between its physics-consistency score and actual forecast error, the entire verification concept fails.

## F. Composite Score

Combining multiple residuals (mass balance, temporal, runoff ratio) into a single scalar requires:
- Normalization (each has different units/scales)
- Weighting (which diagnostic matters more?)
- Calibration (what score threshold separates "good" from "bad"?)

All of these involve arbitrary choices. The composite score is a **heuristic**, not a "formal diagnostic."

---

# PHASE 6 — ATTACKING "TRUSTWORTHINESS"

## Rigorous Definitions

| Term | Mathematical Definition | Does AETHER Estimate This? |
|------|------------------------|:-------------------------:|
| **Accuracy** | $\text{NSE}(\hat{Q}, Q) = 1 - \frac{\sum(Q - \hat{Q})^2}{\sum(Q - \bar{Q})^2}$ | Computable only ex-post |
| **Uncertainty** | $\text{Var}[\hat{Q} \mid X]$ — variance of prediction | Via CP interval width (indirect) |
| **Calibration** | $P(Q \in C(X)) = 1 - \alpha$ — coverage matches stated level | Via CP (if valid) |
| **Reliability** | Consistency of calibration across subgroups/conditions | Via conditional coverage analysis |
| **Validity** | Whether the model's assumptions hold in the test domain | NOT estimated by AETHER |
| **Physical plausibility** | $\hat{Q}$ satisfies known conservation laws | Via physics residuals (with caveats) |
| **Forecast error** | $e = Q - \hat{Q}$ | Unknown at prediction time |
| **Confidence** | $P(\hat{Q} \text{ is within } \epsilon \text{ of } Q)$ | Not directly estimated |
| **Risk** | $\mathbb{E}[L(\hat{Q}, Q)]$ for some loss $L$ | Via Conformal Risk Control (possible) |
| **Trustworthiness** | ??? | **UNDEFINED** |

> [!CAUTION]
> **"Trustworthiness" is not a mathematical concept.** AETHER cannot claim to produce "trustworthy" forecasts unless this term is rigorously defined. Every use of this word in the paper will be attacked by reviewers.

What AETHER can legitimately claim:
- "Calibrated prediction intervals" (if CP is correctly applied)
- "Controlled expected risk" (if CRC is used)
- "Physics-plausibility-screened forecasts" (if residuals are informative)
- "Selectively released forecasts" (if abstention is implemented)

It cannot claim "trustworthy" or "verified" without defining these formally.

---

# PHASE 7 — ATTACKING THE RECURSIVE CORRECTION LOOP

## The 12 Questions

| # | Question | Answer |
|---|---------|--------|
| 1 | What performs the correction? | Unclear. Phase 0 said "physics-constrained model" or "physics-loss-augmented network." No specific mechanism defined. |
| 2 | What objective does it optimize? | Not specified. Presumably minimizes some combination of physics residual and prediction uncertainty. |
| 3 | What information does it receive? | The original prediction $\hat{Q}$, meteorological forcing, basin attributes, and the physics residual. But NOT the ground truth $Q$. |
| 4 | What prevents it from making things worse? | **Nothing specified.** No monotonic improvement guarantee exists. |
| 5 | What determines when correction should occur? | The "verification gate." But the gate's statistical validity is questionable (Phase 4). |
| 6 | What determines when correction should stop? | "Max K iterations" or "convergence." But convergence of what? Physics residual? That's circular (Phase 5). |
| 7 | What guarantees convergence? | **Nothing.** No contraction mapping argument, no Lyapunov analysis, no descent guarantee. |
| 8 | Can correction oscillate? | **Yes.** Without a descent guarantee, the corrector could push predictions back and forth. |
| 9 | Can correction amplify errors? | **Yes.** If the corrector's training distribution doesn't match the test scenario, it can make predictions worse. |
| 10 | Does every correction require additional computation? | **Yes.** Each iteration runs the correction module + physics diagnostic + CP interval. |
| 11 | Does correction improve extreme events specifically? | **Unknown.** This is the central empirical claim but has no theoretical backing. |
| 12 | Can the system abstain instead of correcting? | Not in the current design. But abstention may be safer than unreliable correction. |

## Is Recursion Necessary?

Compare these alternatives:

| Strategy | Description | Advantage | Disadvantage |
|----------|-------------|-----------|-------------|
| **No correction** | Release base model output | Simple, valid CP | No improvement |
| **Always-correct (one-shot)** | Always apply correction module once | Deterministic, predictable overhead | May correct good predictions unnecessarily |
| **Always-correct (multi-shot)** | Apply K corrections always | More refinement | Higher cost, no convergence guarantee |
| **Uncertainty-gated one-shot** | Correct only when interval is wide | Targeted, efficient | Heuristic gating |
| **Physics-gated one-shot** | Correct only when physics residual is high | Domain-informed | Residual may be unreliable (Phase 5) |
| **Recursive** (AETHER proposal) | Correct repeatedly until gate passes | Most thorough | Statistically invalid, no convergence guarantee, highest cost |

> [!IMPORTANT]
> **One-shot correction is likely sufficient.** Standard post-processing in hydrology is one-shot. PhysicsCorrect is one-shot. SCaSML is one-shot. No evidence suggests that recursive correction provides meaningful benefit over one-shot correction in forecasting contexts (as opposed to PDE solving where you iterate a solver).
>
> The burden of proof is on AETHER to show recursion outperforms one-shot. If it doesn't, the architecture is over-engineered.

---

# PHASE 8 — ATTACKING THE HYPOTHESIS

The Phase 0 hypothesis:

> "A flood forecasting system that (1) computes physics-consistency diagnostics, (2) uses adaptive conformal prediction to estimate uncertainty, and (3) recursively refines predictions that fail a combined consistency-uncertainty gate will produce forecasts with ≥5% higher coverage-conditioned NSE during extreme events, ≤15% mass-balance residual reduction, and maintained or improved PICP."

## Problems

| Issue | Problem |
|-------|---------|
| "≥5% higher coverage-conditioned NSE" | Arbitrary threshold. What is "coverage-conditioned NSE"? Not a standard metric. Why 5%? |
| "≤15% mass-balance residual reduction" | Mass-balance residual is circular at event scale (Phase 5). Reducing it may mean the model learned to predict $\Delta S$ better, not $Q$ better. |
| "maintained or improved PICP" | CP guarantees PICP by construction (it's the point of CP). This is not a meaningful test of the correction loop. |
| "During extreme events" | How defined? Top 1%? Top 5%? Return period > 10 years? This requires defining a threshold. |
| "Recursively refines" | Not mathematically justified (Phase 7). One-shot may suffice. |
| "Physics-consistency diagnostics" | Already exist (PIR, signatures). Must specify what is NEW. |
| Not falsifiable as stated | Multiple vague conditions, no single decisive test. |

## Statistically Defensible Alternative

A hypothesis must be: specific, falsifiable, measurable with standard metrics, and free of arbitrary thresholds.

> **Revised Hypothesis**: "For the same base forecasting model $f$, applying a learned post-hoc correction module $g$ selectively — only to predictions whose estimated reliability score $r(x)$ falls below a data-driven threshold $\tau$ (calibrated via conformal risk control to bound expected loss) — produces (a) statistically significantly lower CRPS over peak-flow events (defined as $Q > Q_{95}$) compared to applying $g$ unconditionally, and (b) calibrated prediction intervals with empirical coverage within $[1-\alpha-\epsilon, 1-\alpha+\epsilon]$ for $\epsilon = 0.03$, as measured on held-out temporal splits across 671 CAMELS-US basins with 10-fold temporal cross-validation."

This version:
- Uses CRPS (standard probabilistic metric), not invented metrics
- Defines "extreme events" as $Q > Q_{95}$ (reproducible threshold)
- Tests selective vs. unconditional correction (not recursive vs. non-recursive)
- Specifies coverage tolerance
- Uses temporal cross-validation to prevent leakage

---

# PHASE 9 — ATTACKING THE EXPERIMENTAL DESIGN

## Data Leakage Risks

| Risk | Severity | Mitigation |
|------|:--------:|-----------|
| **Temporal leakage** (using future data to predict past) | 🔴 HIGH | Strict temporal split: train ≤ 2005, calibrate 2006–2010, test 2011–2018. No shuffling across time. |
| **Basin leakage** (testing on basins seen during training) | 🟡 MODERATE | For cross-basin experiments, use leave-basin-out. For same-basin, use temporal split only. |
| **Calibration/test contamination** | 🔴 HIGH | CP calibration set MUST be separate from both training and test. Three-way split required. |
| **Hyperparameter tuning on test** | 🟡 MODERATE | All hyperparameters (including gating threshold $\tau$) must be set on calibration set, never test. |
| **Post-hoc threshold selection** | 🔴 HIGH | The gating threshold cannot be optimized on the test set. Use CRC on calibration set to determine $\tau$. |

## Conformal Exchangeability

Hydrological time-series are **not exchangeable**. Consecutive discharge values are strongly autocorrelated ($\rho_1 \approx 0.9$ for daily discharge). This violates the fundamental assumption of split conformal prediction.

**Mitigation:** Use ACI (Gibbs & Candès) or AcMCP. These handle temporal dependence but provide weaker guarantees (asymptotic, not finite-sample).

## Extreme-Event Sampling

Testing on $Q > Q_{95}$ or $Q > Q_{99}$ produces very small sample sizes:
- CAMELS-US, 671 basins, ~30 years daily data → ~11,000 days/basin
- Top 1% → ~110 data points per basin
- Top 0.1% → ~11 data points per basin

Statistical tests on 11 data points are meaningless. Must aggregate across basins and use bootstrap confidence intervals.

## Multiple Hypothesis Testing

6 ablation variants × 5 metrics × 671 basins = thousands of comparisons. Without correction (Bonferroni, Benjamini-Hochberg), false discoveries are inevitable.

---

# PHASE 10 — CORRECT BASELINES

The minimum baseline set for credibility:

| # | Baseline | Type | Why Necessary |
|---|---------|------|--------------|
| 1 | Persistence (lag-1) | Naive | Sanity check; any model must beat this |
| 2 | Climatological mean | Statistical | Are we better than the long-term average? |
| 3 | LSTM (NeuralHydrology, no physics) | Pure ML | Standard ML baseline; demonstrates value of physics |
| 4 | LSTM + unconditional one-shot post-processing | ML + correction | Shows whether one-shot correction suffices |
| 5 | LSTM + CQR (Conformalized Quantile Regression) | ML + CP | Proper conformal baseline for UQ comparison |
| 6 | LSTM + physics training loss (dPL/xLSTM-MTV-style) | Physics-guided ML | Shows whether training-time physics suffices |
| 7 | LSTM + ACI (adaptive conformal) | ML + adaptive CP | Proper adaptive conformal baseline |
| 8 | **AETHER: LSTM + selective correction (one-shot, CRC-gated)** | Proposed method | The actual AETHER contribution |

**Baselines 4, 5, and 7 are critical.** If AETHER doesn't outperform "LSTM + CQR" (a simple conformal wrapper) or "LSTM + unconditional correction" (standard post-processing), it provides no value.

---

# PHASE 11 — ACTUAL NOVELTY ASSESSMENT

| Component | Status | Evidence |
|-----------|:------:|---------|
| LSTM for flood prediction | Already solved | Kratzert et al. (2024), NeuralHydrology |
| Physics-based training losses | Already solved | dPL, xLSTM-MTV, Willard et al. |
| Conformal prediction for hydrology | Partially solved | STACI, AcMCP, HopCPT — active area, multiple papers |
| Physics residuals as CP nonconformity scores | Already solved | **CP-PRE (ICML)** |
| Inference-time physics correction | Already solved | **PhysicsCorrect (AAAI), SCaSML (ICLR)** |
| Selective prediction / abstention | Partially solved | **SCRC, Selective Learning (NeurIPS)** |
| Physics-consistency diagnostics | Already solved | **PIR, hydrological signatures, KGE decomposition** |
| Conformal-gated selective correction loop | Novel (as integration) | No single paper does "selective conformal risk control + domain-specific physics reliability estimation + one-shot correction" in hydrology |
| "Trustworthy" flood forecasting | Unknown | Term is undefined; the goal is valid but the formulation needs work |

## The Smallest Defensible Novel Contribution

> **The novel contribution is NOT any single component. It is the rigorous empirical study of whether selective correction — where a data-driven reliability estimator (trained on physics-derived features) triggers one-shot post-processing — improves probabilistic flood forecasting quality, especially during extreme events, compared to unconditional post-processing and no correction.**

This contribution is:
- Empirical, not architectural
- Specific to hydrology (CAMELS/Caravan)
- Testable via rigorous ablation
- Not dependent on invalid conformal-gating claims
- Not dependent on uncomputable mass-balance checks

---

# PHASE 12 — ALTERNATIVE RESEARCH DIRECTIONS

| # | Direction | Novelty | Depth | Feasibility | Data | Publication | Engineering | Thesis | Industry |
|---|-----------|:-------:|:-----:|:-----------:|:----:|:-----------:|:-----------:|:------:|:--------:|
| 1 | **Selective prediction for flood forecasting** — when should a model abstain vs. predict? | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 2 | **Forecast reliability prediction** — can you predict the error of a forecast before ground truth arrives? | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 3 | **Physics-informed conformal prediction for hydrology** — domain-specific nonconformity scores using hydrological signatures | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 4 | **Conformal prediction under hydrological non-stationarity** — how do coverage guarantees degrade under climate-driven distribution shift? | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 5 | **Selective correction for extreme flood events** — does targeted post-processing outperform unconditional post-processing for high-flow events? | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recommended: Direction 2 (Forecast Reliability Prediction) combined with Direction 5 (Selective Correction).** This gives AETHER a clean, novel, and deeply scientific research question.

---

# PHASE 13 — REASSESSING THE PRODUCT

## What Belongs Where

### Research Prototype (Months 1–9)
- Reliability estimator: a model that predicts forecast error/uncertainty using physics-derived features
- Selective correction module: one-shot post-processor triggered by low reliability
- Conformal wrapper: ACI/CRC around the final pipeline output
- Ablation framework: systematic comparison of correction strategies
- Evaluation suite: CRPS, PICP, MPIW, FHV, NSE, KGE across CAMELS/Caravan

### Production-Grade Platform (Post-publication, if results positive)
- Data ingestion pipeline (ERA5, Caravan, India-WRIS)
- NeuralHydrology integration
- Reliability estimation API
- Selective correction API
- Conformal prediction intervals
- Forecast versioning and audit trails
- Dashboard for visualization

### Future Expansion (V2+, beyond thesis)
- Multi-basin spatial consistency checking (requires multi-gauge predictions)
- Inundation mapping integration
- Real-time alerting
- Historical event replay analysis
- Model comparison framework

---

# PHASE 14 — REASSESSING THE USER

## Primary User: Hydrological Researcher

**Decision they make:** Whether to trust and publish results from a flood forecasting model.

**What AETHER provides:** A rigorous framework for assessing when ML flood forecasts are reliable and when they should be corrected or withheld. Reproducible metrics. Open-source code.

**Why they'd use it:** Because no existing framework provides selective correction with formal risk control for streamflow forecasting. NeuralHydrology provides the model; AETHER provides the reliability wrapper.

## Secondary User: Flood Forecasting Agency

**Decision they make:** Whether to issue a flood warning.

**What AETHER provides:** A prediction interval with coverage guarantee + a reliability score indicating whether the prediction was in the model's "comfort zone."

**Why they'd use it over Google Flood Hub:** Honestly? **They probably wouldn't, yet.** Google Flood Hub has global coverage, operational support, and institutional backing. AETHER's value to agencies is medium-term: if the selective correction framework is adopted into operational systems like NeuralHydrology or GloFAS.

> [!IMPORTANT]
> **Honest answer:** AETHER's primary value is academic/research. Its product value depends entirely on whether the selective correction framework shows significant improvement in peer-reviewed evaluation. Do not over-promise operational impact during the thesis phase.

---

# PHASE 15 — REASSESSING THE OUTPUT

| Output | Scientifically Justified? | Notes |
|--------|:------------------------:|-------|
| Forecast hydrograph $\hat{Q}(t)$ | ✅ | Standard |
| Prediction interval $[Q_{lo}, Q_{hi}]$ | ✅ | Via CP (if correctly applied post-correction) |
| Exceedance probability $P(Q > Q_\text{threshold})$ | ✅ | Derivable from prediction interval |
| Reliability score $r(x)$ | ⚠️ Partially | Only if empirically validated to correlate with error |
| "Physics-consistency score" | ❌ | Mass-balance is circular; rename to "hydrological plausibility features" |
| Verification status (PASS/FAIL) | ⚠️ Partially | Only as "high/low reliability," not binary "verified" |
| Correction history | ✅ | Useful for audit |
| "Trustworthiness" | ❌ | Undefined term; do not use |
| Severity classification | ✅ | Engineering, based on threshold exceedance |
| Number of correction iterations | ❌ | If one-shot, this is always 0 or 1 |

---

# PHASE 16 — Q1 REVIEWER SIMULATION

## Reviewer 1: Water Resources Research

**What they would like:**
- Rigorous evaluation on CAMELS/Caravan with proper temporal splits
- Comparison with NeuralHydrology LSTM baseline
- Focus on extreme events (high-flow volume, FHV)
- Honest discussion of limitations

**What they would attack:**
- "Physics-consistency score" — will demand exact equations and proof it's not circular
- Any claim of "trustworthiness" without mathematical definition
- Lack of comparison with standard hydrological post-processing
- If AETHER doesn't beat dPL/δHBV on physics consistency

**What claim they would reject:**
- "Provable coverage guarantees" — will note that temporal autocorrelation violates exchangeability
- "Mass-balance verification" — will identify the $\Delta S$ problem immediately

**What experiment they would demand:**
- Compare AETHER vs. "LSTM + standard bias correction" (Quantile Mapping / MOS)
- Show results on ungauged basins (Pub/Sub splits from Kratzert et al.)

**Decision:** Major Revision (if the math is fixed) / Reject (if circular mass-balance claim remains)

## Reviewer 2: HESS

**What they would like:**
- Process-based understanding of when and why selective correction helps
- Analysis of which basin types benefit most from correction
- Signature-based evaluation alongside standard metrics
- Discussion of non-stationarity and climate change implications

**What they would attack:**
- Calling PIR-like diagnostics "novel"
- Not citing the extensive signature-based evaluation literature
- Over-claiming "verified forecasting" when verification is heuristic

**Decision:** Major Revision (strong potential if positioned correctly)

## Reviewer 3: Journal of Hydrology

**What they would like:**
- Practical utility for flood forecasting
- Comparison with operational systems (GloFAS, NOAA NWM)
- Application to a real flood event case study
- Clear computational cost analysis

**What they would attack:**
- Complexity of the architecture relative to improvement
- If computational overhead doesn't justify marginal accuracy gain

**Decision:** Minor Revision (if results are positive and presentation is clear)

## Reviewer 4: NeurIPS/ICLR AI4Science

**What they would like:**
- Novel methodological contribution (not just application)
- Formal guarantees with proofs
- Connection to broader ML theory (selective prediction, conformal risk control)

**What they would attack:**
- "This is just applying SCRC to a new domain — where is the methodological novelty?"
- "CP-PRE already uses physics residuals as nonconformity scores"
- Lack of theoretical analysis of when selective correction provably helps

**What they would demand:**
- Theoretical characterization of when selective correction improves CRPS
- Comparison with SCRC directly

**Decision:** Reject (unless strong methodological contribution beyond domain application)

---

# PHASE 17 — FINAL RED-TEAM VERDICT

## OUTCOME A — KILL AETHER

**Reason to kill:** The Phase 0 architecture is statistically invalid. The conformal-prediction gating mechanism cannot work as described (nonconformity scores require ground truth). Mass-balance verification is circular at event scale. The recursive correction loop has no convergence guarantee. CP-PRE, PhysicsCorrect, and SCRC collectively cover most of what AETHER proposed. "Inference-time correction" is just "post-processing" rebranded. The remaining novelty is incremental domain application.

**I do NOT recommend killing AETHER.** Despite these flaws, the underlying research question — "Can we predict when a flood forecast is unreliable and selectively correct it?" — is genuinely valuable and not yet answered in the hydrology literature.

## OUTCOME B — REFORMULATE AETHER ✅ RECOMMENDED

**The Phase 0 architecture must be abandoned.** The following elements are fatally flawed and must be dropped:
1. ❌ "Conformal nonconformity score as gating signal" — statistically impossible at inference time
2. ❌ "Mass-balance verification at prediction time" — circular without independent $\Delta S$
3. ❌ "Recursive correction loop" — no convergence guarantee, likely unnecessary
4. ❌ "Physics-consistency score" as a verification score — partially circular, rename to "reliability features"
5. ❌ "Provable coverage guarantees from the verification gate" — CP coverage is destroyed by correction
6. ❌ "Trustworthy forecasts" — undefined

**The reformulated AETHER (see below) is defensible.**

## OUTCOME C — APPROVE AETHER

Not recommended in its current form. The mathematics does not work.

---

# FINAL REQUIRED OUTPUT

## 1. Claims From Our Previous Report That Were Wrong

| Claim | Why It Was Wrong |
|-------|-----------------|
| "No standardized physics-consistency diagnostic exists" | PIR, hydrological signatures, KGE decomposition, and water balance residuals are all established diagnostics |
| "Conformal nonconformity scores can gate correction" | Nonconformity scores require ground truth $y$; cannot be computed at inference time |
| "Coverage guarantees survive correction" | Correction destroys exchangeability; coverage is invalidated |
| "Mass-balance residual is a valid verification metric at event scale" | $\Delta S$ is unknown; the check is circular during floods |
| "Recursive correction provides value" | No evidence vs. one-shot; no convergence guarantee |
| "The conformal-physics intersection is genuinely underexplored" | CP-PRE uses physics residuals as CP scores (ICML); SCRC formalizes selective conformal gating; PhysicsCorrect does inference-time physics correction |
| "Inference-time correction is novel for hydrology" | It's called "post-processing" or "bias correction" and is standard practice |
| "HydroAgent is the most dangerous competitor" | SCaSML (ICLR) and CP-PRE (ICML) are more dangerous methodologically |

## 2. Claims That Survived Verification

| Claim | Why It Survives |
|-------|----------------|
| The research question "Can selective correction improve flood forecasting?" is valuable | No paper rigorously tests selective vs. unconditional correction in hydrology |
| Data feasibility is excellent | CAMELS/Caravan/ERA5 are open, well-documented, and standard |
| Computational feasibility is good | Single GPU sufficient; NeuralHydrology handles base model |
| Publication potential in WRR/HESS exists | If reformulated with correct mathematics |
| The product concept of "reliability-aware forecasting" is commercially relevant | Climate-tech, disaster management, and insurance all need reliability estimates |
| Extreme-event forecasting is a genuine pain point | Existing models degrade during extremes; selective correction could help here |

## 3. Existing Papers That Threaten AETHER

| Paper | Venue | Year | Threat Level | What It Does |
|-------|-------|:----:|:------------:|-------------|
| **CP-PRE** | ICML | 2024–2025 | 🔴 CRITICAL | Physics residuals as CP nonconformity scores |
| **PhysicsCorrect** | AAAI | 2025 | 🔴 CRITICAL | Inference-time physics correction of neural PDE solvers |
| **SCaSML** | ICLR | 2025–2026 | 🔴 CRITICAL | Inference-time defect correction with error bounds |
| **SCRC** | Preprint | 2025–2026 | 🔴 CRITICAL | Selective conformal risk control with formal gating |
| **STACI** | ICLR | 2024 | 🟡 HIGH | Topology-aware CP for stream networks |
| **AcMCP** | Published | 2025 | 🟡 HIGH | Autocorrelated multi-step CP for hydrology |
| **Selective Learning** | NeurIPS | 2025 | 🟡 HIGH | Dual-mask selective prediction for time-series |
| **HydroAgent** | arXiv | 2026 | 🟡 MODERATE | LLM-orchestrated flood forecasting |
| **WaveAgent** | Ocean Eng. | 2025–2026 | 🟡 MODERATE | Closed-loop physics-guided wave forecasting |
| **Forecast post-processing literature** | Multiple | Decades | 🟡 MODERATE | Standard practice — AETHER must differentiate |

## 4. The Strongest Remaining Research Gap

> **No existing work rigorously evaluates whether *selective* post-processing — where a learned reliability estimator decides which predictions to correct — outperforms unconditional post-processing for probabilistic flood forecasting, particularly during extreme events.**

I searched: "selective correction streamflow," "conditional post-processing flood," "reliability-triggered bias correction hydrology," "when to correct flood forecast," "selective post-processing time series," "uncertainty-gated correction environmental forecasting."

The closest works are:
- **Selective Learning (NeurIPS 2025)**: Uses dual masks to filter unreliable timesteps during *training*, not to selectively *correct* during inference.
- **SCRC (2025–2026)**: Formalizes selective conformal gating, but in general ML — not applied to hydrology or with domain-specific reliability features.
- **Forecast post-processing**: Always applied unconditionally. No paper asks "should we selectively post-process?"

**The gap is: the rigorous empirical question of selective vs. unconditional correction in hydrological time-series forecasting, using physics-derived features for the selection decision.**

## 5. The Weakest Part of AETHER

The **physics-consistency diagnostic** as a standalone "verification" mechanism. The mass-balance check is circular at event scale. The remaining diagnostics (runoff ratio, temporal smoothness) are trivial checks that any reasonable model satisfies. The diagnostic suite needs to be reconceived as a set of **features for a learned reliability estimator**, not as a standalone "physics verification."

## 6. The Strongest Part of AETHER

The **research question** itself: "Can we predict when a flood forecast will be unreliable, and if so, can targeted correction improve it?" This is a genuinely useful, practically important, and surprisingly unasked question in the hydrology literature. Everyone builds better models; almost no one asks "when should I trust this model's output?"

## 7. Revised Research Question

> **"Can a learned forecast reliability estimator — using physics-derived features, model uncertainty signals, and meteorological context — predict the error of a flood forecast before ground truth arrives, and can selective post-processing triggered by low estimated reliability improve probabilistic forecast quality compared to unconditional post-processing?"**

## 8. Revised Hypothesis

> **"For a regional LSTM flood forecasting model, a reliability estimator $r(x)$ trained to predict forecast error magnitude using features derived from (a) conformal prediction interval properties, (b) hydrological plausibility indicators (runoff ratio bounds, recession-curve consistency, basin-specific flow duration curve deviations), and (c) meteorological forcing characteristics will:**
>
> 1. **Exhibit statistically significant rank correlation ($\rho > 0.3$, $p < 0.01$) with realized absolute forecast error across CAMELS-US basins;**
> 2. **When used to gate one-shot correction (correct predictions with $r(x) < \tau$ using a post-processing module, release predictions with $r(x) \geq \tau$ unchanged), produce a system whose CRPS on $Q > Q_{95}$ events is statistically significantly lower ($p < 0.05$, paired bootstrap test) than both (a) the uncorrected baseline and (b) an unconditionally corrected baseline;**
> 3. **When wrapped with Adaptive Conformal Inference (ACI), produce prediction intervals with empirical marginal coverage within $[0.87, 0.93]$ for nominal $90\%$ coverage across a held-out temporal test period."**

This hypothesis is:
- **Falsifiable**: Clear metrics, statistical tests, and thresholds
- **Non-arbitrary**: Uses standard metrics (CRPS, coverage); significance defined by statistical test, not percentage thresholds
- **Specific**: Defines features, comparison baselines, and evaluation protocol
- **Novel**: No paper tests selective vs. unconditional correction in hydrology
- **Achievable**: All data and methods are available

## 9. Revised Scientific Contribution

**AETHER contributes:**

1. **A forecast reliability estimator for flood prediction** — a model that predicts whether a flood forecast will be accurate or not, using domain-specific features, before ground truth arrives. This estimator is validated to correlate with actual forecast error across diverse basins.

2. **A selective correction framework** — using the reliability estimator to gate one-shot post-processing (correct unreliable predictions, release reliable ones unchanged). Empirical proof that selective correction outperforms both no-correction and always-correct strategies.

3. **A rigorous empirical study** — systematic ablation across CAMELS-US and CAMELS-GB, with proper temporal splits, multiple baselines, and statistical significance testing, answering: "Does selective correction work, and what makes it work?"

**What AETHER does NOT contribute:**
- A new flood forecasting model (use NeuralHydrology)
- A new conformal prediction method (use ACI/CRC)
- A new physics-consistency diagnostic (use existing metrics)
- "Trustworthy" or "verified" forecasts (undefined terms)
- A recursive correction architecture (unnecessary complexity)

## 10. Revised Experimental Design

### Data Split (Three-Way Temporal)
```
Train:       1980–2003  (base model + correction model training)
Calibrate:   2004–2008  (reliability estimator training + CRC threshold + CP calibration)
Test:        2009–2018  (final evaluation — NEVER touched during development)
```

### Baselines (8 total)
1. Persistence (lag-1)
2. Climatological mean
3. LSTM (NeuralHydrology, no physics)
4. LSTM + CQR (conformalized quantile regression)
5. LSTM + ACI (adaptive conformal inference)
6. LSTM + unconditional one-shot correction
7. LSTM + physics-informed training loss (dPL-style)
8. **AETHER: LSTM + selective correction (CRC-gated) + ACI wrapper**

### Ablation (5 variants of AETHER)
| Variant | Reliability Features | Correction | Selection |
|---------|:-------------------:|:----------:|:---------:|
| A0: No correction | — | ❌ | — |
| A1: Always-correct | — | ✅ (always) | — |
| A2: Random-select correction | — | ✅ (random 50%) | Random |
| A3: Uncertainty-only selection | CP width only | ✅ (selective) | CP width |
| A4: Full AETHER | CP + physics + meteo features | ✅ (selective) | Learned $r(x)$ |

### Evaluation Metrics
- **CRPS** (Continuous Ranked Probability Score) — primary metric
- **NSE, KGE** — standard accuracy metrics
- **PICP, MPIW** — prediction interval calibration and sharpness
- **FHV** — high-flow volume bias
- **Reliability score–error correlation** ($\rho$, $R^2$)
- **Selection rate** — what fraction of predictions get corrected?
- **Computational overhead** — wall-clock time ratio vs. baseline

### Statistical Tests
- Paired bootstrap test for CRPS comparison ($B = 10000$)
- Benjamini-Hochberg correction for multiple comparisons
- 10-fold temporal cross-validation for robustness

### Datasets
| Dataset | Basins | Use |
|---------|:------:|-----|
| CAMELS-US | 671 | Primary evaluation |
| CAMELS-GB | 671 | Cross-region generalization |
| Caravan-India | ~200 | Optional regional demonstration |

## 11. Revised Product Concept

### Research Prototype: `aether-forecast-reliability`
A Python library that wraps any point+interval flood forecasting model with:
1. **Reliability estimation module**: Extracts features from prediction intervals, hydrological plausibility indicators, and forcing data. Outputs a scalar reliability score $r(x) \in [0,1]$.
2. **Selective correction module**: One-shot correction triggered when $r(x) < \tau$. Threshold $\tau$ set via conformal risk control on calibration data.
3. **Conformal wrapper**: ACI applied to the final (possibly corrected) output to produce prediction intervals.
4. **Evaluation suite**: All metrics, ablation framework, and statistical tests pre-built.

### Production Platform (Post-Thesis, If Results Positive)
- NeuralHydrology integration plugin
- REST API for reliability scoring
- Dashboard: forecast + interval + reliability badge (GREEN/YELLOW/RED)
- Forecast audit log
- Historical event replay

## 12. What We Must NOT Build

1. ❌ A recursive correction loop — unnecessary, no convergence guarantee
2. ❌ A "conformal verification gate" that uses nonconformity scores to trigger correction — statistically invalid
3. ❌ A mass-balance "verification" at event scale — circular
4. ❌ An LLM/agent-based verification system — HydroAgent territory
5. ❌ A "physics-consistency score" claimed as novel — PIR exists
6. ❌ A multi-hazard prediction system — scope creep
7. ❌ A production dashboard as the primary deliverable — the research comes first
8. ❌ "Trustworthy" or "verified" forecasting — undefined terms

## 13. What We MUST Prove

| # | What Must Be Proven | How | Kill Criterion |
|---|-------------------|-----|:-------------:|
| 1 | The reliability estimator predicts forecast error | Rank correlation $\rho > 0.3$ between $r(x)$ and $|e|$ on test set | If $\rho < 0.2$: the estimator is noise 🔴 |
| 2 | Selective correction beats unconditional correction for extreme events | CRPS comparison on $Q > Q_{95}$ events, paired bootstrap $p < 0.05$ | If $p > 0.1$: selection doesn't help 🔴 |
| 3 | Selective correction beats no correction | CRPS comparison, full test set and extreme events | If no improvement: correction is useless 🔴 |
| 4 | ACI wrapper maintains approximate coverage | PICP $\in [0.87, 0.93]$ for nominal 90% | If PICP < 0.80: coverage is broken 🟡 |
| 5 | Physics-derived features add value over uncertainty-only features | Compare A3 (CP-width-only) vs A4 (full features) | If A3 ≥ A4: physics features are noise 🟡 |
| 6 | Results generalize across basins | CAMELS-US → CAMELS-GB transfer | If performance collapses: overfitting 🟡 |

## 14. Kill Criteria

| Condition | Action |
|-----------|--------|
| Reliability estimator doesn't predict error ($\rho < 0.2$) | 🔴 KILL the selective correction concept. Pivot to "Conformal prediction for flood forecasting under non-stationarity" (Direction 4 from Phase 12). |
| Selective correction doesn't beat unconditional ($p > 0.1$) | 🔴 KILL the selection mechanism. Publish the reliability estimator as a standalone diagnostic tool. |
| ACI coverage is severely broken (PICP < 0.80) | 🟡 REDESIGN the conformal wrapper. Consider CQR instead of ACI. |
| Physics features add no value over CP width | 🟡 SIMPLIFY. Drop physics features. Publish as "uncertainty-aware selective correction." |
| Results don't generalize to CAMELS-GB | 🟡 LIMIT claims to single-region. Still publishable but weaker. |

## 15. Final PI Decision

### Decision: **CONDITIONAL APPROVAL of reformulated AETHER**

I approve proceeding with the **reformulated** AETHER — the "Selective Forecast Correction" framework — under these mandatory conditions:

1. **Abandon the Phase 0 architecture entirely.** The conformal-gated recursive correction loop is mathematically invalid. Do not implement it.

2. **Start with the reliability estimator.** Before building any correction pipeline, prove that you can predict forecast error before ground truth arrives. If you cannot ($\rho < 0.2$), stop.

3. **Use one-shot correction, not recursive.** There is no evidence that recursion helps for forecasting (as opposed to PDE solving).

4. **Conformalize the final output, not the intermediate steps.** Apply ACI or CRC to the entire pipeline's output after correction decisions have been made.

5. **Do not claim novelty for any single component.** The novelty is the empirical demonstration that selective correction improves probabilistic flood forecasting. Position the paper as a rigorous empirical study, not a methodological innovation.

6. **Properly cite and differentiate from CP-PRE, SCRC, PhysicsCorrect, SCaSML, STACI, and forecast post-processing literature.** A reviewer who knows this literature will reject any paper that ignores it.

7. **Define every term mathematically.** No "trustworthiness." No "verification status." No "physics-consistency score" without exact equations and a proof that it's not circular.

### Timeline (Revised)

| Month | Activity |
|:-----:|---------|
| 1 | Literature deep-dive: CP-PRE, SCRC, PhysicsCorrect, STACI, forecast post-processing. Define exact contribution. |
| 2 | Implement reliability estimator. Feature engineering. Train on CAMELS-US calibration split. **Prove $\rho > 0.3$ or STOP.** |
| 3 | Implement one-shot correction module. Train on calibration split. |
| 4 | Implement selective correction pipeline. Calibrate gating threshold via CRC. |
| 5 | Implement ACI wrapper. Full pipeline integration. |
| 6 | Full ablation on CAMELS-US (8 baselines × 5 AETHER variants). Statistical tests. |
| 7 | Transfer experiments on CAMELS-GB. Robustness analysis. |
| 8 | Paper writing. Focus on empirical rigor, proper framing, honest claims. |
| 9 | Dashboard demonstration (optional). Revisions. |

---

# MOST IMPORTANT QUESTION

> **If another research group submitted a paper tomorrow claiming "physics-guided conformal verification and recursive correction for flood forecasting," what exact scientific contribution would AETHER need to contain for a reviewer to still consider it meaningfully different?**

## Answer

If a competing paper claims the exact architecture from AETHER Phase 0 (conformal-gated recursive physics correction), that paper will face the same statistical validity problems identified here. No reviewer at WRR/HESS/NeurIPS should accept a paper where:
- Nonconformity scores are "computed" without ground truth
- Coverage claims survive a correction loop
- Mass-balance is "verified" without knowing $\Delta S$

**If the competing paper fixes these problems** (which would require abandoning conformal gating and adopting something like CRC post-correction), then AETHER's differentiation must be:

1. **The reliability estimator.** If AETHER demonstrates that a learned model can predict forecast error using physics-derived features — and publishes which features are most predictive, for which basin types, under which conditions — this is a standalone contribution that a competing "recursive correction" paper does not provide.

2. **The selective-vs-unconditional comparison.** If AETHER rigorously proves that selecting which predictions to correct (rather than always correcting) improves probabilistic accuracy, especially during extremes, this is an empirical finding that a system paper would not test.

3. **The ablation.** If AETHER provides a systematic, statistically rigorous ablation showing exactly which components matter (uncertainty features? physics features? the correction module? the selection mechanism?), this empirical decomposition is the most defensible contribution of all.

**In short: AETHER's survival does not depend on the architecture. It depends on the rigor of the empirical study and the quality of the scientific questions it answers.**

A well-executed empirical study asking "when should we correct flood forecasts, and does it help?" will remain valuable regardless of what competing architectures are proposed. A poorly justified architecture will be rejected regardless of how novel it appears.

> **The paper that proves *when* correction helps beats the paper that proposes *how* to correct.**
