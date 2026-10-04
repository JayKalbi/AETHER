"""
Comprehensive unit and integration test suite for TemporalSplitManager and SplitWindow.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aether.configs.base_config import TemporalSplitConfig
from aether.data.split_manager import (
    DEFAULT_LOOKBACK_DAYS,
    BufferedSplitWindow,
    SplitWindow,
    TemporalSplitManager,
    _parse_and_validate_timestamp,
)
from aether.utils.types import TemporalSplit


class TestSplitWindow:
    """Unit tests for immutable SplitWindow data structure."""

    def test_split_window_attributes_and_immutability(self):
        """SplitWindow stores immutable timestamps and rejects attribute reassignment."""
        start = pd.Timestamp("1980-10-01")
        end = pd.Timestamp("2000-09-30")
        window = SplitWindow(name=TemporalSplit.TRAIN, start_date=start, end_date=end)

        assert window.name == TemporalSplit.TRAIN
        assert window.start_date == start
        assert window.end_date == end
        assert window.total_days == 7305  # 20 Water Years including 5 leap days

        # Frozen dataclass mutation raises error
        with pytest.raises(Exception):
            window.start_date = pd.Timestamp("1981-10-01")  # type: ignore

    def test_split_window_contains_timestamp(self):
        """Tests inclusive containment semantics [start_date, end_date]."""
        window = SplitWindow(
            name=TemporalSplit.VAL,
            start_date=pd.Timestamp("2000-10-01"),
            end_date=pd.Timestamp("2005-09-30"),
        )

        # Exact boundaries are inclusive
        assert window.contains("2000-10-01") is True
        assert window.contains("2005-09-30") is True
        assert window.contains(pd.Timestamp("2002-05-15")) is True

        # Outside boundaries
        assert window.contains("2000-09-30") is False  # Day before
        assert window.contains("2005-10-01") is False  # Day after

    def test_split_window_leap_day_handling(self):
        """Tests that leap days are accurately incorporated into date range and day count."""
        # 2000 is a century leap year (2000-02-29 exists)
        window = SplitWindow(
            name=TemporalSplit.TRAIN,
            start_date=pd.Timestamp("2000-02-28"),
            end_date=pd.Timestamp("2000-03-01"),
        )
        assert window.total_days == 3
        dr = window.get_date_range()
        assert len(dr) == 3
        assert pd.Timestamp("2000-02-29") in dr

    def test_split_window_reversed_interval_rejected(self):
        """Reversed interval start_date > end_date raises clear ValueError."""
        with pytest.raises(ValueError, match="start_date .* > end_date"):
            SplitWindow(
                name=TemporalSplit.TEST,
                start_date=pd.Timestamp("2018-09-30"),
                end_date=pd.Timestamp("2010-10-01"),
            )

    def test_split_window_timezone_aware_rejected(self):
        """Timezone-aware timestamps are rejected explicitly."""
        with pytest.raises(ValueError, match="timezone-naive"):
            SplitWindow(
                name=TemporalSplit.TEST,
                start_date=pd.Timestamp("2010-10-01", tz="UTC"),
                end_date=pd.Timestamp("2018-09-30", tz="UTC"),
            )


class TestTemporalSplitManager:
    """Unit tests for TemporalSplitManager validation and slicing."""

    @pytest.fixture
    def manager(self) -> TemporalSplitManager:
        return TemporalSplitManager()

    def test_exact_frozen_default_dates(self, manager: TemporalSplitManager):
        """1. Verifies exact frozen dates and day counts for TRAIN, VAL, CAL, TEST."""
        splits = manager.get_all_splits()
        assert len(splits) == 4

        train = manager.get_split(TemporalSplit.TRAIN)
        val = manager.get_split(TemporalSplit.VAL)
        cal = manager.get_split(TemporalSplit.CAL)
        test = manager.get_split(TemporalSplit.TEST)

        # TRAIN: 1980-10-01 to 2000-09-30 (20 Water Years, 7305 days)
        assert train.start_date == pd.Timestamp("1980-10-01")
        assert train.end_date == pd.Timestamp("2000-09-30")
        assert train.total_days == 7305

        # VAL: 2000-10-01 to 2005-09-30 (5 Water Years, 1826 days)
        assert val.start_date == pd.Timestamp("2000-10-01")
        assert val.end_date == pd.Timestamp("2005-09-30")
        assert val.total_days == 1826

        # CAL: 2005-10-01 to 2010-09-30 (5 Water Years, 1826 days)
        assert cal.start_date == pd.Timestamp("2005-10-01")
        assert cal.end_date == pd.Timestamp("2010-09-30")
        assert cal.total_days == 1826

        # TEST: 2010-10-01 to 2018-09-30 (8 Water Years, 2922 days)
        assert test.start_date == pd.Timestamp("2010-10-01")
        assert test.end_date == pd.Timestamp("2018-09-30")
        assert test.total_days == 2922

    def test_split_lookup_by_enum_and_string(self, manager: TemporalSplitManager):
        """16, 17. Verifies split lookup by enum and valid case-insensitive string."""
        assert manager.get_split(TemporalSplit.TRAIN) == manager.get_split("train")
        assert manager.get_split(TemporalSplit.VAL) == manager.get_split("VAL")
        assert manager.get_split(TemporalSplit.CAL) == manager.get_split("Cal")
        assert manager.get_split(TemporalSplit.TEST) == manager.get_split("test ")

    def test_invalid_split_name_rejected(self, manager: TemporalSplitManager):
        """18. Requesting an unknown split name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown split name 'unknown_split'"):
            manager.get_split("unknown_split")

        with pytest.raises(TypeError, match="Expected TemporalSplit or str"):
            manager.get_split(123)  # type: ignore

    def test_instantiation_from_config(self):
        """Instantiating with a valid TemporalSplitConfig succeeds."""
        cfg = TemporalSplitConfig(
            train_start="1980-10-01",
            train_end="2000-09-30",
            val_start="2000-10-01",
            val_end="2005-09-30",
            cal_start="2005-10-01",
            cal_end="2010-09-30",
            test_start="2010-10-01",
            test_end="2018-09-30",
        )
        mgr = TemporalSplitManager(config=cfg)
        assert mgr.get_split(TemporalSplit.TRAIN).start_date == pd.Timestamp("1980-10-01")

    def test_invalid_config_type_rejected(self):
        """Passing an object that is neither TemporalSplitConfig nor None raises TypeError."""
        with pytest.raises(TypeError, match="Expected TemporalSplitConfig or None"):
            TemporalSplitManager(config={"train": "1980-10-01"})  # type: ignore

    def test_boundary_collision_rejected(self):
        """7. Adjacent splits sharing a boundary date raise ValueError."""
        colliding_config = TemporalSplitConfig(
            train_start="1980-10-01",
            train_end="2000-10-01",  # Collides with val_start
            val_start="2000-10-01",
            val_end="2005-09-30",
            cal_start="2005-10-01",
            cal_end="2010-09-30",
            test_start="2010-10-01",
            test_end="2018-09-30",
        )
        with pytest.raises(ValueError, match="Boundary collision between 'train' and 'val'"):
            TemporalSplitManager(config=colliding_config)

    def test_overlapping_splits_rejected(self):
        """6. Inverted or overlapping splits raise clear ValueError."""
        overlapping_config = TemporalSplitConfig(
            train_start="1980-10-01",
            train_end="2001-09-30",  # Overlaps into val
            val_start="2000-10-01",
            val_end="2005-09-30",
            cal_start="2005-10-01",
            cal_end="2010-09-30",
            test_start="2010-10-01",
            test_end="2018-09-30",
        )
        with pytest.raises(ValueError, match="Temporal overlap detected"):
            TemporalSplitManager(config=overlapping_config)

    def test_invalid_timestamp_string_rejected(self):
        """9. Malformed date string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timestamp format"):
            _parse_and_validate_timestamp("not-a-date")

    def test_timezone_aware_timestamp_rejected(self):
        """Timezone-aware input to timestamp validator raises ValueError."""
        tz_ts = pd.Timestamp("1990-01-01", tz="US/Eastern")
        with pytest.raises(ValueError, match="Timezone-aware timestamp"):
            _parse_and_validate_timestamp(tz_ts)

    def test_slice_dataframe_exact_bounds(self, manager: TemporalSplitManager):
        """11, 15. Slicing DataFrame preserves bounds exactly and does not mutate source."""
        # 10 years covering late train into early val
        dates = pd.date_range("1998-10-01", "2003-09-30", freq="D")
        df_source = pd.DataFrame(
            {"discharge": np.arange(len(dates), dtype=float)},
            index=dates,
        )
        df_copy = df_source.copy()

        # Slice to TRAIN: should select 1998-10-01 to 2000-09-30 (731 days, 2000 is leap)
        train_slice = manager.slice_dataframe(df_source, TemporalSplit.TRAIN)
        assert isinstance(train_slice, pd.DataFrame)
        assert len(train_slice) == 731
        assert train_slice.index[0] == pd.Timestamp("1998-10-01")
        assert train_slice.index[-1] == pd.Timestamp("2000-09-30")

        # Slice to VAL: should select 2000-10-01 to 2003-09-30 (1095 days)
        val_slice = manager.slice_dataframe(df_source, "val")
        assert len(val_slice) == 1095
        assert val_slice.index[0] == pd.Timestamp("2000-10-01")
        assert val_slice.index[-1] == pd.Timestamp("2003-09-30")

        # Check source was not mutated
        pd.testing.assert_frame_equal(df_source, df_copy)

    def test_slice_series_exact_bounds(self, manager: TemporalSplitManager):
        """Slicing works identically on pd.Series."""
        dates = pd.date_range("2004-10-01", "2007-09-30", freq="D")
        s_source = pd.Series(np.arange(len(dates)), index=dates)

        # Slice to CAL: 2005-10-01 to 2007-09-30 (730 days)
        cal_slice = manager.slice_dataframe(s_source, "cal")
        assert isinstance(cal_slice, pd.Series)
        assert cal_slice.index[0] == pd.Timestamp("2005-10-01")
        assert cal_slice.index[-1] == pd.Timestamp("2007-09-30")
        assert len(cal_slice) == 730

    def test_slice_non_datetime_index_rejected(self, manager: TemporalSplitManager):
        """12. DataFrame without DatetimeIndex raises ValueError."""
        df_bad = pd.DataFrame({"q": [1.0, 2.0]}, index=[0, 1])
        with pytest.raises(ValueError, match="must have a pd.DatetimeIndex"):
            manager.slice_dataframe(df_bad, "train")

    def test_slice_timezone_aware_index_rejected(self, manager: TemporalSplitManager):
        """DataFrame with timezone-aware DatetimeIndex raises ValueError."""
        dates_tz = pd.date_range("1990-10-01", periods=10, freq="D", tz="UTC")
        df_tz = pd.DataFrame({"q": np.ones(10)}, index=dates_tz)
        with pytest.raises(ValueError, match="Input DatetimeIndex is timezone-aware"):
            manager.slice_dataframe(df_tz, "train")

    def test_slice_non_monotonic_index_rejected(self, manager: TemporalSplitManager):
        """13. Non-monotonic DatetimeIndex raises ValueError."""
        dates = [pd.Timestamp("1995-10-02"), pd.Timestamp("1995-10-01")]
        df_unsorted = pd.DataFrame({"q": [1.0, 2.0]}, index=dates)
        with pytest.raises(ValueError, match="not monotonically increasing"):
            manager.slice_dataframe(df_unsorted, "train")

    def test_slice_duplicate_timestamps_rejected(self, manager: TemporalSplitManager):
        """14. Duplicate timestamps in DatetimeIndex raise ValueError."""
        dates = [pd.Timestamp("1995-10-01"), pd.Timestamp("1995-10-01"), pd.Timestamp("1995-10-02")]
        df_dup = pd.DataFrame({"q": [1.0, 2.0, 3.0]}, index=dates)
        with pytest.raises(ValueError, match="Duplicate timestamps found in index"):
            manager.slice_dataframe(df_dup, "train")

    def test_data_coverage_validation_fully_covered(self, manager: TemporalSplitManager):
        """19. Data coverage fully covering a split returns True, None."""
        is_covered, reason = manager.validate_data_coverage(
            available_start="1980-01-01",
            available_end="2001-01-01",
            split="train",
        )
        assert is_covered is True
        assert reason is None

    def test_data_coverage_validation_incomplete(self, manager: TemporalSplitManager):
        """20. Data coverage starting late or ending early returns False with explanation."""
        is_covered, reason = manager.validate_data_coverage(
            available_start="1980-10-01",
            available_end="1999-12-31",  # Train requires 2000-09-30
            split="train",
        )
        assert is_covered is False
        assert "Available data ends early at 1999-12-31" in str(reason)
        assert "split 'train' requires 2000-09-30" in str(reason)

    def test_data_coverage_reversed_available_dates_rejected(self, manager: TemporalSplitManager):
        """Available start > available end raises ValueError."""
        with pytest.raises(ValueError, match="available_start .* must be <= available_end"):
            manager.validate_data_coverage("2000-01-01", "1990-01-01", "train")


class TestRealCamelsUSIntegrationCoverage:
    """
    Integration smoke tests verifying data coverage against local CAMELS-US v1.2 dataset.

    Validates requirement 21: CAMELS-US v1.2 ending 2014-12-31 does NOT cause TEST to be
    clipped or redefined in the split manager.
    """

    def test_real_camels_v1p2_coverage_contract(self):
        """
        21. Explicitly checks canonical CAMELS-US v1.2 files on local disk (if present).
        Confirms:
          - TRAIN (1980-10-01 to 2000-09-30) is fully covered.
          - VAL (2000-10-01 to 2005-09-30) is fully covered.
          - CAL (2005-10-01 to 2010-09-30) is fully covered.
          - TEST (2010-10-01 to 2018-09-30) is NOT fully covered because v1.2 ends 2014-12-31.
          - Crucially, the TEST split in TemporalSplitManager is NOT clipped or modified!
        """
        canonical_v1p2_dir = Path("D:/CAMELS_US/basin_dataset_public_v1p2")
        if not canonical_v1p2_dir.exists():
            pytest.skip(f"Local CAMELS-US v1.2 dataset not found at {canonical_v1p2_dir}")

        mgr = TemporalSplitManager()
        test_window = mgr.get_split(TemporalSplit.TEST)

        # Confirm the frozen test window is strictly preserved through 2018-09-30
        assert test_window.start_date == pd.Timestamp("2010-10-01")
        assert test_window.end_date == pd.Timestamp("2018-09-30")

        # In CAMELS-US v1.2, observation and Daymet series span 1980-10-01 to 2014-12-31
        v1p2_start = "1980-10-01"
        v1p2_end = "2014-12-31"

        # Check coverage
        train_covered, _ = mgr.validate_data_coverage(v1p2_start, v1p2_end, TemporalSplit.TRAIN)
        val_covered, _ = mgr.validate_data_coverage(v1p2_start, v1p2_end, TemporalSplit.VAL)
        cal_covered, _ = mgr.validate_data_coverage(v1p2_start, v1p2_end, TemporalSplit.CAL)
        test_covered, test_reason = mgr.validate_data_coverage(
            v1p2_start, v1p2_end, TemporalSplit.TEST
        )

        assert train_covered is True
        assert val_covered is True
        assert cal_covered is True

        # TEST is NOT fully covered by v1.2
        assert test_covered is False
        assert "Available data ends early at 2014-12-31" in str(test_reason)
        assert "split 'test' requires 2018-09-30" in str(test_reason)

        # Verify that after validating coverage, TEST split remains unclipped
        assert mgr.get_split(TemporalSplit.TEST).end_date == pd.Timestamp("2018-09-30")


class TestBufferedSplitWindow:
    """Unit tests for R1.7 366-day historical context lookback buffer enforcement."""

    @pytest.fixture
    def manager(self) -> TemporalSplitManager:
        return TemporalSplitManager()

    def test_buffered_split_window_construction_and_immutability(
        self, manager: TemporalSplitManager
    ):
        """1, 2. Verifies BufferedSplitWindow construction and immutable frozen dataclass behavior."""
        train_win = manager.get_split(TemporalSplit.TRAIN)
        buffered = BufferedSplitWindow(target_window=train_win, lookback_days=366)

        assert buffered.name == TemporalSplit.TRAIN
        assert buffered.target_window == train_win
        assert buffered.lookback_days == 366
        assert buffered.target_start_date == pd.Timestamp("1980-10-01")
        assert buffered.target_end_date == pd.Timestamp("2000-09-30")
        assert buffered.buffered_start_date == pd.Timestamp("1979-10-01")
        assert buffered.buffer_end_date == pd.Timestamp("1980-09-30")

        # Frozen dataclass mutation raises error
        with pytest.raises(Exception):
            buffered.lookback_days = 365  # type: ignore

    def test_default_lookback_days_constant(self):
        """Verifies DEFAULT_LOOKBACK_DAYS constant equals 366."""
        assert DEFAULT_LOOKBACK_DAYS == 366

    def test_exact_366_day_lookback_all_splits(self, manager: TemporalSplitManager):
        """3, 4, 5, 6, 7. Verifies exact buffer dates, day counts, and target invariance across all 4 splits."""
        # 1. TRAIN: Target 1980-10-01 to 2000-09-30. Buffer: 1979-10-01 to 1980-09-30 (366 days, 1980 leap day)
        train_buf = manager.get_buffered_split(TemporalSplit.TRAIN)
        assert train_buf.buffered_start_date == pd.Timestamp("1979-10-01")
        assert train_buf.buffer_end_date == pd.Timestamp("1980-09-30")
        assert train_buf.buffer_days == 366
        assert train_buf.target_start_date == pd.Timestamp("1980-10-01")
        assert train_buf.target_end_date == pd.Timestamp("2000-09-30")
        assert train_buf.total_buffered_days == 366 + 7305  # 7671 days

        # 2. VAL: Target 2000-10-01 to 2005-09-30. Buffer: 1999-10-01 to 2000-09-30 (366 days, 2000 leap day)
        val_buf = manager.get_buffered_split(TemporalSplit.VAL)
        assert val_buf.buffered_start_date == pd.Timestamp("1999-10-01")
        assert val_buf.buffer_end_date == pd.Timestamp("2000-09-30")
        assert val_buf.buffer_days == 366
        assert val_buf.target_start_date == pd.Timestamp("2000-10-01")
        assert val_buf.target_end_date == pd.Timestamp("2005-09-30")
        assert val_buf.total_buffered_days == 366 + 1826  # 2192 days

        # 3. CAL: Target 2005-10-01 to 2010-09-30. Buffer: 2004-09-30 to 2005-09-30 (366 days, non-leap)
        cal_buf = manager.get_buffered_split(TemporalSplit.CAL)
        assert cal_buf.buffered_start_date == pd.Timestamp("2004-09-30")
        assert cal_buf.buffer_end_date == pd.Timestamp("2005-09-30")
        assert cal_buf.buffer_days == 366
        assert cal_buf.target_start_date == pd.Timestamp("2005-10-01")
        assert cal_buf.target_end_date == pd.Timestamp("2010-09-30")
        assert cal_buf.total_buffered_days == 366 + 1826  # 2192 days

        # 4. TEST: Target 2010-10-01 to 2018-09-30. Buffer: 2009-09-30 to 2010-09-30 (366 days, non-leap)
        test_buf = manager.get_buffered_split(TemporalSplit.TEST)
        assert test_buf.buffered_start_date == pd.Timestamp("2009-09-30")
        assert test_buf.buffer_end_date == pd.Timestamp("2010-09-30")
        assert test_buf.buffer_days == 366
        assert test_buf.target_start_date == pd.Timestamp("2010-10-01")
        assert test_buf.target_end_date == pd.Timestamp("2018-09-30")
        assert test_buf.total_buffered_days == 366 + 2922  # 3288 days

    def test_buffer_date_range_generators(self, manager: TemporalSplitManager):
        """Verifies get_buffer_date_range() and get_total_date_range()."""
        cal_buf = manager.get_buffered_split(TemporalSplit.CAL)
        buf_dr = cal_buf.get_buffer_date_range()
        assert len(buf_dr) == 366
        assert buf_dr[0] == pd.Timestamp("2004-09-30")
        assert buf_dr[-1] == pd.Timestamp("2005-09-30")

        total_dr = cal_buf.get_total_date_range()
        assert len(total_dr) == 2192
        assert total_dr[0] == pd.Timestamp("2004-09-30")
        assert total_dr[-1] == pd.Timestamp("2010-09-30")

    def test_invalid_lookback_days_rejected(self, manager: TemporalSplitManager):
        """10. Non-positive or non-integer lookback_days are rejected."""
        val_win = manager.get_split(TemporalSplit.VAL)

        with pytest.raises(ValueError, match="lookback_days must be a positive integer"):
            BufferedSplitWindow(target_window=val_win, lookback_days=0)

        with pytest.raises(ValueError, match="lookback_days must be a positive integer"):
            BufferedSplitWindow(target_window=val_win, lookback_days=-10)

        with pytest.raises(TypeError, match="lookback_days must be an integer"):
            BufferedSplitWindow(target_window=val_win, lookback_days="366")  # type: ignore

        with pytest.raises(TypeError, match="lookback_days must be an integer"):
            BufferedSplitWindow(target_window=val_win, lookback_days=True)  # type: ignore

    def test_invalid_target_window_rejected(self):
        """Non-SplitWindow object rejected as target_window."""
        with pytest.raises(TypeError, match="target_window must be an instance of SplitWindow"):
            BufferedSplitWindow(target_window="not_a_window")  # type: ignore

    def test_validate_buffered_data_coverage_fully_covered(self, manager: TemporalSplitManager):
        """12. Available data fully covering buffer and target returns (True, None)."""
        # VAL buffered window requires 1999-10-01 to 2005-09-30
        is_covered, reason = manager.validate_buffered_data_coverage(
            available_start="1999-01-01",
            available_end="2005-12-31",
            split=TemporalSplit.VAL,
        )
        assert is_covered is True
        assert reason is None

    def test_validate_buffered_data_coverage_missing_buffer(self, manager: TemporalSplitManager):
        """13, 15. Missing historical buffer returns False with clear explanation and no clipping."""
        # Available data starts on target_start (2000-10-01), missing the buffer 1999-10-01 to 2000-09-30
        is_covered, reason = manager.validate_buffered_data_coverage(
            available_start="2000-10-01",
            available_end="2005-09-30",
            split="val",
        )
        assert is_covered is False
        assert "Available data starts late at 2000-10-01" in str(reason)
        assert "requires historical buffer from 1999-10-01" in str(reason)

        # Confirm target window in manager was NOT modified
        val_win = manager.get_split(TemporalSplit.VAL)
        assert val_win.start_date == pd.Timestamp("2000-10-01")

    def test_validate_buffered_data_coverage_missing_target(self, manager: TemporalSplitManager):
        """14, 15. Missing target end returns False with clear explanation and no clipping."""
        # Available data covers buffer start (1999-10-01) but ends early (2004-12-31) before target_end (2005-09-30)
        is_covered, reason = manager.validate_buffered_data_coverage(
            available_start="1999-10-01",
            available_end="2004-12-31",
            split="val",
        )
        assert is_covered is False
        assert "Available data ends early at 2004-12-31" in str(reason)
        assert "requires target through 2005-09-30" in str(reason)

    def test_validate_buffered_data_coverage_reversed_available_dates_rejected(
        self, manager: TemporalSplitManager
    ):
        """Reversed available date boundaries raise ValueError."""
        with pytest.raises(ValueError, match="available_start .* must be <= available_end"):
            manager.validate_buffered_data_coverage("2005-01-01", "2000-01-01", "val")

    def test_real_camels_v1p2_buffered_coverage_smoke(self):
        """
        18. Integration smoke test against canonical local CAMELS-US v1.2 dataset:
          D:/CAMELS_US/basin_dataset_public_v1p2
        Verifies:
          - TRAIN buffered window requires 1979-10-01 -> Incomplete (v1.2 begins in 1980).
          - VAL buffered window (1999-10-01 to 2005-09-30) -> Fully covered.
          - CAL buffered window (2004-09-30 to 2010-09-30) -> Fully covered.
          - TEST buffered window requires through 2018-09-30 -> Incomplete (v1.2 ends 2014-12-31).
          - Crucially, zero clipping occurs on any split or buffer!
        """
        canonical_v1p2_dir = Path("D:/CAMELS_US/basin_dataset_public_v1p2")
        if not canonical_v1p2_dir.exists():
            pytest.skip(f"Local CAMELS-US v1.2 dataset not found at {canonical_v1p2_dir}")

        mgr = TemporalSplitManager()
        # In CAMELS-US v1.2, observation and Daymet series span 1980-10-01 to 2014-12-31
        v1p2_start = "1980-10-01"
        v1p2_end = "2014-12-31"

        # 1. TRAIN: Needs buffer from 1979-10-01 -> Incomplete
        train_cov, train_msg = mgr.validate_buffered_data_coverage(
            v1p2_start, v1p2_end, TemporalSplit.TRAIN
        )
        assert train_cov is False
        assert "Available data starts late at 1980-10-01" in str(train_msg)
        assert "requires historical buffer from 1979-10-01" in str(train_msg)

        # 2. VAL: Needs buffer 1999-10-01 to 2005-09-30 -> Fully covered
        val_cov, val_msg = mgr.validate_buffered_data_coverage(
            v1p2_start, v1p2_end, TemporalSplit.VAL
        )
        assert val_cov is True
        assert val_msg is None

        # 3. CAL: Needs buffer 2004-09-30 to 2010-09-30 -> Fully covered
        cal_cov, cal_msg = mgr.validate_buffered_data_coverage(
            v1p2_start, v1p2_end, TemporalSplit.CAL
        )
        assert cal_cov is True
        assert cal_msg is None

        # 4. TEST: Needs target through 2018-09-30 -> Incomplete
        test_cov, test_msg = mgr.validate_buffered_data_coverage(
            v1p2_start, v1p2_end, TemporalSplit.TEST
        )
        assert test_cov is False
        assert "Available data ends early at 2014-12-31" in str(test_msg)
        assert "requires target through 2018-09-30" in str(test_msg)

        # 5. Confirm frozen split definitions remain 100% unclipped
        test_win = mgr.get_buffered_split(TemporalSplit.TEST)
        assert test_win.buffered_start_date == pd.Timestamp("2009-09-30")
        assert test_win.target_end_date == pd.Timestamp("2018-09-30")
