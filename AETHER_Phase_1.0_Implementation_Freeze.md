# AETHER PHASE 1.0 — EXPERIMENTAL SPECIFICATION & IMPLEMENTATION FREEZE

**Document Status:** FINAL CONTRACT & IMPLEMENTATION FREEZE  
**Effective Date:** August 27, 2026  
**Target Domain:** Hydrological Streamflow & Flood Hazard Forecasting  
**Benchmark Dataset:** CAMELS-US (531 Core Benchmark Basins)  
**Primary Research Objective:** Pre-Outcome Forecast Failure Prediction & Selective Forecasting  
**Author / Role:** Principal Investigator & System Architect  

---

## 1. FINAL RESEARCH QUESTIONS

### Primary Research Question
> **"Can pre-outcome information—specifically predictive uncertainty representations, input-space out-of-distribution signals, and hydrologically informed domain diagnostics—predict streamflow forecast failure at a 1-day lead time before ground truth is observed, and do hydrologically informed domain diagnostics provide statistically significant incremental predictive value beyond standard uncertainty and OOD signals alone?"**

### Secondary Research Question
> **"Can the resulting pre-outcome failure probability estimate drive an operational selective forecasting policy (Release vs. Abstain / Human Review) that achieves a statistically significant reduction in selective risk (higher conditional accuracy) on accepted forecasts during extreme hydrological events without unacceptably degrading operational coverage?"**

---

## 2. FINAL HYPOTHESES

### Hypothesis 1 (H1) — Forecast Failure Predictability
* **Null Hypothesis ($H_{1,0}$):** Pre-outcome signals available at forecast time $t$ have no discriminatory power for forecast failure at time $t+1$. The area under the ROC curve ($AUROC$) equals $0.50$, the area under the Precision-Recall curve ($AUPRC$) equals the empirical base rate of failure $\pi$, and the rank correlation between estimated failure probability $R_t$ and realized error $|e_t|$ satisfies $\rho(R_t, |e_t|) \le 0$.
* **Alternative Hypothesis ($H_{1,1}$):** Pre-outcome signals discriminate forecast failure significantly better than random guessing ($AUROC > 0.50$, $AUPRC > \pi$, $\rho(R_t, |e_t|) > 0$) with $p < 0.01$ under block-bootstrapped hypothesis testing across held-out temporal splits.
* **Measurable Quantity:** Out-of-sample $AUROC$, $AUPRC$, Brier Skill Score ($BSS$), and Spearman rank correlation $\rho(R_t, |e_t|)$ on the test split $\mathcal{D}_{\text{test}}$.
* **Falsification Condition:** Failure to reject $H_{1,0}$ at $\alpha = 0.01$ via moving-block bootstrap ($B=10,000$), or an empirical test set $AUROC \le 0.55$.

### Hypothesis 2 (H2) — Incremental Information from Hydrological Domain Features
* **Null Hypothesis ($H_{2,0}$):** The conditional mutual information between realized forecast failure $F_t$ and hydrological domain diagnostics $\Phi_t$, given model uncertainty $U_t$, out-of-distribution distance $OOD_t$, and context $C_t$, is zero:
  $$I(F_t; \Phi_t \mid U_t, OOD_t, C_t) = 0$$
  Consequently, adding $\Phi_t$ to a reliability model containing $\{U_t, OOD_t, C_t\}$ produces zero gain in discrimination:
  $$\Delta AUROC = AUROC_{\text{Full}} - AUROC_{\text{Uncertainty+OOD+Context}} \le 0$$
* **Alternative Hypothesis ($H_{2,1}$):** Hydrological domain features provide non-redundant, incremental predictive information:
  $$I(F_t; \Phi_t \mid U_t, OOD_t, C_t) > 0 \implies \Delta AUROC > 0 \quad (p < 0.05)$$
* **Measurable Quantity:** $\Delta AUROC$ and $\Delta AUPRC$ between the Full AETHER reliability estimator and the Ablated (Uncertainty + OOD + Context) baseline on $\mathcal{D}_{\text{test}}$.
* **Falsification Condition:** $\Delta AUROC \le 0.01$ or clustered basin bootstrap paired test yielding $p \ge 0.05$.

### Hypothesis 3 (H3) — Selective Forecasting Utility
* **Null Hypothesis ($H_{3,0}$):** A selective release policy $\pi_\tau(R_t)$ based on predicted failure risk $R_t$ achieves no lower selective risk than a random abstention policy or unconditional release at identical coverage levels $c \in [0.50, 0.95]$:
  $$\text{Risk}(\pi_\tau \mid \text{Coverage}=c) \ge \text{Risk}(\pi_{\text{random}} \mid \text{Coverage}=c)$$
* **Alternative Hypothesis ($H_{3,1}$):** Selective forecasting using $R_t$ achieves strictly lower selective risk (lower Mean Absolute Error / Root Mean Squared Error / Continuous Ranked Probability Score) on accepted forecasts across target coverage levels, with the largest absolute risk reduction occurring during extreme hydrological events ($Q_{t+1} > Q_{95, b}$).
  $$\text{AURC}(\pi_\tau) < \text{AURC}(\pi_{\text{random}}) \quad (p < 0.01)$$
* **Measurable Quantity:** Area Under the Risk-Coverage Curve ($AURC$), Excess Risk-Coverage Area ($E\text{-}AURC$), and Peak-Flow Selective MAE at $80\%$ coverage ($RC_{80}$).
* **Falsification Condition:** $AURC(\pi_\tau) \ge AURC(\pi_{\text{random}})$ or paired bootstrap $p \ge 0.05$ on extreme flow subsets ($Q > Q_{95}$).

---

## 3. FORMAL MATHEMATICAL DEFINITION

Let $b \in \{1, \dots, B\}$ index catchments/basins, and let discrete time $t \in \{1, \dots, T\}$ denote daily operational time steps.

### Variable Taxonomy
1. **$X_{t, b} \in \mathbb{R}^{L \times d_x}$**: Dynamic meteorological forcing history over lookback window $[t-L+1, t]$ with $L = 365$ days. Variables include daily total precipitation $P$, minimum temperature $T_{\min}$, maximum temperature $T_{\max}$, incoming shortwave radiation $R_{\text{sw}}$, and vapor pressure $V_p$.
2. **$S_b \in \mathbb{R}^{d_s}$**: Static catchment attributes ($d_s = 27$) describing topography, climate indices, soil texture, vegetation, and geology.
3. **$Y_{t, b} = Q_{t+1, b} \in \mathbb{R}_+$**: Ground-truth streamflow discharge at horizon $h=1$ day ($t+1$), observable strictly at time $t+1$.
4. **$\hat{Y}_{t, b} = \hat{Q}_{t+1, b} = f_\theta(X_{t, b}, S_b) \in \mathbb{R}_+$**: Point forecast for lead time $t+1$ issued at time $t$ by the frozen base model $f_\theta$.
5. **$U_{t, b} \in \mathbb{R}^{d_u}$**: Uncertainty representations computable at time $t$:
   * Conformalized Quantile Regression (CQR) interval width: $W_{t, b} = \hat{Q}_{t+1, b}^{\text{high}} - \hat{Q}_{t+1, b}^{\text{low}}$.
   * Normalized CQR interval width: $\tilde{W}_{t, b} = \frac{W_{t, b}}{\hat{Q}_{t+1, b} + \epsilon}$.
   * Deep ensemble predictive standard deviation across $K$ seeds: $\sigma_{t, b}^{\text{ens}} = \sqrt{\frac{1}{K}\sum_{k=1}^K (\hat{Q}_{t+1, b}^{(k)} - \bar{Q}_{t+1, b})^2}$.
6. **$OOD_{t, b} \in \mathbb{R}^{d_o}$**: Out-of-distribution distance metrics computed from inputs available at $t$:
   * Mahalanobis distance $D_M(X_{t, b})$ to training forcing centroid.
   * Rolling precipitation percentile anomaly $z_P(t) = \frac{\sum_{i=0}^2 P_{t-i} - \mu_{P, b}}{\sigma_{P, b}}$.
7. **$\Phi_{t, b} \in \mathbb{R}^{d_\phi}$**: Hydrologically informed diagnostic features computable at time $t$ (e.g., Antecedent Precipitation Index $API_t$, historical runoff ratio deviation $RR_{\text{dev}}$, baseflow recession anomaly).
8. **$C_{t, b} \in \mathbb{R}^{d_c}$**: Contextual and seasonal features (day-of-year cyclic harmonics $\sin(2\pi \frac{\text{DOY}}{365.25})$, $\cos(2\pi \frac{\text{DOY}}{365.25})$, current flow level $Q_t / \bar{Q}_b$).
9. **$F_{t, b} \in \{0, 1\}$**: Binary forecast failure ground truth evaluated ex-post at time $t+1$:
   $$F_{t, b} = \mathbb{I}\left( \frac{|\hat{Q}_{t+1, b} - Q_{t+1, b}|}{\sigma_{Q, b} + \epsilon} > \theta_{\text{fail}} \right)$$
10. **$R_{t, b} \in [0, 1]$**: Pre-outcome failure probability estimated by the reliability estimator $g_\psi$:
    $$R_{t, b} = g_\psi(X_{t, b}, S_b, \hat{Y}_{t, b}, U_{t, b}, OOD_{t, b}, \Phi_{t, b}, C_{t, b}) \equiv P(F_{t, b} = 1 \mid \mathcal{I}_{t, b})$$
    where $\mathcal{I}_{t, b} = \{X_{t, b}, S_b, \hat{Y}_{t, b}, U_{t, b}, OOD_{t, b}, \Phi_{t, b}, C_{t, b}\}$ represents the complete information filtration strictly available at time $t$.
11. **$A_{t, b} \in \{\text{RELEASE}, \text{ABSTAIN}\}$**: The operational selective decision governed by policy $\pi_\tau$:
    $$A_{t, b} = \begin{cases} \text{RELEASE} & \text{if } R_{t, b} \le \tau \\ \text{ABSTAIN} & \text{if } R_{t, b} > \tau \end{cases}$$
    where $\tau \in [0, 1]$ is a fixed threshold calibrated on the independent calibration split $\mathcal{D}_{\text{cal}}$ to achieve either a bounded selective risk level $\alpha_{\text{risk}}$ or a target coverage rate $c^*$.

---

## 4. FAILURE LABEL DESIGN

To ensure the research program does not hinge on a single arbitrary threshold, we establish **ONE PRIMARY LABEL** and **FOUR SECONDARY LABELS**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FAILURE ONTOLOGY                                │
├────────────────────────┬────────────────────────────────────────────────────┤
│ PRIMARY LABEL          │ Normalized Absolute Forecast Error (NAFE > 1.0)    │
├────────────────────────┼────────────────────────────────────────────────────┤
│ SECONDARY LABEL 1      │ Flood-Threshold Decision Disagreement (FTDD)       │
│ SECONDARY LABEL 2      │ Probabilistic Conformal Interval Miss (PCIM)       │
│ SECONDARY LABEL 3      │ Extreme-Event Forecast Error (EEFE)                │
│ SECONDARY LABEL 4      │ Peak Magnitude Relative Error (PMRE)               │
└────────────────────────┴────────────────────────────────────────────────────┘
```

### Label Specifications

#### 1. PRIMARY LABEL: Normalized Absolute Forecast Error Threshold Exceedance (NAFE)
* **Mathematical Formula:**
  $$e_{t, b} = \frac{|\hat{Q}_{t+1, b} - Q_{t+1, b}|}{\sigma_{Q, b} + \epsilon}$$
  $$F_{t, b}^{\text{primary}} = \mathbb{I}(e_{t, b} > \theta_{\text{fail}}), \quad \text{with } \theta_{\text{fail}} = 1.0$$
* **Exact Data Needed:** Point forecast $\hat{Q}_{t+1, b}$, observed discharge $Q_{t+1, b}$, and historical basin discharge standard deviation $\sigma_{Q, b}$ (computed strictly over $\mathcal{D}_{\text{train}}$).
* **Temporal Availability:** Retrospective only (evaluated at $t+1$).
* **Leakage Risk:** Zero, provided $\sigma_{Q, b}$ is computed strictly on $\mathcal{D}_{\text{train}}$ and never on $\mathcal{D}_{\text{cal}}$ or $\mathcal{D}_{\text{test}}$.
* **Sample Size & Class Imbalance:** Across 531 basins over 8 test years ($\approx 1.55 \times 10^6$ daily instances), failure base rate is $\pi \approx 8.5\% - 12.0\%$. Moderately imbalanced, statistically stable.
* **Scientific Meaning:** Measures whether the forecast error exceeds one standard deviation of natural catchment flow variability, standardizing across ephemeral creeks ($1 \text{ m}^3/\text{s}$) and major rivers ($10,000 \text{ m}^3/\text{s}$).

#### 2. SECONDARY LABEL 1: Flood-Threshold Decision Disagreement (FTDD)
* **Mathematical Formula:**
  $$F_{t, b}^{\text{flood}} = \mathbb{I}\Big( (\hat{Q}_{t+1, b} > Q_{95, b} \wedge Q_{t+1, b} \le Q_{95, b}) \vee (\hat{Q}_{t+1, b} \le Q_{95, b} \wedge Q_{t+1, b} > Q_{95, b}) \Big)$$
  where $Q_{95, b}$ is the 95th percentile of discharge computed strictly on $\mathcal{D}_{\text{train}}$.
* **Exact Data Needed:** $\hat{Q}_{t+1, b}$, $Q_{t+1, b}$, and training quantile $Q_{95, b}$.
* **Class Imbalance:** Base rate $\approx 3.0\% - 5.0\%$. Highly imbalanced.
* **Scientific Meaning:** Evaluates operational categorical decision failure (False Alarm or Missed Flood Warning).

#### 3. SECONDARY LABEL 2: Probabilistic Conformal Interval Miss (PCIM)
* **Mathematical Formula:**
  $$F_{t, b}^{\text{interval}} = \mathbb{I}\left( Q_{t+1, b} \notin \left[\hat{Q}_{t+1, b}^{\text{low}}, \hat{Q}_{t+1, b}^{\text{high}}\right] \right)$$
  for a nominal $90\%$ Conformalized Quantile Regression (CQR) interval calibrated on $\mathcal{D}_{\text{cal}}$.
* **Exact Data Needed:** Calibrated prediction interval bounds $[\hat{Q}_{t+1, b}^{\text{low}}, \hat{Q}_{t+1, b}^{\text{high}}]$ and $Q_{t+1, b}$.
* **Class Imbalance:** Base rate $\approx 10.0\%$ by conformal construction.
* **Scientific Meaning:** Tests whether the aleatoric/epistemic uncertainty wrapper failed to cover the realization.

#### 4. SECONDARY LABEL 3: Extreme-Event Forecast Error (EEFE)
* **Mathematical Formula:**
  $$F_{t, b}^{\text{extreme}} = \mathbb{I}\left( e_{t, b} > 1.0 \wedge Q_{t+1, b} > Q_{90, b} \right)$$
* **Class Imbalance:** Base rate $\approx 1.5\% - 2.5\%$. Severely imbalanced.
* **Scientific Meaning:** Isolates forecast failure occurring exclusively in the high-flow tail regime.

#### 5. SECONDARY LABEL 4: Peak Magnitude Relative Error (PMRE)
* **Mathematical Formula:** Evaluated only on event peak days $\mathcal{T}_{\text{peak}} = \{t : Q_{t+1} > Q_{t} \wedge Q_{t+1} > Q_{t+2} \wedge Q_{t+1} > Q_{90, b}\}$:
  $$F_{t, b}^{\text{peak}} = \mathbb{I}\left( \frac{|\hat{Q}_{t+1, b} - Q_{t+1, b}|}{Q_{t+1, b}} > 0.25 \right)$$
* **Class Imbalance:** Evaluated conditional on peak events ($N \approx 15,000$ event peaks across the dataset). Base rate $\approx 25\% - 35\%$ conditional on peak occurrence.
* **Scientific Meaning:** Directly measures hydrologic peak underestimation/overestimation.

### Justification for Primary Label Choice
$F^{\text{primary}}$ (NAFE) is chosen because:
1. It is **continuous-underlying and scale-free**, preventing high-discharge basins from dominating loss gradients.
2. It has an **empirically balanced base rate ($\approx 10\%$)** that allows reliable gradient estimation without pathological gradient vanishing.
3. It can be computed on **every single timestep**, ensuring unbroken time-series continuity during training.

---

## 5. DATASET SPECIFICATION: CAMELS-US

```
===============================================================================
DATASET SPECIFICATION: CAMELS-US
===============================================================================
Dataset Name:          Catchment Attributes and Meteorology for Large-Sample Studies
Version:               CAMELS-US v1.2
Geographic Scope:      Contiguous United States (CONUS)
Benchmark Catchments:  531 Basins (USGS Non-Impacted Benchmark Subset)
Temporal Coverage:     October 1, 1980 – September 30, 2018 (38 Hydrological Years)
Temporal Resolution:   Daily (1-day step, dt = 24h)
===============================================================================
```

### Required Files & Directory Hierarchy
```
data/camels_us/
├── basin_dataset_public_v1p2/
│   ├── basin_metadata/
│   │   └── gauge_information.txt
│   ├── basin_mean_forcing/
│   │   └── daymet/                      # Primary forcing data
│   │       ├── 01/ ... 18/ (HUC regions)
│   │       │   └── *_forcing_leap.txt
│   └── usgs_streamflow/                 # Ground truth streamflow
│       ├── 01/ ... 18/
│       │   └── *_streamflow_qc.txt
└── camels_attributes_v2.0/
    ├── camels_topo.txt                  # Topographic attributes
    ├── camels_clim.txt                  # Climatic attributes
    ├── camels_hydro.txt                 # Hydrological signatures
    ├── camels_vege.txt                  # Vegetation characteristics
    ├── camels_soil.txt                  # Soil characteristics
    └── camels_geol.txt                  # Geological attributes
```

### Variable Contract & Units

| Variable Category | Variable Name | Symbol | Units | Source | Description / Transform |
|:---|:---|:---:|:---:|:---|:---|
| **Target Variable** | `streamflow` | $Q$ | $\text{mm/day}$ | USGS Streamflow | Converted from $\text{cfs}$ via catchment area: $Q = \frac{\text{cfs} \times 0.0283168 \times 86400}{\text{Area}(\text{m}^2)} \times 1000$ |
| **Dynamic Forcing** | `prcp` | $P$ | $\text{mm/day}$ | Daymet | Daily total precipitation |
| **Dynamic Forcing** | `tmin` | $T_{\min}$ | $^\circ\text{C}$ | Daymet | Daily minimum 2m temperature |
| **Dynamic Forcing** | `tmax` | $T_{\max}$ | $^\circ\text{C}$ | Daymet | Daily maximum 2m temperature |
| **Dynamic Forcing** | `srad` | $R_{\text{sw}}$ | $\text{W/m}^2$ | Daymet | Daily incident shortwave radiation |
| **Dynamic Forcing** | `vp` | $V_p$ | $\text{Pa}$ | Daymet | Daily average vapor pressure |
| **Static Attribute** | `elev_mean` | $z_{\text{mean}}$ | $\text{m}$ | `camels_topo.txt` | Catchment mean elevation |
| **Static Attribute** | `slope_mean` | $S_{\text{mean}}$ | $\text{m/km}$ | `camels_topo.txt` | Catchment mean slope |
| **Static Attribute** | `area_gages2` | $A_{\text{basin}}$ | $\text{km}^2$ | `camels_topo.txt` | Official GAGES-II drainage area |
| **Static Attribute** | `p_mean` | $\bar{P}$ | $\text{mm/day}$ | `camels_clim.txt` | Long-term mean daily precipitation |
| **Static Attribute** | `pet_mean` | $\bar{ET}_0$ | $\text{mm/day}$ | `camels_clim.txt` | Long-term mean potential evapotranspiration |
| **Static Attribute** | `aridity` | $I_{\text{arid}}$ | $-$ | `camels_clim.txt` | Aridity index: $\bar{ET}_0 / \bar{P}$ |
| **Static Attribute** | `frac_snow` | $f_{\text{snow}}$ | $-$ | `camels_clim.txt` | Fraction of precipitation falling as snow |
| **Static Attribute** | `high_prec_freq` | $f_{\text{hprec}}$ | $\text{days/yr}$ | `camels_clim.txt` | Frequency of high precipitation days |
| **Static Attribute** | `high_prec_dur` | $d_{\text{hprec}}$ | $\text{days}$ | `camels_clim.txt` | Average duration of high precipitation events |
| **Static Attribute** | `low_prec_freq` | $f_{\text{lprec}}$ | $\text{days/yr}$ | `camels_clim.txt` | Frequency of dry days |
| **Static Attribute** | `low_prec_dur` | $d_{\text{lprec}}$ | $\text{days}$ | `camels_clim.txt` | Average duration of dry periods |
| **Static Attribute** | `clay_frac` | $f_{\text{clay}}$ | $\%$ | `camels_soil.txt` | Volumetric clay fraction |
| **Static Attribute** | `sand_frac` | $f_{\text{sand}}$ | $\%$ | `camels_soil.txt` | Volumetric sand fraction |
| **Static Attribute** | `silt_frac` | $f_{\text{silt}}$ | $\%$ | `camels_soil.txt` | Volumetric silt fraction |
| **Static Attribute** | `water_frac` | $f_{\text{water}}$ | $\%$ | `camels_soil.txt` | Volumetric water content fraction |
| **Static Attribute** | `organic_frac` | $f_{\text{org}}$ | $\%$ | `camels_soil.txt` | Volumetric organic matter fraction |
| **Static Attribute** | `soil_depth_pelletier` | $d_{\text{soil}}$ | $\text{m}$ | `camels_soil.txt` | Depth to bedrock (Pelletier) |
| **Static Attribute** | `soil_conductivity` | $K_{\text{sat}}$ | $\text{cm/hr}$ | `camels_soil.txt` | Saturated hydraulic conductivity |
| **Static Attribute** | `max_water_content` | $\theta_{\max}$ | $\text{m}$ | `camels_soil.txt` | Maximum soil water content |
| **Static Attribute** | `root_depth` | $d_{\text{root}}$ | $\text{m}$ | `camels_vege.txt` | Rooting depth |
| **Static Attribute** | `forest_frac` | $f_{\text{forest}}$ | $-$ | `camels_vege.txt` | Forest cover fraction |
| **Static Attribute** | `lai_max` | $LAI_{\max}$ | $-$ | `camels_vege.txt` | Maximum Leaf Area Index |
| **Static Attribute** | `lai_diff` | $\Delta LAI$ | $-$ | `camels_vege.txt` | Difference between max and min LAI |
| **Static Attribute** | `dom_land_cover_frac`| $f_{\text{dom}}$ | $-$ | `camels_vege.txt` | Dominant land cover fraction |
| **Static Attribute** | `geol_permeability` | $k_{\text{geol}}$ | $\text{m}^2$ | `camels_geol.txt` | Subsurface permeability |
| **Static Attribute** | `geol_porosity` | $\phi_{\text{geol}}$ | $-$ | `camels_geol.txt` | Subsurface porosity |

### Quality Control & Missing Data Protocols
1. **Streamflow Missing Flag:** USGS flag `Q_FLAG == 'M'` or $Q < 0$ denotes missing observations. Missing values are masked out from loss functions and evaluation metrics.
2. **Missing Rate Filter:** Any basin with $> 5.0\%$ missing streamflow records across the training or test period is excluded.
3. **Area Consistency:** Basin area recorded in `camels_topo.txt` must match `gauge_information.txt` within $1.0\%$.

> [!IMPORTANT]
> **VERIFY BEFORE IMPLEMENTATION [VBI-01]:** Confirm local Daymet file headers in `basin_mean_forcing/daymet/` match the expected columns (`Year`, `Mn`, `Day`, `Hr`, `dayl(s)`, `prcp(mm/day)`, `srad(W/m2)`, `swe(mm)`, `tmax(C)`, `tmin(C)`, `vp(Pa)`).

---

## 6. TEMPORAL SPLIT & EMBARGO SPECIFICATION

To guarantee zero data contamination and maintain strict physical causality, the 38-year record (1980–2018) is partitioned into **FOUR STRICTLY DISJOINT TEMPORAL BLOCKS**.

```
1980-10-01                2000-09-30      2005-09-30      2010-09-30            2018-09-30
├──────────────────────────────┼───────────────┼───────────────┼─────────────────────┤
│         TRAIN SET            │  VALIDATION   │  CALIBRATION  │      TEST SET       │
│         (20 Years)           │   (5 Years)   │   (5 Years)   │      (8 Years)      │
│  Base Model Optimization     │ Early Stop    │  UQ / LightGBM│   Final Evaluation  │
│  Normalization Parameters    │ Arch Tuning   │  Tau Selection│  STRICTLY UNTOUCHED │
└──────────────────────────────┴───────────────┴───────────────┴─────────────────────┘
```

### Exact Split Dates

| Split Name | Start Date | End Date | Duration | Hydrological Purpose | Permitted Operations |
|:---|:---:|:---:|:---:|:---|:---|
| **TRAIN** | `1980-10-01` | `2000-09-30` | 20 Years | Base forecasting model training; computation of feature normalization statistics $(\mu, \sigma)$ and historical basin quantiles ($Q_{90}, Q_{95}, \sigma_Q$). | Weight backpropagation; static scaling fit. |
| **VALIDATION** | `2000-10-01` | `2005-09-30` | 5 Years | Base model early stopping; neural hyperparameter tuning. | Loss monitoring; checkpoint selection. |
| **CALIBRATION** | `2005-10-01` | `2010-09-30` | 5 Years | Reliability estimator training; Conformal Quantile Calibration ($\hat{q}_{1-\alpha}$); selective threshold ($\tau$) tuning via Conformal Risk Control. | GBDT training; nonconformity calibration; threshold selection. |
| **TEST** | `2010-10-01` | `2018-09-30` | 8 Years | Out-of-sample benchmarking of all baselines, reliability metrics, and selective policies. | **INFERENCE & EVALUATION ONLY.** Zero weight updates or parameter tuning permitted. |

### Lookback Buffers & Embargo Isolation
* **Lookback Buffer Prepending:** To compute predictions starting on day 1 of any split without losing data, each split is prepended with an internal history buffer of $L = 365$ days. The buffer provides input history only; losses are computed strictly on split dates.
* **Autocorrelation Embargo:** Streamflow exhibits autoregressive memory ($\rho_1 \approx 0.85 - 0.95$). An embargo period of $L + h = 366$ days separates the loss evaluation regions between splits, guaranteeing zero overlapping receptive fields across splits.

---

## 7. BASIN SPLIT PROTOCOLS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BASIN EXPERIMENT SPLITS                          │
├─────────────────────────┬───────────────────────────────────────────────────┤
│ Experiment A (Temporal) │ All 531 Benchmark Basins (In-Sample Space,        │
│                         │ Out-of-Sample Time: Train 1980-2000, Test 2010-18)│
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Experiment B (Spatial)  │ 425 Basins Train/Cal (80%), 106 Basins Test (20%) │
│                         │ (Ungauged Basin Generalization)                   │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Experiment C (Climate)  │ Train/Cal on Humid ($I_{\text{arid}} < 1.0$),     │
│                         │ Test on Arid ($I_{\text{arid}} \ge 1.0$)          │
└─────────────────────────┴───────────────────────────────────────────────────┘
```

1. **Experiment A (Temporal Holdout — Core Milestone):** All 531 basins are evaluated on the held-out temporal test period (`2010-10-01` to `2018-09-30`).
2. **Experiment B (Spatial / Ungauged Basin Holdout):** 80% of basins ($N=425$) assigned to training/calibration; 20% ($N=106$) held out entirely. Tests whether the reliability estimator transfers to ungauged catchments.
3. **Experiment C (Climate Regime Shift Holdout):** Stratified partition by Aridity Index ($I_{\text{arid}} = \bar{ET}_0 / \bar{P}$). Train/calibrate on Humid catchments ($I_{\text{arid}} < 1.0$, $N \approx 360$), test on Arid catchments ($I_{\text{arid}} \ge 1.0$, $N \approx 171$).

---

## 8. FORECASTING MODEL SPECIFICATION

We freeze the base forecasting architecture to the established, peer-reviewed gold standard in deep hydrological modeling: **NeuralHydrology Entity-Aware LSTM (EA-LSTM)** (Kratzert et al., 2019, 2024).

```
Dynamic Inputs X_t [365 x 5] ───► Standard LSTM Cell Input Gate (i_t, f_t, o_t)
                                         ▲
Static Attributes S_b [27]  ───► Static Entity Gate: e_b = σ(W_s S_b + b_s)
                                         │
                                 Hidden State h_t (256-dim)
                                         │
                                 Linear Head W_y h_t + b_y
                                         ▼
                                Point Forecast Q̂_{t+1}
```

### Frozen Hyperparameter Contract

| Parameter | Specification | Scientific / Operational Justification |
|:---|:---|:---|
| **Model Family** | Entity-Aware LSTM (EA-LSTM) | Standardized in Kratzert et al. (2019/2024); separate static/dynamic gating prevents attribute overfitting. |
| **Framework** | `neuralhydrology` v1.1.0+ / PyTorch 2.2+ | Community standard, fully reproducible. |
| **Input Sequence Length ($L$)**| 365 Days (1 Full Hydrological Cycle) | Captures seasonal snowpack accumulation, soil moisture memory, and groundwater recharge. |
| **Forecast Horizon ($h$)** | 1 Day ($t+1$) | Primary operational flood lead time for flash-to-medium basins. |
| **Hidden State Dimension** | 256 | Empirical sweet spot between capacity and overfitting across 531 basins. |
| **Number of Layers** | 1 (Single Recurrent Layer) | Multi-layer LSTMs show empirical degradation in CAMELS regional training (Kratzert et al., 2019). |
| **Recurrent Dropout** | 0.40 | Prevents co-adaptation of recurrent units. |
| **Loss Function** | Basin-Averaged Regularized NSE Loss: $\mathcal{L}_{\text{NSE}} = \frac{1}{B}\sum_{b=1}^B \frac{\sum_{t=1}^T (\hat{Q}_{t, b} - Q_{t, b})^2}{(\sigma_{Q, b} + 0.1)^2}$ | Directly optimizes hydrological efficiency metric while normalizing variance across basins. |
| **Optimizer** | Adam ($\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$) | Standard robust gradient optimization. |
| **Learning Rate Schedule** | Initial $1 \times 10^{-3}$; decayed to $5 \times 10^{-4}$ at Epoch 15, $1 \times 10^{-4}$ at Epoch 25 | Stable convergence to flat minima. |
| **Batch Size** | 256 Basins per Batch | Balances GPU memory and gradient variance. |
| **Training Epochs** | 30 Epochs Max with Early Stopping | Patience = 5 epochs on $\mathcal{D}_{\text{val}}$ NSE loss. |
| **Model Seeds** | 5 Random Seeds: `[101, 102, 103, 104, 105]` | Generates deep ensemble spread $\sigma_{t, b}^{\text{ens}}$ for uncertainty quantification. |
| **Checkpointing** | Save best model weights based on minimum validation loss $\mathcal{L}_{\text{val}}$. | Deterministic weight freezing. |

---

## 9. UNCERTAINTY ESTIMATION SPECIFICATION

To supply rigorous uncertainty representations without invalidating downstream guarantees, we freeze a **Two-Tier Uncertainty Mechanism**:
1. **Conformalized Quantile Regression (CQR)** (Romano, Patterson, & Candès, 2019) for formal distribution-free prediction intervals.
2. **Deep Ensemble Variance** across the 5 frozen base model seeds for epistemic model disagreement.

```
Base Models (5 Seeds) ──────► Ensemble Mean Q̂_{t+1}, Ensemble Spread σ_{ens}
                                      │
Quantile Head LSTM ────────► Lower (q_0.05), Median (q_0.50), Upper (q_0.95)
                                      │
Calibration Set D_cal ──────► Nonconformity Scores s_i = max(q_0.05 - Y, Y - q_0.95)
                                      │
Conformal Quantile q̂_0.90 ──► Conformal Interval: [q_0.05 - q̂, q_0.95 + q̂]
                                      │
Features Extracted ─────────► Interval Width W_t, Norm Width W_t / (Q̂_{t+1} + ε)
```

### CQR Formulation & Calibration Protocol
1. **Pinball Loss Training:** Train an auxiliary multi-quantile LSTM head to output quantiles $\hat{q}_{\alpha/2}(X_t)$, $\hat{q}_{0.50}(X_t)$, $\hat{q}_{1-\alpha/2}(X_t)$ for $\alpha = 0.10$ (nominal $90\%$ coverage) using the tilted pinball loss:
   $$\mathcal{L}_{\tau}(y, \hat{y}) = \max(\tau(y - \hat{y}), (\tau - 1)(y - \hat{y}))$$
2. **Calibration Step on $\mathcal{D}_{\text{cal}}$:** For each calibration instance $i \in \{1, \dots, N_{\text{cal}}\}$, compute the nonconformity score:
   $$s_i = \max\left( \hat{q}_{0.05}(X_i) - Y_i, \; Y_i - \hat{q}_{0.95}(X_i) \right)$$
3. **Calibrated Cutoff $\hat{q}_{1-\alpha}$:** Compute the empirical $(1-\alpha)(1 + 1/N_{\text{cal}})$-th quantile of $\{s_1, \dots, s_{N_{\text{cal}}}\}$.
4. **Prediction Interval on Test $\mathcal{D}_{\text{test}}$:**
   $$C(X_t) = \left[ \hat{q}_{0.05}(X_t) - \hat{q}_{1-\alpha}, \; \hat{q}_{0.95}(X_t) + \hat{q}_{1-\alpha} \right]$$
5. **Interval Width Features Extracted at time $t$:**
   * $W_{t, b} = (\hat{q}_{0.95}(X_{t, b}) + \hat{q}_{1-\alpha}) - (\hat{q}_{0.05}(X_{t, b}) - \hat{q}_{1-\alpha})$
   * $\tilde{W}_{t, b} = \frac{W_{t, b}}{\hat{Q}_{t+1, b} + 0.1}$

### Role of Uncertainty in AETHER
Uncertainty $U_t$ is used **strictly as a pre-outcome feature** for the reliability estimator $g_\psi$ and as a **comparative baseline (B3, B4, B5)**. It does *not* dynamically alter the base model weights at inference time, guaranteeing that exchangeability and finite-sample calibration properties are maintained.

---

## 10. COMPLETE FEATURE CONTRACT

Every feature input to the reliability estimator $g_\psi$ must satisfy the **Strict Causality Contract**: computable strictly at time $t$ using data available at or before time $t$.

```
========================================================================================================
FEATURE REGISTRY & IMPLEMENTATION CONTRACT (AETHER RELIABILITY ENGINE)
========================================================================================================
Group A: Context & Climatology
Group B: Out-Of-Distribution (OOD)
Group C: Model Output Representations
Group D: Uncertainty Signals
Group E: Hydrologically Informed Domain Features
========================================================================================================
```

| ID | Feature Name | Formula / Definition | Units | Receptive Field | Data Source | Normalization Method | Leakage Verification Test |
|:---|:---|:---|:---:|:---:|:---|:---|:---|
| **A1** | `flow_current_ratio` | $Q_t / (\bar{Q}_b + \epsilon)$ | $-$ | $t$ | USGS Streamflow | Division by training mean $\bar{Q}_b$ | `test_feature_causality` |
| **A2** | `flow_percentile` | $\hat{F}_{Q, b}(Q_t) \in [0, 1]$ (Empirical CDF) | $-$ | $t$ | USGS Streamflow | Empirical CDF fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **A3** | `doy_sin` | $\sin(2\pi \cdot \text{DOY}_t / 365.25)$ | $-$ | $t$ | Calendar | None ($[-1, 1]$) | `test_temporal_order` |
| **A4** | `doy_cos` | $\cos(2\pi \cdot \text{DOY}_t / 365.25)$ | $-$ | $t$ | Calendar | None ($[-1, 1]$) | `test_temporal_order` |
| **A5** | `aridity_index` | $\bar{ET}_{0, b} / \bar{P}_b$ | $-$ | Static | `camels_clim.txt` | Standard scaling $(\mu, \sigma)_{\text{train}}$ | `test_static_isolation` |
| **B1** | `mahalanobis_forcing` | $\sqrt{(X_{t}^{\text{recent}} - \mu_X)^T \Sigma_X^{-1} (X_{t}^{\text{recent}} - \mu_X)}$ | $-$ | $[t-6, t]$ | Daymet Forcing | Mean/Covariance fit on $\mathcal{D}_{\text{train}}$ | `test_no_test_in_scaling` |
| **B2** | `prcp_3d_anomaly` | $\frac{\sum_{i=0}^2 P_{t-i} - \mu_{P3, b}}{\sigma_{P3, b} + \epsilon}$ | $-$ | $[t-2, t]$ | Daymet Forcing | Standard scaling fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **B3** | `tmax_anomaly` | $\frac{T_{\max, t} - \mu_{T\max, b}}{\sigma_{T\max, b} + \epsilon}$ | $-$ | $t$ | Daymet Forcing | Standard scaling fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **C1** | `forecast_point` | $\hat{Q}_{t+1, b}$ | $\text{mm/day}$ | Output at $t$ | Base Model $f_\theta$ | Division by $\sigma_{Q, b}$ | `test_feature_causality` |
| **C2** | `forecast_delta` | $\hat{Q}_{t+1, b} - Q_{t, b}$ | $\text{mm/day}$ | Output at $t$ | Base Model + USGS | Division by $\sigma_{Q, b}$ | `test_feature_causality` |
| **C3** | `forecast_flood_prob` | $\mathbb{I}(\hat{Q}_{t+1, b} > Q_{95, b})$ | $\{0, 1\}$ | Output at $t$ | Base Model + Train Q95 | None | `test_feature_causality` |
| **D1** | `cqr_interval_width` | $W_{t, b} = \hat{Q}_{t+1, b}^{\text{high}} - \hat{Q}_{t+1, b}^{\text{low}}$ | $\text{mm/day}$ | Output at $t$ | CQR Quantile Head | Division by $\sigma_{Q, b}$ | `test_feature_causality` |
| **D2** | `cqr_norm_width` | $W_{t, b} / (\hat{Q}_{t+1, b} + 0.1)$ | $-$ | Output at $t$ | CQR Quantile Head | Log1p transform | `test_feature_causality` |
| **D3** | `ensemble_std` | $\sigma_{t, b}^{\text{ens}} = \text{std}(\hat{Q}_{t+1, b}^{(1..5)})$ | $\text{mm/day}$ | Output at $t$ | 5 Base Seeds | Division by $\sigma_{Q, b}$ | `test_feature_causality` |
| **D4** | `ensemble_cv` | $\sigma_{t, b}^{\text{ens}} / (\bar{Q}_{t+1, b}^{\text{ens}} + 0.1)$ | $-$ | Output at $t$ | 5 Base Seeds | Log1p transform | `test_feature_causality` |
| **E1** | `api_14d` (Antecedent Prcp) | $\text{API}_t = \sum_{i=0}^{13} P_{t-i} \cdot (0.85)^i$ | $\text{mm}$ | $[t-13, t]$ | Daymet Forcing | Standard scaling fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **E2** | `runoff_ratio_7d_dev` | $\frac{\sum_{i=0}^6 Q_{t-i}}{\sum_{i=0}^6 P_{t-i} + 1.0} - \overline{RR}_{b, \text{month}}$ | $-$ | $[t-6, t]$ | USGS + Daymet | Historical monthly mean fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **E3** | `recession_rate_anomaly` | $(Q_t - Q_{t-1}) - (-a_b Q_{t-1}^{b_{\text{rec}}})$ (if $P_t=0$) | $\text{mm/day}$ | $[t-1, t]$ | USGS Streamflow | Master recession curve fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |
| **E4** | `water_balance_7d_proxy` | $\sum_{i=0}^6 (P_{t-i} - \hat{ET}_{0, t-i} - Q_{t-i})$ | $\text{mm}$ | $[t-6, t]$ | USGS + Daymet + Hargreaves | Division by $\sigma_{Q, b} \times 7$ | `test_feature_causality` |
| **E5** | `snowmelt_potential` | $\max(0, T_{\text{mean}, t}) \cdot \mathbb{I}(\text{SWE}_{t-1} > 0 \vee \text{FracSnow}_b > 0.3)$ | $^\circ\text{C}$ | $t$ | Daymet Forcing | Standard scaling fit on $\mathcal{D}_{\text{train}}$ | `test_feature_causality` |

---

## 11. PHYSICS & DOMAIN FEATURE FREEZE & SCIENTIFIC NOMENCLATURE

### Rigorous Categorization Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SCIENTIFIC EPISTEMIC TAXONOMY                         │
├────────────────────────────────┬────────────────────────────────────────────┤
│ PURE PHYSICS                   │ None at daily lumped catchment scale       │
│                                │ (due to unobserved storage change ΔS)      │
├────────────────────────────────┼────────────────────────────────────────────┤
│ HYDROLOGICAL DOMAIN KNOWLEDGE  │ Antecedent Precipitation Index (E1),       │
│                                │ Runoff Ratio Anomaly (E2),                 │
│                                │ Master Recession Anomaly (E3),             │
│                                │ Water Balance Residual Proxy (E4),         │
│                                │ Snowmelt Potential (E5)                    │
├────────────────────────────────┼────────────────────────────────────────────┤
│ STATISTICAL UNCERTAINTY        │ CQR Width (D1, D2), Ensemble Std (D3, D4)  │
├────────────────────────────────┼────────────────────────────────────────────┤
│ OUT-OF-DISTRIBUTION (OOD)      │ Mahalanobis Distance (B1),                 │
│                                │ Forcing Anomalies (B2, B3)                 │
├────────────────────────────────┼────────────────────────────────────────────┤
│ MODEL-DERIVED CONTEXT          │ Point Forecast (C1), Delta (C2),           │
│                                │ Current Flow Ratios (A1, A2, A3, A4)       │
└────────────────────────────────┴────────────────────────────────────────────┘
```

### Scientific Honesty Verdict & Nomenclature Freeze

> [!CAUTION]
> **MANDATORY TERMINOLOGY REFORM:** Catchment-scale hydrology operates without closed-form boundary conditions; subterranean storage change $\Delta S$ is unobserved at daily time scales. Calling empirical lumped diagnostics "First-Principles Physics" is scientifically indefensible and will invite immediate rejection from rigorous hydrology reviewers (WRR/HESS).

**WE OFFICIALLY FREEZE THE PROJECT TITLE AND FORMULATION AS:**
> **AETHER: Hydrologically Informed Reliability Estimation and Selective Forecasting for Environmental Extremes**

*(All references to "Physics-Guided Recursive Self-Verification" are permanently retired.)*

---

## 12. BASELINE MATRIX

To establish whether failure is predictable and whether hydrological signals add value, we freeze an exhaustive **8-Model Baseline Suite**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BASELINE PROGRESSION SUITE                        │
├──────┬────────────────────────┬─────────────────────────────────────────────┤
│ B0   │ Random Classifier      │ Permutation baseline                        │
│ B1   │ Climatology / Context  │ Calendar DOY + Long-term mean               │
│ B2   │ OOD-Only               │ Mahalanobis distance + Forcing anomalies    │
│ B3   │ Uncertainty-Only       │ CQR Width + Ensemble Spread                 │
│ B4   │ Context + Uncertainty  │ Context (A) + Uncertainty (D)               │
│ B5   │ Context + OOD + Uncert │ Context (A) + OOD (B) + Uncertainty (D)     │
│ B6   │ Hydro-Domain Only      │ Hydrological Features (E) only              │
│ B7   │ Full AETHER Model      │ All Feature Groups (A + B + C + D + E)      │
└──────┴────────────────────────┴─────────────────────────────────────────────┘
```

### Baseline Specifications

| ID | Model Identifier | Feature Subsets Included | Model Architecture | Scientific Role & Evaluation Purpose |
|:---:|:---|:---|:---|:---|
| **B0** | `Baseline_Random` | None | Uniform random score $R_t \sim \mathcal{U}(0, 1)$ | Theoretical zero-information floor. |
| **B1** | `Baseline_Context` | Group A (`A1–A5`) | LightGBM | Tests whether failure is simply predicted by season and baseflow level. |
| **B2** | `Baseline_OOD` | Group B (`B1–B3`) | LightGBM | Tests whether input-space distribution shift alone explains failure. |
| **B3** | `Baseline_Uncertainty`| Group D (`D1–D4`) | LightGBM | Tests whether standard model uncertainty (CQR width + ensemble spread) is sufficient. |
| **B4** | `Baseline_Context_Uncert` | Group A + Group D | LightGBM | Standard ML uncertainty baseline with climatological context. |
| **B5** | `Baseline_Context_OOD_Uncert` | Group A + Group B + Group D | LightGBM | SOTA general ML failure prediction baseline (equivalent to FIPER/SCRC). |
| **B6** | `Baseline_Hydro_Only` | Group E (`E1–E5`) | LightGBM | Tests predictive power of hydrological domain features in isolation. |
| **B7** | **`AETHER_Full`** | **Groups A + B + C + D + E** | **LightGBM** | **Full proposed system; evaluates incremental value $\Delta AUROC = B7 - B5$.** |

---

## 13. RELIABILITY ESTIMATOR SPECIFICATION

We freeze **LightGBM** (Light Gradient Boosting Machine) as the primary reliability estimator $g_\psi$.

```
Inputs Filtration I_t [d = 21 features]
                 │
      LightGBM GBDT Classifier (500 Trees, Depth 6)
                 │
      Raw Output Log-Odds z_t
                 │
      Platt Scaling / Isotonic Calibration (Fit on Validation Fold of Cal Split)
                 │
      Calibrated Failure Probability R_t = P̂(F_t = 1 | I_t) ∈ [0, 1]
```

### Hyperparameter & Training Protocol
* **Objective Function:** Binary Cross-Entropy (Logloss) with scale positive weight:
  $$\mathcal{L}_{\text{GBDT}}(y, p) = - \left( w_{\text{pos}} \cdot y \log(p) + (1-y)\log(1-p) \right)$$
  where $w_{\text{pos}} = \frac{N_{\text{neg}}}{N_{\text{pos}}}$ on $\mathcal{D}_{\text{cal}}$.
* **Tree Hyperparameters:**
  * `learning_rate`: $0.03$
  * `num_leaves`: $31$
  * `max_depth`: $6$
  * `min_child_samples`: $50$
  * `subsample` (bagging fraction): $0.80$
  * `colsample_bytree` (feature fraction): $0.80$
  * `n_estimators`: $500$ with Early Stopping (patience: 25 rounds on cal-validation fold).
* **Probability Calibration:** Isotonic Regression fit on out-of-fold predictions within $\mathcal{D}_{\text{cal}}$ to guarantee that $R_t = 0.80$ translates to an empirical $80\%$ failure rate.
* **Leakage-Free Label Generation:**
  1. Base model $f_\theta$ is trained strictly on $\mathcal{D}_{\text{train}}$ (`1980–2000`).
  2. Base model generates inference predictions $\hat{Q}_{t+1}$ on $\mathcal{D}_{\text{cal}}$ (`2005–2010`).
  3. Ground truth labels $F_{t, b}$ are computed on $\mathcal{D}_{\text{cal}}$.
  4. LightGBM $g_\psi$ is trained on $\mathcal{D}_{\text{cal}}$ and frozen.
  5. $g_\psi$ is evaluated on $\mathcal{D}_{\text{test}}$ (`2010–2018`). Base model never sees test labels; LightGBM never sees test data.

---

## 14. SELECTIVE ACTION POLICY

We explicitly **ELIMINATE** the complex, unproven multi-iteration recursive refinement loop and implement a mathematically rigorous **Selective Action Policy**: **RELEASE vs. ABSTAIN / HUMAN REVIEW**.

```
                                 Reliability Engine Output R_t
                                               │
                                 ┌─────────────┴─────────────┐
                                 │                           │
                            R_t ≤ τ                     R_t > τ
                                 │                           │
                                 ▼                           ▼
                           ACTION: RELEASE             ACTION: ABSTAIN
                          (Issue Forecast)         (Flag for Forecaster Review)
```

### Mathematical Policy Formulation
For a decision threshold $\tau \in [0, 1]$, the selective policy $\pi_\tau$ defines:
$$A_{t, b} = \begin{cases} \text{RELEASE} (\text{Accept}) & \text{if } R_{t, b} \le \tau \\ \text{ABSTAIN} (\text{Reject/Flag}) & \text{if } R_{t, b} > \tau \end{cases}$$

### Operational Metrics
1. **Coverage ($c(\tau)$):** Fraction of forecasts released to the operational pipeline:
   $$c(\tau) = \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} \mathbb{I}(R_i \le \tau)$$
2. **Selective Risk ($\mathcal{R}_{\text{sel}}(\tau)$):** Mean forecast error over accepted predictions:
   $$\mathcal{R}_{\text{sel}}(\tau) = \frac{\sum_{i=1}^{N_{\text{test}}} \mathcal{L}(\hat{Q}_i, Q_i) \cdot \mathbb{I}(R_i \le \tau)}{\sum_{i=1}^{N_{\text{test}}} \mathbb{I}(R_i \le \tau)}$$
   where $\mathcal{L}(\hat{Q}, Q) = |\hat{Q} - Q|$ (MAE) or $(\hat{Q} - Q)^2$ (MSE).
3. **Risk-Coverage Curve ($RC$):** The parametric trajectory of $(\text{Coverage}(\tau), \mathcal{R}_{\text{sel}}(\tau))$ as $\tau$ sweeps from $0$ to $1$.
4. **Area Under Risk-Coverage Curve ($AURC$):**
   $$\text{AURC} = \int_{0}^1 \mathcal{R}_{\text{sel}}(c) \, dc$$
5. **Threshold Calibration via Conformal Risk Control (CRC):**
   Given user risk tolerance $\alpha^*$, choose $\hat{\tau}$ on $\mathcal{D}_{\text{cal}}$:
   $$\hat{\tau} = \sup \left\{ \tau \in [0, 1] : \frac{1}{|\mathcal{D}_{\text{cal}}|}\sum_{i \in \mathcal{D}_{\text{cal}}} \mathcal{L}(\hat{Q}_i, Q_i)\mathbb{I}(R_i \le \tau) \le \alpha^* \right\}$$

---

## 15. EXPERIMENT MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXPERIMENT EXECUTION ROADMAP                      │
├─────────┬───────────────────────────────────────────────────────────────────┤
│ EXP 001 │ Failure Predictability Benchmark (The Foundational Experiment)    │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ EXP 002 │ Information Decomposition & Hydrological Incremental Value        │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ EXP 003 │ Selective Forecasting & Risk-Coverage Optimization                │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ EXP 004 │ Spatial / Ungauged Basin Generalization Benchmark                 │
└─────────┴───────────────────────────────────────────────────────────────────┘
```

### Detailed Experiment Specifications

#### EXP 001: Failure Predictability Benchmark
* **Core Question:** *"Can streamflow forecast failure be predicted at all from pre-outcome data before ground truth arrives?"*
* **Inputs:** Base model predictions $\hat{Q}$, uncertainty features $U_t$, context $C_t$, OOD features $B_t$, hydrological features $\Phi_t$ on $\mathcal{D}_{\text{cal}}$ and $\mathcal{D}_{\text{test}}$.
* **Method:** Train LightGBM reliability estimator on $\mathcal{D}_{\text{cal}}$; evaluate on $\mathcal{D}_{\text{test}}$ against Random (B0) and Climatology (B1).
* **Outputs:** Test $AUROC$, $AUPRC$, Brier Score, Reliability Diagram, Spearman $\rho(R_t, |e_t|)$.
* **Success Criterion:** $AUROC \ge 0.70$ and $AUPRC \ge 2.0 \times \pi_{\text{base}}$ with moving-block bootstrap $p < 0.001$.
* **Failure Criterion:** $AUROC \le 0.55$ or bootstrap $p \ge 0.05$ $\implies$ **STOP. Forecast failure is intrinsically unpredictable.**

#### EXP 002: Information Source Decomposition
* **Core Question:** *"Does hydrological domain knowledge provide statistically significant incremental information beyond standard uncertainty and OOD signals?"*
* **Inputs:** 8 Baseline models (B0 through B7).
* **Method:** Evaluate discrimination and calibration metrics across all 8 variants on $\mathcal{D}_{\text{test}}$. Perform paired DeLong tests and clustered block bootstrap tests on $\Delta AUROC$.
* **Outputs:** Feature importance table (SHAP values), $\Delta AUROC$, $\Delta AUPRC$, partial dependence plots.
* **Success Criterion:** $AUROC(\text{B7}) - AUROC(\text{B5}) \ge 0.03$ with paired clustered bootstrap $p < 0.01$.
* **Failure Criterion:** $\Delta AUROC \le 0.005$ or $p \ge 0.05$ $\implies$ **REVISE CLAIMS. Drop hydrological domain advantage; publish as general ML uncertainty post-processing.**

#### EXP 003: Selective Forecasting Utility
* **Core Question:** *"Does predicted failure risk enable effective selective forecasting that reduces error during extreme floods?"*
* **Inputs:** Calibrated reliability score $R_t$, point forecast $\hat{Q}_{t+1}$, ground truth $Q_{t+1}$ on $\mathcal{D}_{\text{test}}$.
* **Method:** Sweep threshold $\tau$; construct Risk-Coverage curves. Evaluate selective MAE/NSE on $Q > Q_{95}$ subset at $80\%$ and $90\%$ coverage.
* **Outputs:** $RC$ curves, $AURC$, $E\text{-}AURC$, Extreme Event Selective Risk Table.
* **Success Criterion:** $\ge 20\%$ MAE reduction on extreme events ($Q > Q_{95}$) at $80\%$ coverage compared to unconditional base model.
* **Failure Criterion:** Selective MAE reduction $< 5\%$ at $80\%$ coverage $\implies$ **Selective policy is practically unviable.**

#### EXP 004: Spatial / Ungauged Basin Generalization
* **Core Question:** *"Can a reliability estimator trained on gauged basins predict failure in completely unseen ungauged basins?"*
* **Inputs:** 425 Training basins, 106 strictly held-out test basins (Experiment B basin split).
* **Method:** Train base model and reliability estimator on 425 basins; evaluate on 106 held-out basins.
* **Outputs:** Ungauged $AUROC$, ungauged $AURC$, performance drop $\Delta AUROC_{\text{spatial}} = AUROC_{\text{gauged}} - AUROC_{\text{ungauged}}$.
* **Success Criterion:** Ungauged $AUROC \ge 0.65$ (retains $\ge 85\%$ of gauged discriminatory power).
* **Failure Criterion:** Ungauged $AUROC \le 0.55$ $\implies$ Reliability estimator requires local basin calibration.

---

## 16. ABLATION MATRIX

To isolate the exact contribution of each component, we execute the following frozen ablation suite:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FROZEN ABLATION SUITE                                     │
├─────────────────┬───────────┬─────────────┬──────────────┬──────────────────┬───────────────┤
│ Ablation ID     │ Context   │ OOD Features│ Uncertainty  │ Hydrological     │ Tested        │
│                 │ Group A   │ Group B     │ Group D      │ Group E          │ Hypothesis    │
├─────────────────┼:─────────:┼:───────────:┼:────────────:┼:────────────────:┼:─────────────:┤
│ ABL-0 (Full)    │     ✅    │      ✅     │      ✅      │        ✅        │ Full System   │
│ ABL-1 (No-Hydro)│     ✅    │      ✅     │      ✅      │        ❌        │ Test H2       │
│ ABL-2 (No-Uncert│     ✅    │      ✅     │      ❌      │        ✅        │ UQ Value      │
│ ABL-3 (No-OOD)  │     ✅    │      ❌     │      ✅      │        ✅        │ OOD Value     │
│ ABL-4 (No-Cont) │     ❌    │      ✅     │      ✅      │        ✅        │ Context Value │
│ ABL-5 (Hydro-Only)❌        │      ❌     │      ❌      │        ✅        │ Domain Alone  │
│ ABL-6 (Uncert-Only)❌       │      ❌     │      ✅      │        ❌        │ UQ Alone      │
└─────────────────┴───────────┴─────────────┴──────────────┴──────────────────┴───────────────┘
```

### Single-Feature Leave-One-Out Ablations
For Group E (Hydrological Domain), evaluate marginal contribution by dropping one feature at a time:
1. `ABL-E1-Drop-API`: Drop Antecedent Precipitation Index ($API_{14d}$).
2. `ABL-E2-Drop-RunoffRatio`: Drop Runoff Ratio Anomaly ($RR_{\text{dev}}$).
3. `ABL-E3-Drop-Recession`: Drop Baseflow Recession Anomaly.
4. `ABL-E4-Drop-WaterBalance`: Drop Water Balance Residual Proxy.
5. `ABL-E5-Drop-Snowmelt`: Drop Snowmelt Potential Proxy.

---

## 17. STATISTICAL EVALUATION & RESAMPLING PROTOCOL

To ensure that reported results are not artifacts of temporal autocorrelation, spatial clustering, or multiple comparisons, we enforce a **Four-Pillar Statistical Verification Protocol**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STATISTICAL TESTING ARCHITECTURE                      │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Discrimination    │ AUROC, AUPRC (with Base Rate Benchmark),             │
│                      │ Spearman Rank Correlation ρ(R_t, |e_t|)              │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 2. Calibration       │ Brier Score, Expected Calibration Error (ECE, 10 bin)│
│                      │ Reliability Diagram Intercept & Slope                │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 3. Selective Utility │ Area Under Risk-Coverage (AURC), Excess-AURC,        │
│                      │ Selective MAE / NSE at Coverage c ∈ {0.7, 0.8, 0.9} │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 4. Resampling Tests  │ Block Bootstrap (Temporal, Block = 30d),             │
│                      │ Clustered Basin Bootstrap (Spatial, B = 10,000),      │
│                      │ Benjamini-Hochberg False Discovery Rate (FDR = 0.05) │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

### Statistical Methodology Rules
1. **No Naive IID Tests:** Standard Student's t-test and naive likelihood ratio tests are strictly prohibited due to severe serial correlation ($\rho_1 \approx 0.9$) and spatial clustering.
2. **Moving Block Bootstrap:** When assessing temporal metrics, resample time blocks of $L_{\text{block}} = 30$ continuous days ($B = 10,000$ iterations) to compute empirical $95\%$ confidence intervals.
3. **Clustered Basin Bootstrap:** When assessing CONUS-wide metric superiority, resample entire basins with replacement ($B = 10,000$) to account for cross-basin spatial correlation.
4. **Multiple Testing Correction:** When reporting basin-specific statistical significance across 531 basins, apply the Benjamini-Hochberg (BH) procedure with False Discovery Rate $q = 0.05$.

---

## 18. AUTOMATED LEAKAGE TEST SUITE

The 14 leakage rules established in Phase 0.9 are formalized as automated, executable unit/integration test assertions that run in CI/CD before any experiment executes.

```
========================================================================================================
LEAKAGE TEST SUITE (14 AUTOMATED INTEGRATION CHECKS)
========================================================================================================
```

| Rule # | Test Name | Python Assertion / Execution Logic | Failure Behavior |
|:---:|:---|:---|:---|
| **L01** | `test_temporal_order_strictly_monotonic` | `assert (df['date'].diff().iloc[1:] == pd.Timedelta(days=1)).all()` | Fatal Error: Abort Pipeline |
| **L02** | `test_lookback_window_boundary_isolation` | Receptive field for index $t$ must strictly span $[t-364, t]$. Assert no timestamp in input tensor $> t$. | Fatal Error: Abort Training |
| **L03** | `test_feature_timestamp_pre_outcome` | For target $Q_{t+1}$, assert all forcing/state features have timestamp $\le t$. Assert $P_{t+1}, T_{t+1}$ not in feature matrix. | Fatal Error: Abort Feature Extractor |
| **L04** | `test_no_ground_truth_in_feature_matrix` | Assert target variable `streamflow` column is absent from feature tensor $X_t$ at forecast time. | Fatal Error: Abort Feature Extractor |
| **L05** | `test_reliability_estimator_cal_split_only` | Assert LightGBM training index set $\subseteq \mathcal{D}_{\text{cal}}$ (`2005-10-01` to `2010-09-30`). Assert $\mathcal{D}_{\text{test}} \cap \mathcal{D}_{\text{train\_gpsi}} = \emptyset$. | Fatal Error: Reject Model Checkpoint |
| **L06** | `test_conformal_calibrator_split_isolation` | Assert CQR nonconformity scores $\{s_i\}$ computed strictly over $\mathcal{D}_{\text{cal}}$. Assert zero test instances in calibrator. | Fatal Error: Invalidate Conformal Bounds |
| **L07** | `test_normalization_derived_from_train` | Assert scaler parameters $(\mu, \sigma)$ match $\mathcal{D}_{\text{train}}$ statistics within numerical precision $10^{-6}$. | Fatal Error: Abort Scaler Pipeline |
| **L08** | `test_spatial_holdout_basins_disjoint` | For spatial experiments, assert $\text{Basins}_{\text{train}} \cap \text{Basins}_{\text{test}} = \emptyset$. | Fatal Error: Abort Spatial Split |
| **L09** | `test_embargo_gap_between_splits` | Assert gap between $\text{Train}_{\text{end}}$ and $\text{Cal}_{\text{start}}$, and $\text{Cal}_{\text{end}}$ and $\text{Test}_{\text{start}}$ is $\ge 366$ days of non-loss-evaluated buffer. | Fatal Error: Abort Dataset Loader |
| **L10** | `test_flood_threshold_quantiles_train_only`| Assert $Q_{95, b}$ quantiles match empirical distribution of $\mathcal{D}_{\text{train}}$ exactly. | Fatal Error: Invalidate Labels |
| **L11** | `test_selective_threshold_frozen_on_cal` | Assert gating threshold $\hat{\tau}$ is determined on $\mathcal{D}_{\text{cal}}$ and passed as constant scalar to test evaluator. | Fatal Error: Invalidate Evaluation |
| **L12** | `test_hydro_signatures_historical_only` | Assert master recession curves and runoff ratios are parameterized over $\mathcal{D}_{\text{train}}$ only. | Fatal Error: Invalidate Features |
| **L13** | `test_test_set_predictions_never_influence_weights` | Assert base model and reliability estimator hashes match pre-test checkpoints. | Fatal Error: Abort Evaluation |
| **L14** | `test_deterministic_reproducibility_via_hash`| Assert exact hash match of generated feature arrays across repeated runs with identical random seed. | Fatal Error: Invalidate Run |

---

## 19. REPOSITORY ARCHITECTURE

```
aether/
├── configs/                             # Hydra / YAML experiment configurations
│   ├── base_lstm_camels.yaml            # Base EA-LSTM configuration
│   ├── cqr_uncertainty.yaml             # CQR uncertainty configuration
│   ├── reliability_lightgbm.yaml        # LightGBM reliability estimator config
│   ├── selective_policy.yaml            # Selective forecasting threshold config
│   └── experiments/
│       ├── exp001_failure_pred.yaml     # Exp 001 pipeline configuration
│       ├── exp002_ablation.yaml         # Exp 002 ablation configuration
│       ├── exp003_selective.yaml        # Exp 003 selective forecasting config
│       └── exp004_spatial_holdout.yaml  # Exp 004 spatial generalization config
├── data/                                # Data ingestion, caching, and preprocessing
│   ├── camels_loader.py                 # CAMELS-US v1.2 file parsing and QC
│   ├── split_manager.py                 # Temporal and spatial split management
│   ├── normalizer.py                    # Leakage-free feature scaling
│   └── signatures.py                    # Historical catchment signature computation
├── forecasting/                         # Base forecasting engine
│   ├── nh_adapter.py                    # NeuralHydrology EA-LSTM wrapper
│   ├── ensemble_trainer.py              # 5-seed deep ensemble manager
│   └── inferencer.py                    # Out-of-sample inference generator
├── uncertainty/                         # Uncertainty quantification modules
│   ├── quantile_loss.py                 # Pinball loss implementation
│   ├── cqr_calibrator.py                # Conformalized Quantile Regression engine
│   └── ensemble_uncertainty.py          # Epistemic spread and CV extractor
├── labels/                              # Ground truth failure label generators
│   ├── nafe_label.py                    # Primary NAFE failure label generator
│   ├── flood_threshold_label.py         # Secondary FTDD label generator
│   ├── interval_miss_label.py           # Secondary PCIM label generator
│   └── peak_error_label.py              # Secondary PMRE label generator
├── features/                            # Causal feature extraction pipeline
│   ├── context_features.py              # Group A (flow level, DOY, aridity)
│   ├── ood_features.py                  # Group B (Mahalanobis, forcing anomalies)
│   ├── model_features.py                # Group C (point forecast, delta)
│   ├── uncertainty_features.py          # Group D (CQR width, ensemble std)
│   ├── hydro_features.py                # Group E (API, runoff ratio, recession)
│   └── feature_registry.py              # Master pipeline orchestrator & contract validator
├── reliability/                         # Reliability estimation engine
│   ├── lightgbm_estimator.py            # LightGBM failure classifier
│   ├── probability_calibrator.py        # Isotonic regression / Platt scaling
│   └── feature_importance.py            # SHAP value decomposition
├── selection/                           # Selective decision policy
│   ├── threshold_tuner.py               # CRC-based threshold calibrator
│   ├── policy_evaluator.py              # Release vs. Abstain execution
│   └── risk_coverage_curve.py           # RC trajectory generator
├── evaluation/                          # Statistical evaluation & resampling
│   ├── metrics.py                       # AUROC, AUPRC, Brier, AURC, NSE, KGE
│   ├── bootstrap_temporal.py            # Moving block bootstrap (30-day block)
│   ├── bootstrap_spatial.py             # Clustered basin bootstrap
│   └── fdr_correction.py                # Benjamini-Hochberg correction
├── experiments/                         # Executable experiment entry points
│   ├── run_exp001_failure_pred.py
│   ├── run_exp002_ablation.py
│   ├── run_exp003_selective.py
│   └── run_exp004_spatial.py
├── tests/                               # Test suite
│   ├── leakage/                         # 14 automated leakage tests (Section 18)
│   │   ├── test_causality.py
│   │   ├── test_splits.py
│   │   └── test_normalization.py
│   └── unit/                            # Unit tests for components
│       ├── test_cqr.py
│       ├── test_hydro_features.py
│       └── test_lightgbm.py
├── pyproject.toml                       # Build & dependency management
└── README.md                            # Comprehensive execution guide
```

---

## 20. REPRODUCIBILITY CONTRACT

```
===============================================================================
REPRODUCIBILITY CONTRACT & EXECUTION SPECIFICATION
===============================================================================
Python Runtime:        Python 3.10.13 (x86_64)
Dependency Tool:       uv (Fast, deterministic lockfile via uv.lock)
Deep Learning Stack:   PyTorch 2.2.1 + CUDA 12.1
Hydrological Stack:    neuralhydrology 1.1.0
Tabular / ML Stack:    lightgbm 4.3.0, scikit-learn 1.4.1, scipy 1.12.0
Data Handling:         pandas 2.2.1, numpy 1.26.4, xarray 2024.2.0
Experiment Tracking:   MLflow 2.11.0 (local SQLite backend)
Hardware Target:       1x NVIDIA GPU (A100 / V100 / RTX 4090 with ≥ 16GB VRAM)
===============================================================================
```

### Deterministic Seed Contract
* **Global Master Seeds:** Base models trained with seeds `101, 102, 103, 104, 105`.
* **Reliability GBDT Seed:** `42`.
* **Bootstrap Resampling Seed:** `2026`.
* **PyTorch Determinism Flags:**
  ```python
  torch.manual_seed(seed)
  torch.cuda.manual_seed_all(seed)
  np.random.seed(seed)
  random.seed(seed)
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  ```

---

## 21. FIRST IMPLEMENTATION MILESTONE (MILESTONE 1.0)

Milestone 1.0 is formally **COMPLETE** when and only when the following 6 concrete deliverables exist and pass verification:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MILESTONE 1.0 COMPLETION CRITERIA                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ [1] Base Model Training: 5-seed EA-LSTM trained on CAMELS-US (1980–2000).   │
│     Benchmark verification: Mean test NSE across 531 basins ≥ 0.70.         │
│                                                                             │
│ [2] Out-of-Sample Predictions: Point and CQR uncertainty predictions        │
│     generated for Calibration (2005–2010) and Test (2010–2018) splits.      │
│                                                                             │
│ [3] Feature Matrix Generation: Full 21-feature contract extracted across    │
│     all splits and stored in Parquet format with SHA-256 validation.        │
│                                                                             │
│ [4] Leakage Suite Validation: 100% pass rate across all 14 automated        │
│     leakage tests (`pytest tests/leakage/`).                                │
│                                                                             │
│ [5] Exp 001 Execution: LightGBM reliability estimator trained on Cal split; │
│     AUROC, AUPRC, and Spearman ρ computed on held-out Test split.           │
│                                                                             │
│ [6] Milestone Report Artifact: Generated markdown summary documenting       │
│     whether H1 is supported (test AUROC ≥ 0.70, p < 0.001).                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 22. OBJECTIVE KILL & PIVOT CRITERIA

```
========================================================================================================
OBJECTIVE KILL / PIVOT DECISION FRAMEWORK
========================================================================================================
```

| Decision Level | Trigger Condition on Test Split | Mandatory Strategic Action | Scientific Rationale |
|:---|:---|:---|:---|
| 🔴 **FATAL KILL** | Exp 001 yields test $AUROC \le 0.55$ or block bootstrap $p \ge 0.05$ against Random. | **TERMINATE THE RELIABILITY/SELECTION RESEARCH PROGRAM.** Pivot thesis to *"Conformal Prediction under Hydrological Distribution Shift"* or document the definitive negative result. | Pre-outcome failure prediction is statistically impossible; further engineering is pointless. |
| 🟡 **PIVOT CLAIM** | Exp 002 yields $\Delta AUROC = AUROC(\text{B7}) - AUROC(\text{B5}) \le 0.005$ or $p \ge 0.05$. | **DROP ALL HYDROLOGICAL/PHYSICS INCREMENTAL CLAIMS.** Reframe paper purely as an empirical evaluation of general ML uncertainty and selective prediction in hydrology. | Hydrological features provide no non-redundant signal beyond standard uncertainty metrics. |
| 🟡 **SIMPLIFY POLICY** | Exp 003 yields $< 5\%$ selective risk reduction at $80\%$ coverage during extreme floods ($Q > Q_{95}$). | **ELIMINATE SELECTIVE FORECASTING CLAIMS.** Present the reliability score strictly as a passive diagnostic indicator, not an active decision policy. | Selective abstention provides insufficient operational benefit to justify withholding forecasts. |
| 🟢 **PROCEED** | Exp 001 $AUROC \ge 0.70$ ($p < 0.001$), Exp 002 $\Delta AUROC \ge 0.03$ ($p < 0.01$), Exp 003 Risk Reduction $\ge 20\%$. | **FULL EXECUTION & Q1 MANUSCRIPT DRAFTING.** Target *Water Resources Research* (WRR) or *Hydrology and Earth System Sciences* (HESS). | Complete scientific vindication across all three hypotheses. |

---

## 23. ANTI-SCOPE (WHAT WE WILL NOT IMPLEMENT)

To protect the project from catastrophic scope creep and maintain strict execution velocity, the following technologies and features are **EXPLICITLY EXCLUDED FROM PHASE 1.0**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXPLICIT ANTI-SCOPE LIST                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ ❌ No Transformer / Diffusion Base Models (EA-LSTM is the frozen baseline)   │
│ ❌ No Recursive Refinement Loops (Strictly one-shot selective release/abstain)│
│ ❌ No Multi-Horizon Forecasting (Frozen strictly at h = 1 day lead time)     │
│ ❌ No Multi-Dataset Ingestion (CAMELS-GB and Caravan-India deferred to V2)   │
│ ❌ No Large Language Models (LLMs) or Agentic Critique Frameworks            │
│ ❌ No 2D Hydrodynamic / Inundation Modeling (HEC-RAS, LISFLOOD, DEM mapping) │
│ ❌ No Full-Stack Web Dashboards, React Frontends, or FastAPI Microservices   │
│ ❌ No Docker / Kubernetes Deployment Orchestration                           │
│ ❌ No Multi-Hazard Disasters (Strictly riverine streamflow forecasting)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 24. FINAL IMPLEMENTATION READINESS CHECKLIST

```
========================================================================================================
FINAL IMPLEMENTATION READINESS CHECKLIST
========================================================================================================
[X] READY   1. RESEARCH QUESTION: Frozen, precise, and falsifiable (Section 1).
[X] READY   2. HYPOTHESES: H1, H2, H3 with exact mathematical falsification bounds (Section 2).
[X] READY   3. FORMAL MATHEMATICS: Complete variable filtration taxonomy defined (Section 3).
[X] READY   4. FAILURE LABELS: 1 Primary (NAFE) + 4 Secondary labels mathematically specified (Section 4).
[X] READY   5. DATASET CONTRACT: CAMELS-US v1.2 files, columns, units, and QC locked (Section 5).
[X] READY   6. TEMPORAL SPLITS: 4-way disjoint splits with 366-day embargo locked (Section 6).
[X] READY   7. BASIN SPLITS: Temporal, Spatial, and Climate regimes locked (Section 7).
[X] READY   8. BASE MODEL: NeuralHydrology EA-LSTM architecture & hyperparameters frozen (Section 8).
[X] READY   9. UNCERTAINTY: Two-tier CQR + Deep Ensemble spread frozen (Section 9).
[X] READY  10. FEATURE REGISTRY: 21 pre-outcome features with formulas and units frozen (Section 10).
[X] READY  11. DOMAIN NOMENCLATURE: Scientifically honest naming and categorization locked (Section 11).
[X] READY  12. BASELINE MATRIX: 8 distinct baseline models specified (Section 12).
[X] READY  13. RELIABILITY ESTIMATOR: LightGBM GBDT + probability calibrator locked (Section 13).
[X] READY  14. SELECTIVE POLICY: Release vs. Abstain policy with CRC risk control locked (Section 14).
[X] READY  15. EXPERIMENT MATRIX: Exp 001 through Exp 004 execution contracts locked (Section 15).
[X] READY  16. ABLATION MATRIX: Full component-wise and leave-one-out suite frozen (Section 16).
[X] READY  17. STATISTICAL PROTOCOL: Moving block & clustered bootstrap testing locked (Section 17).
[X] READY  18. LEAKAGE TEST SUITE: 14 automated CI unit/integration assertions locked (Section 18).
[X] READY  19. REPOSITORY ARCHITECTURE: Complete directory layout & module roles locked (Section 19).
[X] READY  20. REPRODUCIBILITY: Python 3.10, uv, seed contract, and MLflow tracking locked (Section 20).
[X] READY  21. MILESTONE CRITERIA: Exact Definition of Done for Milestone 1.0 locked (Section 21).
[X] READY  22. KILL/PIVOT CRITERIA: Quantitative kill and claim-pivot thresholds locked (Section 22).
[X] READY  23. ANTI-SCOPE: Scope boundaries permanently frozen (Section 23).
========================================================================================================
```

---

## 25. FINAL FREEZE DECISION

```
========================================================================================================
                                   FINAL VERDICT:
                             🟢 IMPLEMENTATION READY
========================================================================================================
The conceptual research phase for AETHER is officially closed. All theoretical ambiguities,
mathematical definitions, label formulations, feature contracts, and leakage safeguards are fully
resolved. The engineering implementation of Milestone 1.0 may begin immediately.
========================================================================================================
```

---

# IMPLEMENTATION START POINT: THE FIRST 10 ENGINEERING TASKS

The following 10 tasks must be executed sequentially. Completing Task 10 yields the first scientifically meaningful result from AETHER.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FIRST 10 ENGINEERING TASKS                            │
├─────────┬───────────────────────────────────────────────────────────────────┤
│ TASK 01 │ Initialize repository skeleton, virtual environment with `uv`,   │
│         │ and install pinned dependencies (PyTorch, NeuralHydrology, GBDT). │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 02 │ Download and verify CAMELS-US v1.2 dataset (531 basins) with      │
│         │ automated SHA-256 checksum validation.                            │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 03 │ Implement `split_manager.py` to generate the 4-way temporal       │
│         │ splits (Train, Val, Cal, Test) with 366-day lookback buffers.     │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 04 │ Train the 5-seed base EA-LSTM ensemble using NeuralHydrology and  │
│         │ verify mean Test NSE ≥ 0.70 across 531 benchmark catchments.      │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 05 │ Implement auxiliary multi-quantile LSTM head and calibrate CQR    │
│         │ prediction intervals on the Calibration split (2005–2010).        │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 06 │ Implement failure label generators (`nafe_label.py` and secondary │
│         │ labels) with training-period quantile normalization.              │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 07 │ Implement causal feature extraction pipeline (`features/`) for    │
│         │ all 21 features across Context, OOD, Uncertainty, and Hydro.      │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 08 │ Implement and execute the 14-point Automated Leakage Test Suite   │
│         │ (`tests/leakage/`) and achieve a 100% pass rate.                  │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 09 │ Train and calibrate the LightGBM reliability estimator on the     │
│         │ Calibration split feature matrix.                                 │
├─────────┼───────────────────────────────────────────────────────────────────┤
│ TASK 10 │ Execute **Experiment 001** (Failure Predictability Benchmark) on   │
│         │ held-out Test split (2010–2018) and compute block-bootstrapped    │
│         │ AUROC, AUPRC, Brier Score, and Risk-Coverage curves.             │
└─────────┴───────────────────────────────────────────────────────────────────┘
```
