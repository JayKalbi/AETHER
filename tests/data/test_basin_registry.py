"""
Unit and regression tests for CAMELS-US benchmark basin registry.
"""

import json
from pathlib import Path

import pytest

from aether.data.basin_registry import (
    BenchmarkRegistry,
    compute_manifest_sha256,
    load_benchmark_registry,
)
from aether.utils.types import BasinMetadata


class TestBenchmarkRegistry:
    """Test suite validating BenchmarkRegistry mechanics, integrity, and safety invariants."""

    def test_load_default_registry(self):
        """1. Registry can be loaded with default parameters without network access."""
        registry = load_benchmark_registry()
        assert isinstance(registry, BenchmarkRegistry)
        assert registry.total_benchmark_count == 531

    def test_expected_benchmark_population(self):
        """2. Registry contains the expected 531 benchmark population count."""
        registry = load_benchmark_registry()
        basins = registry.included_basins()
        assert len(basins) == 531
        assert len(set(basins)) == 531

    def test_basin_ids_format_and_uniqueness(self):
        """3 & 4. All basin IDs are 8 numeric characters, uniquely identified, and zero-padded."""
        registry = load_benchmark_registry()
        basins = registry.included_basins()
        for b in basins:
            assert isinstance(b, str)
            assert len(b) == 8
            assert b.isdigit()

    def test_registry_ordering_is_deterministic(self):
        """5. Registry ordering is deterministically sorted."""
        registry = load_benchmark_registry()
        basins_1 = registry.included_basins()
        basins_2 = registry.included_basins()
        assert basins_1 == basins_2
        assert basins_1 == sorted(basins_1)

    def test_is_included_lookup(self):
        """6. Inclusion queries handle string and integer formats with deterministic behavior."""
        registry = load_benchmark_registry()

        # Known benchmark basins
        assert registry.is_included("01022500") is True
        assert registry.is_included(1022500) is True  # Automatic zero-padding
        assert registry.is_included("14400000") is True

        # Known non-benchmark / excluded basins
        assert registry.is_included("99999999") is False
        assert registry.is_included("00000000") is False

    def test_unknown_basin_metadata_behavior(self):
        """7. Querying metadata for unknown basin raises explicit KeyError."""
        registry = load_benchmark_registry()
        with pytest.raises(KeyError, match="not registered"):
            registry.metadata("99999999")

    def test_invalid_basin_id_formats_rejected(self):
        """8. Invalid basin ID formats are strictly rejected."""
        registry = load_benchmark_registry()
        with pytest.raises(ValueError, match="Invalid basin ID format"):
            registry.is_included("invalid_id")

        with pytest.raises(ValueError, match="Invalid basin ID format"):
            registry.is_included("123456789")  # 9 digits

        with pytest.raises(ValueError, match="Invalid CAMELS-US basin ID"):
            BenchmarkRegistry(benchmark_basins=["invalid_id"])

    def test_duplicate_basin_ids_rejected(self):
        """9. Duplicate basin IDs during instantiation raise ValueError."""
        with pytest.raises(ValueError, match="Duplicate basin ID"):
            BenchmarkRegistry(benchmark_basins=["01022500", "01022500"])

    def test_missing_manifest_raises_filenotfound(self, tmp_path: Path):
        """10. Attempting to load a nonexistent manifest raises FileNotFoundError."""
        nonexistent = tmp_path / "nonexistent_manifest.json"
        with pytest.raises(FileNotFoundError):
            load_benchmark_registry(manifest_path=nonexistent)

    def test_corrupted_manifest_rejected(self, tmp_path: Path):
        """11. Manifest with incorrect basin count or corrupt structure is rejected."""
        corrupt_manifest = tmp_path / "corrupt_manifest.json"
        with open(corrupt_manifest, "w", encoding="utf-8") as f:
            json.dump({"provenance": {"count": 531}, "basins": ["01022500"]}, f)

        with pytest.raises(ValueError, match="Manifest basin count mismatch"):
            load_benchmark_registry(manifest_path=corrupt_manifest)

        invalid_structure = tmp_path / "invalid_structure.json"
        with open(invalid_structure, "w", encoding="utf-8") as f:
            json.dump({"some_other_key": 123}, f)

        with pytest.raises(ValueError, match="Invalid manifest structure"):
            load_benchmark_registry(manifest_path=invalid_structure)

    def test_provenance_metadata_available(self):
        """12. Provenance metadata is accessible and accurately reflects dataset sources."""
        registry = load_benchmark_registry()
        prov = registry.provenance
        assert isinstance(prov, dict)
        assert prov.get("dataset") == "CAMELS-US"
        assert prov.get("version") == "v1.2"
        assert prov.get("count") == 531
        assert "Newman et al." in prov.get("source", "")
        assert "criteria" in prov

    def test_manifest_sha256_computation(self):
        """13. Manifest SHA256 digest is computable and deterministic."""
        digest = compute_manifest_sha256()
        assert isinstance(digest, str)
        assert len(digest) == 64
        # Recomputing gives exact same result
        assert compute_manifest_sha256() == digest

    def test_register_and_query_metadata(self):
        """14. Metadata registration and retrieval works seamlessly with typed BasinMetadata."""
        registry = load_benchmark_registry()
        meta = BasinMetadata(
            basin_id="01022500",
            huc_02="01",
            area_km2=619.5,
            lat=44.6,
            lon=-67.9,
            elevation_mean_m=84.0,
            slope_mean_m_per_km=15.0,
            aridity_index=0.65,
            fraction_snow=0.20,
            is_benchmark=True,
        )
        registry.register_metadata(meta)
        retrieved = registry.metadata("01022500")
        assert retrieved is not None
        assert retrieved.basin_id == "01022500"
        assert retrieved.area_km2 == 619.5
        assert retrieved.is_benchmark is True

    def test_load_metadata_from_attributes_directory(self, tmp_path: Path):
        """15. Registry successfully parses static CAMELS attributes files when provided."""
        attr_dir = tmp_path / "camels_attributes_v2.0"
        attr_dir.mkdir()

        # Create mock camels_topo.txt
        topo_content = (
            "gauge_id;huc_02;gauge_lat;gauge_lon;elev_mean;slope_mean;area_gages2\n"
            "01022500;01;44.60744;-67.93524;84.0;15.2;619.5\n"
            "01031500;01;45.17505;-69.31472;201.0;22.4;769.0\n"
        )
        with open(attr_dir / "camels_topo.txt", "w", encoding="utf-8") as f:
            f.write(topo_content)

        # Create mock camels_clim.txt
        clim_content = (
            "gauge_id;p_mean;pet_mean;aridity;frac_snow\n"
            "01022500;3.45;2.20;0.6377;0.22\n"
            "01031500;3.20;2.10;0.6562;0.31\n"
        )
        with open(attr_dir / "camels_clim.txt", "w", encoding="utf-8") as f:
            f.write(clim_content)

        registry = load_benchmark_registry(attributes_dir=attr_dir)
        meta_1 = registry.metadata("01022500")
        assert meta_1 is not None
        assert meta_1.basin_id == "01022500"
        assert meta_1.area_km2 == 619.5
        assert meta_1.elevation_mean_m == 84.0
        assert meta_1.aridity_index == pytest.approx(0.6377)
        assert meta_1.is_benchmark is True

    def test_compute_manifest_sha256_with_explicit_path(self, tmp_path: Path):
        """16. compute_manifest_sha256 handles explicit file paths correctly."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": 123}', encoding="utf-8")
        h = compute_manifest_sha256(test_file)
        assert len(h) == 64

    def test_load_metadata_empty_when_missing_files(self, tmp_path: Path):
        """17. Attribute loading safely returns empty map if topo/clim files do not exist."""
        empty_attr_dir = tmp_path / "empty_attributes"
        empty_attr_dir.mkdir()
        registry = load_benchmark_registry(attributes_dir=empty_attr_dir)
        assert registry.total_benchmark_count == 531
