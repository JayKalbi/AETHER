"""
Tests verifying basic Python environment integrity, package imports, and tensor math.
"""

import sys

import pytest
import torch


@pytest.mark.unit
def test_python_version():
    """Assert Python runtime is at least 3.10."""
    assert sys.version_info >= (3, 10), f"Python version {sys.version} is older than required 3.10"


@pytest.mark.unit
def test_core_dependencies():
    """Assert all core packages import cleanly."""
    import lightgbm as lgb
    import pandas as pd
    import scipy

    assert pd.__version__ is not None
    assert lgb.__version__ is not None
    assert torch.__version__ is not None
    assert scipy.__version__ is not None


@pytest.mark.unit
def test_pytorch_tensor_operations():
    """Verify PyTorch tensor computation and gradient backpropagation."""
    x = torch.randn(10, 5, requires_grad=True)
    w = torch.randn(5, 1)
    y = torch.matmul(x, w)
    loss = y.sum()
    loss.backward()
    assert x.grad is not None
    assert x.grad.shape == (10, 5)
