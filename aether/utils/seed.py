"""
Deterministic random seed management across PyTorch, NumPy, Python standard library, and LightGBM.
"""

import os
import random

import numpy as np
import torch


def set_global_seed(seed: int = 101, deterministic_cudnn: bool = True) -> int:
    """
    Sets global deterministic seeds across all random number generators.

    Args:
        seed: Master random seed.
        deterministic_cudnn: If True, enforces deterministic PyTorch backend execution.

    Returns:
        The active seed integer.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic_cudnn:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    return seed
