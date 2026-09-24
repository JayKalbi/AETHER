"""
CAMELS-US Benchmark Catchment Registry.

Provides an auditable, deterministic registry for the 531 core non-impacted
CAMELS-US benchmark basins established by Newman et al. (2015, 2017) and
standardized in large-sample machine learning hydrology by Kratzert et al. (2019).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Union

import pandas as pd

from aether.utils.types import BasinMetadata


class BenchmarkRegistry:
    """
    Registry for CAMELS-US catchments and benchmark membership status.

    Parameters
    ----------
    benchmark_basins : Sequence[str]
        Explicit sequence of 8-digit USGS gauge identifiers included in the benchmark.
    metadata_map : Optional[Dict[str, BasinMetadata]]
        Catchment metadata keyed by 8-digit basin ID.
    provenance : Optional[Dict[str, Union[str, int]]]
        Provenance and audit tracking metadata for the benchmark definition.
    """

    def __init__(
        self,
        benchmark_basins: Sequence[str],
        metadata_map: Optional[Dict[str, BasinMetadata]] = None,
        provenance: Optional[Dict[str, Union[str, int]]] = None,
    ) -> None:
        # Validate and canonicalize basin identifiers
        cleaned_basins: List[str] = []
        seen: Set[str] = set()

        for b in benchmark_basins:
            basin_str = str(b).strip()
            if not (len(basin_str) == 8 and basin_str.isdigit()):
                raise ValueError(
                    f"Invalid CAMELS-US basin ID '{b}': expected 8 numeric digits, got '{basin_str}'."
                )
            if basin_str in seen:
                raise ValueError(f"Duplicate basin ID '{basin_str}' found in benchmark basin list.")
            seen.add(basin_str)
            cleaned_basins.append(basin_str)

        # Enforce deterministic alphanumeric sorting
        self._benchmark_basins: List[str] = sorted(cleaned_basins)
        self._benchmark_set: Set[str] = set(self._benchmark_basins)
        self._metadata_map: Dict[str, BasinMetadata] = metadata_map or {}
        self._provenance: Dict[str, Union[str, int]] = provenance or {}

    @property
    def total_benchmark_count(self) -> int:
        """Returns the total number of benchmark catchments in the registry."""
        return len(self._benchmark_basins)

    @property
    def provenance(self) -> Dict[str, Union[str, int]]:
        """Returns provenance metadata describing dataset origin, version, and criteria."""
        return dict(self._provenance)

    def included_basins(self) -> List[str]:
        """
        Returns a deterministically sorted list of all included 8-digit benchmark basin IDs.

        Returns
        -------
        List[str]
            Sorted list of 8-digit USGS gauge IDs.
        """
        return list(self._benchmark_basins)

    def is_included(self, basin_id: Union[str, int]) -> bool:
        """
        Queries whether a given catchment identifier belongs to the benchmark population.

        Parameters
        ----------
        basin_id : Union[str, int]
            USGS station identifier (e.g., '01022500' or 1022500).

        Returns
        -------
        bool
            True if the basin is an included benchmark catchment, False otherwise.
        """
        formatted_id = self._format_basin_id(basin_id)
        return formatted_id in self._benchmark_set

    def metadata(self, basin_id: Union[str, int]) -> Optional[BasinMetadata]:
        """
        Retrieves the typed BasinMetadata for a specific catchment if available.

        Parameters
        ----------
        basin_id : Union[str, int]
            USGS station identifier.

        Returns
        -------
        Optional[BasinMetadata]
            Basin metadata record or None if metadata has not been loaded from CAMELS files.
        """
        formatted_id = self._format_basin_id(basin_id)
        if formatted_id not in self._benchmark_set and formatted_id not in self._metadata_map:
            raise KeyError(f"Basin '{formatted_id}' is not registered in the benchmark registry.")
        return self._metadata_map.get(formatted_id)

    def register_metadata(self, metadata: BasinMetadata) -> None:
        """
        Attaches a validated BasinMetadata instance to the registry.

        Parameters
        ----------
        metadata : BasinMetadata
            Typed catchment metadata record.
        """
        basin_id = self._format_basin_id(metadata.basin_id)
        self._metadata_map[basin_id] = metadata

    @staticmethod
    def _format_basin_id(basin_id: Union[str, int]) -> str:
        """Standardizes a basin ID into an 8-character zero-padded string."""
        s = str(basin_id).strip()
        if len(s) < 8 and s.isdigit():
            s = s.zfill(8)
        if len(s) != 8 or not s.isdigit():
            raise ValueError(
                f"Invalid basin ID format: '{basin_id}'. Expected an 8-digit numeric identifier."
            )
        return s


def load_benchmark_registry(
    manifest_path: Optional[Union[str, Path]] = None,
    attributes_dir: Optional[Union[str, Path]] = None,
) -> BenchmarkRegistry:
    """
    Loads the canonical CAMELS-US 531-basin benchmark registry.

    This function operates fully offline without network access, loading the
    curated, auditable benchmark manifest bundled within the package.
    Optionally enriches the registry with static physical attributes from a local
    CAMELS attributes directory (`camels_attributes_v2.0/`).

    Parameters
    ----------
    manifest_path : Optional[Union[str, Path]]
        Explicit path to a JSON manifest. If None, defaults to the canonical
        package manifest `aether/data/camels_us_benchmark_531.json`.
    attributes_dir : Optional[Union[str, Path]]
        Optional path to the `camels_attributes_v2.0` directory containing
        `camels_topo.txt`, `camels_clim.txt`, etc.

    Returns
    -------
    BenchmarkRegistry
        Instantiated and validated benchmark registry containing 531 catchments.
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent / "camels_us_benchmark_531.json"
    else:
        manifest_path = Path(manifest_path)

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"CAMELS benchmark manifest file not found at: {manifest_path.resolve()}"
        )

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "basins" not in data or not isinstance(data["basins"], list):
        raise ValueError(
            f"Invalid manifest structure in {manifest_path}: expected top-level key 'basins' with a list."
        )

    basins: List[str] = data["basins"]
    provenance: Dict[str, Union[str, int]] = data.get("provenance", {})

    expected_count = provenance.get("count", 531)
    if len(basins) != expected_count:
        raise ValueError(
            f"Manifest basin count mismatch: expected {expected_count}, found {len(basins)} in {manifest_path}."
        )

    metadata_map: Dict[str, BasinMetadata] = {}

    # If attributes directory is supplied, ingest metadata for all catchments
    if attributes_dir is not None:
        attr_path = Path(attributes_dir)
        if attr_path.exists():
            metadata_map = _load_metadata_from_attributes(attr_path, basins)

    return BenchmarkRegistry(
        benchmark_basins=basins,
        metadata_map=metadata_map,
        provenance=provenance,
    )


def compute_manifest_sha256(manifest_path: Optional[Union[str, Path]] = None) -> str:
    """
    Computes the SHA-256 digest of the canonical benchmark manifest file.

    Parameters
    ----------
    manifest_path : Optional[Union[str, Path]]
        Path to manifest file. If None, uses canonical packaged manifest.

    Returns
    -------
    str
        Hexadecimal SHA-256 hash string for experiment metadata provenance logging.
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent / "camels_us_benchmark_531.json"
    else:
        manifest_path = Path(manifest_path)

    hasher = hashlib.sha256()
    with open(manifest_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _load_metadata_from_attributes(
    attributes_dir: Path,
    benchmark_basins: Sequence[str],
) -> Dict[str, BasinMetadata]:
    """
    Internal helper to parse static CAMELS attributes into typed BasinMetadata records.
    """
    topo_file = attributes_dir / "camels_topo.txt"
    clim_file = attributes_dir / "camels_clim.txt"

    if not (topo_file.exists() and clim_file.exists()):
        return {}

    # Read topo attributes (semicolon-separated per CAMELS v2.0 convention)
    df_topo = pd.read_csv(topo_file, sep=";", dtype={"gauge_id": str})
    df_topo["gauge_id"] = df_topo["gauge_id"].str.strip().str.zfill(8)
    df_topo = df_topo.set_index("gauge_id")

    # Read clim attributes
    df_clim = pd.read_csv(clim_file, sep=";", dtype={"gauge_id": str})
    df_clim["gauge_id"] = df_clim["gauge_id"].str.strip().str.zfill(8)
    df_clim = df_clim.set_index("gauge_id")

    metadata_map: Dict[str, BasinMetadata] = {}
    benchmark_set = set(benchmark_basins)

    for gauge_id, topo_row in df_topo.iterrows():
        gauge_str = str(gauge_id)
        if gauge_str not in df_clim.index:
            continue

        clim_row = df_clim.loc[gauge_str]
        is_bench = gauge_str in benchmark_set

        # Determine HUC 02
        huc_02 = str(topo_row.get("huc_02", gauge_str[:2])).zfill(2)

        record = BasinMetadata(
            basin_id=gauge_str,
            huc_02=huc_02,
            area_km2=float(topo_row.get("area_gages2", 0.0)),
            lat=float(topo_row.get("gauge_lat", 0.0)),
            lon=float(topo_row.get("gauge_lon", 0.0)),
            elevation_mean_m=float(topo_row.get("elev_mean", 0.0)),
            slope_mean_m_per_km=float(topo_row.get("slope_mean", 0.0)),
            aridity_index=float(clim_row.get("aridity", 0.0)),
            fraction_snow=float(clim_row.get("frac_snow", 0.0)),
            is_benchmark=is_bench,
            exclusion_reason=None if is_bench else "Catchment area > 2000 km2 or area discrepancy > 10%",
        )
        metadata_map[gauge_str] = record

    return metadata_map
