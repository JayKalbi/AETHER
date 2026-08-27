"""
Domain-specific types, enums, and data models for AETHER.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TemporalSplit(str, Enum):
    """Frozen temporal partitions for water-year hydrological splits."""

    TRAIN = "train"  # [1980-10-01, 2000-09-30]
    VAL = "val"  # [2000-10-01, 2005-09-30]
    CAL = "cal"  # [2005-10-01, 2010-09-30]
    TEST = "test"  # [2010-10-01, 2018-09-30]


class FeatureGroup(str, Enum):
    """Categorization of predictive signals according to epistemic source."""

    CONTEXT = "context"  # Group A: Climatological / temporal context
    OOD = "ood"  # Group B: Input-space distribution shifts
    MODEL_OUTPUT = "model_output"  # Group C: Base model point predictions & deltas
    UNCERTAINTY = "uncertainty"  # Group D: Quantile spreads & ensemble variance
    HYDRO_DOMAIN = "hydro_domain"  # Group E: Hydrologically motivated state proxies


class FailureLabelType(str, Enum):
    """Taxonomy of forecast failure definitions."""

    NAFE = "nafe"  # Normalized Absolute Forecast Error (Primary)
    FLOOD_MISCLASSIFICATION = "flood_mis"  # False Alarm / Missed Flood Warning (Secondary)
    INTERVAL_MISS = "interval_miss"  # Realization outside prediction interval (Secondary)
    EXTREME_ERROR = "extreme_error"  # Failure specifically on high-flow days (Secondary)
    PEAK_ERROR = "peak_error"  # Peak magnitude error on hydrograph peaks (Secondary)


class SelectiveAction(str, Enum):
    """Operational decision states."""

    RELEASE = "RELEASE"  # Low failure risk: publish forecast
    ABSTAIN = "ABSTAIN"  # High failure risk: flag for human forecaster review


class BasinMetadata(BaseModel):
    """Metadata record for an individual catchment in CAMELS-US."""

    basin_id: str
    huc_02: str
    area_km2: float
    lat: float
    lon: float
    elevation_mean_m: float
    slope_mean_m_per_km: float
    aridity_index: float
    fraction_snow: float
    is_benchmark: bool = True
    exclusion_reason: Optional[str] = None
