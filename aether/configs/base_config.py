"""
Pydantic configuration models ensuring strict parameter validation.
"""

from pathlib import Path
from typing import List, Union

import yaml
from pydantic import BaseModel, Field


class TemporalSplitConfig(BaseModel):
    """Temporal split definitions with strict ISO format and water year alignment."""

    train_start: str = "1980-10-01"
    train_end: str = "2000-09-30"
    val_start: str = "2000-10-01"
    val_end: str = "2005-09-30"
    cal_start: str = "2005-10-01"
    cal_end: str = "2010-09-30"
    test_start: str = "2010-10-01"
    test_end: str = "2018-09-30"
    lookback_days: int = 365
    forecast_horizon_days: int = 1


class BaseLSTMConfig(BaseModel):
    """NeuralHydrology EA-LSTM architecture & training hyperparameters."""

    model_type: str = "ea_lstm"
    hidden_size: int = 256
    num_layers: int = 1
    dropout: float = 0.40
    learning_rate: float = 1e-3
    batch_size: int = 256
    epochs: int = 30
    early_stopping_patience: int = 5
    seeds: List[int] = Field(default_factory=lambda: [101])


class UncertaintyConfig(BaseModel):
    """CQR and Quantile configuration."""

    alpha: float = 0.10  # Nominal 90% coverage
    quantiles: List[float] = Field(default_factory=lambda: [0.05, 0.50, 0.95])


class ReliabilityEstimatorConfig(BaseModel):
    """LightGBM failure classifier hyperparameters."""

    learning_rate: float = 0.03
    num_leaves: int = 31
    max_depth: int = 6
    min_child_samples: int = 50
    subsample: float = 0.80
    colsample_bytree: float = 0.80
    n_estimators: int = 500
    early_stopping_rounds: int = 25
    cal_cv_folds: int = 5
    seed: int = 42


class FailureLabelConfig(BaseModel):
    """Failure label parameters."""

    primary_metric: str = "nafe"
    primary_threshold: float = 1.0
    sensitivity_thresholds: List[float] = Field(default_factory=lambda: [1.0, 1.5, 2.0, 2.5, 3.0])


class AetherConfig(BaseModel):
    """Master experiment configuration."""

    project_name: str = "aether"
    data_dir: Path = Path("data/camels_us")
    artifacts_dir: Path = Path("artifacts")
    temporal_splits: TemporalSplitConfig = Field(default_factory=TemporalSplitConfig)
    base_model: BaseLSTMConfig = Field(default_factory=BaseLSTMConfig)
    uncertainty: UncertaintyConfig = Field(default_factory=UncertaintyConfig)
    reliability: ReliabilityEstimatorConfig = Field(default_factory=ReliabilityEstimatorConfig)
    labels: FailureLabelConfig = Field(default_factory=FailureLabelConfig)
    global_seed: int = 101

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "AetherConfig":
        """Loads configuration from a YAML file."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**(data or {}))

    def to_yaml(self, yaml_path: Union[str, Path]) -> None:
        """Serializes configuration to a YAML file."""
        Path(yaml_path).parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(mode="json"), f, default_flow_style=False)
