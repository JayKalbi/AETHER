# AETHER — Research North Star & End-Goal Reference

> **Purpose:** This document is the standing research reference for AETHER development.  
> Before implementing a major feature, changing the architecture, adding experiments, or defining a new benchmark, check this document first.
>
> **Core principle:** Build the scientific contribution first; build the polished open-source library around validated research.

---

## 1. End Goal

AETHER is intended to become an **open-source, reproducible, model-agnostic reliability framework for hydrological forecasting**.

Its central research question is:

> **Can we predict whether a hydrological forecast is likely to fail before the ground-truth outcome becomes available, and use that reliability estimate to make calibrated accept/refine/abstain decisions?**

AETHER is **not primarily**:

- another flood-prediction model,
- another LSTM/Transformer forecasting model,
- a generic uncertainty-estimation library,
- a dashboard,
- or simply a collection of hydrology notebooks.

The distinctive target is the **reliability and decision layer surrounding forecasts**.

---

## 2. The Scientific Problem

A conventional forecasting pipeline is:

```text
Hydrological data
      ↓
Forecast model
      ↓
Forecast
      ↓
Use forecast
```

AETHER adds a reliability layer:

```text
Hydrological data
      ↓
Forecast model
      ↓
Forecast
      ↓
┌─────────────────────────────┐
│           AETHER            │
│                             │
│ Forecast reliability        │
│ / failure prediction        │
│ / uncertainty / context     │
└──────────────┬──────────────┘
               ↓
       Decision policy
          ↙    ↓    ↘
     RELEASE  REFINE  ABSTAIN
```

The research problem is therefore not merely:

> "Can we improve the forecast?"

It is:

> **"Can we identify unreliable forecasts before their outcomes are known?"**

---

## 3. What AETHER Must Ultimately Demonstrate

AETHER should eventually establish evidence for the following:

### 3.1 Pre-outcome failure prediction

Using only information available at forecast/decision time, AETHER should estimate:

```text
P(forecast failure | information available before outcome)
```

The system must not use future observations or leaked information.

### 3.2 Calibration

If AETHER assigns approximately 0.8 failure probability to a population of forecasts, the observed failure frequency in that population should be approximately consistent with that probability.

Reliability probabilities must therefore be evaluated for calibration, not only discrimination.

### 3.3 Decision usefulness

AETHER should convert reliability estimates into explicit actions such as:

- **Release** — forecast is sufficiently reliable for use.
- **Refine** — request additional computation, information, or processing.
- **Abstain** — do not automatically trust the forecast; escalate or request review.

The exact final policy/API is not frozen yet.

### 3.4 Selective forecasting

A key evaluation should investigate whether accepting only forecasts judged sufficiently reliable produces lower error at controlled coverage levels.

Conceptually:

```text
100% coverage → baseline forecast quality

90% coverage  → lower accepted-set error

80% coverage  → lower accepted-set error

70% coverage  → lower accepted-set error
```

This should be evaluated using rigorous risk–coverage/selective-prediction analysis.

### 3.5 Generalization

AETHER should not be designed around a single benchmark/model.

The research should test generalization across:

- time,
- basins,
- hydrological regimes,
- extreme events,
- and, where feasible, independent datasets.

---

## 4. CAMELS-US: Why It Exists in AETHER

The CAMELS-US 531-basin benchmark is a **scientific foundation**, not the final product.

The canonical basin registry answers:

> **"Exactly which catchments constitute the benchmark population?"**

This supports reproducibility of:

- basin population,
- train/validation/calibration/test splits,
- labels,
- feature construction,
- experiments,
- and evaluation.

The repository should not commit large raw CAMELS datasets merely to make the benchmark reproducible.

The registry is infrastructure that enables a controlled research experiment.

### Important distinction

```text
CAMELS-US registry
       ↓
Benchmark population
       ↓
Reproducible experiments
       ↓
Scientific evidence
       ↓
AETHER reliability research
```

The registry itself is **not** the novel research contribution.

---

## 5. Current Reproducibility Direction

The project currently targets a controlled temporal protocol:

```text
TRAIN        1980–2000
VALIDATION   2000–2005
CALIBRATION  2005–2010
TEST         2010–2018
```

with the established project lookback-buffer requirements.

The current research contract also includes:

- CAMELS-US v1.2
- 531 core/non-impacted benchmark basins
- primary failure label based on NAFE > 1.0
- normalization using training-period streamflow standard deviation
- LightGBM 5-fold block cross-fitting
- out-of-fold isotonic probability calibration
- clustered moving-block bootstrap
- 10,000 bootstrap replicates
- 30-day block length
- no naive DeLong tests
- reproducibility metadata and provenance

These are current project invariants. They should not be changed casually.

If a scientific reason requires changing an invariant, document the change explicitly and update the relevant ADR/reproducibility documentation.

---

## 6. The Research Gap Must Be Defended Against Existing Methods

AETHER must **not** claim novelty simply because it predicts uncertainty or forecast error.

Relevant existing areas include:

- probabilistic hydrological forecasting,
- uncertainty quantification,
- conformal prediction,
- forecast calibration,
- forecast-error prediction,
- ensemble uncertainty,
- selective prediction,
- abstention/reject-option learning,
- out-of-distribution detection,
- physics-informed hydrology,
- hydrological benchmarking.

Therefore, future experiments must answer:

> **What does AETHER provide beyond existing uncertainty, calibration, error-prediction, and selective-prediction methods?**

AETHER should be compared against meaningful baselines rather than only against an unmodified forecasting model.

Potential baseline families include:

- simple recent-error/persistence indicators,
- forecast magnitude,
- ensemble spread,
- conformal interval width,
- standard probabilistic uncertainty,
- anomaly/OOD scores,
- error-prediction models,
- AETHER without physics/context features,
- AETHER without uncertainty features,
- AETHER without temporal/context history,
- full AETHER.

The exact baseline set must be finalized after a formal literature review.

---

## 7. The Most Important Scientific Test

AETHER should demonstrate **incremental value**.

A reviewer should not be able to explain the result simply by saying:

> "AETHER works because the forecast was already obviously uncertain."

Therefore, the study should investigate whether AETHER's reliability signal contains predictive information about future failure **beyond ordinary uncertainty indicators**.

This should be tested with:

- strong baselines,
- ablation studies,
- calibration analysis,
- statistical uncertainty,
- temporal holdouts,
- spatial/basin holdouts,
- and, where feasible, independent datasets.

---

## 8. Model-Agnostic Design Goal

AETHER should ultimately be usable around different forecasting models.

Conceptually:

```text
                 ┌── LSTM
                 │
Forecast ────────┼── Transformer
                 │
                 ├── Hydrological foundation model
                 │
                 └── Other forecasting model
                         ↓
                      AETHER
                         ↓
                 Reliability estimate
                         ↓
                 Decision / abstention
```

AETHER should not become inseparably coupled to one forecasting architecture.

A strong future result would show that the reliability layer remains useful across multiple forecasting models.

---

## 9. Cross-Dataset Validation

CAMELS-US should be treated as the primary development benchmark, not the permanent boundary of the scientific claim.

A stronger research program should eventually investigate independent datasets, potentially including broader datasets such as Caravan and other hydrological regions where scientifically appropriate.

The progression should be:

```text
CAMELS-US
   ↓
Internal validation
   ↓
Temporal / basin generalization
   ↓
Independent dataset
   ↓
Independent region / forecasting model
```

If AETHER only works on the exact population used to design it, the scientific claim must remain narrow.

If it generalizes across datasets and forecasting models, the contribution becomes substantially stronger.

---

## 10. What Would NOT Be Sufficient for a Strong Paper

The following alone are not enough:

### "We trained LightGBM to predict NAFE > 1."

Too close to ordinary supervised error classification.

### "We use conformal prediction."

Conformal prediction is already established in hydrological uncertainty research.

### "We use an LSTM to predict floods."

Forecast-model novelty alone is not AETHER's intended contribution.

### "We created a 531-basin JSON registry."

Useful reproducibility infrastructure, but not a research contribution by itself.

### "We built a beautiful Python package."

Software quality supports the research; it does not substitute for scientific novelty and evidence.

---

## 11. The Intended Final AETHER Product

AETHER should eventually have three tightly connected layers.

```text
                         AETHER
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       RESEARCH          BENCHMARK        SOFTWARE
        METHOD             SUITE           LIBRARY
          │                │                │
          │                │                │
   failure prediction    datasets/       Python API
   reliability           splits          configs
   calibration           labels          evaluation
   abstention            baselines       reproducibility
   adaptation
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                     Research paper
                           +
                    Open-source release
```

The end product is therefore **not merely a benchmark** and **not merely a Python library**.

It should be:

> **A scientifically validated reliability framework + reproducible benchmark/evaluation protocol + open-source implementation.**

---

## 12. Desired Research-to-Software Sequence

Do not reverse this order.

### Correct order

```text
Research question
       ↓
Literature review
       ↓
Research gap
       ↓
Precise hypothesis
       ↓
Benchmark
       ↓
Baselines
       ↓
AETHER method
       ↓
Ablations
       ↓
Statistical evaluation
       ↓
Cross-dataset validation
       ↓
Research paper
       ↓
Polished open-source library
```

### Avoid

```text
Build huge library
       ↓
Add many features
       ↓
Find a paper idea afterward
```

The scientific hypothesis must drive implementation.

---

## 13. Q1 Publication Goal — Honest Standard

AETHER is **not currently a Q1-level contribution**.

It is a promising research direction that could become a strong paper if the eventual evidence supports a meaningful and well-defined contribution.

A Q1-level outcome is **not guaranteed**.

The strongest version of the research case would demonstrate:

1. A clearly defined pre-outcome forecast-failure problem.
2. A genuine gap relative to existing uncertainty/error-prediction methods.
3. A model-agnostic reliability mechanism.
4. Proper probability calibration.
5. Useful selective/abstaining decisions.
6. Strong baselines.
7. Ablation studies explaining where the improvement comes from.
8. Strict temporal and leakage controls.
9. Robust statistical evaluation.
10. Generalization beyond the development benchmark.
11. Reproducible experiments.
12. Open-source implementation.

Only after these are demonstrated should AETHER be positioned as a mature research contribution.

---

## 14. Non-Negotiable Scientific Principles

### No future information

AETHER must never use information that would be unavailable at the forecast decision time.

### No benchmark leakage

Train, validation, calibration, and test roles must remain strictly separated according to the project protocol.

### No cherry-picking

Report predefined or justified metrics across the relevant population.

### No weak baselines

Compare against meaningful existing approaches.

### No "AI" for decoration

Every model/component must have a scientific reason to exist.

### No unnecessary complexity

A more complicated system is not automatically a better contribution.

### No dashboard-first development

A visualization layer comes after the scientific pipeline is validated.

### No premature API freeze

The public library API should emerge from validated research requirements rather than dictate the science.

---

## 15. AETHER's North-Star Statement

Use this statement when deciding whether a proposed feature belongs in the project:

> **AETHER investigates whether hydrological forecast failure can be predicted before the outcome is observed, whether that failure probability can be reliably calibrated, and whether it can support model-agnostic selective decisions such as release, refinement, or abstention under temporal and spatial distribution shift.**

If a proposed feature does not contribute meaningfully to this goal, question whether it belongs in AETHER.

---

## 16. Current Project Maturity

At the current stage:

```text
Repository foundation             ✅
Reproducibility contract          ✅
Reliability architecture ADR      ✅
CAMELS-US benchmark registry      ✅
Scientific hypothesis              🔬 Developing
Formal literature-gap analysis     ⏳ Required
Baseline suite                     ⏳ Required
Reliability model                  ⏳ Future
Calibration evaluation             ⏳ Future
Selective prediction evaluation    ⏳ Future
Cross-dataset validation           ⏳ Future
Research paper                     ⏳ Future
Public library release             ⏳ Future
```

This is intentional.

The project should progress through scientific gates rather than pretending the final contribution already exists.

---

## 17. Decision Rule for Future Development

Before starting a significant AETHER issue, ask:

### Scientific relevance
Does this help answer the central research question?

### Reproducibility
Can another researcher reproduce the result?

### Leakage safety
Could this introduce future-information leakage?

### Baseline validity
Does this allow meaningful comparison against existing methods?

### Generalization
Does this help establish that AETHER is not benchmark-specific?

### Interpretability
Can we explain why the system considers a forecast unreliable?

### Simplicity
Is this complexity scientifically justified?

### Research contribution
Does this help establish a publishable scientific contribution rather than merely increasing software size?

If the answer is unclear, pause and resolve the scientific question before coding.

---

## 18. Final North Star

The ultimate goal is:

> **Build AETHER into a reproducible, model-agnostic hydrological forecast reliability framework whose scientific contribution is demonstrated through rigorous benchmarked evidence, and whose validated research methods are released as high-quality open-source software.**

The repository is the vehicle.

The benchmark is the experimental foundation.

The reliability/abstention research is the scientific core.

The paper is the research output.

The open-source library is the long-term public artifact.
