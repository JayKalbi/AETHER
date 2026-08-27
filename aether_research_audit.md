# AETHER — Research Audit, Literature Survey & Product Definition

**Date:** August 10, 2026  
**Status:** Phase 0 — Pre-Implementation Research Audit  
**Verdict:** CONDITIONAL APPROVAL — with mandatory redesign (see Section 25)

---

## 1. Executive Verdict

> **The original AETHER concept — "Physics-Guided Recursive Self-Verification for Flood Prediction" — is no longer novel as a high-level idea.** The field has moved decisively in this direction during 2025–2026. However, a specifically formulated version of AETHER remains viable and publishable.

### The Brutal Truth

The core idea — "predict → verify against physics → correct → repeat" — has been independently proposed and published in multiple domains during 2025–2026:

| System | Year | Domain | Status |
|--------|------|--------|--------|
| **HydroAgent** | 2026 | Flood forecasting | arXiv preprint, operational validation |
| **WaveAgent** | 2025–2026 | Coastal wave forecasting | Published (Ocean Engineering) |
| **PhysVEC** | 2026 | Quantum physics discovery | arXiv preprint |
| **SETS** | 2025 | General ML reasoning | TMLR (peer-reviewed) |
| **SCaSML** | 2025–2026 | PDE solving | ICLR (peer-reviewed) |
| **P1 Physics Model** | 2025 | Physics problem-solving | arXiv preprint |
| **DISC** | 2026 | Time-series forecasting | Preprint |

**HydroAgent is the most dangerous competitor.** It is an LLM-based agentic framework for flood forecasting that uses skill-orchestrated hydrological reasoning, physics-based constraints, and human-in-the-loop verification. It was published in 2026, validated on real river basins, and has a dedicated lab (HydroAgent-Lab).

**This means AETHER cannot simply propose "an AI agent that verifies flood predictions against physics" — that paper has effectively been written.**

### But AETHER Is Not Dead

What HydroAgent, WaveAgent, and the others do NOT do:
1. **Formal uncertainty-aware verification** — they use heuristic or LLM-based critique, not mathematically rigorous verification with coverage guarantees
2. **Conformal-prediction-based verification loops** — no existing system uses conformal prediction as the verification mechanism in a recursive correction loop
3. **Quantified verification scoring** — no system produces a "physics-consistency score" with provable properties
4. **Systematic ablation of verification mechanisms** — no paper rigorously proves which components of the verification loop actually matter

**AETHER's survival depends on pivoting from "we do physics-guided self-verification" (now crowded) to "we provide the first rigorous, uncertainty-quantified verification framework for flood forecasting with provable coverage guarantees."**

---

## 2. Current State of the Field (August 2026)

The flood prediction / hydrological ML landscape as of August 2026:

### Established (No Longer Novel)
- **LSTM for rainfall-runoff**: Solved. Kratzert et al. (2024, HESS) established that regional LSTMs trained on CAMELS/Caravan are the gold standard. NeuralHydrology is the reference framework.
- **Physics-guided loss functions**: Well-explored. Mass-balance, water-balance constraints in training losses are standard practice (xLSTM-MTV, dPL framework).
- **Google Flood Hub**: Operational in 150+ countries. LSTMs for streamflow + AI inundation models. Open-sourced in 2025.
- **GloFAS/EFAS + AIFS**: ECMWF integrated AI forecasting (AIFS) into operational flood warning in September 2025.
- **Foundation models for weather**: GraphCast, GenCast, WeatherNext, ClimaX are operational or near-operational.

### Active Frontier (2025–2026)
- **Differentiable hydrology (dPL)**: Tsai, Feng, Shen — end-to-end differentiable HBV models. Very active.
- **Neural Operators for flood simulation**: FNO/DeepONet achieving 10,000–100,000× speedup over HEC-RAS.
- **Agentic AI for hydrology**: HydroAgent (2026), NeuralRiverOps. LLM-orchestrated forecasting workflows.
- **Test-time compute for scientific prediction**: SCaSML, SETS. Inference-time correction is the paradigm.
- **Conformal prediction for hydrology**: STACI, HopCPT. Emerging but NOT yet integrated into verification loops.
- **FloodTransformer**: Physics-informed multi-task Transformer for real-time flood forecasting (2025).

### Underexplored
- Formal verification of ML flood predictions with provable guarantees
- Recursive correction loops with rigorous uncertainty quantification
- Conformal prediction as a verification/gating mechanism (not just UQ wrapper)
- Systematic comparison of verification strategies for hydrological forecasts
- Physics-consistency scoring with calibrated confidence

---

## 3. Comprehensive Literature Survey

### A. Flood Prediction / Forecasting

| Paper | Year | Venue | Key Contribution |
|-------|------|-------|-----------------|
| Kratzert et al., "Never train an LSTM on a single basin" | 2024 | HESS | Best practices for regional LSTM training |
| Nearing et al., "Global prediction of extreme floods in ungauged watersheds" | 2024 | Nature | Google Flood Hub — global LSTM flood prediction |
| FloodGNN-GRU (Kazadi et al.) | 2024 | Environmental Data Science | Spatiotemporal GNN for flood emulation |
| FloodTransformer | 2025 | Southern Cross U. | Physics-informed multi-task Transformer, 3s inference |
| Water Level Forecasting (TFT, Baitarani Basin) | 2025 | J. Hydrologic Engineering | Temporal Fusion Transformer for flash flood |
| Google Flood Hub urban flash flood update | 2026 | Google Research | Urban flash flood prediction, 24h lead time |
| Deep Learning urban pluvial flood modeling | 2025 | EGU | Hybrid Transformer-CNN with drainage networks |
| SAR+DEM flood mapping (GLNet/U-Net) | 2025 | Remote Sensing | 93% IoU flood inundation from Sentinel-1 |
| MFED multimodal flood dataset | 2024 | Remote Sensing | 18-year multimodal flood event dataset |
| GenCast (DeepMind) | 2024 | Nature | Diffusion model for probabilistic weather ensembles |
| ClimaX (Microsoft) | 2024 | ICLR | Foundation model for Earth system, fine-tuned for flood extent |
| WeatherNext (DeepMind) | 2026 | DeepMind | SOTA tropical cyclone forecasting |

### B. Physics-Informed/Guided ML for Hydrology

| Paper/Framework | Year | Venue | Key Contribution |
|----------------|------|-------|-----------------|
| dPL Framework (Tsai et al.) | 2021–2025 | HESS, WRR | Differentiable parameter learning for HBV |
| δHBV1.1p (Feng et al.) | 2024 | Zenodo/WRR | Extreme event prediction via differentiable hydrology |
| δHBV-globe1.0 | 2025 | HESS | Global-scale differentiable HBV |
| Willard et al., "Integrating Scientific Knowledge with ML" | 2022 | CSUR | Taxonomy of physics-ML integration |
| Karpatne et al., Theory-Guided Data Science | 2017 | IEEE TKDE | Foundational TGDS framework |
| xLSTM-MTV with Physics Water Balance Constraints | 2026 | Taylor & Francis | Physics-informed water balance in xLSTM architecture |
| PINN-xLSTM (Yang et al.) | 2026 | ResearchGate | Dynamic physical constraints in xLSTM |
| Neural Operators for SWE (FNO/DeepONet) | 2024–2025 | Various | 10,000–100,000× speedup for flood simulation |
| CLDNet (Neural ODE for hydrology) | 2024 | Various | Continuous-time watershed state modeling |
| Process-based model emulation (UNet/GNN) | 2024–2025 | Various | ML surrogates for HEC-RAS/LISFLOOD |

### C. Self-Verification / Recursive Correction

| Paper/System | Year | Venue | Domain | Verification Type | Recursive? | Physics? |
|-------------|------|-------|--------|-------------------|-----------|---------|
| **HydroAgent** | 2026 | arXiv | **Flood forecasting** | LLM skill-orchestrated critique | Yes | Yes (physics-based simulation) |
| **WaveAgent** | 2025–2026 | Ocean Engineering | Coastal wave | Closed-loop physics verification | Yes | Yes |
| **PhysVEC** | 2026 | arXiv | Quantum physics | Two-tier (code + science) verification | Yes | Yes |
| **SETS** | 2025 | TMLR | General reasoning | Self-verification + self-correction | Yes | No |
| **SCaSML** | 2025–2026 | ICLR | PDE solving | Law-of-Defect correction | No (single-pass) | Yes |
| **P1 Review Studio** | 2025 | arXiv | Physics problems | Agentic PhysicsMinions critique | Yes | Yes |
| **DISC** | 2026 | Preprint | Time-series | Denoising verify-judge-correct | Yes | Indirect |
| Recursive refinement in weather models | 2024 | arXiv | Meteorology | Boundary condition verification | Yes | Yes |
| Stabilizing generative loops (physics correction) | 2025 | arXiv | Scientific AI | Physics simulator as verifier | Yes | Yes |

### D. Uncertainty Quantification

| Method/Paper | Year | Application | Key Finding |
|-------------|------|-------------|------------|
| STACI (Spatio-Temporal Adaptive Conformal Inference) | 2025–2026 | Stream networks | Context-aware conformal prediction for hydrology |
| HopCPT (Hopfield Conformal Prediction for Time-series) | 2025 | General time-series | Modern Hopfield Networks for CP |
| Extreme Conformal Prediction | 2025 | Extreme events | EVT + CP integration for tail risk |
| Online CP for weather models | 2026 | Weather | CP applied to GenCast, NeuralGCM, AIFS-ENS |
| Deep Neural Network Ensembles (DNNE) | 2024 | Hydrology | Consistent probabilistic predictions |
| Diffusion-based Runoff Models (DRUM) | 2025 | Runoff | Generative AI for ensemble runoff |

---

## 4. Closest Existing Work

### The 5 Most Dangerous Competitors to AETHER

#### 1. HydroAgent (2026) — **THREAT LEVEL: CRITICAL**
- **What it does**: LLM-orchestrated flood forecasting with skill-based hydrological reasoning
- **Architecture**: Skills (physics rules) → LLM planning → simulation execution → human-in-loop review
- **Validation**: South Yamhill River basin, 5% tolerance on flood peaks
- **What it lacks**: No formal uncertainty quantification, no conformal prediction, no automated recursive correction without human, LLM-dependent (brittle)
- **AETHER differentiator**: Automated, mathematically grounded verification (not LLM critique)

#### 2. WaveAgent (2025–2026) — **THREAT LEVEL: HIGH**
- **What it does**: Closed-loop physics-guided wave forecasting with adaptive model selection and verification
- **Architecture**: Forecast → physics verification (wind-wave, spatial, temporal) → correction
- **Validation**: 5 years, 13 coastal stations
- **What it lacks**: Domain-specific to coastal waves, no uncertainty-aware gating, no conformal framework
- **AETHER differentiator**: Different domain, formal uncertainty integration

#### 3. dPL / δHBV Framework (Feng, Tsai, Shen, 2021–2025) — **THREAT LEVEL: MODERATE-HIGH**
- **What it does**: End-to-end differentiable hydrological model with physics built into the architecture
- **What it lacks**: No test-time verification, no recursive correction, no uncertainty-triggered re-evaluation
- **AETHER differentiator**: Verification is at inference time, not training time

#### 4. Google Flood Hub (2024–2026) — **THREAT LEVEL: MODERATE**
- **What it does**: Operational global flood prediction, open-sourced framework
- **What it lacks**: No explicit self-verification, no physics-consistency scoring, limited uncertainty communication
- **AETHER differentiator**: Verification transparency, uncertainty quantification, physics-consistency audit

#### 5. SCaSML (2025–2026) — **THREAT LEVEL: MODERATE**
- **What it does**: Inference-time physics-based correction of ML PDE solvers
- **What it lacks**: Single-pass correction (not recursive), specific to PDE solving, not applied to hydrology
- **AETHER differentiator**: Recursive, uncertainty-aware, applied to forecasting not PDE solving

---

## 5. Physics-Guided Flood Prediction Landscape

### What Is Solved
1. **Physics-based loss functions** — mass/water/energy balance as soft constraints. Standard practice since Willard et al. (2022).
2. **Differentiable parameter learning** — Tsai/Feng/Shen dPL framework is mature and published in top hydrology journals.
3. **Hard constraints via architecture** — Lagrangian NNs, mass-conserving layers exist but are niche.
4. **Hybrid coupling** — SWAT/HEC-RAS + ML is routine engineering.

### What Is Active but Not Solved
1. **Physics constraints at inference time** (test-time enforcement) — SCaSML is pioneering but not applied to hydrology
2. **Balancing soft vs. hard constraints** — active debate; hard constraints limit expressivity
3. **Physics-guided architectures for extreme events** — xLSTM-MTV (2026) is very recent
4. **Differentiable hydrology at global scale** — δHBV-globe1.0 (2025) is just emerging

### What Is Missing
1. **Physics-consistency as a verification criterion** (not just a loss term) — no one treats physics consistency as a runtime diagnostic that triggers correction
2. **Quantified physics-consistency scores** — no system produces a scalar "this prediction is X% consistent with mass balance" with provable calibration
3. **Physics-aware conformal prediction** — integrating physical constraints into the conformal prediction framework itself

---

## 6. Self-Verification / Recursive Correction Landscape

### The Honest Assessment

**The general idea of self-verification is no longer novel.** Since OpenAI's o1 (2024) and the test-time compute revolution, "predict → verify → correct → repeat" is mainstream in AI. Hundreds of papers now exist on self-correction in LLMs, agentic verification, and recursive refinement.

**However, the specific application to earth science forecasting with formal guarantees is still novel.** Here's the hierarchy:

1. **LLM self-correction** (2024–2026): Massive literature. SETS, CoVe, Self-Refine, etc. **Not novel at all.**
2. **Physics-based verification in scientific AI** (2025–2026): PhysVEC, P1. Emerging. **Novel but being explored.**
3. **Agentic verification in earth science** (2026): HydroAgent, WaveAgent. **Very recent, our direct competitor.**
4. **Formally rigorous verification with coverage guarantees in earth science forecasting** (2026): **NO EXISTING WORK.** This is the gap.

### The Key Distinction

All existing self-verification systems use heuristic criteria:
- LLM-based critique (HydroAgent) — no formal guarantee the critique is correct
- Physics simulator comparison (WaveAgent) — binary pass/fail, no calibration
- Rule-based checks (DISC) — domain rules, not provable

**No system uses conformal prediction or formal statistical tests as the verification mechanism in a recursive correction loop for environmental forecasting.**

---

## 7. Novelty Matrix

| Existing Work | Flood Prediction | Physics Guidance | Formal UQ | Verification Loop | Recursive Correction | Multimodal | Decision Support | Key Limitation |
|--------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|----------------|
| Google Flood Hub | ✅ | ❌ | ❌ | ❌ | ❌ | Partial | ✅ | No physics, no verification |
| dPL/δHBV (Feng et al.) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Training-time only, no UQ |
| NeuralHydrology LSTM | ✅ | Partial | MC Dropout | ❌ | ❌ | ❌ | ❌ | No verification |
| HydroAgent | ✅ | ✅ | ❌ | ✅ (LLM) | ✅ (LLM-driven) | ❌ | ✅ | Heuristic verification, LLM-dependent |
| WaveAgent | ❌ (waves) | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | Wrong domain, no formal UQ |
| FloodTransformer | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | No verification loop |
| xLSTM-MTV | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Training-time constraints only |
| GloFAS + AIFS | ✅ | ✅ | Ensemble | ❌ | ❌ | ✅ | ✅ | No formal verification |
| SCaSML | ❌ (PDEs) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Single-pass, wrong domain |
| STACI / HopCPT | ✅ | ❌ | ✅ (CP) | ❌ | ❌ | ❌ | ❌ | Passive UQ, no verification loop |
| PhysVEC | ❌ (quantum) | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | Wrong domain entirely |
| **AETHER (proposed)** | ✅ | ✅ | ✅ (CP) | ✅ (formal) | ✅ (uncertainty-gated) | ✅ | ✅ | **Unproven** |

**The gap AETHER fills**: the intersection of {flood prediction} ∩ {physics guidance} ∩ {formal UQ with coverage guarantees} ∩ {verification loop} ∩ {recursive correction}.

No existing system occupies this intersection.

---

## 8. Research Gap

### What Has Already Been Done
1. LSTM/Transformer for flood prediction — fully explored
2. Physics-based training losses — standard practice
3. Differentiable hydrology — mature framework (dPL)
4. LLM-based agentic verification for hydrology — HydroAgent (2026)
5. Conformal prediction for hydrology — STACI, emerging
6. Physics-based closed-loop forecasting — WaveAgent (coastal)

### What Has Been Partially Done
1. Test-time physics correction — SCaSML (for PDEs, not hydrology)
2. Uncertainty-aware forecasting in hydrology — MC Dropout, ensembles (but not conformal-prediction-gated verification)
3. Recursive refinement in weather — architectural (spatial upsampling), not agentic verification

### What Is Genuinely Underexplored

> **Using conformal prediction as a formal verification mechanism that gates recursive physics-guided correction of flood forecasts, producing predictions with provable coverage guarantees.**

Specifically:
1. **Conformal Verification Gating**: Using nonconformity scores to decide whether a prediction needs correction — not just to produce prediction intervals
2. **Physics-Consistency Scoring with Calibration**: Producing a calibrated score that quantifies how consistent a prediction is with physical constraints
3. **Uncertainty-Triggered Recursive Correction**: A loop where high epistemic uncertainty or low physics-consistency triggers additional inference-time correction, with convergence guarantees
4. **Ablation of Verification Strategies**: Systematic comparison of verification mechanisms (physics-checking, ensemble disagreement, conformal, hybrid)

### What Is Engineering, Not Research
- "We built a dashboard" — engineering
- "We combined LSTM + weather API + satellite" — integration engineering
- "We used multiple data sources" — data engineering
- "Our system runs in real-time" — systems engineering

---

## 9. What Is Actually Novel

### The Three Strongest Novel Contribution Directions

#### Direction 1: Conformal-Physics Verification Framework (MOST NOVEL)
**Novelty**: Formalize a verification framework where conformal prediction and physics-consistency checks are combined into a single verification score with provable coverage guarantees. The verification score gates whether a prediction is "released" or sent to a correction module.

**Why it's novel**: No existing work combines conformal prediction guarantees with physics-consistency verification as a gating mechanism. STACI provides conformal prediction for streams but doesn't use it as a verification gate. HydroAgent uses LLM critique but has no formal guarantees.

**Publication potential**: HIGH — bridges formal UQ (statistics/ML community) with operational hydrology. Targets: NeurIPS, ICML, Water Resources Research.

#### Direction 2: Uncertainty-Gated Recursive Correction Architecture (MOST FEASIBLE)
**Novelty**: Design an architecture where a base flood predictor is wrapped in an uncertainty-aware correction loop: predict → estimate uncertainty → check physics → if uncertain or inconsistent, correct using a physics-guided refinement module → re-estimate → converge or bound iterations.

**Why it's novel**: Recursive correction exists (HydroAgent, WaveAgent) but is always heuristic. This version uses calibrated uncertainty to gate correction and can prove convergence or termination guarantees.

**Publication potential**: HIGH — directly publishable in hydrology journals (WRR, HESS) with ablation showing each component's contribution.

#### Direction 3: Physics-Consistency Diagnostic for Flood Forecasts (HIGHEST PUBLICATION POTENTIAL)
**Novelty**: Develop a suite of physics-consistency diagnostic metrics (mass balance residual, trend consistency, spatial coherence, temporal continuity) that can be computed for ANY flood forecast from ANY model, producing a calibrated "trustworthiness score." Demonstrate that this score correlates with actual forecast error.

**Why it's novel**: No standardized physics-consistency diagnostic exists for flood forecasts. This could become a widely adopted tool/benchmark.

**Publication potential**: HIGHEST — immediately useful to the entire flood forecasting community, adoptable by Google Flood Hub, GloFAS, etc.

### Ranking

| Direction | Scientific Novelty | Feasibility | Publication Potential |
|-----------|:---:|:---:|:---:|
| 1. Conformal-Physics Verification | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 2. Uncertainty-Gated Recursive Correction | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 3. Physics-Consistency Diagnostic | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommended strategy**: Combine Directions 2 and 3. Build the diagnostic (Direction 3) first — it's immediately publishable and useful. Then use it as the verification mechanism inside the recursive correction loop (Direction 2). Direction 1's conformal-physics integration becomes the theoretical contribution of the combined work.

---

## 10. What Is NOT Novel

The following elements, if presented as AETHER's contribution, would be rejected by Q1 reviewers:

1. ❌ "We used LSTM for flood prediction" — Kratzert solved this
2. ❌ "We added physics loss terms" — Standard since 2022
3. ❌ "We built an AI flood dashboard" — Google Flood Hub exists
4. ❌ "We combined satellite + weather + terrain data" — Integration, not research
5. ❌ "We used an LLM agent for forecasting" — HydroAgent (2026) did this
6. ❌ "We did physics-guided prediction" — dPL/δHBV framework, xLSTM-MTV, FloodTransformer
7. ❌ "We predicted disasters with AI" — Overly broad claim
8. ❌ "We used ensemble uncertainty" — Standard meteorological practice for decades
9. ❌ "Our system is real-time" — Engineering, not research
10. ❌ "We verified predictions against observations" — Standard model evaluation

---

## 11. Disaster Prediction Claim — Reality Check

### Can a System "Predict Disasters"?

**No. This claim is scientifically indefensible and should be abandoned immediately.**

#### Why?

1. **"Disaster" is a socio-economic construct**, not a physical variable. A flood is a hydrological event; a disaster occurs when that event impacts people, infrastructure, or economies. You can predict the flood; you cannot predict whether it becomes a "disaster" without modeling human systems.

2. **Multi-hazard prediction is a completely different research program.** Predicting floods, droughts, earthquakes, cyclones, and wildfires requires entirely different physics, data, and models. No single system can credibly predict "disasters."

3. **Exaggerated claims destroy credibility.** A Q1 reviewer will immediately flag "disaster prediction" as hype.

### What AETHER Can Legitimately Claim

| Claim | Defensible? | Why |
|-------|:---:|------|
| "Predicts disasters" | ❌ | Socio-economic construct |
| "Predicts floods" | ✅ | Hydrological variable |
| "Forecasts flood hazard" | ✅ | Physical hazard |
| "Estimates flood risk" | ⚠️ | Only if exposure/vulnerability data included |
| "Provides flood early warning" | ✅ | With sufficient lead time |
| "Provides flood intelligence" | ✅ | If multiple information types are integrated |
| "Multi-hazard prediction" | ❌ | Unless actually implemented for multiple hazards |

### Recommended Scope

**AETHER should be a flood forecasting and flood intelligence system.** Period. Not "disaster prediction." The title should reflect this.

---

## 12. AETHER Research Hypothesis

### Testing the Original Hypothesis

> "A predictive AI system that recursively verifies its forecasts against physical constraints, independent observations, and uncertainty estimates can produce more reliable flood forecasts than conventional data-driven and physics-guided models."

**Assessment: WEAK as stated.**

- **Too broad**: "more reliable" is vague. More reliable how? Better NSE? Better calibration? Better during extremes?
- **Partially demonstrated**: HydroAgent showed that agentic verification improves flood forecasting. The general principle is no longer in question.
- **Not falsifiable enough**: "can produce" allows cherry-picking. Under what conditions?

### Proposed Stronger Hypothesis

> **"A conformal-prediction-gated recursive correction loop, where physics-consistency violations trigger inference-time refinement, produces flood forecasts with (a) better calibrated prediction intervals (measured by coverage and interval width), (b) improved extreme-event reliability (measured by NSE and KGE at return periods > 10 years), and (c) reduced physical inconsistency (measured by mass-balance residuals), compared to the same base model without the verification loop, across a diverse set of hydrologically distinct basins."**

This hypothesis is:
- **Specific**: defines what "better" means (calibration, extreme events, physical consistency)
- **Falsifiable**: clear metrics, clear comparison (with vs. without verification loop)
- **Novel**: conformal-prediction-gating + physics-consistency → recursive correction is unstudied
- **Ablatable**: each component (conformal gating, physics checking, recursive correction) can be independently evaluated

---

## 13. AETHER Scientific Contribution

### The Defensible Contribution (Combining Directions 2 & 3)

**AETHER contributes a *Verified Adaptive Forecasting* (VAF) framework for flood prediction, consisting of:**

1. **A physics-consistency diagnostic suite** — a set of computable, model-agnostic metrics (mass-balance residual, precipitation-runoff trend consistency, spatial coherence, temporal smoothness) that quantify how "physically plausible" any flood forecast is, with calibrated interpretation (i.e., "a score of X corresponds to Y expected error").

2. **A conformal verification gate** — using adaptive conformal prediction (STACI-style) to produce prediction intervals, and using the width and coverage of these intervals as a trigger for correction. When the conformal nonconformity score exceeds a threshold, the prediction is sent to the correction module.

3. **A physics-guided recursive correction module** — when triggered, this module refines the forecast using a secondary physics-constrained model (e.g., a differentiable HBV or a physics-loss-augmented network) and re-evaluates until convergence or iteration bound.

4. **A rigorous ablation** proving that each component independently and jointly improves forecast quality, with particular emphasis on extreme events and out-of-distribution scenarios.

### What Is NOT the Contribution
- The base ML model (use existing LSTM/Transformer via NeuralHydrology)
- The data pipeline (use existing CAMELS/Caravan)
- The dashboard (engineering layer)
- The fact that physics matters (already established)

---

## 14. AETHER 2.0 Proposed Architecture — Conceptual Only

```
┌─────────────────────────────────────────────────────┐
│                  AETHER 2.0 Architecture             │
│                                                       │
│  INPUT: Meteorological forcing + basin attributes     │
│         + historical discharge + DEM + land cover     │
│                                                       │
│  ┌───────────────┐                                    │
│  │ Base Predictor │ ← Regional LSTM/Transformer       │
│  │ (NeuralHydro)  │   (trained on Caravan/CAMELS)     │
│  └───────┬───────┘                                    │
│          │ forecast ŷ                                 │
│          ▼                                            │
│  ┌───────────────────────────┐                        │
│  │ Physics-Consistency       │                        │
│  │ Diagnostic Module         │                        │
│  │ ├─ Mass-balance residual  │                        │
│  │ ├─ Trend consistency      │                        │
│  │ ├─ Spatial coherence      │                        │
│  │ └─ Temporal continuity    │                        │
│  └───────┬───────────────────┘                        │
│          │ physics_score                              │
│          ▼                                            │
│  ┌───────────────────────────┐                        │
│  │ Conformal Verification    │                        │
│  │ Gate                      │                        │
│  │ ├─ Nonconformity score    │                        │
│  │ ├─ Coverage check         │                        │
│  │ └─ Combined gate decision │                        │
│  └───────┬───────────────────┘                        │
│          │                                            │
│    ┌─────┴─────┐                                      │
│    │           │                                      │
│  PASS       FAIL                                      │
│    │           │                                      │
│    ▼           ▼                                      │
│  Release   ┌──────────────────┐                       │
│  forecast  │ Physics-Guided   │                       │
│            │ Correction Module│  ← dPL-style or       │
│            │ (Refinement)     │    physics-loss model  │
│            └────────┬─────────┘                       │
│                     │ refined ŷ'                      │
│                     │                                 │
│                     └──→ (loop back to Diagnostic     │
│                           Module, max K iterations)   │
│                                                       │
│  OUTPUT:                                              │
│  ├─ Final forecast ŷ*                                 │
│  ├─ Conformal prediction interval [ŷ_lo, ŷ_hi]       │
│  ├─ Physics-consistency score                         │
│  ├─ Number of correction iterations                   │
│  ├─ Epistemic uncertainty estimate                    │
│  └─ Verification status (PASS / CORRECTED)            │
└─────────────────────────────────────────────────────┘
```

---

## 15. Final Product Definition

### What AETHER 2.0 Delivers

**A verified flood forecasting system that provides forecasts with quantified trustworthiness.**

#### Input
| Data Source | Required? | Open Access? |
|------------|:---------:|:------------:|
| Precipitation (observed + forecast) | ✅ | ✅ (IMD, ERA5, IMERG) |
| Temperature | ✅ | ✅ (ERA5) |
| Basin attributes (area, slope, soil, land cover) | ✅ | ✅ (Caravan, HydroATLAS) |
| Historical discharge | ✅ | ✅ (Caravan, India-WRIS) |
| DEM | ✅ | ✅ (SRTM, Copernicus DEM) |
| Weather forecast (NWP/AIFS) | ⚠️ Desirable | ✅ (GFS, ECMWF open) |
| Satellite imagery (Sentinel-1 SAR) | ⚠️ Optional | ✅ (Copernicus) |

#### Intelligence Layer
| Capability | Included? | Research or Engineering? |
|-----------|:---------:|:-----------------------:|
| Forecast discharge/water level | ✅ | Engineering (use existing models) |
| Physics-consistency score | ✅ | **RESEARCH** |
| Conformal prediction intervals | ✅ | **RESEARCH** |
| Verification gate (pass/fail/corrected) | ✅ | **RESEARCH** |
| Recursive correction | ✅ | **RESEARCH** |
| Number of correction iterations | ✅ | **RESEARCH** |
| Severity classification | ✅ | Engineering |
| Explanation of verification result | ⚠️ Optional | Engineering |

#### User Output
| Output | Included? |
|--------|:---------:|
| Predicted discharge/water level | ✅ |
| Prediction interval with coverage guarantee | ✅ |
| Physics-consistency score (0–1, calibrated) | ✅ |
| Verification status | ✅ |
| Confidence level | ✅ |
| Lead time | ✅ |
| Severity level | ✅ |
| Spatial flood extent | ⚠️ V2 (requires separate inundation model) |
| Affected population estimate | ❌ (requires exposure data — out of scope) |
| Recommended action | ❌ (liability concern — out of scope) |

---

## 16. Target Users

| User | Primary? | Decision They Make | What AETHER Provides | What AETHER Does NOT Provide |
|------|:--------:|-------------------|---------------------|------------------------------|
| **Disaster management authority** | ✅ PRIMARY | Issue warning or not | Verified forecast + uncertainty + physics-consistency | Evacuation routes, resource allocation |
| **Emergency response team** | ⚠️ Secondary | Deploy resources | Severity level, lead time | Logistics, personnel decisions |
| **Hydrologist / Researcher** | ✅ PRIMARY | Evaluate model, publish | Full verification diagnostics, ablation | Literature survey, hypothesis generation |
| **Municipal authority** | ⚠️ Secondary | Infrastructure preparedness | Risk level, affected area (V2) | Budget, policy recommendations |
| **Infrastructure operator** | ❌ | Protect specific assets | N/A | Asset-specific risk (requires custom model) |
| **General public** | ❌ | Personal safety | N/A | Not designed for direct public use |

**Primary users: Disaster management authorities and hydrological researchers.**

---

## 17. User Workflow

### For Disaster Management Authority
```
1. INPUT    → Select basin/location + time horizon
2. FORECAST → AETHER produces discharge forecast
3. VERIFY   → System shows:
               - Prediction: "River X will reach 12.3m ± 0.8m (90% CI)"
               - Physics-consistency: 0.87 / 1.00
               - Status: CORRECTED (2 iterations)
               - Confidence: HIGH
               - Severity: ORANGE (threshold breach likely)
4. DECIDE   → Authority decides whether to issue warning
5. AUDIT    → Full verification log available for post-event analysis
```

### For Researcher
```
1. INPUT    → Upload basin data / select from Caravan
2. RUN      → AETHER produces verified forecast ensemble
3. ANALYZE  → Researcher examines:
               - Physics-consistency metrics per timestep
               - Conformal prediction coverage
               - Correction convergence behavior
               - Comparison with baselines
4. EXPORT   → Full metrics, predictions, and verification logs for publication
```

---

## 18. Product vs Research Contribution

### This Separation Is Critical

| Layer | What It Is | Novel? |
|-------|-----------|:------:|
| **Scientific Contribution** | Physics-consistency diagnostic + conformal verification gate + uncertainty-gated recursive correction. The VAF framework. | ✅ YES |
| **Engineering Contribution** | Integration of NeuralHydrology + Caravan + verification modules into a working pipeline. API design. Real-time capability. | ❌ NO (important but not publishable) |
| **Demonstration Layer** | Dashboard showing forecasts, uncertainty, verification status. Maps. Visualizations. | ❌ NO (not research) |

**The paper publishes the VAF framework and ablation. The product demonstrates it. These are separate deliverables.**

---

## 19. Competitive Landscape

| System | Prediction | Verification | Formal UQ | Open Source | AETHER Advantage |
|--------|:----------:|:------------:|:---------:|:-----------:|:----------------:|
| Google Flood Hub | ✅ Global | ❌ | ❌ | ✅ (2025) | Verification + formal UQ |
| GloFAS/EFAS | ✅ Global | ❌ | Ensemble | Partial | Formal verification + correction |
| HydroAgent | ✅ Regional | ✅ (LLM) | ❌ | ❌ | Formal (non-LLM) verification |
| NOAA NWM | ✅ USA | ❌ | ❌ | Partial | Verification + UQ |
| India CWC | ✅ India | ❌ | ❌ | ❌ | Everything |
| Tomorrow.io | ✅ Global | ❌ | Partial | ❌ | Formal verification |
| Fathom | ✅ Global | ❌ | ❌ | ❌ | Verification + UQ |

### Why Would Anyone Need AETHER?

**Honest answer**: AETHER will not compete with Google Flood Hub or GloFAS on prediction accuracy or geographic coverage. It cannot.

**AETHER's value proposition is different**: It provides **verified, trustworthy forecasts** — a forecast that comes with a formal statement about its reliability, physics-consistency, and uncertainty. This is what operational agencies need to justify issuing warnings.

No existing system provides this. The closest competitor (HydroAgent) uses LLM-based verification, which is inherently non-rigorous and non-reproducible.

If AETHER cannot provide meaningfully better verification than existing systems, it has no reason to exist.

---

## 20. Feasibility Audit

### Data Availability

| Data | Source | Access | Quality | Verdict |
|------|--------|--------|---------|---------|
| Discharge (global) | Caravan (6,800+ basins) | ✅ Free | ✅ Good | Use this |
| Discharge (India) | India-WRIS / NWIC API | ✅ Free (mostly) | ⚠️ Variable | Supplement with Caravan-India |
| Precipitation | ERA5, IMERG, IMD | ✅ Free | ✅ Good | Use ERA5 for training |
| Temperature | ERA5 | ✅ Free | ✅ Good | Standard |
| Basin attributes | Caravan, HydroATLAS | ✅ Free | ✅ Good | Included in Caravan |
| DEM | SRTM (30m), Copernicus (30m) | ✅ Free | ✅ Good | Standard |
| Soil properties | SoilGrids | ✅ Free | ✅ Good | Standard |
| Land cover | ESA WorldCover | ✅ Free | ✅ Good | Standard |
| Weather forecasts | GFS (NOAA), ECMWF open | ✅ Free | ✅ Good | For operational testing |

**Data verdict: FEASIBLE.** Caravan + ERA5 provides everything needed for the research contribution. India-WRIS/NWIC API provides India-specific data for demonstration.

### Computational Requirements

| Component | GPU Requirement | Training Time (Est.) | Feasibility |
|-----------|:--------------:|:-------------------:|:-----------:|
| Base LSTM (NeuralHydrology) | 1× A100 or equivalent | 2–8 hours | ✅ Easy |
| Physics correction module | 1× A100 | 4–12 hours | ✅ Easy |
| Conformal prediction | CPU only | Minutes | ✅ Trivial |
| Physics-consistency diagnostics | CPU only | Minutes | ✅ Trivial |
| Full ablation (5 variants × 10 seeds × multiple basins) | 1× A100, ~1 week | 1–2 weeks | ✅ Feasible |

**Compute verdict: FEASIBLE.** This is not a foundation model. The research contribution is in the verification framework, not in scaling model size. An M.Tech team with access to a single decent GPU (or Colab Pro+) can do this.

### Key Risks
1. **Conformal prediction on non-stationary hydrological data**: Exchangeability assumptions may be violated. Mitigation: use adaptive/online conformal prediction (ACI).
2. **Recursive correction convergence**: The loop may not converge or may oscillate. Mitigation: bound iterations (K ≤ 5), monitor loss.
3. **Physics-consistency metrics may not correlate with actual error**: The diagnostic suite may be informative in theory but not in practice. Mitigation: validate correlation on held-out data.

---

## 21. Experimental Validation Strategy

### Datasets

| Dataset | Basins | Region | Use |
|---------|:------:|--------|-----|
| CAMELS-US | 671 | USA | Primary benchmark |
| CAMELS-GB | 671 | UK | Generalization test |
| Caravan (India subset) | ~200 | India | Regional demonstration |
| Caravan (global) | 6,800+ | Global | Stress test (optional) |

### Baselines

| Model | Type | Purpose |
|-------|------|---------|
| Persistence (lag-1) | Naive | Sanity check |
| Linear regression | Statistical | Minimal baseline |
| LSTM (NeuralHydrology, no physics) | Pure ML | Data-driven baseline |
| Transformer (TFT) | Pure ML | Architecture comparison |
| LSTM + physics loss | Physics-guided training | Shows training-time physics isn't enough |
| dPL / δHBV | Differentiable hydrology | SOTA physics-guided baseline |

### AETHER Ablation Variants

| Variant | Base Model | Physics Diagnostic | Conformal Gate | Recursive Correction | Purpose |
|---------|:----------:|:------------------:|:--------------:|:--------------------:|---------|
| A0: Base LSTM | ✅ | ❌ | ❌ | ❌ | Pure ML baseline |
| A1: + Physics diagnostic | ✅ | ✅ | ❌ | ❌ | Does the diagnostic detect bad predictions? |
| A2: + Conformal UQ | ✅ | ❌ | ✅ | ❌ | Does conformal prediction improve calibration? |
| A3: + Correction (no gate) | ✅ | ❌ | ❌ | ✅ (always) | Does always-correcting help or hurt? |
| A4: + Diagnostic + Gate | ✅ | ✅ | ✅ | ❌ | Does the gate correctly identify bad predictions? |
| A5: Full AETHER | ✅ | ✅ | ✅ | ✅ | Full system |

### Metrics

| Metric | What It Measures | Critical? |
|--------|-----------------|:---------:|
| NSE (Nash-Sutcliffe Efficiency) | Overall prediction quality | ✅ |
| KGE (Kling-Gupta Efficiency) | Bias, correlation, variability | ✅ |
| PICP (Prediction Interval Coverage Probability) | UQ calibration | ✅ |
| MPIW (Mean Prediction Interval Width) | UQ sharpness | ✅ |
| FHV (High-flow volume bias) | Extreme event performance | ✅ |
| Mass-balance residual | Physics consistency | ✅ |
| Physical Inconsistency Ratio (PIR) | Fraction of physically impossible predictions | ✅ |
| Correction convergence rate | How often does the loop converge? | ✅ |
| Computational overhead | Inference time cost | ⚠️ |

### Critical Experiments

1. **Does the physics-consistency diagnostic predict forecast error?** Correlation between diagnostic score and actual NSE. If not → physics diagnostic is useless.

2. **Does conformal gating improve calibration?** PICP with and without gating. If not → gate adds no value.

3. **Does recursive correction improve extreme events?** FHV and NSE during top-5% flow events, with vs. without correction. If not → correction doesn't help where it matters.

4. **Does the full AETHER system outperform always-correcting?** A5 vs. A3. If A3 ≥ A5 → the gate/diagnostic is unnecessary overhead.

5. **Transfer experiment**: Train on CAMELS-US, test on CAMELS-GB. Does verification improve generalization?

---

## 22. Failure Conditions

> **Under what conditions should we conclude AETHER failed?**

| Failure Condition | Implication | Severity |
|------------------|-------------|:--------:|
| Physics-consistency diagnostic doesn't correlate with actual error (R² < 0.1) | The diagnostic is noise, not signal | 🔴 FATAL |
| Conformal gate doesn't improve calibration (PICP doesn't change) | The gating mechanism is useless | 🔴 FATAL |
| Recursive correction doesn't improve extreme-event NSE | Correction fails exactly when it matters | 🔴 FATAL |
| Always-correcting (A3) ≥ Full AETHER (A5) | The gate/diagnostic adds no value | 🟡 MAJOR |
| AETHER adds < 2% NSE over LSTM baseline | Marginal improvement, not publishable | 🟡 MAJOR |
| Correction loop doesn't converge in > 30% of cases | Instability makes system unreliable | 🟡 MAJOR |
| Computational overhead > 10× baseline with < 5% improvement | Not worth the cost | 🟡 MAJOR |
| dPL/δHBV already achieves same physics consistency | AETHER's verification is redundant | 🟡 MAJOR |
| HydroAgent publishes full peer-reviewed version with formal UQ before us | Priority lost | 🟡 MAJOR |

**If any 🔴 FATAL condition occurs: abandon the verification loop idea. Pivot to the physics-consistency diagnostic as a standalone contribution (Direction 3).**

**If any 🟡 MAJOR conditions occur: the paper may still be publishable with reduced claims, but the "system" story is weakened.**

---

## 23. Q1 Publication Potential

### Target Venues

| Venue | Impact Factor | Fit | Likelihood |
|-------|:------------:|:---:|:----------:|
| **Water Resources Research (WRR)** | ~5.4 | ✅ Excellent | ⭐⭐⭐⭐ |
| **Hydrology and Earth System Sciences (HESS)** | ~6.3 | ✅ Excellent | ⭐⭐⭐⭐ |
| **Journal of Hydrology** | ~6.4 | ✅ Good | ⭐⭐⭐⭐ |
| **Environmental Modelling & Software** | ~4.9 | ✅ Good | ⭐⭐⭐ |
| **NeurIPS / ICML Workshop** | N/A | ⚠️ Partial | ⭐⭐⭐ |
| **Nature Water** | New, high | ⚠️ Ambitious | ⭐⭐ |

**Best strategy**: Submit to WRR or HESS as primary venue. These communities value the combination of hydrological rigor + ML innovation. The conformal-prediction angle is novel enough for these journals.

**Avoid**: Generic AI/ML venues (they won't value the hydrology contribution) unless targeting a workshop or applications track.

---

## 24. Brutal Final Verdict

### Scores

| Criterion | Score | Justification |
|-----------|:-----:|---------------|
| **Research novelty** | **6/10** | The high-level idea (verify → correct) is no longer novel. But the specific formulation (conformal gating + physics diagnostics + recursive correction) remains unstudied. |
| **Scientific significance** | **7/10** | Trustworthy forecasting is a genuine need. If the framework works, it addresses a real problem. |
| **Q1 publication potential** | **7/10** | Publishable in WRR/HESS/J.Hydrology if ablation is rigorous and results are positive. Not sufficient for Nature/Science without extraordinary results. |
| **Engineering difficulty** | **5/10** | Moderate. The core research components are algorithmically tractable. The integration is complex but not unprecedented. |
| **Data feasibility** | **9/10** | Caravan/CAMELS/ERA5/India-WRIS provide everything needed. Open access. |
| **Product potential** | **7/10** | A verified flood forecasting system is commercially valuable. "Trustworthy AI" is a major selling point. |
| **Industry relevance** | **7/10** | Climate-tech companies, disaster management agencies, insurance — all need trustworthy flood forecasts. |
| **Risk of being derivative** | **5/10** | Medium risk. Must differentiate clearly from HydroAgent, WaveAgent, and standard physics-guided approaches. The conformal prediction angle is the key differentiator. |

### GREEN — Genuinely Strong
- ✅ Data feasibility is excellent — Caravan + ERA5 + India-WRIS provides everything
- ✅ The specific conformal-gated verification framework is novel
- ✅ Physics-consistency diagnostics as a standalone contribution is immediately useful
- ✅ Computationally feasible on academic hardware
- ✅ Addresses a real operational need (trustworthy forecasting)
- ✅ Multiple fallback publication strategies (if the loop fails, the diagnostic is still publishable)

### YELLOW — Needs Redesign
- ⚠️ **Title and framing**: "Disaster Prediction" must go. "Recursive Self-Verification" is now crowded terminology.
- ⚠️ **Differentiation from HydroAgent**: Must be very clear that AETHER uses formal/statistical verification (conformal prediction), not LLM-based critique.
- ⚠️ **Scope control**: Do NOT try to build inundation mapping, multi-hazard prediction, or population impact estimation in the first version.
- ⚠️ **The recursive correction loop may not work**: Have a fallback plan (publish the diagnostic suite without the loop).

### RED — Should Be Abandoned
- 🔴 **"Disaster Prediction"** — abandon this claim entirely
- 🔴 **Multi-hazard scope** — abandon. Focus purely on riverine flood forecasting.
- 🔴 **LLM/agent-based verification** — HydroAgent owns this space. Do NOT use LLMs for verification.
- 🔴 **Claiming novelty for "LSTM + physics + satellite"** — this is engineering integration, not research.
- 🔴 **Building a production-grade dashboard as the primary deliverable** — the dashboard is NOT the research.

---

## 25. Recommended Next Phase — AETHER 2.0

### New Title

> **AETHER: Verified Adaptive Forecasting with Conformal Physics-Consistency Gates for Flood Prediction**

Or more concisely:

> **AETHER: Uncertainty-Gated Physics-Verified Flood Forecasting**

### Central Problem

> Current AI-based flood forecasting systems produce predictions without formal guarantees of physical consistency or calibrated uncertainty. When predictions are wrong — especially during extreme events — there is no mechanism to detect, flag, or correct unreliable forecasts at inference time.

### Research Question

> Can a conformal-prediction-gated verification loop, informed by physics-consistency diagnostics, detect and correct unreliable flood forecasts at inference time, producing predictions with improved calibration, physical plausibility, and extreme-event reliability?

### Hypothesis (Falsifiable)

> A flood forecasting system that (1) computes physics-consistency diagnostics, (2) uses adaptive conformal prediction to estimate uncertainty, and (3) recursively refines predictions that fail a combined consistency-uncertainty gate will produce forecasts with ≥5% higher coverage-conditioned NSE during extreme events, ≤15% mass-balance residual reduction, and maintained or improved PICP, compared to the same base model without the verification loop, across CAMELS-US (671 basins) and CAMELS-GB (671 basins).

### Scientific Contribution

**The Verified Adaptive Forecasting (VAF) framework**, comprising:
1. A model-agnostic physics-consistency diagnostic suite for flood forecasts
2. A conformal verification gate that uses nonconformity scores + physics scores to trigger correction
3. An uncertainty-gated recursive correction loop with convergence bounds
4. A rigorous multi-basin ablation proving component-wise and joint contribution

### Product

A Python library (`aether-vaf`) that wraps any flood forecasting model (LSTM, Transformer, dPL) with the VAF verification framework. Includes:
- Physics-consistency diagnostic computation
- Conformal prediction intervals
- Verification gating
- Recursive correction
- Verification logs and audit trails
- Optional web dashboard for demonstration

### User Workflow
```
Input (basin, forcing data)
    → Base Model Prediction (NeuralHydrology)
    → Physics Diagnostic (mass balance, trend check)
    → Conformal Uncertainty Estimation
    → Verification Gate (pass/fail based on combined score)
    → [If FAIL] Physics-Guided Correction → Re-verify → (max K iterations)
    → Final Output: Prediction + Interval + Consistency Score + Status
```

### Evaluation
- CAMELS-US (671 basins): Primary benchmark
- CAMELS-GB (671 basins): Transfer/generalization test
- Caravan-India (~200 basins): Regional demonstration
- 6 baselines × 6 AETHER variants × 10 seeds
- Metrics: NSE, KGE, PICP, MPIW, FHV, PIR, mass-balance residual, convergence rate

### Publication Positioning
- **Primary**: Water Resources Research or Hydrology and Earth System Sciences
- **Secondary**: Journal of Hydrology, Environmental Modelling & Software
- **Workshop**: NeurIPS Climate Change AI, ICML AI4Science
- **Communities**: Computational hydrology, AI for Earth, trustworthy AI, uncertainty quantification

---

## Final Question Answered

> **"If you were the principal investigator and had to spend the next 6–9 months of your research team's life on this project, would you approve AETHER?"**

### Answer: **Conditional Yes.**

I would approve AETHER 2.0 as described above — the **Verified Adaptive Forecasting** formulation — under the following conditions:

**Mandatory conditions:**
1. **Drop "Disaster Prediction"** from the title and scope immediately. This is a flood forecasting system.
2. **Drop any LLM/agent framing.** HydroAgent owns that space. AETHER uses statistical/mathematical verification, not LLM critique.
3. **The physics-consistency diagnostic must be validated independently before building the loop.** If the diagnostic doesn't correlate with actual forecast error, stop and publish the negative result.
4. **Use NeuralHydrology and Caravan as-is.** Do not waste months building a custom base model. The research contribution is the verification framework, not the predictor.
5. **The ablation must be rigorous.** 6 variants, 10 seeds, multiple basins, proper statistical testing. This is what makes or breaks the paper.

**What I would NOT approve:**
- The original "Physics-Guided Recursive Self-Verification for Flood and Disaster Prediction" — too broad, key terms now owned by competitors, "disaster prediction" is indefensible.
- Any version that treats the dashboard as the primary contribution.
- Any version that uses LLM-based verification (HydroAgent territory).
- Any version that attempts multi-hazard prediction.

**Timeline recommendation:**
- Months 1–2: Literature deep-dive finalization + physics-consistency diagnostic development + validation
- Months 3–4: Conformal prediction integration + verification gate implementation
- Months 5–6: Recursive correction module + full ablation on CAMELS-US
- Months 7–8: Transfer experiments (CAMELS-GB, India) + paper writing
- Month 9: Dashboard demonstration + final revisions

**This project, if executed as AETHER 2.0, has a realistic path to a Q1 hydrology journal publication, a strong M.Tech thesis, and a demonstrable product. But only if the scope is disciplined and the novelty claims are honest.**

The team that builds a rigorous, well-ablated conformal-physics verification framework for flood forecasting — and proves each component matters — will have made a genuine contribution. The team that builds "yet another AI flood dashboard with physics loss" will have wasted their time.

**Choose wisely.**
