# CAMELS-US Dataset Provenance & Data Contract

**Document Version:** 1.0.0  
**Status:** Authoritative Scientific Provenance Record (Milestone R1.9)  
**Scope:** Raw dataset identity, benchmark catchment registry, schema contracts, quality control invariants, and reproducibility protocols for CAMELS-US in AETHER.

---

## 1. Executive Summary & Epistemic Boundaries

This document defines the exact data provenance, schema expectations, and scientific invariants governing the use of the **Catchment Attributes and Meteorology for Large-Sample Studies (CAMELS-US)** dataset within the AETHER research framework.

To eliminate ambiguity and prevent conflation between external facts and project decisions, all statements in this document are explicitly categorized into four epistemic tiers:

1. **[SOURCE FACT]**: Verifiable metadata and physical structures documented by the upstream dataset creators (NCAR / USGS).
2. **[LOCAL OBSERVATION]**: Empirical observations verified against the canonical local filesystem distribution (`D:\CAMELS_US\basin_dataset_public_v1p2`).
3. **[AETHER POLICY]**: Methodological choices, quality control thresholds, and unit transformations adopted by the AETHER framework.
4. **[RESEARCH FREEZE]**: Immutable scientific benchmark protocols governing the Phase 1.0 experimental evaluation.

---

## 2. Dataset Identity & Upstream Provenance

### 2.1 Upstream Dataset Identity
* **[SOURCE FACT] Name:** Catchment Attributes and Meteorology for Large-Sample Studies (CAMELS-US).
* **[SOURCE FACT] Release Version:** Version 1.2 (public release date: March 11, 2016 per upstream `readme_FIRST.txt`).
* **[SOURCE FACT] Originating Institution:** National Center for Atmospheric Research (NCAR), Research Applications Laboratory (RAL) / Hydrometeorological Applications Program (HAP).
* **[SOURCE FACT] Primary Authors / Compilers:** A. J. Newman, M. P. Clark, K. Sampson, A. Wood, L. E. Hay, A. Bock, R. J. Viger, D. Blodgett, F. G. Freire, N. Mizukami, and J. R. Arnold.
* **[SOURCE FACT] Canonical Publication:**
  > Newman, A. J., Clark, M. P., Sampson, K., Wood, A., Hay, L. E., Bock, A., Viger, R. J., Blodgett, D., Freire, F. G., Mizukami, N., and Arnold, J. R. (2015): *Development of a large-sample watershed-scale hydrometeorological dataset for the contiguous USA: dataset characteristics and assessment of regional variability in hydrologic model performance*, Hydrology and Earth System Sciences (HESS), 19, 209–223, doi:[10.5194/hess-19-209-2015](https://doi.org/10.5194/hess-19-209-2015).
* **[SOURCE FACT] Catchment Attributes Reference:**
  > Addor, N., Newman, A. J., Mizukami, N., and Clark, M. P. (2017): *The CAMELS data set: catchment attributes and meteorology for large-sample studies*, Hydrology and Earth System Sciences (HESS), 21, 5293–5313, doi:[10.5194/hess-21-5293-2017](https://doi.org/10.5194/hess-21-5293-2017).
* **[AETHER POLICY] Permanent Upstream Archival Identifiers:** Permanent DOI landing pages and HydroShare archive identifiers are not currently recorded in AETHER provenance metadata; version tracking relies on the verified v1.2 release headers and file manifests.

### 2.2 Canonical Local Distribution
* **[AETHER POLICY] Canonical Local Directory Name:** `basin_dataset_public_v1p2` (relative to the configured `data_dir` or local dataset root).
* **[LOCAL OBSERVATION] Canonical Local Verification Path:** `D:\CAMELS_US\basin_dataset_public_v1p2`.
* **[AETHER POLICY] Deprecated / Excluded Siblings:** The adjacent directory `D:\CAMELS_US\basin_dataset_public` represents an older/different distribution (v1.0/v1.1) and is strictly **prohibited** from being used as a source or fallback in AETHER.

---

## 3. Benchmark Catchment Registry (531 Basins)

### 3.1 Benchmark Population Provenance
* **[SOURCE FACT] Full Catchment Set:** The raw CAMELS-US dataset contains 671 minimally impacted catchments across CONUS.
* **[SOURCE FACT] 531 Benchmark Subset Origin:** Newman et al. (2017) and subsequently standardized in large-sample deep learning hydrology by Kratzert et al. (2019):
  > Kratzert, F., Klotz, D., Shalev, G., Günther, G., Rubin, M., and Hochreiter, S. (2019): *Towards learning universal, regional, and local hydrological behaviors via machine learning applied to large-sample datasets*, Hydrology and Earth System Sciences (HESS), 23, 5089–5110, doi:[10.5194/hess-23-5089-2019](https://doi.org/10.5194/hess-23-5089-2019).
* **[SOURCE FACT] Selection Criteria:**
  1. Catchment drainage area $\le 2000 \text{ km}^2$.
  2. Discrepancy between USGS GAGES-II drainage area and Geospatial Fabric drainage area $\le 10\%$.
* **[AETHER POLICY] Upstream Source URL:** `https://raw.githubusercontent.com/kratzert/ealstm_regional_modeling/master/data/basin_list.txt`.

### 3.2 Packaged Registry & Cryptographic Verification
* **[AETHER POLICY] Packaged Manifest File:** [`aether/data/camels_us_benchmark_531.json`](file:///d:/Aether/aether/data/camels_us_benchmark_531.json).
* **[AETHER POLICY] In-Code Loader & Registry:** [`aether/data/basin_registry.py`](file:///d:/Aether/aether/data/basin_registry.py) (`BenchmarkRegistry`).
* **[SOURCE FACT] Upstream Raw File SHA-256 Digest:**
  ```text
  c3fb069f9fe644ed3102edca456989393ce28ee4864283c1fe37d5db6562bddf
  ```
* **[AETHER POLICY] AETHER Manifest SHA-256 Digest:**
  ```text
  8d046962308a47df40fa9aa690209c98d331982cd3db480cee2885f0681e69ce
  ```
  *Verification command:*
  ```bash
  uv run python -c "from aether.data.basin_registry import compute_manifest_sha256; print(compute_manifest_sha256())"
  ```
* **[AETHER POLICY] Immutability:** The 531-basin registry is immutable and bundled with the software repository to guarantee offline reproducibility without network calls.

---

## 4. Directory Structure & Required Components

### 4.1 Canonical Logical Hierarchy
A standard CAMELS-US v1.2 distribution contains multiple subdirectories. AETHER strictly relies on the following logical hierarchy:

```text
<data_dir>/
├── basin_dataset_public_v1p2/
│   ├── basin_metadata/
│   │   ├── gauge_information.txt                        # [REQUIRED] Station IDs, HUC-02, names, coords
│   │   └── basin_physical_characteristics.txt           # [REQUIRED] Geospatial Fabric areas (Size(km2))
│   ├── basin_mean_forcing/
│   │   └── daymet/                                      # [REQUIRED] Primary meteorological forcings
│   │       ├── 01/ ... 18/                              # HUC-02 subdirectories
│   │       │   └── <basin_id>_lump_cida_forcing_leap.txt
│   └── usgs_streamflow/                                 # [REQUIRED] Ground-truth streamflow
│       ├── 01/ ... 18/                                  # HUC-02 subdirectories
│       │   └── <basin_id>_streamflow_qc.txt
└── camels_attributes_v2.0/                              # [REQUIRED for attributes]
    ├── camels_topo.txt                                  # Topographic attributes (area_gages2)
    ├── camels_clim.txt                                  # Climatic attributes
    ├── camels_soil.txt                                  # Soil characteristics
    ├── camels_vege.txt                                  # Vegetation indices
    ├── camels_geol.txt                                  # Geology & permeability
    └── camels_hydro.txt                                 # Hydrologic signatures
```

### 4.2 Required vs. Optional Distribution Contents
* **[AETHER POLICY] Required Components:** `basin_mean_forcing/daymet/`, `usgs_streamflow/`, `basin_metadata/` (specifically `gauge_information.txt` and `basin_physical_characteristics.txt`), and static attribute tables (`camels_topo.txt`, `camels_clim.txt`, etc.).
* **[LOCAL OBSERVATION] Non-Required Distribution Contents:** The raw distribution also includes `basin_mean_forcing/maurer/`, `basin_mean_forcing/nldas/`, `elev_bands_forcing/`, `hru_forcing/`, and `shapefiles/`. These components are present in `basin_dataset_public_v1p2` but are **not** loaded or required by the baseline AETHER pipeline.

---

## 5. Schema Contracts & Data Formats

### 5.1 Daymet Meteorological Forcing
* **[SOURCE FACT] File Path Pattern:** `basin_mean_forcing/daymet/<HUC_02>/<basin_id>_lump_cida_forcing_leap.txt`.
* **[SOURCE FACT] Metadata Preamble:** Lines 1–3 contain catchment coordinate and elevation metadata. Line 4 contains the column headers.
* **[SOURCE FACT] Exact Header Spelling:**
  ```text
  Year Mnth Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)
  ```
  *(Note: Month is spelled `Mnth`).*
* **[SOURCE FACT] Column Semantics & Units:**
  - `Year`, `Mnth`, `Day`: Gregorian calendar date components.
  - `Hr`: Timestamp hour (consistently set to `12` noon local standard time).
  - `dayl(s)`: Day length in seconds.
  - `prcp(mm/day)`: Total daily precipitation ($P$).
  - `srad(W/m2)`: Incident shortwave radiation ($R_{\text{sw}}$).
  - `swe(mm)`: Snow water equivalent.
  - `tmax(C)`: Daily maximum 2m air temperature ($T_{\max}$).
  - `tmin(C)`: Daily minimum 2m air temperature ($T_{\min}$).
  - `vp(Pa)`: Daily average water vapor pressure ($V_p$).
* **[SOURCE FACT] Leap-Year Accounting:** Files bearing the `_forcing_leap.txt` suffix explicitly include leap days (February 29).
* **[AETHER POLICY] Parser Invariants:** Enforced by [`aether/data/camels_loader.py`](file:///d:/Aether/aether/data/camels_loader.py#L43) (`validate_forcing_schema`). Requires strict numeric types, non-null values, non-infinite values, and strictly monotonic, duplicate-free daily calendar dates.

### 5.2 USGS Streamflow Observations
* **[SOURCE FACT] File Path Pattern:** `usgs_streamflow/<HUC_02>/<basin_id>_streamflow_qc.txt`.
* **[SOURCE FACT] File Structure:** Whitespace-delimited ASCII, **no header line**.
* **[SOURCE FACT] Column Ordering:**
  1. `GAGEID`: 8-digit USGS stream gauge identifier.
  2. `Year`: 4-digit calendar year.
  3. `Month`: 1- or 2-digit calendar month.
  4. `Day`: 1- or 2-digit calendar day.
  5. `Streamflow(cfs)`: Mean daily discharge in cubic feet per second ($\text{cfs}$).
  6. `QC_flag`: Quality flag string assigned by USGS / NCAR.
* **[SOURCE FACT] Quality Flags:**
  - `A`: Certified actual daily mean discharge.
  - `A:e`: Certified estimated daily mean discharge.
  - `A:<`: Approved discharge below measurement threshold.
  - `M`: Missing discharge record.
* **[SOURCE FACT] Missing Sentinel:** Missing streamflow values in raw files are coded as `-999.00`.
* **[AETHER POLICY] Validity Invariant:** Zero flow (`Streamflow(cfs) == 0.0`) is scientifically valid. Negative values ($< 0$) and flag `M` denote unobserved ground truth.

---

## 6. Unit Transformations & QC Invariants

### 6.1 Discharge Unit Conversion (cfs to mm/day)
* **[AETHER POLICY] Mathematical Transformation:** Handled purely by [`aether/data/camels_loader.py`](file:///d:/Aether/aether/data/camels_loader.py#L127) (`convert_discharge_cfs_to_mm_day`).
  $$Q\,(\text{mm/day}) = Q\,(\text{cfs}) \times \frac{0.028316846592 \times 86400 \times 1000}{A_{\text{basin}}\,(\text{km}^2) \times 1\,000\,000} = Q\,(\text{cfs}) \times \frac{2.4465755455488}{A_{\text{basin}}\,(\text{km}^2)}$$
* **[AETHER POLICY] Catchment Area for Normalization:** The drainage area $A_{\text{basin}}$ must strictly be the authoritative `area_gages2` (in $\text{km}^2$) from `camels_topo.txt`.
* **[AETHER POLICY] Non-Destructive Invariant:** Conversion is a pure linear scale transformation. Missing sentinels (`-999.00`) are not dropped or clipped during unit conversion; QC masking is strictly separated into the QC layer.

### 6.2 Catchment Area Consistency Verification
* **[AETHER POLICY] Authoritative Field:** `area_gages2` ($\text{km}^2$) from `camels_topo.txt` (USGS GAGES-II official survey).
* **[AETHER POLICY] Comparison Field:** `Size(km2)` from `basin_metadata/basin_physical_characteristics.txt` (Geospatial Fabric delineation).
* **[AETHER POLICY] Consistency Invariant:** Handled by [`aether/data/qc.py`](file:///d:/Aether/aether/data/qc.py#L225) (`validate_basin_area_consistency`):
  $$\frac{|\text{area\_gages2} - \text{Size(km2)}|}{\text{area\_gages2}} \le 0.01 \quad (1.0\%)$$
  Any catchment exceeding a $1.0\%$ discrepancy fails automated quality control.

### 6.3 Streamflow Missingness & Exclusion Thresholds
* **[AETHER POLICY] Identification of Missing Flow:** Observation at day $t$ is marked missing if:
  1. `qc_flag == 'M'`
  2. $Q < 0$ (including `-999.00`)
  3. $Q$ is non-finite (`NaN`, `+Inf`, `-Inf`)
* **[AETHER POLICY] Missingness Rate Formula:**
  $$\text{missing\_rate} = \frac{\text{missing\_observed\_days} + \text{unobserved\_calendar\_gap\_days}}{\text{total\_expected\_calendar\_days}}$$
  The denominator strictly counts all expected Gregorian calendar days (including leap days) in $[start\_date, end\_date]$. Missing calendar dates are penalized as unobserved gaps and never silently infilled.
* **[AETHER POLICY] Exclusion Criterion:** Catchments with $\text{missing\_rate} > 0.05$ ($5.0\%$) over the training or test evaluation window are excluded from model training/testing. Exactly $5.0\%$ is accepted.

---

## 7. Critical Temporal Dual-Contract

A critical distinction exists between the **Physical Local Files** and the **Frozen Scientific Research Protocol**:

```text
========================================================================================
TEMPORAL DUAL-CONTRACT COMPARISON
========================================================================================
1. Canonical Local CAMELS-US v1.2 Physical Files:
   [1980-01-01] ──────────────────────────────────────────────── [2014-12-31]
   (Daymet forcing & USGS streamflow terminate strictly on 2014-12-31)

2. AETHER Frozen Scientific Benchmark Protocol:
   [1980-10-01] ──────── [2000-09-30] ── [2005-09-30] ── [2010-09-30] ──────── [2018-09-30]
   ├────────────────────┼────────────┼────────────┼──────────────────────────┤
   │     TRAIN (20 yr)  │  VAL (5 yr)│  CAL (5 yr)│       TEST (8 yr)        │
   │ [1979-10-01 buf]   │ [1999-10-01│ [2004-09-30│ [2009-09-30 buffer]      │
   └────────────────────┴────────────┴────────────┴──────────────────────────┘
========================================================================================
```

### 7.1 Local Distribution Reality
* **[LOCAL OBSERVATION] Actual File Bounds:** In `D:\CAMELS_US\basin_dataset_public_v1p2`, both Daymet forcing and USGS streamflow for all inspected basins (e.g., `01022500`) begin on **`1980-01-01`** and terminate on **`2014-12-31`** (exactly 12,784 daily records).
* **[LOCAL OBSERVATION] Coverage Implications:**
  - **TRAIN Buffered Window (`1979-10-01` to `2000-09-30`):** Incomplete on local v1.2 files because the required 366-day historical context begins 9 months prior to available Daymet records.
  - **VAL Buffered Window (`1999-10-01` to `2005-09-30`):** Fully covered on local v1.2 files.
  - **CAL Buffered Window (`2004-09-30` to `2010-09-30`):** Fully covered on local v1.2 files.
  - **TEST Buffered Window (`2009-09-30` to `2018-09-30`):** Incomplete on local v1.2 files because the physical records terminate on `2014-12-31`.

### 7.2 Frozen Research Protocol
* **[RESEARCH FREEZE] Benchmark Evaluation Windows:** Formally frozen in Phase 1.0 Specification:
  - **TRAIN:** `1980-10-01` → `2000-09-30` (20 Water Years, 7,305 days)
  - **VAL:** `2000-10-01` → `2005-09-30` (5 Water Years, 1,826 days)
  - **CAL:** `2005-10-01` → `2010-09-30` (5 Water Years, 1,826 days)
  - **TEST:** `2010-10-01` → `2018-09-30` (8 Water Years, 2,922 days)
* **[RESEARCH FREEZE] Historical Context Lookback:** All splits prepend an input context buffer of $L + h = 366$ calendar days:
  $$\text{buffer\_start} = \text{target\_start} - 366 \text{ days}, \quad \text{buffer\_end} = \text{target\_start} - 1 \text{ day}$$
  No losses or model updates are evaluated on buffer dates.
* **[AETHER POLICY] Zero Silent Clipping:** When validating coverage against local v1.2 files, [`TemporalSplitManager.validate_buffered_data_coverage`](file:///d:/Aether/aether/data/split_manager.py#L370) reports `is_covered=False` for TRAIN and TEST without altering or clipping the requested dates.
* **[AETHER POLICY] Local QC Missingness Test Window:** For missingness filtering against local CAMELS-US v1.2 files, the test missingness evaluation window is evaluated over `2010-10-01` through `2014-12-31` (1,553 expected calendar days), as specified in Section 5 of the Phase 1.0 Freeze.

---

## 8. Offline Reproducibility & Verification Checklist

To independently verify an environment or local dataset distribution for AETHER research, execute the following audit checklist:

- [ ] **1. Canonical Distribution Present:** Confirm the dataset directory is named `basin_dataset_public_v1p2` and contains `readme_FIRST.txt` citing Newman et al. (2015) v1.2.
- [ ] **2. Packaged Registry Hash:** Verify that `aether/data/camels_us_benchmark_531.json` matches SHA-256:
  ```bash
  uv run python -c "from aether.data.basin_registry import compute_manifest_sha256; print(compute_manifest_sha256())"
  # Must output: 8d046962308a47df40fa9aa690209c98d331982cd3db480cee2885f0681e69ce
  ```
- [ ] **3. Upstream Basin List SHA-256:** Confirm that any downloaded upstream `basin_list.txt` has SHA-256 digest:
  ```text
  c3fb069f9fe644ed3102edca456989393ce28ee4864283c1fe37d5db6562bddf
  ```
- [ ] **4. Daymet Forcing Schema:** Ensure column headers in `*_lump_cida_forcing_leap.txt` match `Year Mnth Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)`.
- [ ] **5. USGS Streamflow Schema:** Ensure streamflow files in `usgs_streamflow/` are 5-column whitespace-delimited files without headers.
- [ ] **6. Area Discrepancy QC:** Verify that GAGES-II `area_gages2` matches Geospatial Fabric `Size(km2)` within $1.0\%$.
- [ ] **7. Temporal Dual-Contract Recognition:** Confirm that local v1.2 file coverage reports incomplete status for the frozen 1979 buffer and 2018 test endpoint without silent truncation.
- [ ] **8. Clean Git Working Tree:** Verify that no raw data files (`.txt`, `.csv`, `.nc`) are tracked in the Git repository:
  ```bash
  git status
  ```
- [ ] **9. Automated Test Suite:** Run the complete suite including data loading, QC, split management, and temporal leakage checks:
  ```bash
  uv run pytest -v --cov=aether --cov-report=term-missing
  ```
