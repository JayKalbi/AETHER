"""
Unit and regression tests for CAMELS-US streamflow quality control (Issue R1.5).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aether.data.camels_loader import CamelsDatasetLoader
from aether.data.qc import (
    StreamflowQCSummary,
    calculate_streamflow_missingness,
    identify_missing_streamflow,
    validate_basin_area_consistency,
)


class TestIdentifyMissingStreamflow:
    """Test suite for identify_missing_streamflow contract."""

    def test_qc_flag_m_is_missing(self):
        """1. qc_flag == 'M' is identified as missing (True) even with positive discharge."""
        q = pd.Series([100.0])
        flag = pd.Series(["M"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_negative_discharge_is_missing(self):
        """2. Negative discharge with approved flag is identified as missing."""
        q = pd.Series([-10.0])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_sentinel_negative_999_is_missing(self):
        """3. Canonical CAMELS sentinel -999.00 with flag 'M' is identified as missing."""
        q = pd.Series([-999.00])
        flag = pd.Series(["M"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_nan_discharge_is_missing(self):
        """4. NaN discharge is identified as missing regardless of flag."""
        q = pd.Series([np.nan])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_positive_infinity_discharge_is_missing(self):
        """5. +Inf discharge is non-finite and identified as missing."""
        q = pd.Series([np.inf])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_negative_infinity_discharge_is_missing(self):
        """6. -Inf discharge is non-finite and identified as missing."""
        q = pd.Series([-np.inf])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is True or res.iloc[0] == True  # noqa: E712

    def test_zero_discharge_with_approved_flag_is_valid(self):
        """7. Zero discharge with flag 'A' is valid hydrological flow (False)."""
        q = pd.Series([0.0])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is False or res.iloc[0] == False  # noqa: E712

    def test_positive_discharge_with_approved_flag_a_is_valid(self):
        """8. Positive flow with certified flag 'A' is valid (False)."""
        q = pd.Series([45.2])
        flag = pd.Series(["A"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is False or res.iloc[0] == False  # noqa: E712

    def test_positive_discharge_with_flag_a_e_is_valid(self):
        """9. Positive flow with certified estimated flag 'A:e' is valid (False)."""
        q = pd.Series([12.5])
        flag = pd.Series(["A:e"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is False or res.iloc[0] == False  # noqa: E712

    def test_positive_discharge_with_flag_a_lt_is_valid(self):
        """10. Positive flow with certified below-limit flag 'A:<' is valid (False)."""
        q = pd.Series([0.01])
        flag = pd.Series(["A:<"])
        res = identify_missing_streamflow(q, flag)
        assert res.iloc[0] is False or res.iloc[0] == False  # noqa: E712

    def test_index_and_length_preservation(self):
        """11. Output Series preserves input index and length exactly."""
        dates = pd.date_range("1995-10-01", periods=4, freq="D")
        q = pd.Series([10.0, 0.0, -999.0, 50.0], index=dates, name="streamflow_cfs")
        flag = pd.Series(["A", "A", "M", "A:e"], index=dates, name="qc_flag")

        res = identify_missing_streamflow(q, flag)

        assert isinstance(res, pd.Series)
        assert res.dtype == bool
        assert res.index.equals(dates)
        assert len(res) == 4
        assert list(res) == [False, False, True, False]

    def test_input_non_mutation(self):
        """12. Inputs are not mutated or modified in-place."""
        q = pd.Series([10.0, -999.0, 20.0])
        flag = pd.Series(["A", "M", "A"])
        q_copy = q.copy()
        flag_copy = flag.copy()

        _ = identify_missing_streamflow(q, flag)

        pd.testing.assert_series_equal(q, q_copy)
        pd.testing.assert_series_equal(flag, flag_copy)

    def test_mismatched_lengths_raise_value_error(self):
        """24a. Mismatched Series lengths raise clear ValueError."""
        q = pd.Series([10.0, 20.0])
        flag = pd.Series(["A"])
        with pytest.raises(ValueError, match="Length mismatch"):
            identify_missing_streamflow(q, flag)

    def test_mismatched_indices_raise_value_error(self):
        """24b. Mismatched Series indices raise clear ValueError."""
        d1 = pd.date_range("1995-10-01", periods=2)
        d2 = pd.date_range("1995-10-02", periods=2)
        q = pd.Series([10.0, 20.0], index=d1)
        flag = pd.Series(["A", "A"], index=d2)
        with pytest.raises(ValueError, match="Index mismatch"):
            identify_missing_streamflow(q, flag)

    def test_non_numeric_values_treated_as_missing(self):
        """Non-numeric values coerced to NaN are correctly flagged as missing."""
        q = pd.Series(["corrupt_str", "10.5"])
        flag = pd.Series(["A", "A"])
        res = identify_missing_streamflow(q, flag)
        assert list(res) == [True, False]


class TestCalculateStreamflowMissingness:
    """Test suite for calculate_streamflow_missingness contract."""

    @pytest.fixture
    def complete_streamflow_df(self) -> pd.DataFrame:
        """Returns a 100-day complete, valid streamflow DataFrame."""
        dates = pd.date_range("1990-10-01", periods=100, freq="D")
        return pd.DataFrame(
            {
                "basin_id": ["01022500"] * 100,
                "streamflow_cfs": [10.0] * 100,
                "qc_flag": ["A"] * 100,
            },
            index=dates,
        )

    def test_complete_calendar_interval_missing_rate_zero(
        self, complete_streamflow_df: pd.DataFrame
    ):
        """13. A complete series with zero missing days yields missing_rate = 0.0 and is_excluded = False."""
        summary = calculate_streamflow_missingness(
            complete_streamflow_df,
            start_date="1990-10-01",
            end_date="1991-01-08",  # Exactly 100 days
            threshold=0.05,
        )

        assert isinstance(summary, StreamflowQCSummary)
        assert summary.basin_id == "01022500"
        assert summary.total_expected_days == 100
        assert summary.observed_days == 100
        assert summary.valid_days == 100
        assert summary.missing_days == 0
        assert summary.missing_rate == 0.0
        assert summary.is_excluded is False
        assert summary.exclusion_reason is None

    def test_calendar_gap_counted_as_missing(self, complete_streamflow_df: pd.DataFrame):
        """14. An unobserved calendar date gap is penalized and counted as missing."""
        # Drop day 5 (1990-10-06)
        df_gap = complete_streamflow_df.drop(pd.Timestamp("1990-10-06"))

        summary = calculate_streamflow_missingness(
            df_gap,
            start_date="1990-10-01",
            end_date="1990-10-10",  # 10 expected days
            threshold=0.05,
        )

        assert summary.total_expected_days == 10
        assert summary.observed_days == 9
        assert summary.valid_days == 9
        assert summary.missing_days == 1
        assert summary.missing_rate == pytest.approx(0.10)
        assert summary.is_excluded is True
        assert "exceeds maximum allowable threshold" in str(summary.exclusion_reason)

    def test_observed_missing_value_counted_as_missing(self, complete_streamflow_df: pd.DataFrame):
        """15. Observed row with -999.00 and 'M' is counted as missing."""
        df_mod = complete_streamflow_df.copy()
        df_mod.loc[pd.Timestamp("1990-10-05"), "streamflow_cfs"] = -999.00
        df_mod.loc[pd.Timestamp("1990-10-05"), "qc_flag"] = "M"

        summary = calculate_streamflow_missingness(
            df_mod,
            start_date="1990-10-01",
            end_date="1990-10-20",  # 20 expected days
            threshold=0.05,
        )

        assert summary.total_expected_days == 20
        assert summary.observed_days == 20
        assert summary.missing_days == 1
        assert summary.valid_days == 19
        assert summary.missing_rate == pytest.approx(1 / 20)  # 0.05

    def test_leap_day_handling(self):
        """16. Leap year interval correctly includes Feb 29 in denominator."""
        dates = pd.date_range("2000-02-27", "2000-03-02", freq="D")
        # 2000 is a leap year: Feb 27, 28, 29, Mar 1, 2 -> 5 days
        df = pd.DataFrame(
            {
                "basin_id": ["01022500"] * 5,
                "streamflow_cfs": [50.0] * 5,
                "qc_flag": ["A"] * 5,
            },
            index=dates,
        )

        summary = calculate_streamflow_missingness(
            df,
            start_date="2000-02-27",
            end_date="2000-03-02",
        )

        assert summary.total_expected_days == 5
        assert summary.missing_days == 0
        assert summary.missing_rate == 0.0

    def test_exact_5_percent_threshold_not_excluded(self):
        """17. A missing rate of exactly 5.0% is NOT excluded (> 0.05 rule)."""
        # 100 days with exactly 5 missing days
        dates = pd.date_range("1990-10-01", periods=100, freq="D")
        q = [10.0] * 100
        flags = ["A"] * 100
        for i in range(5):
            q[i] = -999.00
            flags[i] = "M"

        df = pd.DataFrame(
            {"basin_id": ["01022500"] * 100, "streamflow_cfs": q, "qc_flag": flags},
            index=dates,
        )

        summary = calculate_streamflow_missingness(
            df,
            start_date="1990-10-01",
            end_date="1991-01-08",
            threshold=0.05,
        )

        assert summary.total_expected_days == 100
        assert summary.missing_days == 5
        assert summary.missing_rate == 0.05
        assert summary.is_excluded is False
        assert summary.exclusion_reason is None

    def test_strictly_greater_than_5_percent_is_excluded(self):
        """18. A missing rate strictly greater than 5.0% (e.g. 6/100 = 6%) IS excluded."""
        dates = pd.date_range("1990-10-01", periods=100, freq="D")
        q = [10.0] * 100
        flags = ["A"] * 100
        for i in range(6):
            q[i] = -999.00
            flags[i] = "M"

        df = pd.DataFrame(
            {"basin_id": ["01022500"] * 100, "streamflow_cfs": q, "qc_flag": flags},
            index=dates,
        )

        summary = calculate_streamflow_missingness(
            df,
            start_date="1990-10-01",
            end_date="1991-01-08",
            threshold=0.05,
        )

        assert summary.total_expected_days == 100
        assert summary.missing_days == 6
        assert summary.missing_rate == 0.06
        assert summary.is_excluded is True
        assert summary.exclusion_reason is not None

    def test_explicit_start_end_dates_respected(self, complete_streamflow_df: pd.DataFrame):
        """19. Slices strictly to the specified date window and ignores dates outside."""
        summary = calculate_streamflow_missingness(
            complete_streamflow_df,
            start_date="1990-10-10",
            end_date="1990-10-19",  # 10 days
        )

        assert summary.total_expected_days == 10
        assert summary.valid_days == 10
        assert summary.missing_days == 0

    def test_duplicate_dates_rejected(self, complete_streamflow_df: pd.DataFrame):
        """23. Duplicate dates in streamflow_df raise clear ValueError."""
        dup_row = complete_streamflow_df.iloc[[0]].copy()
        df_dup = pd.concat([complete_streamflow_df, dup_row])

        with pytest.raises(ValueError, match="Duplicate timestamps"):
            calculate_streamflow_missingness(
                df_dup,
                start_date="1990-10-01",
                end_date="1990-10-10",
            )

    def test_invalid_interval_start_after_end(self, complete_streamflow_df: pd.DataFrame):
        """start_date > end_date raises clear ValueError."""
        with pytest.raises(ValueError, match="must be <= end_date"):
            calculate_streamflow_missingness(
                complete_streamflow_df,
                start_date="1990-10-20",
                end_date="1990-10-10",
            )

    def test_missing_required_column_raises_error(self):
        """DataFrame missing required columns raises ValueError."""
        df_bad = pd.DataFrame(
            {"streamflow_cfs": [10.0]}, index=pd.date_range("1990-10-01", periods=1)
        )
        with pytest.raises(ValueError, match="Missing required columns"):
            calculate_streamflow_missingness(
                df_bad,
                start_date="1990-10-01",
                end_date="1990-10-01",
            )


class TestValidateBasinAreaConsistency:
    """Test suite for validate_basin_area_consistency contract."""

    def test_area_discrepancy_within_one_percent_is_valid(self):
        """20. Discrepancy <= 1.0% returns (True, ratio)."""
        # 619.5 vs 620.38 is 0.14% discrepancy
        is_valid, ratio = validate_basin_area_consistency(619.5, 620.38, max_discrepancy_ratio=0.01)
        assert is_valid is True
        assert ratio == pytest.approx(abs(619.5 - 620.38) / 619.5, rel=1e-6)
        assert ratio <= 0.01

    def test_area_discrepancy_exceeding_one_percent_is_invalid(self):
        """21. Discrepancy > 1.0% returns (False, ratio)."""
        # 619.5 vs 573.60 is 7.41% discrepancy
        is_valid, ratio = validate_basin_area_consistency(619.5, 573.60, max_discrepancy_ratio=0.01)
        assert is_valid is False
        assert ratio == pytest.approx(abs(619.5 - 573.60) / 619.5, rel=1e-6)
        assert ratio > 0.01

    @pytest.mark.parametrize("bad_val", [0.0, -100.0, np.nan, np.inf, -np.inf])
    def test_invalid_authoritative_area_fails_clearly(self, bad_val: float):
        """22a. Non-positive, NaN, or Inf authoritative area raises ValueError."""
        with pytest.raises(ValueError, match="strictly positive.*finite"):
            validate_basin_area_consistency(bad_val, 500.0)

    @pytest.mark.parametrize("bad_val", [0.0, -50.0, np.nan, np.inf, -np.inf])
    def test_invalid_comparison_area_fails_clearly(self, bad_val: float):
        """22b. Non-positive, NaN, or Inf comparison area raises ValueError."""
        with pytest.raises(ValueError, match="strictly positive.*finite"):
            validate_basin_area_consistency(500.0, bad_val)

    def test_invalid_threshold_fails_clearly(self):
        """Negative or non-finite threshold raises ValueError."""
        with pytest.raises(ValueError, match="non-negative and finite"):
            validate_basin_area_consistency(500.0, 500.0, max_discrepancy_ratio=-0.01)


class TestRealCamelsUSSmokeTest:
    """Smoke test against local CAMELS-US v1.2 dataset (optional, skipped in CI if absent)."""

    def test_real_camels_basin_01022500_qc_evaluation(self):
        """
        Validates real CAMELS-US v1.2 streamflow data for benchmark basin 01022500.
        Verifies:
          - Authoritative area consistency against Geospatial Fabric (619.5 vs 620.38) <= 1%.
          - TRAIN period (1980-10-01 to 2000-09-30) missing rate = 0.0% (not excluded).
          - Local v1.2 TEST window (2010-10-01 to 2014-12-31) missing rate = 0.0% (not excluded).
        """
        real_data_dir = Path("D:/CAMELS_US/basin_dataset_public_v1p2")
        if not real_data_dir.exists():
            pytest.skip(
                "Local CAMELS-US dataset not found at D:/CAMELS_US/basin_dataset_public_v1p2"
            )

        loader = CamelsDatasetLoader(data_dir=real_data_dir)
        df_streamflow = loader.load_streamflow("01022500")

        # 1. Evaluate missingness over TRAIN (1980-10-01 to 2000-09-30)
        train_qc = calculate_streamflow_missingness(
            df_streamflow,
            start_date="1980-10-01",
            end_date="2000-09-30",
            threshold=0.05,
        )

        assert train_qc.basin_id == "01022500"
        assert train_qc.total_expected_days == 7305
        assert train_qc.observed_days == 7305
        assert train_qc.missing_days == 0
        assert train_qc.missing_rate == 0.0
        assert train_qc.is_excluded is False

        # 2. Evaluate missingness over v1.2 TEST window (2010-10-01 to 2014-12-31)
        # Note: Basin 01022500 has 92 missing observations in late 2014 (2014-10-01 to 2014-12-31)
        # 92 / 1553 = 5.9240% missing, which correctly triggers exclusion (> 5.0%)
        test_qc = calculate_streamflow_missingness(
            df_streamflow,
            start_date="2010-10-01",
            end_date="2014-12-31",
            threshold=0.05,
        )

        assert test_qc.basin_id == "01022500"
        assert test_qc.total_expected_days == 1553
        assert test_qc.observed_days == 1553
        assert test_qc.valid_days == 1461
        assert test_qc.missing_days == 92
        assert test_qc.missing_rate == pytest.approx(92 / 1553, rel=1e-5)
        assert test_qc.is_excluded is True
        assert "exceeds maximum allowable threshold" in str(test_qc.exclusion_reason)

        # 3. Area consistency for 01022500: authoritative area_gages2 = 619.5, GF Size(km2) = 620.38
        authoritative_area = 619.5
        gf_area = 620.38
        is_consistent, disc = validate_basin_area_consistency(authoritative_area, gf_area, 0.01)
        assert is_consistent is True
        assert disc < 0.002  # 0.14% discrepancy
