"""Configuration for FOMO300K minimal preprocessing."""

import os
from pathlib import Path

DATA_ROOT = Path(os.environ.get("FOMO300K_DATA_ROOT", "/data/users/fomo2026/FOMO300K"))
OUTPUT_ROOT = Path(
    os.environ.get("FOMO300K_OUTPUT_ROOT", "/shared/home/akshatha/FOMO300K/preprocessed")
)

MIN_SLICES = 15
B0_MAX = 5  # b <= 5 treated as b0 / near-b0
SHELL_TOLERANCE = 50  # |b_i - b_j| <= 50 -> same shell
ADC_RATIO_MIN = 1e-10
ADC_RATIO_MAX = 1.0

CANONICAL_AXES = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)

# Filename suffixes treated as DWI-related in released FOMO300K layout
DWI_SUFFIXES = frozenset({"dwi"})
BVAL_PREFIX = "bval"

# Perfusion-related suffixes (multi-volume or multi-file sessions)
PERFUSION_SUFFIXES = frozenset({"asl", "cbf", "m0scan", "att"})
