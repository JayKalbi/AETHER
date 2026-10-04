"""
Data ingestion, basin registry, split management, and preprocessing.
"""

from aether.data.basin_registry import (
    BenchmarkRegistry,
    compute_manifest_sha256,
    load_benchmark_registry,
)
from aether.data.camels_loader import (
    CFS_TO_M3S,
    DAYMET_METEOROLOGICAL_COLUMNS,
    DAYMET_RAW_FORCING_COLUMNS,
    DISCHARGE_CFS_TO_MM_DAY_SCALE,
    M2_PER_KM2,
    MM_PER_METER,
    SECONDS_PER_DAY,
    CamelsDatasetLoader,
    convert_discharge_cfs_to_mm_day,
    validate_forcing_schema,
)
from aether.data.qc import (
    StreamflowQCSummary,
    calculate_streamflow_missingness,
    identify_missing_streamflow,
    validate_basin_area_consistency,
)
from aether.data.split_manager import (
    SplitWindow,
    TemporalSplitManager,
)

__all__ = [
    "BenchmarkRegistry",
    "load_benchmark_registry",
    "compute_manifest_sha256",
    "CamelsDatasetLoader",
    "DAYMET_RAW_FORCING_COLUMNS",
    "DAYMET_METEOROLOGICAL_COLUMNS",
    "validate_forcing_schema",
    "convert_discharge_cfs_to_mm_day",
    "CFS_TO_M3S",
    "SECONDS_PER_DAY",
    "MM_PER_METER",
    "M2_PER_KM2",
    "DISCHARGE_CFS_TO_MM_DAY_SCALE",
    "StreamflowQCSummary",
    "identify_missing_streamflow",
    "calculate_streamflow_missingness",
    "validate_basin_area_consistency",
    "SplitWindow",
    "TemporalSplitManager",
]
