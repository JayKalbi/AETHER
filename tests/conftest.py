"""
Pytest fixtures for AETHER testing.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aether.configs.base_config import AetherConfig
from aether.utils.seed import set_global_seed


@pytest.fixture(autouse=True)
def setup_seed():
    """Sets a deterministic random seed before every test."""
    set_global_seed(101)


@pytest.fixture
def sample_config(tmp_path: Path) -> AetherConfig:
    """Returns an in-memory AetherConfig with temporary directories."""
    config = AetherConfig(
        project_name="aether_test",
        data_dir=tmp_path / "data",
        artifacts_dir=tmp_path / "artifacts",
        global_seed=101,
    )
    return config


@pytest.fixture
def sample_synthetic_basin_df() -> pd.DataFrame:
    """Generates 40 years of synthetic daily hydrological data for testing."""
    dates = pd.date_range(start="1980-01-01", end="2019-12-31", freq="D")
    n = len(dates)

    np.random.seed(101)
    prcp = np.random.exponential(scale=3.0, size=n)
    tmin = 5.0 + 10.0 * np.sin(2 * np.pi * np.arange(n) / 365.25) + np.random.normal(0, 2, size=n)
    tmax = tmin + np.random.uniform(5.0, 15.0, size=n)
    srad = np.maximum(
        50.0,
        200.0 + 150.0 * np.sin(2 * np.pi * np.arange(n) / 365.25) + np.random.normal(0, 20, size=n),
    )
    vp = np.maximum(
        100.0,
        1000.0
        + 500.0 * np.sin(2 * np.pi * np.arange(n) / 365.25)
        + np.random.normal(0, 50, size=n),
    )

    # Synthetic streamflow with lag and baseflow
    q = np.zeros(n)
    q[0] = 1.0
    for i in range(1, n):
        q[i] = 0.90 * q[i - 1] + 0.10 * prcp[i - 1] + np.random.exponential(scale=0.1)

    df = pd.DataFrame(
        {
            "prcp(mm/day)": prcp,
            "tmin(C)": tmin,
            "tmax(C)": tmax,
            "srad(W/m2)": srad,
            "vp(Pa)": vp,
            "streamflow": q,
        },
        index=dates,
    )
    return df
