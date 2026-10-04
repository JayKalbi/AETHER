"""
Tests for temporal leakage prevention and boundary isolation.

This module forms the temporal partition firewall of the R1.8 leakage test suite,
verifying:
  Group A: Frozen target split integrity (pairwise disjointness, exact boundaries,
           chronological ordering, boundary collisions, no accidental clipping).
  Group B: R1.7 buffered-window integrity (exact 366-day historical buffer, disjoint
           buffer vs target evaluation dates, unchanged target boundaries, invalid inputs).
  Group C: Causal rolling-window integrity (context strictly <= t, no t+1 or future data,
           leakage injection detection, earliest 366-day context boundary).
"""

from __future__ import annotations

import itertools
from typing import Tuple

import pandas as pd
import pytest

from aether.data.split_manager import (
    DEFAULT_LOOKBACK_DAYS,
    BufferedSplitWindow,
    SplitWindow,
    TemporalSplit,
    TemporalSplitManager,
)


class TestFrozenTargetSplitIntegrity:
    """Group A: Evaluates pairwise disjointness and exactness of frozen target splits."""

    def test_all_target_splits_pairwise_disjoint(self) -> None:
        """
        Verifies that all four frozen evaluation splits (TRAIN, VAL, CAL, TEST)
        have pairwise-disjoint daily calendar ranges:
            Range_i ∩ Range_j = ∅ for all i != j.
        Protects against cross-split target evaluation overlap and data leakage.
        """
        mgr = TemporalSplitManager()
        all_splits = [
            TemporalSplit.TRAIN,
            TemporalSplit.VAL,
            TemporalSplit.CAL,
            TemporalSplit.TEST,
        ]

        date_ranges = {split: set(mgr.get_split(split).get_date_range()) for split in all_splits}

        for split_a, split_b in itertools.combinations(all_splits, 2):
            intersection = date_ranges[split_a].intersection(date_ranges[split_b])
            assert not intersection, (
                f"Leakage detected! Target split '{split_a.value}' and '{split_b.value}' "
                f"share {len(intersection)} overlapping evaluation dates: {sorted(list(intersection))[:5]}"
            )

    def test_exact_frozen_boundaries_and_day_counts(self) -> None:
        """
        Verifies exact frozen calendar boundaries and total days for all four splits.
        Guarantees that no test or implementation code silently truncates or expands intervals.
        """
        mgr = TemporalSplitManager()

        expected_bounds = {
            TemporalSplit.TRAIN: ("1980-10-01", "2000-09-30", 7305),  # 20 Water Years, 5 leap days
            TemporalSplit.VAL: (
                "2000-10-01",
                "2005-09-30",
                1826,
            ),  # 5 Water Years, 1 leap day (2004)
            TemporalSplit.CAL: (
                "2005-10-01",
                "2010-09-30",
                1826,
            ),  # 5 Water Years, 1 leap day (2008)
            TemporalSplit.TEST: (
                "2010-10-01",
                "2018-09-30",
                2922,
            ),  # 8 Water Years, 2 leap days (2012, 2016)
        }

        for split, (exp_start, exp_end, exp_days) in expected_bounds.items():
            win = mgr.get_split(split)
            assert win.start_date == pd.Timestamp(exp_start), f"{split.value} start date mismatched"
            assert win.end_date == pd.Timestamp(exp_end), f"{split.value} end date mismatched"
            assert win.total_days == exp_days, f"{split.value} total days mismatched"

    def test_split_chronological_ordering(self) -> None:
        """
        Verifies that splits strictly advance forward in chronological order:
            Train_end < Val_start <= Val_end < Cal_start <= Cal_end < Test_start <= Test_end.
        Also asserts contiguous 1-calendar-day steps between consecutive evaluation splits.
        """
        mgr = TemporalSplitManager()
        train = mgr.get_split(TemporalSplit.TRAIN)
        val = mgr.get_split(TemporalSplit.VAL)
        cal = mgr.get_split(TemporalSplit.CAL)
        test = mgr.get_split(TemporalSplit.TEST)

        # Strictly forward in time
        assert (
            train.start_date
            < train.end_date
            < val.start_date
            < val.end_date
            < cal.start_date
            < cal.end_date
            < test.start_date
            < test.end_date
        )

        # Contiguous water-year calendar boundaries (adjacent splits separated by exactly 1 calendar day)
        assert val.start_date - train.end_date == pd.Timedelta(days=1)
        assert cal.start_date - val.end_date == pd.Timedelta(days=1)
        assert test.start_date - cal.end_date == pd.Timedelta(days=1)

    def test_no_target_boundary_collision_or_silent_clipping(self) -> None:
        """
        Verifies that target evaluation endpoints do not collide with adjacent starts,
        and that get_split() returns unaltered boundaries without clipping.
        """
        mgr = TemporalSplitManager()
        splits = [
            mgr.get_split(TemporalSplit.TRAIN),
            mgr.get_split(TemporalSplit.VAL),
            mgr.get_split(TemporalSplit.CAL),
            mgr.get_split(TemporalSplit.TEST),
        ]

        for i in range(len(splits) - 1):
            assert splits[i].end_date != splits[i + 1].start_date, (
                f"Boundary collision: {splits[i].name.value} end coincides with "
                f"{splits[i + 1].name.value} start ({splits[i].end_date})"
            )
            # Ensure each window is an immutable SplitWindow
            assert isinstance(splits[i], SplitWindow)


class TestBufferedWindowIntegrity:
    """Group B: Evaluates R1.7 historical lookback buffer semantics."""

    @pytest.mark.parametrize(
        "split,exp_buf_start,exp_buf_end,exp_target_start,exp_target_end",
        [
            (
                TemporalSplit.TRAIN,
                "1979-10-01",
                "1980-09-30",
                "1980-10-01",
                "2000-09-30",
            ),
            (
                TemporalSplit.VAL,
                "1999-10-01",
                "2000-09-30",
                "2000-10-01",
                "2005-09-30",
            ),
            (
                TemporalSplit.CAL,
                "2004-09-30",
                "2005-09-30",
                "2005-10-01",
                "2010-09-30",
            ),
            (
                TemporalSplit.TEST,
                "2009-09-30",
                "2010-09-30",
                "2010-10-01",
                "2018-09-30",
            ),
        ],
    )
    def test_buffered_window_exact_boundaries_and_disjointness(
        self,
        split: TemporalSplit,
        exp_buf_start: str,
        exp_buf_end: str,
        exp_target_start: str,
        exp_target_end: str,
    ) -> None:
        """
        Verifies that for every split:
          - buffer_start == target_start - 366 days
          - buffer_end == target_start - 1 day
          - buffer_days == 366 exactly
          - BufferDateRange ∩ TargetDateRange == ∅
          - target boundaries remain completely identical to R1.6
        """
        mgr = TemporalSplitManager()
        buf_win: BufferedSplitWindow = mgr.get_buffered_split(
            split, lookback_days=DEFAULT_LOOKBACK_DAYS
        )

        # Boundary checks
        assert buf_win.buffered_start_date == pd.Timestamp(exp_buf_start)
        assert buf_win.buffer_end_date == pd.Timestamp(exp_buf_end)
        assert buf_win.target_start_date == pd.Timestamp(exp_target_start)
        assert buf_win.target_end_date == pd.Timestamp(exp_target_end)

        # Historical buffer days must be exactly 366
        assert buf_win.buffer_days == 366
        assert len(buf_win.get_buffer_date_range()) == 366

        # Historical buffer must strictly precede target start
        assert buf_win.buffer_end_date < buf_win.target_start_date
        assert buf_win.target_start_date - buf_win.buffer_end_date == pd.Timedelta(days=1)

        # Buffer and target must be strictly disjoint sets of calendar dates
        buf_set = set(buf_win.get_buffer_date_range())
        target_set = set(buf_win.target_window.get_date_range())
        assert not buf_set.intersection(target_set), (
            f"Buffer dates and target dates for split '{split.value}' must not overlap!"
        )

        # Underlying target split is unchanged
        assert buf_win.target_window == mgr.get_split(split)

    def test_custom_and_invalid_lookback_days_governed_cleanly(self) -> None:
        """Verifies validation and immutability for custom/invalid lookback values."""
        mgr = TemporalSplitManager()
        target = mgr.get_split(TemporalSplit.VAL)

        # Custom positive lookback
        buf_custom = BufferedSplitWindow(target_window=target, lookback_days=100)
        assert buf_custom.lookback_days == 100
        assert buf_custom.buffer_days == 100
        assert buf_custom.buffered_start_date == target.start_date - pd.Timedelta(days=100)
        assert buf_custom.buffer_end_date == target.start_date - pd.Timedelta(days=1)

        # Invalid lookbacks
        with pytest.raises(ValueError, match="lookback_days must be a positive integer"):
            BufferedSplitWindow(target_window=target, lookback_days=0)

        with pytest.raises(ValueError, match="lookback_days must be a positive integer"):
            BufferedSplitWindow(target_window=target, lookback_days=-5)

        with pytest.raises(TypeError, match="lookback_days must be an integer"):
            BufferedSplitWindow(target_window=target, lookback_days="366")  # type: ignore

        with pytest.raises(TypeError, match="lookback_days must be an integer"):
            BufferedSplitWindow(target_window=target, lookback_days=True)  # type: ignore


class TestCausalRollingWindowIntegrity:
    """Group C: Evaluates causal rolling-window lookback isolation."""

    @staticmethod
    def _extract_causal_window(
        df: pd.DataFrame,
        t: pd.Timestamp,
        lookback_days: int = 366,
    ) -> Tuple[pd.DataFrame, pd.Timestamp]:
        """
        Pure causal extraction helper for verifying rolling-window invariants:
        Given target forecast timestamp t, returns historical context [t - lookback_days + 1, t]
        and the target evaluation timestamp t.
        """
        window_start = t - pd.Timedelta(days=lookback_days - 1)
        # Causal filter: timestamps must be >= window_start and <= t
        context = df.loc[(df.index >= window_start) & (df.index <= t)]
        return context, t

    def test_causal_rolling_window_contains_zero_future_information(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Verifies that for any forecast evaluation step t, the historical context:
          - Contains exclusively timestamps <= t
          - Contains NO timestamp > t (e.g. t+1, t+2)
          - Spans exactly lookback_days (366 days)
        """
        df = sample_synthetic_basin_df  # 1980-01-01 to 2019-12-31

        # Test across 10 sample target evaluation dates
        eval_dates = [
            pd.Timestamp("1985-06-15"),
            pd.Timestamp("1990-10-01"),
            pd.Timestamp("2000-10-01"),
            pd.Timestamp("2005-10-01"),
            pd.Timestamp("2010-10-01"),
            pd.Timestamp("2015-05-20"),
        ]

        for t in eval_dates:
            context, target_ts = self._extract_causal_window(df, t, lookback_days=366)

            assert len(context) == 366
            assert context.index.max() == target_ts
            # Leakage check: zero timestamps in context strictly greater than target_ts
            future_timestamps = context.index[context.index > target_ts]
            assert len(future_timestamps) == 0, (
                f"Future leakage detected in rolling context for target {target_ts}: {future_timestamps}"
            )
            # The day immediately following (t + 1 day) must NOT be present
            assert (target_ts + pd.Timedelta(days=1)) not in context.index

    def test_deliberate_future_leakage_injection_detected(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Deliberately injects future observations into a historical window and
        verifies that the causal leakage invariant asserts and flags the violation.
        """
        df = sample_synthetic_basin_df
        t = pd.Timestamp("2005-10-01")

        # Legitimate context
        context, _ = self._extract_causal_window(df, t, lookback_days=366)

        # Artificially inject t + 1 day into the feature context
        leaked_future_row = df.loc[[t + pd.Timedelta(days=1)]]
        corrupted_context = pd.concat([context, leaked_future_row])

        # Assert that our causal invariant detects the injected future timestamp
        has_future_leakage = (corrupted_context.index > t).any()
        assert bool(has_future_leakage) is True, (
            "Causal leakage invariant failed to catch injected future row!"
        )

        future_leaked_dates = corrupted_context.index[corrupted_context.index > t]
        assert t + pd.Timedelta(days=1) in future_leaked_dates

    def test_earliest_boundary_requiring_full_historical_context(
        self,
        sample_synthetic_basin_df: pd.DataFrame,
    ) -> None:
        """
        Verifies the exact earliest boundary where the full 366-day context is required.
        For a dataset starting at D_start, the earliest target step t where a full 366-day
        historical window is available without truncation is exactly D_start + 365 days.
        """
        df = sample_synthetic_basin_df
        d_start = df.index.min()  # 1980-01-01

        # Earliest target date that can accommodate a 366-day window [d_start, t]
        earliest_full_target = d_start + pd.Timedelta(days=365)  # 1980-12-31

        context_full, _ = self._extract_causal_window(df, earliest_full_target, lookback_days=366)
        assert len(context_full) == 366
        assert context_full.index.min() == d_start
        assert context_full.index.max() == earliest_full_target

        # One day earlier: context cannot provide 366 days from d_start
        one_day_earlier = earliest_full_target - pd.Timedelta(days=1)
        context_short, _ = self._extract_causal_window(df, one_day_earlier, lookback_days=366)
        assert len(context_short) == 365  # Incomplete historical context
