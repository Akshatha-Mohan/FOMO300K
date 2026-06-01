"""DWI preprocessing: b0 extraction, shell grouping, axis-aligned selection."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from preprocessing.config import (
    ADC_RATIO_MAX,
    ADC_RATIO_MIN,
    B0_MAX,
    CANONICAL_AXES,
    SHELL_TOLERANCE,
)


@dataclass
class DWIVolume:
    data: np.ndarray
    b_value: float
    gradient: tuple[float, float, float] | None = None


def parse_bval_suffix(name: str) -> float | None:
    """Parse b-value from filenames like bval0, bval1000, sub-01_bval2000."""
    m = re.search(r"bval(\d+(?:\.\d+)?)", name.lower())
    return float(m.group(1)) if m else None


def is_b0(b: float) -> bool:
    return b <= B0_MAX


def group_into_shells(b_values: list[float], tolerance: int = SHELL_TOLERANCE) -> list[list[int]]:
    """Group volume indices into b-shells (excluding b0 indices)."""
    non_b0 = [(i, b) for i, b in enumerate(b_values) if not is_b0(b)]
    if not non_b0:
        return []

    shells: list[list[int]] = []
    used = set()

    for i, b in sorted(non_b0, key=lambda x: x[1]):
        if i in used:
            continue
        shell = [i]
        used.add(i)
        for j, bj in non_b0:
            if j in used:
                continue
            if abs(bj - b) <= tolerance:
                shell.append(j)
                used.add(j)
        shells.append(shell)

    return shells


def _cosine_sim(g: np.ndarray, axis: tuple[float, float, float]) -> float:
    a = np.array(axis, dtype=np.float64)
    gn = np.linalg.norm(g)
    if gn < 1e-8:
        return -1.0
    return float(np.dot(g / gn, a / np.linalg.norm(a)))


def select_axis_aligned_indices(
    gradients: list[tuple[float, float, float] | None],
    shell_indices: list[int],
) -> list[int]:
    """Pick one volume per canonical axis (+x, +y, +z) within a shell."""
    if not shell_indices:
        return []

    # Default evenly spaced indices if gradients unknown
    if all(g is None for g in (gradients[i] for i in shell_indices)):
        n = len(shell_indices)
        if n >= 3:
            picks = [shell_indices[0], shell_indices[n // 2], shell_indices[-1]]
        else:
            picks = shell_indices[:3]
        while len(picks) < 3:
            picks.append(picks[-1])
        return picks[:3]

    chosen: list[int] = []
    used = set()
    for axis in CANONICAL_AXES:
        best_i, best_sim = None, -2.0
        for i in shell_indices:
            if i in used:
                continue
            g = gradients[i]
            if g is None:
                continue
            sim = _cosine_sim(np.array(g), axis)
            if sim > best_sim:
                best_sim, best_i = sim, i
        if best_i is None:
            for i in shell_indices:
                if i not in used:
                    best_i = i
                    break
        if best_i is not None:
            chosen.append(best_i)
            used.add(best_i)

    while len(chosen) < 3 and shell_indices:
        for i in shell_indices:
            if i not in used:
                chosen.append(i)
                used.add(i)
                break
        else:
            break
    return chosen[:3]


def average_volumes(volumes: list[np.ndarray]) -> np.ndarray:
    return np.mean(np.stack(volumes, axis=0), axis=0)


def compute_trace_adc(
    s0: np.ndarray,
    volumes: list[np.ndarray],
    b_values: list[float],
) -> np.ndarray:
    """Trace ADC = ADC_x + ADC_y + ADC_z per paper."""
    trace = np.zeros_like(s0, dtype=np.float64)
    for vol, b in zip(volumes, b_values):
        if b <= 0:
            continue
        ratio = np.zeros_like(s0, dtype=np.float64)
        valid = (s0 > 0) & (vol > 0) & (vol <= s0)
        ratio[valid] = np.clip(vol[valid] / s0[valid], ADC_RATIO_MIN, ADC_RATIO_MAX)
        adc = np.zeros_like(s0, dtype=np.float64)
        adc[valid] = -np.log(ratio[valid]) / b
        trace += adc
    return trace.astype(np.float32)


def use_trace_adc_strategy(scan_key: str) -> bool:
    """Deterministic 50/50 split for mean vs trace-ADC (SSL variability)."""
    return (hash(scan_key) & 1) == 1


def process_dwi_session(
    volumes: list[DWIVolume],
    scan_key: str,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """
    Process a session's DWI volumes.

    Returns (b0_volume_or_none, processed_3d_per_shell_or_combined).
    For multiple shells, returns mean of per-shell 3D outputs stacked logic:
    caller should run per shell; here we process the dominant non-b0 shell.
    """
    if not volumes:
        return None, None

    b_values = [v.b_value for v in volumes]
    b0_indices = [i for i, b in enumerate(b_values) if is_b0(b)]

    s0_data = None
    if b0_indices:
        s0_data = average_volumes([volumes[i].data for i in b0_indices])

    shells = group_into_shells(b_values)
    if not shells:
        if s0_data is not None:
            return s0_data, s0_data
        return None, average_volumes([v.data for v in volumes])

    # Process largest shell
    shell = max(shells, key=len)
    shell_b = float(np.median([b_values[i] for i in shell]))
    grads = [v.gradient for v in volumes]
    pick = select_axis_aligned_indices(grads, shell)
    picked_vols = [volumes[i].data for i in pick]
    picked_b = [b_values[i] for i in pick]

    if s0_data is None:
        out = average_volumes(picked_vols)
        return None, out

    if use_trace_adc_strategy(scan_key):
        out = compute_trace_adc(s0_data, picked_vols, picked_b)
    else:
        out = average_volumes(picked_vols)

    return s0_data, out
