"""
Streamflow Quality Control (QC) and Missing-Data Diagnostics.

Provides pure, deterministic quality control masks, missingness statistics,
and catchment area consistency checks for CAMELS-US streamflow time series.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StreamflowQCSummary:
    """
    Summary record of streamflow missingness metrics across an evaluation interval.

    Attributes
    ----------
    basin_id : str
        8-digit zero-padded USGS gauge identifier.
    total_expected_days : int
        Total calendar days in the [start_date, end_date] interval, including leap days.
    observed_days : int
        Number of valid ground-truth observation days present in the interval.
    valid_days : int
        Alias/synonym for observed valid observation days.
    missing_days : int
        Total missing days = (invalid/missing observed records) + (calendar gap days).
    missing_rate : float
        Proportion of expected days missing: missing_days / total_expected_days.
    is_excluded : bool
        True if missing_rate strictly exceeds the exclusion threshold (e.g. > 0.05).
    exclusion_reason : Optional[str]
        Descriptive explanation if the catchment is excluded, else None.
    """

    basin_id: str
    total_expected_days: int
    observed_days: int
    valid_days: int
    missing_days: int
    missing_rate: float
    is_excluded: bool
    exclusion_reason: Optional[str] = None


def identify_missing_streamflow(
    streamflow_cfs: Union[pd.Series, Sequence[float], np.ndarray],
    qc_flag: Union[pd.Series, Sequence[str], np.ndarray],
) -> pd.Series:
    """
    Identifies missing or invalid streamflow observations according to frozen QC rules.

    An observation is classified as missing (mask = True) if ANY of the following hold:
      1. qc_flag == 'M' (USGS missing sentinel)
      2. streamflow_cfs < 0 (negative discharge, including -999.00)
      3. streamflow_cfs is non-finite (NaN, +Inf, -Inf)

    Observations with zero flow (streamflow_cfs == 0.0) or positive flow with
    approved flags (e.g., 'A', 'A:e', 'A:<') are classified as VALID (mask = False).

    Parameters
    ----------
    streamflow_cfs : Union[pd.Series, Sequence[float], np.ndarray]
        Streamflow discharge observations in cubic feet per second (cfs).
    qc_flag : Union[pd.Series, Sequence[str], np.ndarray]
        USGS quality certification flags matching the length and ordering of streamflow_cfs.

    Returns
    -------
    pd.Series
        Boolean Series indexed identically to streamflow_cfs where True indicates
        missing/invalid flow, and False indicates valid ground-truth flow.

    Raises
    ------
    ValueError
        If inputs have mismatched lengths, invalid types, or cannot be parsed.
    """
    if not isinstance(streamflow_cfs, pd.Series):
        try:
            streamflow_cfs = pd.Series(streamflow_cfs)
        except Exception as e:
            raise ValueError(f"Failed to convert streamflow_cfs to pd.Series: {e}") from e

    if not isinstance(qc_flag, pd.Series):
        try:
            qc_flag = pd.Series(qc_flag, index=streamflow_cfs.index)
        except Exception as e:
            raise ValueError(f"Failed to convert qc_flag to pd.Series: {e}") from e

    if len(streamflow_cfs) != len(qc_flag):
        raise ValueError(
            f"Length mismatch between streamflow_cfs ({len(streamflow_cfs)}) and qc_flag ({len(qc_flag)})."
        )

    if not streamflow_cfs.index.equals(qc_flag.index):
        raise ValueError("Index mismatch between streamflow_cfs and qc_flag Series.")

    # Ensure numeric type for streamflow
    try:
        numeric_q = pd.to_numeric(streamflow_cfs, errors="coerce")
    except Exception as e:
        raise ValueError(f"Streamflow values could not be parsed as numeric: {e}") from e

    # Condition 1: Non-finite values (NaN, +Inf, -Inf, or non-numeric strings coerced to NaN)
    is_non_finite = numeric_q.isna() | np.isinf(numeric_q)

    # Condition 2: Negative values (e.g. -999.00 or any negative number)
    is_negative = (~is_non_finite) & (numeric_q < 0)

    # Condition 3: USGS Missing flag ('M')
    is_flag_m = qc_flag.astype(str).str.strip() == "M"

    missing_mask = is_non_finite | is_negative | is_flag_m
    missing_mask.name = "is_missing"
    return missing_mask


def calculate_streamflow_missingness(
    streamflow_df: pd.DataFrame,
    start_date: Union[str, pd.Timestamp],
    end_date: Union[str, pd.Timestamp],
    threshold: float = 0.05,
) -> StreamflowQCSummary:
    """
    Calculates streamflow missingness rate over an inclusive calendar interval [start_date, end_date].

    The missingness rate is evaluated against the total expected calendar days in the interval:
        missing_rate = missing_days / total_expected_days

    Where:
        - total_expected_days: All calendar days between start_date and end_date (inclusive, with leap days).
        - missing_days: Days with missing observations (Q < 0, flag 'M', non-finite) PLUS unobserved calendar gap days.
        - valid_days: Observed calendar days with valid (non-missing) streamflow.
        - A catchment is excluded if and only if: missing_rate > threshold (e.g. > 0.05). Exactly 0.05 is NOT excluded.

    Parameters
    ----------
    streamflow_df : pd.DataFrame
        DataFrame indexed by DatetimeIndex containing 'streamflow_cfs' and 'qc_flag',
        and optionally 'basin_id'.
    start_date : Union[str, pd.Timestamp]
        Inclusive start date of the evaluation window.
    end_date : Union[str, pd.Timestamp]
        Inclusive end date of the evaluation window.
    threshold : float
        Maximum allowable fraction of missing days (default: 0.05 for 5%).

    Returns
    -------
    StreamflowQCSummary
        Auditable summary record of expected days, valid days, missing days, and exclusion decision.

    Raises
    ------
    ValueError
        If DataFrame schema is missing required columns, index is not DatetimeIndex,
        duplicate timestamps exist, or date range is invalid.
    """
    if not isinstance(streamflow_df, pd.DataFrame):
        raise ValueError(f"Expected streamflow_df to be pd.DataFrame, got {type(streamflow_df)}.")

    required_cols = {"streamflow_cfs", "qc_flag"}
    if not required_cols.issubset(streamflow_df.columns):
        missing_cols = required_cols - set(streamflow_df.columns)
        raise ValueError(f"Missing required columns in streamflow_df: {sorted(missing_cols)}")

    if not isinstance(streamflow_df.index, pd.DatetimeIndex):
        raise ValueError("streamflow_df must be indexed by a pandas DatetimeIndex.")

    if streamflow_df.index.duplicated().any():
        dups = streamflow_df.index[streamflow_df.index.duplicated()].tolist()
        raise ValueError(f"Duplicate timestamps found in streamflow_df index: {dups[:5]}")

    if not streamflow_df.index.is_monotonic_increasing:
        raise ValueError("Timestamps in streamflow_df index are not monotonically increasing.")

    start_ts = pd.Timestamp(start_date).normalize()
    end_ts = pd.Timestamp(end_date).normalize()

    if start_ts > end_ts:
        raise ValueError(
            f"start_date ({start_ts.strftime('%Y-%m-%d')}) must be <= end_date ({end_ts.strftime('%Y-%m-%d')})."
        )

    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"Missingness threshold must be within [0.0, 1.0], got {threshold}.")

    # Extract basin_id
    basin_id = "unknown"
    if "basin_id" in streamflow_df.columns and len(streamflow_df) > 0:
        raw_b = str(streamflow_df["basin_id"].iloc[0]).strip()
        basin_id = raw_b.zfill(8) if (len(raw_b) <= 8 and raw_b.isdigit()) else raw_b

    # Generate full expected calendar sequence
    expected_calendar = pd.date_range(start=start_ts, end=end_ts, freq="D")
    total_expected_days = len(expected_calendar)

    if total_expected_days == 0:
        raise ValueError(
            f"Expected calendar range produced 0 days for interval [{start_ts}, {end_ts}]."
        )

    # Slice dataframe to interval
    sub_df = streamflow_df.loc[(streamflow_df.index >= start_ts) & (streamflow_df.index <= end_ts)]

    # Reindex to full expected calendar to capture gap days explicitly
    # Missing calendar days will naturally have NaN in streamflow_cfs and qc_flag
    aligned_df = sub_df.reindex(expected_calendar)

    # Identify missing days across the aligned sequence
    missing_mask = identify_missing_streamflow(aligned_df["streamflow_cfs"], aligned_df["qc_flag"])

    missing_days = int(missing_mask.sum())
    valid_days = total_expected_days - missing_days
    observed_days = len(sub_df)
    missing_rate = float(missing_days / total_expected_days)

    is_excluded = missing_rate > threshold
    exclusion_reason = None
    if is_excluded:
        exclusion_reason = (
            f"Missing rate {missing_rate:.4%} exceeds maximum allowable threshold {threshold:.4%} "
            f"({missing_days}/{total_expected_days} days missing)."
        )

    return StreamflowQCSummary(
        basin_id=basin_id,
        total_expected_days=total_expected_days,
        observed_days=observed_days,
        valid_days=valid_days,
        missing_days=missing_days,
        missing_rate=missing_rate,
        is_excluded=is_excluded,
        exclusion_reason=exclusion_reason,
    )


def validate_basin_area_consistency(
    area_authoritative_km2: float,
    area_comparison_km2: float,
    max_discrepancy_ratio: float = 0.01,
) -> Tuple[bool, float]:
    """
    Validates physical drainage area consistency between authoritative GAGES-II area
    and comparison GIS delineated area (e.g., Geospatial Fabric Size(km2)).

    Formula:
        discrepancy = abs(area_authoritative_km2 - area_comparison_km2) / area_authoritative_km2
        is_consistent = discrepancy <= max_discrepancy_ratio

    Parameters
    ----------
    area_authoritative_km2 : float
        Authoritative catchment area in square kilometers (`area_gages2` from `camels_topo.txt`).
        Must be strictly positive and finite.
    area_comparison_km2 : float
        Comparison catchment area in square kilometers (`Size(km2)` from `basin_physical_characteristics.txt`).
        Must be strictly positive and finite.
    max_discrepancy_ratio : float
        Maximum allowable relative discrepancy ratio (default: 0.01 for 1.0%).

    Returns
    -------
    Tuple[bool, float]
        (is_consistent, discrepancy_ratio) where is_consistent is True if discrepancy <= max_discrepancy_ratio.

    Raises
    ------
    ValueError
        If either area is non-numeric, <= 0, or non-finite (NaN or Inf), or max_discrepancy_ratio is negative.
    """
    for val, name in (
        (area_authoritative_km2, "area_authoritative_km2"),
        (area_comparison_km2, "area_comparison_km2"),
    ):
        if not isinstance(val, (int, float, np.number)):
            raise ValueError(f"{name} must be numeric, got {type(val)}.")
        if np.isnan(val) or np.isinf(val) or val <= 0.0:
            raise ValueError(f"{name} must be strictly positive (> 0) and finite, got {val}.")

    if not isinstance(max_discrepancy_ratio, (int, float, np.number)):
        raise ValueError(
            f"max_discrepancy_ratio must be numeric, got {type(max_discrepancy_ratio)}."
        )

    if (
        np.isnan(max_discrepancy_ratio)
        or np.isinf(max_discrepancy_ratio)
        or max_discrepancy_ratio < 0.0
    ):
        raise ValueError(
            f"max_discrepancy_ratio must be non-negative and finite, got {max_discrepancy_ratio}."
        )

    authoritative = float(area_authoritative_km2)
    comparison = float(area_comparison_km2)
    max_ratio = float(max_discrepancy_ratio)

    discrepancy_ratio = abs(authoritative - comparison) / authoritative
    is_consistent = discrepancy_ratio <= max_ratio

    return is_consistent, discrepancy_ratio
