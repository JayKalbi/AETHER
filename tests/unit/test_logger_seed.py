"""
Tests verifying deterministic seed setting and structured logger output.
"""

from pathlib import Path

import numpy as np
import pytest
import torch

from aether.utils.logger import setup_logger
from aether.utils.seed import set_global_seed


@pytest.mark.unit
def test_seed_determinism():
    """Verify that setting global seed produces identical random sequences."""
    set_global_seed(42)
    a1 = np.random.randn(10)
    t1 = torch.randn(10)

    set_global_seed(42)
    a2 = np.random.randn(10)
    t2 = torch.randn(10)

    np.testing.assert_allclose(a1, a2)
    torch.testing.assert_close(t1, t2)


@pytest.mark.unit
def test_logger_file_output(tmp_path: Path):
    """Verify that structured logger outputs to file when configured."""
    log_dir = tmp_path / "logs"
    logger = setup_logger("test_logger", log_dir=log_dir)
    logger.info("AETHER research log test message.")

    log_file = log_dir / "test_logger.log"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "AETHER research log test message." in content
