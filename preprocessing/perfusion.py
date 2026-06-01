"""Perfusion / ASL preprocessing."""

from __future__ import annotations

import numpy as np


def process_perfusion_stack(data: np.ndarray) -> np.ndarray:
    """
    Reduce 4D perfusion stack to 3D.

    >3 channels: mean across channels.
    2–3 channels: last - first.
    """
    if data.ndim == 3:
        return data.astype(np.float32)
    if data.ndim != 4:
        raise ValueError(f"Expected 3D or 4D perfusion data, got {data.shape}")

    n_channels = data.shape[-1]
    if n_channels > 3:
        return np.mean(data, axis=-1).astype(np.float32)
    if n_channels >= 2:
        return (data[..., -1] - data[..., 0]).astype(np.float32)
    return data[..., 0].astype(np.float32)
