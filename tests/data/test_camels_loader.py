"""
Unit tests for CAMELS-US raw dataset loader (Issue R1.2).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aether.data.basin_registry import BenchmarkRegistry
from aether.data.camels_loader import (
    DAYMET_RAW_FORCING_COLUMNS,
    CamelsDatasetLoader,
    validate_forcing_schema,
)


@pytest.fixture
def mock_camels_dir(tmp_path: Path) -> Path:
    """
    Creates an isolated mock CAMELS-US v1.2 directory structure with
    realistic forcing, streamflow, and attribute files.
    """
    camels_dir = tmp_path / "camels_us"

    # 1. Daymet forcing: HUC 01
    huc01_forcing = camels_dir / "basin_mean_forcing" / "daymet" / "01"
    huc01_forcing.mkdir(parents=True)
    forcing_01022500 = huc01_forcing / "01022500_lump_cida_forcing_leap.txt"
    forcing_content = (
        "44.60744 -67.93524\n"
        "84.0\n"
        "619500000.0\n"
        "Year Mnth Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)\n"
        "1995 10 01 12 42300 0.00 245.50 0.00 18.50 6.20 850.00\n"
        "1995 10 02 12 42100 12.40 180.20 0.00 14.10 8.00 920.50\n"
        "1995 10 03 12 41900 5.10 210.00 0.00 16.00 5.50 780.00\n"
    )
    forcing_01022500.write_text(forcing_content, encoding="utf-8")

    # 2. USGS streamflow: HUC 01
    huc01_streamflow = camels_dir / "usgs_streamflow" / "01"
    huc01_streamflow.mkdir(parents=True)
    streamflow_01022500 = huc01_streamflow / "01022500_streamflow_qc.txt"
    streamflow_content = (
        "01022500 1995 10 01 125.50 A\n01022500 1995 10 02 -999.00 M\n01022500 1995 10 03 0.00 A\n"
    )
    streamflow_01022500.write_text(streamflow_content, encoding="utf-8")

    # 3. Static attributes: camels_attributes_v2.0
    attr_dir = camels_dir / "camels_attributes_v2.0"
    attr_dir.mkdir(parents=True)

    topo_content = (
        "gauge_id;huc_02;gauge_lat;gauge_lon;elev_mean;slope_mean;area_gages2\n"
        "01022500;01;44.60744;-67.93524;84.0;15.2;619.5\n"
        "01031500;01;45.17505;-69.31472;201.0;22.4;769.0\n"
    )
    (attr_dir / "camels_topo.txt").write_text(topo_content, encoding="utf-8")

    clim_content = (
        "gauge_id;p_mean;pet_mean;aridity;frac_snow\n"
        "01022500;3.45;2.20;0.6377;0.22\n"
        "01031500;3.20;2.10;0.6562;0.31\n"
    )
    (attr_dir / "camels_clim.txt").write_text(clim_content, encoding="utf-8")

    return camels_dir


class TestCamelsDatasetLoader:
    """Test suite verifying raw CAMELS-US data loading and preservation."""

    def test_load_forcing_raw_preservation(self, mock_camels_dir: Path):
        """Verifies raw forcing values and units are parsed without transformation or scaling."""
        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_forcing("01022500")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.name == "date"
        assert df.index[0] == pd.Timestamp("1995-10-01")
        assert df.index[2] == pd.Timestamp("1995-10-03")

        # Values must match raw file exactly
        assert df.loc[pd.Timestamp("1995-10-01"), "prcp(mm/day)"] == 0.00
        assert df.loc[pd.Timestamp("1995-10-02"), "prcp(mm/day)"] == 12.40
        assert df.loc[pd.Timestamp("1995-10-02"), "tmax(C)"] == 14.10
        assert df.loc[pd.Timestamp("1995-10-03"), "vp(Pa)"] == 780.00

    def test_load_streamflow_raw_values_and_flags_preserved(self, mock_camels_dir: Path):
        """Verifies streamflow preserves negative missing values and QC flags without imputation."""
        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_streamflow(1022500)  # integer auto-padded

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["basin_id", "streamflow_cfs", "qc_flag"]
        assert df.index[0] == pd.Timestamp("1995-10-01")

        # Negative flow -999.00 must NOT be masked or converted to NaN
        assert df.loc[pd.Timestamp("1995-10-02"), "streamflow_cfs"] == -999.00
        assert df.loc[pd.Timestamp("1995-10-02"), "qc_flag"] == "M"

        # Zero flow must be preserved as 0.00
        assert df.loc[pd.Timestamp("1995-10-03"), "streamflow_cfs"] == 0.00
        assert df.loc[pd.Timestamp("1995-10-03"), "qc_flag"] == "A"

    def test_no_synthetic_date_infilling(self, mock_camels_dir: Path):
        """Verifies loader does NOT manufacture continuity or insert missing calendar dates."""
        huc01_streamflow = mock_camels_dir / "usgs_streamflow" / "01"
        gap_file = huc01_streamflow / "01031500_streamflow_qc.txt"
        # 1-day gap between 1995-10-01 and 1995-10-03
        gap_content = "01031500 1995 10 01 50.0 A\n01031500 1995 10 03 60.0 A\n"
        gap_file.write_text(gap_content, encoding="utf-8")

        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_streamflow("01031500")
        assert len(df) == 2
        assert pd.Timestamp("1995-10-02") not in df.index

    def test_non_monotonic_dates_rejected(self, mock_camels_dir: Path):
        """Verifies that non-chronological dates trigger explicit ValueError."""
        huc01_forcing = mock_camels_dir / "basin_mean_forcing" / "daymet" / "01"
        bad_file = huc01_forcing / "01031500_lump_cida_forcing_leap.txt"
        bad_content = (
            "lat lon\nelev\narea\n"
            "Year Mnth Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)\n"
            "1995 10 02 12 42100 12.40 180.20 0.00 14.10 8.00 920.50\n"
            "1995 10 01 12 42300 0.00 245.50 0.00 18.50 6.20 850.00\n"
        )
        bad_file.write_text(bad_content, encoding="utf-8")

        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        with pytest.raises(ValueError, match="not monotonically increasing"):
            loader.load_forcing("01031500")

    def test_duplicate_timestamps_rejected(self, mock_camels_dir: Path):
        """Verifies duplicate timestamps raise ValueError."""
        huc01_streamflow = mock_camels_dir / "usgs_streamflow" / "01"
        dup_file = huc01_streamflow / "01031500_streamflow_qc.txt"
        dup_content = "01031500 1995 10 01 50.0 A\n01031500 1995 10 01 55.0 A\n"
        dup_file.write_text(dup_content, encoding="utf-8")

        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        with pytest.raises(ValueError, match="Duplicate timestamps"):
            loader.load_streamflow("01031500")

    def test_deterministic_attributes_merge(self, mock_camels_dir: Path):
        """Verifies static attribute tables merge deterministically with identical duplicate column retention."""
        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_attributes(groups=["topo", "clim"])

        assert isinstance(df, pd.DataFrame)
        assert df.index.name == "basin_id"
        assert list(df.index) == ["01022500", "01031500"]
        assert "elev_mean" in df.columns
        assert "aridity" in df.columns
        assert df.loc["01022500", "area_gages2"] == 619.5
        assert df.loc["01022500", "aridity"] == pytest.approx(0.6377)

    def test_conflicting_duplicate_attribute_column_raises_error(self, mock_camels_dir: Path):
        """Verifies conflicting values in overlapping attribute columns raise explicit ValueError."""
        attr_dir = mock_camels_dir / "camels_attributes_v2.0"
        # Add soil table with conflicting elev_mean values
        conflicting_soil = "gauge_id;elev_mean;clay_frac\n01022500;999.0;18.5\n"
        (attr_dir / "camels_soil.txt").write_text(conflicting_soil, encoding="utf-8")

        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        with pytest.raises(ValueError, match="Conflicting attribute values encountered"):
            loader.load_attributes(groups=["topo", "soil"])

    def test_identical_duplicate_attribute_column_retained_cleanly(self, mock_camels_dir: Path):
        """Verifies identical overlapping columns between tables are cleanly unified."""
        attr_dir = mock_camels_dir / "camels_attributes_v2.0"
        matching_soil = "gauge_id;elev_mean;clay_frac\n01022500;84.0;18.5\n01031500;201.0;12.0\n"
        (attr_dir / "camels_soil.txt").write_text(matching_soil, encoding="utf-8")

        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_attributes(groups=["topo", "soil"])
        assert "clay_frac" in df.columns
        assert "elev_mean" in df.columns
        assert df.loc["01022500", "elev_mean"] == 84.0

    def test_enforce_benchmark_membership(self, mock_camels_dir: Path):
        """Verifies enforce_benchmark policy rejects basins not in registry."""
        registry = BenchmarkRegistry(benchmark_basins=["01022500"])
        loader = CamelsDatasetLoader(
            data_dir=mock_camels_dir,
            registry=registry,
            enforce_benchmark=True,
        )

        # 01022500 is in registry -> succeeds
        df = loader.load_forcing("01022500")
        assert len(df) == 3

        # 01031500 is not in registry -> raises ValueError
        with pytest.raises(ValueError, match="not a member of the canonical 531-basin"):
            loader.load_forcing("01031500")

    def test_enforce_benchmark_without_registry_rejected(self, mock_camels_dir: Path):
        """Verifies initializing enforce_benchmark=True without a registry raises ValueError."""
        with pytest.raises(
            ValueError, match="Cannot enforce benchmark membership without an active"
        ):
            CamelsDatasetLoader(data_dir=mock_camels_dir, enforce_benchmark=True)

    def test_missing_files_and_directories_raise_filenotfound(self, mock_camels_dir: Path):
        """Verifies missing files or directories raise descriptive FileNotFoundError."""
        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        with pytest.raises(FileNotFoundError, match="No file matching basin ID"):
            loader.load_forcing("01099999")

        nonexistent_loader = CamelsDatasetLoader(data_dir=mock_camels_dir / "missing_root")
        with pytest.raises(FileNotFoundError, match="Required CAMELS directory not found"):
            nonexistent_loader.load_forcing("01022500")


class TestValidateForcingSchema:
    """Test suite for R1.3 CAMELS-US Daymet schema validation contract."""

    @pytest.fixture
    def valid_forcing_df(self) -> pd.DataFrame:
        """Returns a minimal valid DataFrame complying with the canonical Daymet schema."""
        dates = pd.date_range("1995-10-01", periods=3, freq="D")
        return pd.DataFrame(
            {
                "Year": [1995, 1995, 1995],
                "Mnth": [10, 10, 10],
                "Day": [1, 2, 3],
                "Hr": [12, 12, 12],
                "dayl(s)": [42300.0, 42100.0, 41900.0],
                "prcp(mm/day)": [0.0, 12.4, 5.1],
                "srad(W/m2)": [245.5, 180.2, 210.0],
                "swe(mm)": [0.0, 0.0, 0.0],
                "tmax(C)": [18.5, 14.1, 16.0],
                "tmin(C)": [6.2, 8.0, 5.5],
                "vp(Pa)": [850.0, 920.5, 780.0],
            },
            index=pd.DatetimeIndex(dates, name="date"),
        )

    def test_canonical_schema_passes_validation(self, valid_forcing_df: pd.DataFrame):
        """Verifies a fully conforming DataFrame passes validation without error."""
        validate_forcing_schema(valid_forcing_df)

    def test_missing_required_column_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies missing any required column (including raw date columns) raises ValueError."""
        for col in DAYMET_RAW_FORCING_COLUMNS:
            df_missing = valid_forcing_df.drop(columns=[col])
            with pytest.raises(ValueError, match="Missing required columns"):
                validate_forcing_schema(df_missing)

    def test_mn_instead_of_canonical_mnth_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies the non-canonical column 'Mn' is strictly rejected without silent fallback."""
        df_old_mn = valid_forcing_df.rename(columns={"Mnth": "Mn"})
        with pytest.raises(ValueError, match="Missing required columns.*Mnth"):
            validate_forcing_schema(df_old_mn)

    def test_non_numeric_meteorological_column_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies strings/non-numeric values in meteorological columns trigger ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad["prcp(mm/day)"] = ["0.0", "corrupt_str", "5.1"]
        with pytest.raises(ValueError, match="contains non-numeric data"):
            validate_forcing_schema(df_bad)

    def test_nan_in_meteorological_column_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies NaNs in meteorological columns trigger explicit ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad.loc[df_bad.index[1], "tmax(C)"] = np.nan
        with pytest.raises(ValueError, match="contains 1 NaN values"):
            validate_forcing_schema(df_bad)

    def test_inf_in_meteorological_column_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies infinite values in meteorological columns trigger explicit ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad.loc[df_bad.index[0], "srad(W/m2)"] = np.inf
        with pytest.raises(ValueError, match="contains 1 infinite values"):
            validate_forcing_schema(df_bad)

    def test_invalid_calendar_date_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies unparseable or impossible calendar dates (e.g. Feb 30) trigger ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad["Mnth"] = [2, 2, 2]
        df_bad["Day"] = [28, 29, 30]  # Feb 30, 1995 is invalid
        with pytest.raises(ValueError, match="Invalid calendar dates"):
            validate_forcing_schema(df_bad)

    def test_duplicate_dates_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies duplicate calendar dates trigger explicit ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad["Day"] = [1, 1, 3]  # Duplicate Oct 1, 1995
        with pytest.raises(ValueError, match="Duplicate calendar dates found"):
            validate_forcing_schema(df_bad)

    def test_non_monotonic_calendar_dates_rejected(self, valid_forcing_df: pd.DataFrame):
        """Verifies non-chronological raw date ordering triggers explicit ValueError."""
        df_bad = valid_forcing_df.copy()
        df_bad["Day"] = [2, 1, 3]
        with pytest.raises(
            ValueError, match="Calendar dates in forcing data are not monotonically increasing"
        ):
            validate_forcing_schema(df_bad)

    def test_raw_columns_preserved_by_loader(self, mock_camels_dir: Path):
        """Verifies load_forcing preserves Year, Mnth, Day, Hr alongside DatetimeIndex."""
        loader = CamelsDatasetLoader(data_dir=mock_camels_dir)
        df = loader.load_forcing("01022500")

        # DatetimeIndex is present
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.name == "date"

        # Raw date columns MUST be retained
        for col in ("Year", "Mnth", "Day", "Hr"):
            assert col in df.columns
            assert pd.api.types.is_integer_dtype(df[col])

        # Exact raw values preserved
        assert list(df["Year"]) == [1995, 1995, 1995]
        assert list(df["Mnth"]) == [10, 10, 10]
        assert list(df["Day"]) == [1, 2, 3]
        assert list(df["Hr"]) == [12, 12, 12]

    def test_scientific_boundary_no_physical_qc_in_r1_3(self, valid_forcing_df: pd.DataFrame):
        """
        CRITICAL SCIENTIFIC INVARIANT:
        R1.3 does NOT implement physical QC.
        Unphysical values (negative prcp, negative radiation, negative swe,
        negative vp, dayl outside range, Tmin > Tmax) must NOT be rejected
        or altered at the R1.3 schema level (deferred strictly to R1.5).
        """
        df_unphysical = valid_forcing_df.copy()
        df_unphysical.loc[df_unphysical.index[0], "prcp(mm/day)"] = -5.0
        df_unphysical.loc[df_unphysical.index[0], "srad(W/m2)"] = -10.0
        df_unphysical.loc[df_unphysical.index[0], "swe(mm)"] = -1.0
        df_unphysical.loc[df_unphysical.index[0], "vp(Pa)"] = -50.0
        df_unphysical.loc[df_unphysical.index[0], "dayl(s)"] = 999999.0
        # Tmin > Tmax
        df_unphysical.loc[df_unphysical.index[0], "tmin(C)"] = 25.0
        df_unphysical.loc[df_unphysical.index[0], "tmax(C)"] = 10.0

        # Must pass schema validation cleanly without error or clipping
        validate_forcing_schema(df_unphysical)
        assert df_unphysical.loc[df_unphysical.index[0], "prcp(mm/day)"] == -5.0
        assert df_unphysical.loc[df_unphysical.index[0], "tmin(C)"] == 25.0
        assert df_unphysical.loc[df_unphysical.index[0], "tmax(C)"] == 10.0

    def test_real_camels_dataset_smoke_test(self):
        """
        Smoke test against the actual CAMELS-US v1.2 dataset on disk, if present.
        Skipped automatically when running in environments (e.g. CI) without local data.
        """
        real_data_dir = Path("D:/CAMELS_US/basin_dataset_public_v1p2")
        if not real_data_dir.exists():
            pytest.skip(
                "Real CAMELS-US dataset not found at D:/CAMELS_US/basin_dataset_public_v1p2"
            )

        loader = CamelsDatasetLoader(data_dir=real_data_dir)
        df = loader.load_forcing("01022500")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 12784  # Exactly 1980-01-01 to 2014-12-31 (leap years included)
        assert df.index[0] == pd.Timestamp("1980-01-01")
        assert df.index[-1] == pd.Timestamp("2014-12-31")

        for col in DAYMET_RAW_FORCING_COLUMNS:
            assert col in df.columns
