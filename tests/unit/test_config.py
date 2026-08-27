"""
Tests verifying configuration validation, default parsing, and serialization.
"""

from pathlib import Path

import pytest

from aether.configs.base_config import AetherConfig


@pytest.mark.unit
def test_default_config_instantiation():
    """Verify that AetherConfig instantiates cleanly with default values."""
    config = AetherConfig()
    assert config.project_name == "aether"
    assert config.global_seed == 101
    assert config.temporal_splits.train_start == "1980-10-01"
    assert config.temporal_splits.test_end == "2018-09-30"
    assert config.base_model.hidden_size == 256
    assert config.reliability.learning_rate == 0.03


@pytest.mark.unit
def test_config_yaml_roundtrip(tmp_path: Path):
    """Verify that YAML serialization and deserialization are lossless."""
    config = AetherConfig(project_name="aether_roundtrip_test", global_seed=999)
    yaml_file = tmp_path / "test_config.yaml"
    config.to_yaml(yaml_file)

    loaded = AetherConfig.from_yaml(yaml_file)
    assert loaded.project_name == "aether_roundtrip_test"
    assert loaded.global_seed == 999
    assert loaded.temporal_splits.lookback_days == 365
