"""
Unit tests for CAMELS-US raw dataset loader (Issue R1.2).
"""

from pathlib import Path

import pandas as pd
import pytest

from aether.data.basin_registry import BenchmarkRegistry
from aether.data.camels_loader import CamelsDatasetLoader


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
        "Year Mn Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)\n"
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
            "Year Mn Day Hr dayl(s) prcp(mm/day) srad(W/m2) swe(mm) tmax(C) tmin(C) vp(Pa)\n"
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
