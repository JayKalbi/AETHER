"""
Temporal Split Manager.

Provides immutable representations, strict validation, and deterministic
slicing for AETHER's frozen Water-Year temporal partitions (TRAIN, VAL, CAL, TEST).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union

import pandas as pd

from aether.configs.base_config import TemporalSplitConfig
from aether.utils.types import TemporalSplit


def _parse_and_validate_timestamp(ts_input: Union[str, pd.Timestamp]) -> pd.Timestamp:
    """
    Parses a string or Timestamp, rejecting timezone-aware input and invalid dates.
    Normalizes time component to midnight.
    """
    if isinstance(ts_input, str):
        try:
            ts = pd.Timestamp(ts_input)
        except Exception as e:
            raise ValueError(f"Invalid timestamp format or calendar date '{ts_input}': {e}") from e
    elif isinstance(ts_input, pd.Timestamp):
        ts = ts_input
    else:
        raise TypeError(f"Expected str or pd.Timestamp, got {type(ts_input).__name__}")

    # Reject timezone-aware timestamps clearly
    if ts.tzinfo is not None:
        raise ValueError(
            f"Timezone-aware timestamp '{ts_input}' is not permitted. "
            "AETHER temporal splits require timezone-naive daily calendar dates."
        )

    # Normalize to midnight to ensure exact calendar day comparison
    return ts.normalize()


@dataclass(frozen=True)
class SplitWindow:
    """
    Immutable representation of an inclusive temporal partition [start_date, end_date].

    Attributes
    ----------
    name : TemporalSplit
        The canonical split identifier (TRAIN, VAL, CAL, TEST).
    start_date : pd.Timestamp
        The inclusive starting calendar date (normalized to midnight, timezone-naive).
    end_date : pd.Timestamp
        The inclusive ending calendar date (normalized to midnight, timezone-naive).
    """

    name: TemporalSplit
    start_date: pd.Timestamp
    end_date: pd.Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.name, TemporalSplit):
            raise TypeError(
                f"Split name must be a TemporalSplit enum, got {type(self.name).__name__}"
            )
        if not isinstance(self.start_date, pd.Timestamp) or not isinstance(
            self.end_date, pd.Timestamp
        ):
            raise TypeError("start_date and end_date must be pd.Timestamp instances.")
        if self.start_date.tzinfo is not None or self.end_date.tzinfo is not None:
            raise ValueError("SplitWindow boundaries must be timezone-naive.")
        if self.start_date > self.end_date:
            raise ValueError(
                f"Split '{self.name.value}' has start_date ({self.start_date.strftime('%Y-%m-%d')}) "
                f"> end_date ({self.end_date.strftime('%Y-%m-%d')})."
            )

    @property
    def total_days(self) -> int:
        """Total inclusive calendar days, including leap days."""
        return (self.end_date - self.start_date).days + 1

    def contains(self, timestamp: Union[str, pd.Timestamp]) -> bool:
        """Returns True if the timestamp falls within the inclusive interval [start_date, end_date]."""
        ts = _parse_and_validate_timestamp(timestamp)
        return bool(self.start_date <= ts <= self.end_date)

    def get_date_range(self) -> pd.DatetimeIndex:
        """Generates a complete, daily pd.DatetimeIndex spanning [start_date, end_date]."""
        return pd.date_range(start=self.start_date, end=self.end_date, freq="D")


# Default historical context buffer length (L=365 model sequence + h=1 forecast horizon)
DEFAULT_LOOKBACK_DAYS: int = 366


@dataclass(frozen=True)
class BufferedSplitWindow:
    """
    Immutable representation of a temporal split prepended with a historical context buffer.

    Attributes
    ----------
    target_window : SplitWindow
        The authoritative target evaluation split [target_start, target_end].
    lookback_days : int
        Number of historical calendar days required prior to target_start (default 366).
    """

    target_window: SplitWindow
    lookback_days: int = DEFAULT_LOOKBACK_DAYS

    def __post_init__(self) -> None:
        if not isinstance(self.target_window, SplitWindow):
            raise TypeError(
                f"target_window must be an instance of SplitWindow, got {type(self.target_window).__name__}"
            )
        if not isinstance(self.lookback_days, int) or isinstance(self.lookback_days, bool):
            raise TypeError(
                f"lookback_days must be an integer, got {type(self.lookback_days).__name__}"
            )
        if self.lookback_days <= 0:
            raise ValueError(f"lookback_days must be a positive integer, got {self.lookback_days}")

    @property
    def name(self) -> TemporalSplit:
        """The canonical split identifier of the underlying target window."""
        return self.target_window.name

    @property
    def target_start_date(self) -> pd.Timestamp:
        """The inclusive starting calendar date of the target evaluation window."""
        return self.target_window.start_date

    @property
    def target_end_date(self) -> pd.Timestamp:
        """The inclusive ending calendar date of the target evaluation window."""
        return self.target_window.end_date

    @property
    def buffered_start_date(self) -> pd.Timestamp:
        """The inclusive starting calendar date of the historical context buffer."""
        return self.target_window.start_date - pd.Timedelta(days=self.lookback_days)

    @property
    def buffer_end_date(self) -> pd.Timestamp:
        """The inclusive ending calendar date of the historical context buffer (target_start - 1 day)."""
        return self.target_window.start_date - pd.Timedelta(days=1)

    @property
    def buffer_days(self) -> int:
        """Exact count of calendar days in the historical context buffer."""
        return (self.buffer_end_date - self.buffered_start_date).days + 1

    @property
    def total_buffered_days(self) -> int:
        """Total inclusive calendar days spanning [buffered_start_date, target_end_date]."""
        return (self.target_end_date - self.buffered_start_date).days + 1

    def get_buffer_date_range(self) -> pd.DatetimeIndex:
        """Generates a complete daily DatetimeIndex spanning [buffered_start_date, buffer_end_date]."""
        return pd.date_range(start=self.buffered_start_date, end=self.buffer_end_date, freq="D")

    def get_total_date_range(self) -> pd.DatetimeIndex:
        """Generates a complete daily DatetimeIndex spanning [buffered_start_date, target_end_date]."""
        return pd.date_range(start=self.buffered_start_date, end=self.target_end_date, freq="D")


class TemporalSplitManager:
    """
    Manages and validates frozen temporal partitions (TRAIN, VAL, CAL, TEST).

    Guarantees strict chronological ordering, zero temporal overlap, and deterministic slicing.
    """

    def __init__(self, config: Optional[TemporalSplitConfig] = None) -> None:
        """
        Initializes the split manager using either the authoritative frozen defaults
        from TemporalSplitConfig or an explicitly provided TemporalSplitConfig.
        """
        cfg = TemporalSplitConfig() if config is None else config
        if not isinstance(cfg, TemporalSplitConfig):
            raise TypeError(f"Expected TemporalSplitConfig or None, got {type(config).__name__}")

        raw_dates = {
            TemporalSplit.TRAIN: (cfg.train_start, cfg.train_end),
            TemporalSplit.VAL: (cfg.val_start, cfg.val_end),
            TemporalSplit.CAL: (cfg.cal_start, cfg.cal_end),
            TemporalSplit.TEST: (cfg.test_start, cfg.test_end),
        }

        self._splits: Dict[TemporalSplit, SplitWindow] = self._build_and_validate_splits(raw_dates)

    @staticmethod
    def _build_and_validate_splits(
        raw_dates: Dict[TemporalSplit, Tuple[str, str]],
    ) -> Dict[TemporalSplit, SplitWindow]:
        """Validates all canonical splits for presence, boundary order, sequence, and overlap."""
        # 1. Require all four canonical splits
        required_splits = (
            TemporalSplit.TRAIN,
            TemporalSplit.VAL,
            TemporalSplit.CAL,
            TemporalSplit.TEST,
        )
        for req in required_splits:
            if req not in raw_dates:
                raise ValueError(f"Missing required canonical split: '{req.value}'.")

        # 2. Build SplitWindows with parsed timestamps
        windows: Dict[TemporalSplit, SplitWindow] = {}
        for split_key, (start_str, end_str) in raw_dates.items():
            if not isinstance(split_key, TemporalSplit):
                raise TypeError(f"Invalid split key type: {type(split_key).__name__}")
            start_ts = _parse_and_validate_timestamp(start_str)
            end_ts = _parse_and_validate_timestamp(end_str)
            windows[split_key] = SplitWindow(name=split_key, start_date=start_ts, end_date=end_ts)

        # 3. Validate strict chronological sequence and non-overlapping adjacency
        ordered = [
            windows[TemporalSplit.TRAIN],
            windows[TemporalSplit.VAL],
            windows[TemporalSplit.CAL],
            windows[TemporalSplit.TEST],
        ]

        for i in range(len(ordered) - 1):
            curr_split = ordered[i]
            next_split = ordered[i + 1]

            if curr_split.end_date >= next_split.start_date:
                if curr_split.end_date == next_split.start_date:
                    raise ValueError(
                        f"Boundary collision between '{curr_split.name.value}' and '{next_split.name.value}': "
                        f"both include '{curr_split.end_date.strftime('%Y-%m-%d')}'. "
                        "Splits must be strictly non-overlapping."
                    )
                raise ValueError(
                    f"Temporal overlap detected: '{curr_split.name.value}' ends at "
                    f"{curr_split.end_date.strftime('%Y-%m-%d')} which is >= "
                    f"'{next_split.name.value}' start at {next_split.start_date.strftime('%Y-%m-%d')}."
                )

        return windows

    def _resolve_split(self, split: Union[TemporalSplit, str]) -> TemporalSplit:
        """Resolves a split name or enum to a canonical TemporalSplit enum."""
        if isinstance(split, TemporalSplit):
            return split
        if isinstance(split, str):
            clean_str = split.strip().lower()
            for member in TemporalSplit:
                if member.value == clean_str:
                    return member
            valid_names = [m.value for m in TemporalSplit]
            raise ValueError(f"Unknown split name '{split}'. Must be one of: {valid_names}")
        raise TypeError(f"Expected TemporalSplit or str, got {type(split).__name__}")

    def get_split(self, split: Union[TemporalSplit, str]) -> SplitWindow:
        """Returns the immutable SplitWindow for the requested split."""
        resolved = self._resolve_split(split)
        return self._splits[resolved]

    def get_all_splits(self) -> Dict[TemporalSplit, SplitWindow]:
        """Returns an immutable dictionary mapping all canonical splits to their SplitWindow."""
        return dict(self._splits)

    def slice_dataframe(
        self,
        df: Union[pd.DataFrame, pd.Series],
        split: Union[TemporalSplit, str],
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Slices a DataFrame or Series to the requested split interval [start_date, end_date].

        Both boundaries are inclusive. The input is never modified.
        Fails loudly if the index is not a DatetimeIndex, is not monotonic increasing,
        or contains duplicate timestamps.
        """
        if not isinstance(df, (pd.DataFrame, pd.Series)):
            raise TypeError(f"Expected pd.DataFrame or pd.Series, got {type(df).__name__}")

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError(
                f"Input must have a pd.DatetimeIndex to slice by temporal split, got {type(df.index).__name__}."
            )

        if df.index.tz is not None:
            raise ValueError(
                "Input DatetimeIndex is timezone-aware. "
                "AETHER temporal splits require timezone-naive daily calendar indices."
            )

        if not df.index.is_monotonic_increasing:
            raise ValueError(
                "Input DatetimeIndex is not monotonically increasing. Cannot slice cleanly."
            )

        if df.index.duplicated().any():
            dups = df.index[df.index.duplicated()].strftime("%Y-%m-%d").unique().tolist()
            raise ValueError(
                f"Duplicate timestamps found in index: {dups[:5]}. Cannot slice cleanly."
            )

        window = self.get_split(split)
        # Slicing with exact inclusive timestamps [start, end]
        mask = (df.index >= window.start_date) & (df.index <= window.end_date)
        return df.loc[mask]

    def validate_data_coverage(
        self,
        available_start: Union[str, pd.Timestamp],
        available_end: Union[str, pd.Timestamp],
        split: Union[TemporalSplit, str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether available data range [available_start, available_end]
        fully covers the requested split window [split.start_date, split.end_date].

        Returns (is_covered, explanation).
        Does NOT alter or clip the split definition.
        """
        window = self.get_split(split)
        start_ts = _parse_and_validate_timestamp(available_start)
        end_ts = _parse_and_validate_timestamp(available_end)

        if start_ts > end_ts:
            raise ValueError(
                f"available_start ({start_ts.strftime('%Y-%m-%d')}) must be <= "
                f"available_end ({end_ts.strftime('%Y-%m-%d')})"
            )

        missing_reasons = []
        if start_ts > window.start_date:
            missing_reasons.append(
                f"Available data starts late at {start_ts.strftime('%Y-%m-%d')} "
                f"(split '{window.name.value}' requires {window.start_date.strftime('%Y-%m-%d')})"
            )
        if end_ts < window.end_date:
            missing_reasons.append(
                f"Available data ends early at {end_ts.strftime('%Y-%m-%d')} "
                f"(split '{window.name.value}' requires {window.end_date.strftime('%Y-%m-%d')})"
            )

        if missing_reasons:
            explanation = (
                f"Data coverage incomplete for split '{window.name.value}': "
                + "; ".join(missing_reasons)
                + "."
            )
            return False, explanation

        return True, None

    def get_buffered_split(
        self,
        split: Union[TemporalSplit, str],
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> BufferedSplitWindow:
        """
        Returns a BufferedSplitWindow prepending the requested historical context
        buffer (default 366 days) to the target evaluation split.
        """
        target_win = self.get_split(split)
        return BufferedSplitWindow(target_window=target_win, lookback_days=lookback_days)

    def validate_buffered_data_coverage(
        self,
        available_start: Union[str, pd.Timestamp],
        available_end: Union[str, pd.Timestamp],
        split: Union[TemporalSplit, str],
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether available data range [available_start, available_end]
        fully covers BOTH the historical context buffer [buffered_start_date, buffer_end_date]
        AND the target evaluation interval [target_start_date, target_end_date].

        Returns (is_covered, explanation).
        Does NOT alter or clip the split definition.
        """
        buffered_win = self.get_buffered_split(split, lookback_days=lookback_days)
        start_ts = _parse_and_validate_timestamp(available_start)
        end_ts = _parse_and_validate_timestamp(available_end)

        if start_ts > end_ts:
            raise ValueError(
                f"available_start ({start_ts.strftime('%Y-%m-%d')}) must be <= "
                f"available_end ({end_ts.strftime('%Y-%m-%d')})"
            )

        missing_reasons = []
        if start_ts > buffered_win.buffered_start_date:
            missing_reasons.append(
                f"Available data starts late at {start_ts.strftime('%Y-%m-%d')} "
                f"(buffered split '{buffered_win.name.value}' requires historical buffer from "
                f"{buffered_win.buffered_start_date.strftime('%Y-%m-%d')})"
            )
        if end_ts < buffered_win.target_end_date:
            missing_reasons.append(
                f"Available data ends early at {end_ts.strftime('%Y-%m-%d')} "
                f"(split '{buffered_win.name.value}' requires target through "
                f"{buffered_win.target_end_date.strftime('%Y-%m-%d')})"
            )

        if missing_reasons:
            explanation = (
                f"Buffered data coverage incomplete for split '{buffered_win.name.value}': "
                + "; ".join(missing_reasons)
                + "."
            )
            return False, explanation

        return True, None
