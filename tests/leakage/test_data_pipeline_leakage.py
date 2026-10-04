"""
Tests for data pipeline leakage prevention, slicing integrity, and real dataset boundaries.

This module forms the data processing firewall of the R1.8 leakage test suite,
verifying:
  Group D: Slicing integrity (never outside target, values preserved, index unmutated,
           no synthetic date infilling, explicit insufficiency detection, no silent clipping).
  Group E: Timestamp integrity (rejection of duplicates, non-monotonic series, timezone-aware
           indices; exact 1-day cadence for complete synthetic sequences).
  Group F: QC boundary integrity (missingness calculation strictly restricted to requested interval,
           dates outside cannot affect missingness, QC does not modify split definitions).
  Group G: Real CAMELS-US v1.2 integration smoke test against canonical path:
           D:/CAMELS_US/basin_dataset_public_v1p2 (clean skip if absent, verify known forcing/streamflow
           dates, verify TRAIN/VAL/CAL/TEST buffered coverage expectations without clipping).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aether.data.camels_loader import CamelsDatasetLoader
from aether.data.qc import (
    calculate_streamflow_missingness,
    identify_missing_streamflow,
)
from aether.data.split_manager import (
    TemporalSplit,
    TemporalSplitManager,
)


class TestSlicingIntegrity:
    """Group D: Evaluates dataframe/series slicing without leakage, mutation, or interpolation."""

    def test_slicing_never_includes_dates_outside_target_boundaries(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Verifies that manager.slice_dataframe() strictly bounds returned rows
        within [split.start_date, split.end_date].
        """
        mgr = TemporalSplitManager()
        df = sample_synthetic_basin_df

        for split in [
            TemporalSplit.TRAIN,
            TemporalSplit.VAL,
            TemporalSplit.CAL,
            TemporalSplit.TEST,
        ]:
            sliced = mgr.slice_dataframe(df, split)
            win = mgr.get_split(split)

            assert isinstance(sliced, pd.DataFrame)
            # All timestamps must fall within the target window
            assert (sliced.index >= win.start_date).all(), (
                f"Dates before {win.start_date} leaked in {split.value}"
            )
            assert (sliced.index <= win.end_date).all(), (
                f"Dates after {win.end_date} leaked in {split.value}"
            )
            assert sliced.index.min() == win.start_date
            assert sliced.index.max() == win.end_date

    def test_slicing_preserves_values_and_does_not_mutate_source(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Verifies that slicing creates an exact slice of source records without
        mutating the original DataFrame index, columns, or values.
        """
        mgr = TemporalSplitManager()
        df = sample_synthetic_basin_df
        df_original = df.copy(deep=True)

        sliced = mgr.slice_dataframe(df, TemporalSplit.VAL)

        # Source DataFrame is strictly identical
        pd.testing.assert_frame_equal(df, df_original)

        # Sliced subset matches source records exactly
        source_subset = df.loc[sliced.index]
        pd.testing.assert_frame_equal(sliced, source_subset)

    def test_no_synthetic_date_infilling_during_slicing(self) -> None:
        """
        Verifies that when input data has calendar gaps (missing days),
        slice_dataframe() does NOT synthesize or interpolate the missing timestamps.
        """
        mgr = TemporalSplitManager()
        # Create a series with intentional missing dates (e.g. alternating days)
        sparse_dates = pd.date_range("2000-10-01", "2000-10-31", freq="2D")
        df_sparse = pd.DataFrame({"q": np.ones(len(sparse_dates))}, index=sparse_dates)

        sliced = mgr.slice_dataframe(df_sparse, TemporalSplit.VAL)

        # Length must match the sparse input, not full daily count (31 days)
        assert len(sliced) == len(sparse_dates)
        assert sliced.index.equals(sparse_dates)
        # Verify that unobserved intermediate dates are not present
        assert pd.Timestamp("2000-10-02") not in sliced.index

    def test_no_silent_clipping_on_insufficient_coverage(self) -> None:
        """
        Verifies that coverage validation explicitly returns False when data is
        insufficient, and does not silently clip or alter the requested split window.
        """
        mgr = TemporalSplitManager()

        # Data starts 1 year late for TRAIN
        is_cov, reason = mgr.validate_data_coverage("1981-10-01", "2000-09-30", TemporalSplit.TRAIN)
        assert is_cov is False
        assert "starts late at 1981-10-01" in str(reason)

        # Target window remains strictly 1980-10-01
        train_win = mgr.get_split(TemporalSplit.TRAIN)
        assert train_win.start_date == pd.Timestamp("1980-10-01")


class TestTimestampIntegrity:
    """Group E: Evaluates strict timestamp ordering, monotonicity, and timezone handling."""

    def test_duplicate_timestamps_strictly_rejected(self) -> None:
        """Verifies that DataFrame or Series with duplicate timestamps raises ValueError."""
        mgr = TemporalSplitManager()
        dates = [
            pd.Timestamp("2001-01-01"),
            pd.Timestamp("2001-01-02"),
            pd.Timestamp("2001-01-02"),  # Duplicate
            pd.Timestamp("2001-01-03"),
        ]
        df_dups = pd.DataFrame({"q": [1.0, 2.0, 3.0, 4.0]}, index=dates)

        with pytest.raises(ValueError, match="Duplicate timestamps found in index"):
            mgr.slice_dataframe(df_dups, TemporalSplit.VAL)

    def test_non_monotonic_timestamps_strictly_rejected(self) -> None:
        """Verifies that DataFrame or Series with non-monotonic timestamps raises ValueError."""
        mgr = TemporalSplitManager()
        dates = [
            pd.Timestamp("2001-01-01"),
            pd.Timestamp("2001-01-03"),
            pd.Timestamp("2001-01-02"),  # Out of order
        ]
        df_unsorted = pd.DataFrame({"q": [1.0, 2.0, 3.0]}, index=dates)

        with pytest.raises(ValueError, match="not monotonically increasing"):
            mgr.slice_dataframe(df_unsorted, TemporalSplit.VAL)

    def test_timezone_aware_indices_strictly_rejected(self) -> None:
        """Verifies that timezone-aware DatetimeIndex is rejected to avoid solar time leakage."""
        mgr = TemporalSplitManager()
        tz_dates = pd.date_range("2001-01-01", periods=5, freq="D", tz="UTC")
        df_tz = pd.DataFrame({"q": np.ones(5)}, index=tz_dates)

        with pytest.raises(ValueError, match="Input DatetimeIndex is timezone-aware"):
            mgr.slice_dataframe(df_tz, TemporalSplit.VAL)

    def test_complete_synthetic_daily_sequence_has_exact_one_day_cadence(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Evaluates L01 on an explicitly complete daily synthetic dataset:
        Asserts that every consecutive step is exactly 1 calendar day.
        """
        df = sample_synthetic_basin_df
        diffs = df.index.to_series().diff().iloc[1:]
        assert (diffs == pd.Timedelta(days=1)).all(), (
            "Daily sequence does not have exact 1-day cadence!"
        )


class TestQCBoundaryIntegrity:
    """Group F: Evaluates that QC operations are strictly bounded and do not leak or alter splits."""

    def test_missingness_calculation_restricted_to_supplied_interval(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Verifies that missingness rate calculation is strictly evaluated over
        [start_date, end_date] and does not incorporate data outside this interval.
        """
        df = sample_synthetic_basin_df.copy()
        df["streamflow_cfs"] = df["streamflow"] * 10.0
        df["qc_flag"] = "A"

        # Inject severe missingness OUTSIDE the evaluation interval (e.g., year 1990)
        df.loc["1990-01-01":"1990-12-31", "streamflow_cfs"] = -999.0
        df.loc["1990-01-01":"1990-12-31", "qc_flag"] = "M"

        # Evaluate missingness on a clean interval (e.g. 2001-10-01 to 2002-09-30, 365 days)
        summary = calculate_streamflow_missingness(
            streamflow_df=df,
            start_date="2001-10-01",
            end_date="2002-09-30",
            threshold=0.05,
        )

        assert summary.total_expected_days == 365
        assert summary.observed_days == 365
        assert summary.missing_days == 0
        assert summary.missing_rate == 0.0
        assert summary.is_excluded is False

    def test_dates_outside_requested_interval_cannot_affect_missingness(self) -> None:
        """
        Verifies that adding or modifying rows outside [start_date, end_date]
        produces identical missingness summaries within [start_date, end_date].
        """
        dates = pd.date_range("2005-01-01", "2005-12-31", freq="D")
        df_base = pd.DataFrame(
            {
                "streamflow_cfs": np.ones(len(dates)) * 50.0,
                "qc_flag": ["A"] * len(dates),
            },
            index=dates,
        )

        # Baseline summary for July 2005
        sum_base = calculate_streamflow_missingness(df_base, "2005-07-01", "2005-07-31")

        # Now prepend and append corrupted data far outside July
        df_expanded = df_base.copy()
        df_expanded.loc["2005-01-01":"2005-01-31", "streamflow_cfs"] = -999.0
        df_expanded.loc["2005-01-01":"2005-01-31", "qc_flag"] = "M"
        df_expanded.loc["2005-12-01":"2005-12-31", "streamflow_cfs"] = np.nan

        sum_expanded = calculate_streamflow_missingness(df_expanded, "2005-07-01", "2005-07-31")

        # Missingness metrics for July must be completely identical
        assert sum_base.total_expected_days == sum_expanded.total_expected_days
        assert sum_base.missing_days == sum_expanded.missing_days
        assert sum_base.missing_rate == sum_expanded.missing_rate
        assert sum_base.is_excluded == sum_expanded.is_excluded

    def test_qc_masking_does_not_modify_split_definitions(self) -> None:
        """Verifies that calling QC routines does not mutate TemporalSplitManager state."""
        mgr = TemporalSplitManager()
        before_train = mgr.get_split(TemporalSplit.TRAIN)

        # Run QC masking
        q_series = pd.Series([10.0, -999.0, 5.0])
        flag_series = pd.Series(["A", "M", "A"])
        _ = identify_missing_streamflow(q_series, flag_series)

        after_train = mgr.get_split(TemporalSplit.TRAIN)
        assert before_train == after_train


class TestRealCamelsUSIntegrationSmoke:
    """Group G: Real-data smoke test using ONLY D:/CAMELS_US/basin_dataset_public_v1p2."""

    def test_real_camels_v1p2_availability_and_leakage_invariants(self) -> None:
        """
        Integration smoke test against canonical local CAMELS-US v1.2 dataset:
          D:/CAMELS_US/basin_dataset_public_v1p2
        Skips cleanly if the canonical directory is not present.

        Verifies for benchmark basin 01022500:
          1. Canonical date range for Daymet forcing and USGS streamflow is 1980-01-01 to 2014-12-31.
          2. TRAIN buffered window requires 1979-10-01 -> Incomplete (v1.2 begins in 1980).
          3. VAL buffered window (1999-10-01 to 2005-09-30) -> Fully covered.
          4. CAL buffered window (2004-09-30 to 2010-09-30) -> Fully covered.
          5. TEST buffered window requires through 2018-09-30 -> Incomplete (v1.2 ends 2014-12-31).
          6. The manager does NOT silently clip the requested windows!
        """
        canonical_v1p2 = Path("D:/CAMELS_US/basin_dataset_public_v1p2")
        if not canonical_v1p2.exists():
            pytest.skip(f"Canonical CAMELS-US v1.2 dataset not found at {canonical_v1p2}")

        basin_id = "01022500"
        loader = CamelsDatasetLoader(data_dir=canonical_v1p2)

        forcing = loader.load_forcing(basin_id)
        streamflow = loader.load_streamflow(basin_id)

        # 1. Assert exact known v1.2 observation date ranges
        assert forcing.index[0] == pd.Timestamp("1980-01-01")
        assert forcing.index[-1] == pd.Timestamp("2014-12-31")
        assert streamflow.index[0] == pd.Timestamp("1980-01-01")
        assert streamflow.index[-1] == pd.Timestamp("2014-12-31")

        mgr = TemporalSplitManager()
        data_start = forcing.index[0]
        data_end = forcing.index[-1]

        # 2. TRAIN buffered coverage: Incomplete (buffer starts 1979-10-01)
        train_cov, train_reason = mgr.validate_buffered_data_coverage(
            data_start, data_end, TemporalSplit.TRAIN
        )
        assert train_cov is False
        assert "starts late at 1980-01-01" in str(train_reason)
        assert "requires historical buffer from 1979-10-01" in str(train_reason)

        # 3. VAL buffered coverage: Fully covered (1999-10-01 to 2005-09-30)
        val_cov, val_reason = mgr.validate_buffered_data_coverage(
            data_start, data_end, TemporalSplit.VAL
        )
        assert val_cov is True
        assert val_reason is None

        # 4. CAL buffered coverage: Fully covered (2004-09-30 to 2010-09-30)
        cal_cov, cal_reason = mgr.validate_buffered_data_coverage(
            data_start, data_end, TemporalSplit.CAL
        )
        assert cal_cov is True
        assert cal_reason is None

        # 5. TEST buffered coverage: Incomplete (data ends 2014-12-31, test ends 2018-09-30)
        test_cov, test_reason = mgr.validate_buffered_data_coverage(
            data_start, data_end, TemporalSplit.TEST
        )
        assert test_cov is False
        assert "ends early at 2014-12-31" in str(test_reason)
        assert "requires target through 2018-09-30" in str(test_reason)

        # 6. Verify zero silent clipping on unbuffered and buffered windows
        train_buf = mgr.get_buffered_split(TemporalSplit.TRAIN)
        test_buf = mgr.get_buffered_split(TemporalSplit.TEST)
        assert train_buf.buffered_start_date == pd.Timestamp("1979-10-01")
        assert test_buf.target_end_date == pd.Timestamp("2018-09-30")
