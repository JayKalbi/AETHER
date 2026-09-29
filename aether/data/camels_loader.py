"""
CAMELS-US Raw Data Loader.

Deterministic, offline parser and loader for CAMELS-US v1.2 meteorological forcing,
USGS streamflow observations, and static catchment attribute tables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd

from aether.data.basin_registry import BenchmarkRegistry


class CamelsDatasetLoader:
    """
    Deterministic, offline raw data loader for CAMELS-US v1.2.

    Parameters
    ----------
    data_dir : Union[str, Path]
        Path to the root CAMELS-US directory containing:
        - `basin_mean_forcing/`
        - `usgs_streamflow/`
        - `camels_attributes_v2.0/`
    registry : Optional[BenchmarkRegistry]
        Optional benchmark registry instance for basin membership validation.
    enforce_benchmark : bool
        If True, requires an active registry and validates that any loaded basin ID
        belongs to the benchmark population. Defaults to False.
    """

    SUPPORTED_ATTRIBUTE_GROUPS = ("topo", "clim", "soil", "vege", "geol", "hydro")

    def __init__(
        self,
        data_dir: Union[str, Path] = "data/camels_us",
        registry: Optional[BenchmarkRegistry] = None,
        enforce_benchmark: bool = False,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.registry = registry
        self.enforce_benchmark = enforce_benchmark

        if self.enforce_benchmark and self.registry is None:
            raise ValueError(
                "Cannot enforce benchmark membership without an active BenchmarkRegistry instance."
            )

        # Internal cache for basin_id -> huc_02 path mapping
        self._huc_cache: Dict[str, str] = {}

    def _validate_basin(self, basin_id: Union[str, int]) -> str:
        """
        Validates format and optional benchmark membership of a basin identifier.
        """
        s = str(basin_id).strip()
        if len(s) < 8 and s.isdigit():
            s = s.zfill(8)
        if len(s) != 8 or not s.isdigit():
            raise ValueError(
                f"Invalid CAMELS-US basin ID format: '{basin_id}'. Expected an 8-digit numeric identifier."
            )

        if self.enforce_benchmark and self.registry is not None:
            if not self.registry.is_included(s):
                raise ValueError(
                    f"Basin '{s}' is not a member of the canonical 531-basin CAMELS-US benchmark."
                )

        return s

    def _resolve_basin_file(
        self,
        sub_dir: Path,
        basin_id: str,
        file_suffix: str,
    ) -> Path:
        """
        Deterministically locates a basin data file across HUC subdirectories.
        """
        if not sub_dir.exists():
            raise FileNotFoundError(f"Required CAMELS directory not found: {sub_dir.resolve()}")

        # 1. Check cache first
        if basin_id in self._huc_cache:
            huc_dir = sub_dir / self._huc_cache[basin_id]
            if huc_dir.exists():
                matches = sorted(huc_dir.glob(f"{basin_id}_*{file_suffix}"))
                if len(matches) == 1:
                    return matches[0]

        # 2. Check metadata in registry if available
        if self.registry is not None:
            try:
                meta = self.registry.metadata(basin_id)
                if meta is not None and meta.huc_02:
                    candidate_huc = str(meta.huc_02).zfill(2)
                    huc_dir = sub_dir / candidate_huc
                    if huc_dir.exists():
                        matches = sorted(huc_dir.glob(f"{basin_id}_*{file_suffix}"))
                        if len(matches) == 1:
                            self._huc_cache[basin_id] = candidate_huc
                            return matches[0]
            except KeyError:
                pass

        # 3. Deterministically scan sorted HUC subdirectories (01 to 18)
        huc_dirs = sorted([d for d in sub_dir.iterdir() if d.is_dir()])
        found_files: List[Tuple[str, Path]] = []

        for d in huc_dirs:
            matches = sorted(d.glob(f"{basin_id}_*{file_suffix}"))
            for m in matches:
                found_files.append((d.name, m))

        if len(found_files) == 1:
            huc_name, file_path = found_files[0]
            self._huc_cache[basin_id] = huc_name
            return file_path
        elif len(found_files) > 1:
            conflicting = [str(p.resolve()) for _, p in found_files]
            raise RuntimeError(
                f"Conflicting files found for basin '{basin_id}' in multiple directories: {conflicting}"
            )
        else:
            raise FileNotFoundError(
                f"No file matching basin ID '{basin_id}' with suffix '{file_suffix}' found in {sub_dir.resolve()}."
            )

    def load_forcing(
        self,
        basin_id: Union[str, int],
        forcing_type: str = "daymet",
    ) -> pd.DataFrame:
        """
        Loads raw daily meteorological forcing time series for a catchment.

        Parameters
        ----------
        basin_id : Union[str, int]
            8-digit USGS gauge identifier.
        forcing_type : str
            Forcing dataset subdirectory (default: 'daymet').

        Returns
        -------
        pd.DataFrame
            DataFrame indexed by DatetimeIndex ('date') containing unmodified numeric forcing values.
        """
        valid_basin = self._validate_basin(basin_id)
        forcing_dir = self.data_dir / "basin_mean_forcing" / forcing_type
        forcing_file = self._resolve_basin_file(forcing_dir, valid_basin, "forcing_leap.txt")

        # Daymet files have 3 metadata header lines, line 4 is the column headers
        try:
            df = pd.read_csv(
                forcing_file,
                sep=r"\s+",
                skiprows=3,
                header=0,
                dtype={
                    "Year": int,
                    "Mn": int,
                    "Day": int,
                    "Hr": int,
                },
            )
        except Exception as e:
            raise ValueError(f"Failed to parse forcing file {forcing_file.resolve()}: {e}") from e

        required_cols = {
            "Year",
            "Mn",
            "Day",
            "prcp(mm/day)",
            "tmin(C)",
            "tmax(C)",
            "srad(W/m2)",
            "vp(Pa)",
        }
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns in forcing file {forcing_file.resolve()}: {sorted(missing_cols)}"
            )

        # Parse and structurally validate timestamps
        try:
            dates = pd.to_datetime(
                {
                    "year": df["Year"],
                    "month": df["Mn"],
                    "day": df["Day"],
                }
            )
        except Exception as e:
            raise ValueError(
                f"Invalid dates encountered in forcing file {forcing_file.resolve()}: {e}"
            ) from e

        if not dates.is_monotonic_increasing:
            raise ValueError(
                f"Timestamps in forcing file {forcing_file.resolve()} are not monotonically increasing."
            )

        if dates.duplicated().any():
            duplicates = dates[dates.duplicated()].tolist()
            raise ValueError(
                f"Duplicate timestamps found in forcing file {forcing_file.resolve()}: {duplicates[:5]}"
            )

        df.index = pd.DatetimeIndex(dates, name="date")
        return df

    def load_streamflow(
        self,
        basin_id: Union[str, int],
    ) -> pd.DataFrame:
        """
        Loads raw daily USGS streamflow observation time series and quality flags.

        Parameters
        ----------
        basin_id : Union[str, int]
            8-digit USGS gauge identifier.

        Returns
        -------
        pd.DataFrame
            DataFrame indexed by DatetimeIndex ('date') containing:
            ['basin_id', 'streamflow_cfs', 'qc_flag'].
            Values are strictly raw: negative flow values and quality flags are preserved as-is.
        """
        valid_basin = self._validate_basin(basin_id)
        streamflow_dir = self.data_dir / "usgs_streamflow"
        streamflow_file = self._resolve_basin_file(streamflow_dir, valid_basin, "streamflow_qc.txt")

        try:
            df = pd.read_csv(
                streamflow_file,
                sep=r"\s+",
                header=None,
                names=["basin_id", "Year", "Mn", "Day", "streamflow_cfs", "qc_flag"],
                dtype={
                    "basin_id": str,
                    "Year": int,
                    "Mn": int,
                    "Day": int,
                    "streamflow_cfs": float,
                    "qc_flag": str,
                },
            )
        except Exception as e:
            raise ValueError(
                f"Failed to parse streamflow file {streamflow_file.resolve()}: {e}"
            ) from e

        df["basin_id"] = df["basin_id"].str.strip().str.zfill(8)

        # Parse and structurally validate timestamps
        try:
            dates = pd.to_datetime(
                {
                    "year": df["Year"],
                    "month": df["Mn"],
                    "day": df["Day"],
                }
            )
        except Exception as e:
            raise ValueError(
                f"Invalid dates encountered in streamflow file {streamflow_file.resolve()}: {e}"
            ) from e

        if not dates.is_monotonic_increasing:
            raise ValueError(
                f"Timestamps in streamflow file {streamflow_file.resolve()} are not monotonically increasing."
            )

        if dates.duplicated().any():
            duplicates = dates[dates.duplicated()].tolist()
            raise ValueError(
                f"Duplicate timestamps found in streamflow file {streamflow_file.resolve()}: {duplicates[:5]}"
            )

        df.index = pd.DatetimeIndex(dates, name="date")
        # Drop raw integer year/month/day columns to retain clean time-series columns
        df = df[["basin_id", "streamflow_cfs", "qc_flag"]]
        return df

    def load_attributes(
        self,
        basins: Optional[Sequence[Union[str, int]]] = None,
        groups: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """
        Loads raw static catchment attributes merged across requested attribute tables.

        Parameters
        ----------
        basins : Optional[Sequence[Union[str, int]]]
            Subset of 8-digit basin IDs to return. If None, returns all basins present in files.
        groups : Optional[Sequence[str]]
            Subset of attribute groups from ('topo', 'clim', 'soil', 'vege', 'geol', 'hydro').
            Defaults to all six groups.

        Returns
        -------
        pd.DataFrame
            Merged DataFrame indexed by 8-digit 'basin_id' string, sorted alphanumerically.
        """
        attr_dir = self.data_dir / "camels_attributes_v2.0"
        if not attr_dir.exists():
            raise FileNotFoundError(f"Attributes directory not found at: {attr_dir.resolve()}")

        selected_groups = groups or self.SUPPORTED_ATTRIBUTE_GROUPS
        for g in selected_groups:
            if g not in self.SUPPORTED_ATTRIBUTE_GROUPS:
                raise ValueError(
                    f"Unsupported attribute group '{g}'. Supported groups are: {self.SUPPORTED_ATTRIBUTE_GROUPS}"
                )

        target_basins: Optional[List[str]] = None
        if basins is not None:
            target_basins = [self._validate_basin(b) for b in basins]

        merged_df: Optional[pd.DataFrame] = None

        # Iterate in deterministic canonical order
        for group in self.SUPPORTED_ATTRIBUTE_GROUPS:
            if group not in selected_groups:
                continue

            file_path = attr_dir / f"camels_{group}.txt"
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Attribute table for group '{group}' not found at: {file_path.resolve()}"
                )

            try:
                df_group = pd.read_csv(file_path, sep=";", dtype={"gauge_id": str})
            except Exception as e:
                raise ValueError(
                    f"Failed to read attribute table {file_path.resolve()}: {e}"
                ) from e

            if "gauge_id" not in df_group.columns:
                raise ValueError(
                    f"Missing 'gauge_id' column in attribute file: {file_path.resolve()}"
                )

            df_group["gauge_id"] = df_group["gauge_id"].str.strip().str.zfill(8)
            df_group = df_group.set_index("gauge_id")

            if target_basins is not None:
                # Retain only requested basins if present
                df_group = df_group.reindex([b for b in target_basins if b in df_group.index])

            if merged_df is None:
                merged_df = df_group
            else:
                # Check for overlapping column names
                overlapping_cols = set(merged_df.columns).intersection(set(df_group.columns))
                for col in overlapping_cols:
                    # Compare on common index
                    common_idx = merged_df.index.intersection(df_group.index)
                    s_left = merged_df.loc[common_idx, col]
                    s_right = df_group.loc[common_idx, col]

                    # Check if identical (handling NaN equality)
                    both_nan = s_left.isna() & s_right.isna()
                    equal_vals = (s_left == s_right) | both_nan
                    if not equal_vals.all():
                        diff_basins = common_idx[~equal_vals].tolist()
                        raise ValueError(
                            f"Conflicting attribute values encountered for column '{col}' between "
                            f"existing tables and group '{group}' for basins: {diff_basins[:5]}"
                        )

                    # Deterministically drop duplicate column from incoming table
                    df_group = df_group.drop(columns=[col])

                merged_df = merged_df.join(df_group, how="outer")

        if merged_df is None:
            return pd.DataFrame()

        merged_df.index.name = "basin_id"
        merged_df = merged_df.sort_index()

        # If specific basins were requested, enforce final order
        if target_basins is not None:
            merged_df = merged_df.reindex(target_basins)

        return merged_df
